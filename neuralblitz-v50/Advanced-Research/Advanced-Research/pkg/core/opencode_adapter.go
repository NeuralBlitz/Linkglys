package core

import (
	"context"
	"fmt"
	"sync"

	"github.com/sirupsen/logrus"
)

// OpencodeModuleAdapter adapts the Opencode client to work with the bidirectional bridge
type OpencodeModuleAdapter struct {
	client      interface{} // Could be *opencode.Client
	communicator *ModuleCommunicator
	status      ModuleStatus
	mutex       sync.RWMutex
	logger      *logrus.Logger
}

// NewOpencodeModuleAdapter creates a new Opencode module adapter
func NewOpencodeModuleAdapter(client interface{}, logger *logrus.Logger) *OpencodeModuleAdapter {
	return &OpencodeModuleAdapter{
		client: client,
		status:  StatusStopped,
		logger:  logger,
	}
}

func (oc *OpencodeModuleAdapter) Initialize(ctx context.Context) error {
	oc.mutex.Lock()
	defer oc.mutex.Unlock()
	
	oc.status = StatusStarting
	oc.logger.Info("Initializing Opencode module")
	
	oc.status = StatusRunning
	return nil
}

func (oc *OpencodeModuleAdapter) Start(ctx context.Context) error {
	oc.mutex.Lock()
	defer oc.mutex.Unlock()
	
	if oc.status != StatusStarting {
		return fmt.Errorf("Opencode module must be initialized first")
	}
	
	oc.status = StatusRunning
	oc.logger.Info("Opencode module started")
	
	// Register handlers for Opencode-specific events
	if oc.communicator != nil {
		oc.communicator.RegisterHandler("create_document", oc.handleCreateDocument)
		oc.communicator.RegisterHandler("search_documents", oc.handleSearchDocuments)
		oc.communicator.RegisterHandler("update_document", oc.handleUpdateDocument)
		oc.communicator.RegisterHandler("get_document", oc.handleGetDocument)
		oc.communicator.RegisterHandler("get_project_structure", oc.handleGetProjectStructure)
	}
	
	return nil
}

func (oc *OpencodeModuleAdapter) Stop(ctx context.Context) error {
	oc.mutex.Lock()
	defer oc.mutex.Unlock()
	
	oc.status = StatusStopping
	oc.logger.Info("Stopping Opencode module")
	
	oc.status = StatusStopped
	return nil
}

func (oc *OpencodeModuleAdapter) GetStatus() ModuleStatus {
	oc.mutex.RLock()
	defer oc.mutex.RUnlock()
	return oc.status
}

func (oc *OpencodeModuleAdapter) GetName() string {
	return "opencode"
}

func (oc *OpencodeModuleAdapter) GetCapabilities() []string {
	return []string{
		"create_document",
		"search_documents",
		"update_document",
		"get_document",
		"get_project_structure",
		"manage_workflows",
		"track_research_progress",
	}
}

func (oc *OpencodeModuleAdapter) HandleRequest(ctx context.Context, req *ModuleRequest) (*ModuleResponse, error) {
	oc.mutex.RLock()
	defer oc.mutex.RUnlock()
	
	if oc.status != StatusRunning {
		return nil, fmt.Errorf("Opencode module is not running")
	}
	
	response := &ModuleResponse{
		ID:        req.ID,
		Type:      fmt.Sprintf("%s_response", req.Type),
		Source:    oc.GetName(),
		Target:    req.Source,
		Success:   true,
		Metadata:  make(map[string]interface{}),
	}
	
	switch req.Type {
	case "create_document":
		return oc.handleCreateDocument(ctx, req)
	case "search_documents":
		return oc.handleSearchDocuments(ctx, req)
	case "update_document":
		return oc.handleUpdateDocument(ctx, req)
	case "get_document":
		return oc.handleGetDocument(ctx, req)
	case "get_project_structure":
		return oc.handleGetProjectStructure(ctx, req)
	default:
		response.Success = false
		response.Error = fmt.Sprintf("unknown request type: %s", req.Type)
	}
	
	return response, nil
}

func (oc *OpencodeModuleAdapter) SetCommunicator(communicator *ModuleCommunicator) {
	oc.mutex.Lock()
	defer oc.mutex.Unlock()
	oc.communicator = communicator
}

