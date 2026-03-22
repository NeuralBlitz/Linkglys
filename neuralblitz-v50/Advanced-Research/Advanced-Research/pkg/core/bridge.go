package core

import (
	"context"
	"encoding/json"
	"fmt"
	"sync"
	"time"

	"github.com/sirupsen/logrus"
)

// ModuleInterface defines the interface that all modules must implement
type ModuleInterface interface {
	Initialize(ctx context.Context) error
	Start(ctx context.Context) error
	Stop(ctx context.Context) error
	GetStatus() ModuleStatus
	GetName() string
	GetCapabilities() []string
	HandleRequest(ctx context.Context, req *ModuleRequest) (*ModuleResponse, error)
}

// ModuleStatus represents the status of a module
type ModuleStatus string

const (
	StatusStopped   ModuleStatus = "stopped"
	StatusStarting ModuleStatus = "starting"
	StatusRunning  ModuleStatus = "running"
	StatusStopping ModuleStatus = "stopping"
	StatusError    ModuleStatus = "error"
)

// ModuleRequest represents a request between modules
type ModuleRequest struct {
	ID        string                 `json:"id"`
	Type      string                 `json:"type"`
	Source    string                 `json:"source"`
	Target    string                 `json:"target"`
	Data      map[string]interface{} `json:"data"`
	Timestamp time.Time              `json:"timestamp"`
	Timeout   time.Duration          `json:"timeout"`
}

// ModuleResponse represents a response from a module
type ModuleResponse struct {
	ID        string                 `json:"id"`
	Type      string                 `json:"type"`
	Source    string                 `json:"source"`
	Target    string                 `json:"target"`
	Data      map[string]interface{} `json:"data"`
	Timestamp time.Time              `json:"timestamp"`
	Success   bool                   `json:"success"`
	Error     string                 `json:"error,omitempty"`
	Metadata  map[string]interface{} `json:"metadata,omitempty"`
}

// BidirectionalBridge provides bidirectional communication between modules
type BidirectionalBridge struct {
	modules     map[string]ModuleInterface
	communicators map[string]*ModuleCommunicator
	eventBus    *EventBus
	router      *RequestRouter
	mutex       sync.RWMutex
	logger      *logrus.Logger
}

// RequestRouter routes requests between modules
type RequestRouter struct {
	modules map[string]ModuleInterface
	mutex   sync.RWMutex
}

// NewRequestRouter creates a new request router
func NewRequestRouter() *RequestRouter {
	return &RequestRouter{
		modules: make(map[string]ModuleInterface),
	}
}

// AddModule adds a module to the router
func (rr *RequestRouter) AddModule(module ModuleInterface) error {
	rr.mutex.Lock()
	defer rr.mutex.Unlock()
	
	name := module.GetName()
	if _, exists := rr.modules[name]; exists {
		return fmt.Errorf("module %s already registered", name)
	}
	
	rr.modules[name] = module
	return nil
}

// RouteRequest routes a request to the target module
func (rr *RequestRouter) RouteRequest(ctx context.Context, req *ModuleRequest) (*ModuleResponse, error) {
	rr.mutex.RLock()
	defer rr.mutex.RUnlock()
	
	module, exists := rr.modules[req.Target]
	if !exists {
		return nil, fmt.Errorf("target module %s not found", req.Target)
	}
	
	// Check if module can handle the request
	if module.GetStatus() != StatusRunning {
		return nil, fmt.Errorf("module %s is not running (status: %s)", req.Target, module.GetStatus())
	}
	
	return module.HandleRequest(ctx, req)
}

// ListModules returns a list of registered modules
func (rr *RequestRouter) ListModules() []string {
	rr.mutex.RLock()
	defer rr.mutex.RUnlock()
	
	modules := make([]string, 0, len(rr.modules))
	for name := range rr.modules {
		modules = append(modules, name)
	}
	return modules
}

// NewBidirectionalBridge creates a new bidirectional bridge
func NewBidirectionalBridge(logger *logrus.Logger) *BidirectionalBridge {
	if logger == nil {
		logger = logrus.New()
	}
	
	eventBus := NewEventBus(logger)
	
	return &BidirectionalBridge{
		modules:       make(map[string]ModuleInterface),
		communicators: make(map[string]*ModuleCommunicator),
		eventBus:      eventBus,
		router:        NewRequestRouter(),
		logger:        logger,
	}
}

// RegisterModule registers a module with the bridge
func (bb *BidirectionalBridge) RegisterModule(module ModuleInterface) error {
	bb.mutex.Lock()
	defer bb.mutex.Unlock()
	
	name := module.GetName()
	if _, exists := bb.modules[name]; exists {
		return fmt.Errorf("module %s already registered", name)
	}
	
	// Add to router
	if err := bb.router.AddModule(module); err != nil {
		return err
	}
	
	// Create communicator
	communicator := NewModuleCommunicator(name, bb.eventBus, bb.logger)
	bb.communicators[name] = communicator
	bb.modules[name] = module
	
	bb.logger.WithFields(logrus.Fields{
		"module":       name,
		"capabilities": module.GetCapabilities(),
	}).Info("Module registered with bidirectional bridge")
	
	return nil
}

