package core

import (
	"context"
	"encoding/json"
	"fmt"
	"sync"
	"time"

	"github.com/sirupsen/logrus"
)

// EventBus provides event-driven communication between modules
type EventBus struct {
	subscribers map[string][]chan Event
	mutex      sync.RWMutex
	logger     *logrus.Logger
}

// Event represents a message passed between modules
type Event struct {
	ID        string                 `json:"id"`
	Type      string                 `json:"type"`
	Source    string                 `json:"source"`
	Target    string                 `json:"target,omitempty"`
	Data      map[string]interface{} `json:"data"`
	Timestamp time.Time              `json:"timestamp"`
	ReplyTo   string                 `json:"reply_to,omitempty"`
}

// EventSubscription represents a subscription to events
type EventSubscription struct {
	ID       string    `json:"id"`
	Module   string    `json:"module"`
	Topics   []string  `json:"topics"`
	Handler  func(Event) error `json:"-"`
	Active   bool      `json:"active"`
	Created  time.Time `json:"created"`
}

// NewEventBus creates a new event bus
func NewEventBus(logger *logrus.Logger) *EventBus {
	if logger == nil {
		logger = logrus.New()
	}
	
	return &EventBus{
		subscribers: make(map[string][]chan Event),
		logger:     logger,
	}
}

// Subscribe subscribes to events of a specific type
func (eb *EventBus) Subscribe(eventType string, handler chan Event) error {
	eb.mutex.Lock()
	defer eb.mutex.Unlock()
	
	if eb.subscribers[eventType] == nil {
		eb.subscribers[eventType] = make([]chan Event, 0)
	}
	
	eb.subscribers[eventType] = append(eb.subscribers[eventType], handler)
	
	eb.logger.WithFields(logrus.Fields{
		"event_type": eventType,
		"subscribers": len(eb.subscribers[eventType]),
	}).Debug("New subscription added")
	
	return nil
}

// Unsubscribe removes a subscription
func (eb *EventBus) Unsubscribe(eventType string, handler chan Event) error {
	eb.mutex.Lock()
	defer eb.mutex.Unlock()
	
	subscribers, exists := eb.subscribers[eventType]
	if !exists {
		return fmt.Errorf("no subscribers for event type: %s", eventType)
	}
	
	// Remove the handler
	for i, h := range subscribers {
		if h == handler {
			eb.subscribers[eventType] = append(subscribers[:i], subscribers[i+1:]...)
			break
		}
	}
	
	// Clean up if no subscribers left
	if len(eb.subscribers[eventType]) == 0 {
		delete(eb.subscribers, eventType)
	}
	
	return nil
}

// Publish publishes an event to all subscribers
func (eb *EventBus) Publish(ctx context.Context, event Event) error {
	eb.mutex.RLock()
	defer eb.mutex.RUnlock()
	
	// Set timestamp if not provided
	if event.Timestamp.IsZero() {
		event.Timestamp = time.Now()
	}
	
	// Generate ID if not provided
	if event.ID == "" {
		event.ID = fmt.Sprintf("evt_%d_%s", time.Now().UnixNano(), event.Type)
	}
	
	subscribers, exists := eb.subscribers[event.Type]
	if !exists {
		eb.logger.WithField("event_type", event.Type).Debug("No subscribers for event type")
		return nil
	}
	
	// Send to all subscribers
	for _, handler := range subscribers {
		select {
		case handler <- event:
			eb.logger.WithFields(logrus.Fields{
				"event_id":   event.ID,
				"event_type": event.Type,
				"target":     event.Target,
			}).Debug("Event published")
		case <-ctx.Done():
			return ctx.Err()
		default:
			eb.logger.WithField("event_id", event.ID).Warn("Subscriber channel full, dropping event")
		}
	}
	
	return nil
}