func (oc *OpencodeModuleAdapter) handleCreateDocument(ctx context.Context, req *ModuleRequest) (*ModuleResponse, error) {
	title, _ := req.Data["title"].(string)
	content, _ := req.Data["content"].(string)
	stage, _ := req.Data["stage"].(string)
	docType, _ := req.Data["doc_type"].(string)
	
	// Create mock document ID
	docID := fmt.Sprintf("doc_%d", ctx.Value("timestamp"))
	
	oc.logger.WithFields(logrus.Fields{
		"doc_id": docID,
		"title":   title,
		"stage":   stage,
		"type":    docType,
	}).Info("Document created")
	
	response := &ModuleResponse{
		ID:        req.ID,
		Type:      "create_document_response",
		Source:    oc.GetName(),
		Target:    req.Source,
		Success:   true,
		Data: map[string]interface{}{
			"document_id": docID,
			"title":       title,
			"stage":       stage,
			"doc_type":    docType,
		},
		Metadata: map[string]interface{}{
			"created_at": "now",
		},
	}
	
	return response, nil
}

func (oc *OpencodeModuleAdapter) handleSearchDocuments(ctx context.Context, req *ModuleRequest) (*ModuleResponse, error) {
	query, _ := req.Data["query"].(string)
	stage, _ := req.Data["stage"].(string)
	
	// Mock search results
	results := []map[string]interface{}{
		{
			"id":    "doc_1",
			"title": fmt.Sprintf("Document matching: %s", query),
			"stage": stage,
		},
		{
			"id":    "doc_2",
			"title": fmt.Sprintf("Another result for: %s", query),
			"stage": stage,
		},
	}
	
	oc.logger.WithFields(logrus.Fields{
		"query":  query,
		"stage":  stage,
		"results": len(results),
	}).Info("Documents searched")
	
	response := &ModuleResponse{
		ID:        req.ID,
		Type:      "search_documents_response",
		Source:    oc.GetName(),
		Target:    req.Source,
		Success:   true,
		Data: map[string]interface{}{
			"documents": results,
			"count":     len(results),
		},
	}
	
	return response, nil
}

func (oc *OpencodeModuleAdapter) handleUpdateDocument(ctx context.Context, req *ModuleRequest) (*ModuleResponse, error) {
	docID, _ := req.Data["document_id"].(string)
	updates, _ := req.Data["updates"].(map[string]interface{})
	
	oc.logger.WithFields(logrus.Fields{
		"doc_id": docID,
		"updates": updates,
	}).Info("Document updated")
	
	response := &ModuleResponse{
		ID:        req.ID,
		Type:      "update_document_response",
		Source:    oc.GetName(),
		Target:    req.Source,
		Success:   true,
		Data: map[string]interface{}{
			"document_id": docID,
			"updated":    true,
		},
		Metadata: map[string]interface{}{
			"updated_at": "now",
		},
	}
	
	return response, nil
}

func (oc *OpencodeModuleAdapter) handleGetDocument(ctx context.Context, req *ModuleRequest) (*ModuleResponse, error) {
	docID, _ := req.Data["document_id"].(string)
	
	// Mock document data
	document := map[string]interface{}{
		"id":      docID,
		"title":   fmt.Sprintf("Document %s", docID),
		"content": "This is the document content",
		"stage":   "ideas",
		"doc_type": "theory",
	}
	
	oc.logger.WithField("doc_id", docID).Info("Document retrieved")
	
	response := &ModuleResponse{
		ID:        req.ID,
		Type:      "get_document_response",
		Source:    oc.GetName(),
		Target:    req.Source,
		Success:   true,
		Data: map[string]interface{}{
			"document": document,
		},
	}
	
	return response, nil
}

func (oc *OpencodeModuleAdapter) handleGetProjectStructure(ctx context.Context, req *ModuleRequest) (*ModuleResponse, error) {
	// Mock project structure
	structure := map[string]interface{}{
		"research_areas": []map[string]interface{}{
			{
				"name":        "Ideas",
				"description": "Theoretical foundation and brainstorming",
			},
			{
				"name":        "Apical-Synthesis",
				"description": "Integrated frameworks",
			},
			{
				"name":        "Implementation",
				"description": "Experimental code and validation",
			},
		},
		"semantic_tags": []string{"#theory", "#synthesis", "#implementation"},
		"workflows":    []string{"ideas_to_synthesis", "synthesis_to_implementation"},
	}
	
	response := &ModuleResponse{
		ID:        req.ID,
		Type:      "get_project_structure_response",
		Source:    oc.GetName(),
		Target:    req.Source,
		Success:   true,
		Data: map[string]interface{}{
			"structure": structure,
		},
	}
	
	return response, nil
}