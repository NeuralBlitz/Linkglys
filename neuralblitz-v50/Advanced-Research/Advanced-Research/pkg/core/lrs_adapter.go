package core

import (
	"context"
	"fmt"
	"sync"

	"github.com/sirupsen/logrus"
)

// LRSModuleAdapter adapts the LRS client to work with the bidirectional bridge
type LRSModuleAdapter struct {
	client      interface{} // Could be *lrs.Client
	communicator *ModuleCommunicator
	status      ModuleStatus
	mutex       sync.RWMutex
	logger      *logrus.Logger
}

// NewLRSModuleAdapter creates a new LRS module adapter
func NewLRSModuleAdapter(client interface{}, logger *logrus.Logger) *LRSModuleAdapter {
	return &LRSModuleAdapter{
		client: client,
		status:  StatusStopped,
		logger:  logger,
	}
}

func (lrs *LRSModuleAdapter) Initialize(ctx context.Context) error {
	lrs.mutex.Lock()
	defer lrs.mutex.Unlock()
	
	lrs.status = StatusStarting
	lrs.logger.Info("Initializing LRS module")
	
	// Initialize the LRS client if needed
	lrs.status = StatusRunning
	return nil
}

func (lrs *LRSModuleAdapter) Start(ctx context.Context) error {
	lrs.mutex.Lock()
	defer lrs.mutex.Unlock()
	
	if lrs.status != StatusStarting {
		return fmt.Errorf("LRS module must be initialized first")
	}
	
	lrs.status = StatusRunning
	lrs.logger.Info("LRS module started")
	
	// Register handlers for LRS-specific events
	if lrs.communicator != nil {
		lrs.communicator.RegisterHandler("record_learning_event", lrs.handleRecordLearningEvent)
		lrs.communicator.RegisterHandler("get_learning_records", lrs.handleGetLearningRecords)
		lrs.communicator.RegisterHandler("flush_records", lrs.handleFlushRecords)
	}
	
	return nil
}

func (lrs *LRSModuleAdapter) Stop(ctx context.Context) error {
	lrs.mutex.Lock()
	defer lrs.mutex.Unlock()
	
	lrs.status = StatusStopping
	lrs.logger.Info("Stopping LRS module")
	
	// Cleanup resources
	lrs.status = StatusStopped
	return nil
}

func (lrs *LRSModuleAdapter) GetStatus() ModuleStatus {
	lrs.mutex.RLock()
	defer lrs.mutex.RUnlock()
	return lrs.status
}

func (lrs *LRSModuleAdapter) GetName() string {
	return "lrs"
}

func (lrs *LRSModuleAdapter) GetCapabilities() []string {
	return []string{
		"record_learning_event",
		"record_context_interaction",
		"record_conversation",
		"get_learning_records",
		"flush_records",
		"track_user_progress",
	}
}

func (lrs *LRSModuleAdapter) HandleRequest(ctx context.Context, req *ModuleRequest) (*ModuleResponse, error) {
	lrs.mutex.RLock()
	defer lrs.mutex.RUnlock()
	
	if lrs.status != StatusRunning {
		return nil, fmt.Errorf("LRS module is not running")
	}
	
	response := &ModuleResponse{
		ID:        req.ID,
		Type:      fmt.Sprintf("%s_response", req.Type),
		Source:    lrs.GetName(),
		Target:    req.Source,
		Success:   true,
		Metadata:  make(map[string]interface{}),
	}
	
	switch req.Type {
	case "record_learning_event":
		return lrs.handleRecordLearningEvent(ctx, req)
	case "get_learning_records":
		return lrs.handleGetLearningRecords(ctx, req)
	case "flush_records":
		return lrs.handleFlushRecords(ctx, req)
	default:
		response.Success = false
		response.Error = fmt.Sprintf("unknown request type: %s", req.Type)
	}
	
	return response, nil
}

func (lrs *LRSModuleAdapter) SetCommunicator(communicator *ModuleCommunicator) {
	lrs.mutex.Lock()
	defer lrs.mutex.Unlock()
	lrs.communicator = communicator
}

func (lrs *LRSModuleAdapter) handleRecordLearningEvent(ctx context.Context, req *ModuleRequest) (*ModuleResponse, error) {
	// Extract learning event data from request
	actor, ok := req.Data["actor"].(map[string]interface{})
	if !ok {
		return nil, fmt.Errorf("missing actor data")
	}
	
	verb, ok := req.Data["verb"].(string)
	if !ok {
		return nil, fmt.Errorf("missing verb data")
	}
	
	objectData, ok := req.Data["object"].(map[string]interface{})
	if !ok {
		return nil, fmt.Errorf("missing object data")
	}
	
	// Log the event (in real implementation, would send to LRS)
	lrs.logger.WithFields(logrus.Fields{
		"actor":  actor,
		"verb":   verb,
		"object": objectData,
	}).Info("Learning event recorded")
	
	response := &ModuleResponse{
		ID:        req.ID,
		Type:      "record_learning_event_response",
		Source:    lrs.GetName(),
		Target:    req.Source,
		Success:   true,
		Metadata: map[string]interface{}{
			"event_recorded": true,
			"timestamp":      "now",
		},
	}
	
	return response, nil
}

func (lrs *LRSModuleAdapter) handleGetLearningRecords(ctx context.Context, req *ModuleRequest) (*ModuleResponse, error) {
	// Mock response with learning records
	records := []map[string]interface{}{
		{
			"id":   "record_1",
			"verb": "completed",
			"actor": map[string]interface{}{
				"name": "user_1",
			},
		},
	}
	
	response := &ModuleResponse{
		ID:        req.ID,
		Type:      "get_learning_records_response",
		Source:    lrs.GetName(),
		Target:    req.Source,
		Success:   true,
		Data: map[string]interface{}{
			"records": records,
		},
	}
	
	return response, nil
}

func (lrs *LRSModuleAdapter) handleFlushRecords(ctx context.Context, req *ModuleRequest) (*ModuleResponse, error) {
	lrs.logger.Info("Flushing learning records")
	
	response := &ModuleResponse{
		ID:        req.ID,
		Type:      "flush_records_response",
		Source:    lrs.GetName(),
		Target:    req.Source,
		Success:   true,
		Metadata: map[string]interface{}{
			"records_flushed": true,
			"count":          0,
		},
	}
	
	return response, nil
}