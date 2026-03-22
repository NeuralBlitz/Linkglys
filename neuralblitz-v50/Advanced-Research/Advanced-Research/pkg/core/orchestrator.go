package core

import (
	"context"
	"fmt"
	"time"

	"github.com/sirupsen/logrus"
)

// ModuleOrchestrator coordinates communication between all modules
type ModuleOrchestrator struct {
	bridge         *BidirectionalBridge
	lrsAdapter     *LRSModuleAdapter
	opencodeAdapter *OpencodeModuleAdapter
	neuralblitzAdapter *NeuralBlitzModuleAdapter
	logger         *logrus.Logger
}

// NewModuleOrchestrator creates a new module orchestrator
func NewModuleOrchestrator(logger *logrus.Logger) *ModuleOrchestrator {
	if logger == nil {
		logger = logrus.New()
	}
	
	return &ModuleOrchestrator{
		bridge: NewBidirectionalBridge(logger),
		logger: logger,
	}
}

// Initialize initializes all modules and their connections
func (mo *ModuleOrchestrator) Initialize(ctx context.Context) error {
	mo.logger.Info("Initializing module orchestrator")
	
	// Create adapters for each module
	mo.lrsAdapter = NewLRSModuleAdapter(nil, mo.logger) // Pass actual LRS client
	mo.opencodeAdapter = NewOpencodeModuleAdapter(nil, mo.logger) // Pass actual Opencode client
	mo.neuralblitzAdapter = NewNeuralBlitzModuleAdapter(nil, mo.logger) // Pass actual NeuralBlitz engine
	
	// Register modules with bridge
	if err := mo.bridge.RegisterModule(mo.lrsAdapter); err != nil {
		return fmt.Errorf("failed to register LRS module: %w", err)
	}
	
	if err := mo.bridge.RegisterModule(mo.opencodeAdapter); err != nil {
		return fmt.Errorf("failed to register Opencode module: %w", err)
	}
	
	if err := mo.bridge.RegisterModule(mo.neuralblitzAdapter); err != nil {
		return fmt.Errorf("failed to register NeuralBlitz module: %w", err)
	}
	
	// Set communicators
	lrsComm, _ := mo.bridge.GetCommunicator("lrs")
	opencodeComm, _ := mo.bridge.GetCommunicator("opencode")
	neuralblitzComm, _ := mo.bridge.GetCommunicator("neuralblitz")
	
	mo.lrsAdapter.SetCommunicator(lrsComm)
	mo.opencodeAdapter.SetCommunicator(opencodeComm)
	mo.neuralblitzAdapter.SetCommunicator(neuralblitzComm)
	
	// Initialize all modules
	if err := mo.bridge.Initialize(ctx); err != nil {
		return fmt.Errorf("failed to initialize bridge: %w", err)
	}
	
	mo.logger.Info("Module orchestrator initialized successfully")
	return nil
}

// Start starts all modules and their communication
func (mo *ModuleOrchestrator) Start(ctx context.Context) error {
	mo.logger.Info("Starting module orchestrator")
	
	if err := mo.bridge.Start(ctx); err != nil {
		return fmt.Errorf("failed to start bridge: %w", err)
	}
	
	// Setup inter-module communication handlers
	go mo.setupInterModuleCommunication(ctx)
	
	mo.logger.Info("Module orchestrator started successfully")
	return nil
}

// Stop stops all modules
func (mo *ModuleOrchestrator) Stop(ctx context.Context) error {
	mo.logger.Info("Stopping module orchestrator")
	
	return mo.bridge.Stop(ctx)
}

// setupInterModuleCommunication sets up handlers for cross-module communication
func (mo *ModuleOrchestrator) setupInterModuleCommunication(ctx context.Context) {
	// Example: When a document is created in Opencode, record it in LRS
	opencodeComm, _ := mo.bridge.GetCommunicator("opencode")
	lrsComm, _ := mo.bridge.GetCommunicator("lrs")
	neuralblitzComm, _ := mo.bridge.GetCommunicator("neuralblitz")
	
	// Handler for document creation -> learning event
	go func() {
		eventChan := make(chan Event, 100)
		opencodeComm.RegisterHandler("document_created", func(event Event) error {
			// Send learning event to LRS
			lrsData := map[string]interface{}{
				"actor": map[string]interface{}{
					"account": map[string]interface{}{
						"homePage": "advanced-research",
						"name":     event.Data["user_id"],
					},
				},
				"verb": "created",
				"object": map[string]interface{}{
					"id":         event.Data["document_id"],
					"objectType": "Activity",
					"definition": map[string]interface{}{
						"type": "document",
						"name": event.Data["title"],
					},
				},
			}
			
			lrsComm.Broadcast(ctx, "document_created_learning", lrsData)
			return nil
		})
		_ = eventChan
	}()
	
	// Handler for computational tasks -> progress tracking
	go func() {
		neuralblitzComm.RegisterHandler("computation_completed", func(event Event) error {
			// Track computation progress in LRS
			lrsData := map[string]interface{}{
				"actor": map[string]interface{}{
					"account": map[string]interface{}{
						"homePage": "advanced-research",
						"name":     "system",
					},
				},
				"verb": "computed",
				"object": map[string]interface{}{
					"id":         event.Data["computation_id"],
					"objectType": "Activity",
					"definition": map[string]interface{}{
						"type": "geometric_computation",
					},
				},
			}
			
			lrsComm.Broadcast(ctx, "computation_learning", lrsData)
			return nil
		})
	}()
}