// Initialize initializes all registered modules
func (bb *BidirectionalBridge) Initialize(ctx context.Context) error {
	bb.mutex.RLock()
	defer bb.mutex.RUnlock()
	
	for name, module := range bb.modules {
		bb.logger.WithField("module", name).Info("Initializing module")
		
		if err := module.Initialize(ctx); err != nil {
			bb.logger.WithFields(logrus.Fields{
				"module": name,
				"error":  err,
			}).Error("Failed to initialize module")
			return fmt.Errorf("failed to initialize module %s: %w", name, err)
		}
	}
	
	bb.logger.Info("All modules initialized successfully")
	return nil
}

// Start starts all registered modules
func (bb *BidirectionalBridge) Start(ctx context.Context) error {
	bb.mutex.RLock()
	defer bb.mutex.RUnlock()
	
	for name, module := range bb.modules {
		bb.logger.WithField("module", name).Info("Starting module")
		
		if err := module.Start(ctx); err != nil {
			bb.logger.WithFields(logrus.Fields{
				"module": name,
				"error":  err,
			}).Error("Failed to start module")
			return fmt.Errorf("failed to start module %s: %w", name, err)
		}
	}
	
	bb.logger.Info("All modules started successfully")
	return nil
}

// Stop stops all registered modules
func (bb *BidirectionalBridge) Stop(ctx context.Context) error {
	bb.mutex.RLock()
	defer bb.mutex.RUnlock()
	
	for name, module := range bb.modules {
		bb.logger.WithField("module", name).Info("Stopping module")
		
		if err := module.Stop(ctx); err != nil {
			bb.logger.WithFields(logrus.Fields{
				"module": name,
				"error":  err,
			}).Error("Failed to stop module")
			// Continue stopping other modules
		}
	}
	
	bb.logger.Info("All modules stopped")
	return nil
}

// SendRequest sends a request from one module to another
func (bb *BidirectionalBridge) SendRequest(ctx context.Context, req *ModuleRequest) (*ModuleResponse, error) {
	if req.ID == "" {
		req.ID = fmt.Sprintf("req_%d", time.Now().UnixNano())
	}
	
	if req.Timestamp.IsZero() {
		req.Timestamp = time.Now()
	}
	
	bb.logger.WithFields(logrus.Fields{
		"request_id": req.ID,
		"source":     req.Source,
		"target":     req.Target,
		"type":       req.Type,
	}).Debug("Routing request")
	
	return bb.router.RouteRequest(ctx, req)
}

// Broadcast sends a message to all modules
func (bb *BidirectionalBridge) Broadcast(ctx context.Context, source, eventType string, data map[string]interface{}) error {
	event := Event{
		Type:   eventType,
		Source: source,
		Data:   data,
	}
	
	return bb.eventBus.Publish(ctx, event)
}

// GetModuleStatus returns the status of all modules
func (bb *BidirectionalBridge) GetModuleStatus() map[string]ModuleStatus {
	bb.mutex.RLock()
	defer bb.mutex.RUnlock()
	
	status := make(map[string]ModuleStatus)
	for name, module := range bb.modules {
		status[name] = module.GetStatus()
	}
	
	return status
}

// GetModuleCapabilities returns the capabilities of all modules
func (bb *BidirectionalBridge) GetModuleCapabilities() map[string][]string {
	bb.mutex.RLock()
	defer bb.mutex.RUnlock()
	
	capabilities := make(map[string][]string)
	for name, module := range bb.modules {
		capabilities[name] = module.GetCapabilities()
	}
	
	return capabilities
}

// GetCommunicator returns the communicator for a specific module
func (bb *BidirectionalBridge) GetCommunicator(moduleName string) (*ModuleCommunicator, error) {
	bb.mutex.RLock()
	defer bb.mutex.RUnlock()
	
	communicator, exists := bb.communicators[moduleName]
	if !exists {
		return nil, fmt.Errorf("communicator for module %s not found", moduleName)
	}
	
	return communicator, nil
}

// Close closes the bidirectional bridge
func (bb *BidirectionalBridge) Close(ctx context.Context) error {
	bb.logger.Info("Closing bidirectional bridge")
	
	// Stop all modules
	if err := bb.Stop(ctx); err != nil {
		bb.logger.WithError(err).Error("Error stopping modules")
	}
	
	// Close communicators
	for name, communicator := range bb.communicators {
		if err := communicator.Close(); err != nil {
			bb.logger.WithFields(logrus.Fields{
				"module": name,
				"error":  err,
			}).Error("Error closing communicator")
		}
	}
	
	bb.logger.Info("Bidirectional bridge closed")
	return nil
}