// RequestResponse sends a request and waits for a response
func (eb *EventBus) RequestResponse(ctx context.Context, request Event, timeout time.Duration) (*Event, error) {
	responseChan := make(chan Event, 1)
	replyID := fmt.Sprintf("reply_%d", time.Now().UnixNano())
	
	// Subscribe for response
	responseType := fmt.Sprintf("%s_response", request.Type)
	err := eb.Subscribe(responseType, responseChan)
	if err != nil {
		return nil, fmt.Errorf("failed to subscribe for response: %w", err)
	}
	defer eb.Unsubscribe(responseType, responseChan)
	
	// Set reply to field
	request.ReplyTo = replyID
	
	// Send request
	err = eb.Publish(ctx, request)
	if err != nil {
		return nil, fmt.Errorf("failed to publish request: %w", err)
	}
	
	// Wait for response
	select {
	case response := <-responseChan:
		if response.ReplyTo == replyID {
			return &response, nil
		}
		return nil, fmt.Errorf("received mismatched response")
	case <-time.After(timeout):
		return nil, fmt.Errorf("request timeout after %v", timeout)
	case <-ctx.Done():
		return nil, ctx.Err()
	}
}

// GetSubscriberCount returns the number of subscribers for an event type
func (eb *EventBus) GetSubscriberCount(eventType string) int {
	eb.mutex.RLock()
	defer eb.mutex.RUnlock()
	
	return len(eb.subscribers[eventType])
}

// ListEventTypes returns all active event types
func (eb *EventBus) ListEventTypes() []string {
	eb.mutex.RLock()
	defer eb.mutex.RUnlock()
	
	types := make([]string, 0, len(eb.subscribers))
	for eventType := range eb.subscribers {
		types = append(types, eventType)
	}
	return types
}

// ModuleCommunicator provides bidirectional communication between modules
type ModuleCommunicator struct {
	moduleName string
	eventBus   *EventBus
	handlers   map[string]func(Event) error
	mutex      sync.RWMutex
	logger     *logrus.Logger
}

// NewModuleCommunicator creates a new module communicator
func NewModuleCommunicator(moduleName string, eventBus *EventBus, logger *logrus.Logger) *ModuleCommunicator {
	if logger == nil {
		logger = logrus.New()
	}
	
	mc := &ModuleCommunicator{
		moduleName: moduleName,
		eventBus:   eventBus,
		handlers:   make(map[string]func(Event) error),
		logger:     logger,
	}
	
	return mc
}

// RegisterHandler registers a handler for a specific event type
func (mc *ModuleCommunicator) RegisterHandler(eventType string, handler func(Event) error) error {
	mc.mutex.Lock()
	defer mc.mutex.Unlock()
	
	mc.handlers[eventType] = handler
	
	// Subscribe to event bus
	eventChan := make(chan Event, 100)
	return mc.eventBus.Subscribe(eventType, eventChan)
}

// SendMessage sends a message to another module
func (mc *ModuleCommunicator) SendMessage(ctx context.Context, targetModule, eventType string, data map[string]interface{}) error {
	event := Event{
		Type:   eventType,
		Source: mc.moduleName,
		Target: targetModule,
		Data:   data,
	}
	
	return mc.eventBus.Publish(ctx, event)
}

// Request sends a request and waits for response
func (mc *ModuleCommunicator) Request(ctx context.Context, targetModule, eventType string, data map[string]interface{}, timeout time.Duration) (*Event, error) {
	event := Event{
		Type:   eventType,
		Source: mc.moduleName,
		Target: targetModule,
		Data:   data,
	}
	
	return mc.eventBus.RequestResponse(ctx, event, timeout)
}

// Broadcast sends a message to all modules
func (mc *ModuleCommunicator) Broadcast(ctx context.Context, eventType string, data map[string]interface{}) error {
	event := Event{
		Type:   eventType,
		Source: mc.moduleName,
		Data:   data,
	}
	
	return mc.eventBus.Publish(ctx, event)
}

// GetModuleName returns the module name
func (mc *ModuleCommunicator) GetModuleName() string {
	return mc.moduleName
}

// Close closes the communicator
func (mc *ModuleCommunicator) Close() error {
	mc.logger.WithField("module", mc.moduleName).Info("Module communicator closed")
	return nil
}