// CreateResearchDocument creates a document and notifies other modules
func (mo *ModuleOrchestrator) CreateResearchDocument(ctx context.Context, title, content, stage, docType string, user string) (string, error) {
	req := &ModuleRequest{
		Type:   "create_document",
		Source: "orchestrator",
		Target: "opencode",
		Data: map[string]interface{}{
			"title":     title,
			"content":   content,
			"stage":     stage,
			"doc_type":  docType,
			"user_id":   user,
		},
		Timeout: 30 * time.Second,
	}
	
	resp, err := mo.bridge.SendRequest(ctx, req)
	if err != nil {
		return "", err
	}
	
	if !resp.Success {
		return "", fmt.Errorf("failed to create document: %s", resp.Error)
	}
	
	docID, _ := resp.Data["document_id"].(string)
	
	// Notify other modules
	opencodeComm, _ := mo.bridge.GetCommunicator("opencode")
	opencodeComm.Broadcast(ctx, "document_created", map[string]interface{}{
		"document_id": docID,
		"title":       title,
		"user_id":     user,
	})
	
	return docID, nil
}

// ComputeGeometricFeatures performs geometric computation and notifies other modules
func (mo *ModuleOrchestrator) ComputeGeometricFeatures(ctx context.Context, inputData interface{}, featureType string, user string) (interface{}, error) {
	req := &ModuleRequest{
		Type:   "compute_geometric_features",
		Source: "orchestrator",
		Target: "neuralblitz",
		Data: map[string]interface{}{
			"input_data":   inputData,
			"feature_type": featureType,
			"user_id":     user,
		},
		Timeout: 60 * time.Second,
	}
	
	resp, err := mo.bridge.SendRequest(ctx, req)
	if err != nil {
		return nil, err
	}
	
	if !resp.Success {
		return nil, fmt.Errorf("failed to compute geometric features: %s", resp.Error)
	}
	
	features := resp.Data["features"]
	
	// Notify other modules
	neuralblitzComm, _ := mo.bridge.GetCommunicator("neuralblitz")
	neuralblitzComm.Broadcast(ctx, "computation_completed", map[string]interface{}{
		"computation_id": fmt.Sprintf("geom_%d", time.Now().Unix()),
		"feature_type":   featureType,
		"user_id":        user,
	})
	
	return features, nil
}

// RecordLearningEvent records a learning event across all modules
func (mo *ModuleOrchestrator) RecordLearningEvent(ctx context.Context, actor, verb string, objectData map[string]interface{}, user string) error {
	req := &ModuleRequest{
		Type:   "record_learning_event",
		Source: "orchestrator",
		Target: "lrs",
		Data: map[string]interface{}{
			"actor": map[string]interface{}{
				"account": map[string]interface{}{
					"homePage": "advanced-research",
					"name":     user,
				},
			},
			"verb":   verb,
			"object": objectData,
		},
		Timeout: 10 * time.Second,
	}
	
	resp, err := mo.bridge.SendRequest(ctx, req)
	if err != nil {
		return err
	}
	
	if !resp.Success {
		return fmt.Errorf("failed to record learning event: %s", resp.Error)
	}
	
	return nil
}

// SearchDocuments searches documents and aggregates results
func (mo *ModuleOrchestrator) SearchDocuments(ctx context.Context, query, stage, user string) (interface{}, error) {
	req := &ModuleRequest{
		Type:   "search_documents",
		Source: "orchestrator",
		Target: "opencode",
		Data: map[string]interface{}{
			"query":   query,
			"stage":   stage,
			"user_id": user,
		},
		Timeout: 30 * time.Second,
	}
	
	resp, err := mo.bridge.SendRequest(ctx, req)
	if err != nil {
		return nil, err
	}
	
	if !resp.Success {
		return nil, fmt.Errorf("failed to search documents: %s", resp.Error)
	}
	
	// Record search activity in LRS
	mo.RecordLearningEvent(ctx, user, "searched", map[string]interface{}{
		"id":         fmt.Sprintf("search_%d", time.Now().Unix()),
		"objectType": "Activity",
		"definition": map[string]interface{}{
			"type":  "document_search",
			"query": query,
		},
	}, user)
	
	return resp.Data["documents"], nil
}

// GetSystemStatus returns the status of all modules
func (mo *ModuleOrchestrator) GetSystemStatus(ctx context.Context) map[string]interface{} {
	status := mo.bridge.GetModuleStatus()
	capabilities := mo.bridge.GetModuleCapabilities()
	
	return map[string]interface{}{
		"modules":      status,
		"capabilities": capabilities,
		"timestamp":    time.Now().Format(time.RFC3339),
	}
}

// Close closes the orchestrator
func (mo *ModuleOrchestrator) Close(ctx context.Context) error {
	return mo.bridge.Close(ctx)
}