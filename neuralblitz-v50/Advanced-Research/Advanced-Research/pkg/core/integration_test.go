package core

import (
	"context"
	"time"

	"github.com/sirupsen/logrus"
)

// IntegrationTest demonstrates the complete bidirectional communication system
func IntegrationTest() {
	logger := logrus.New()
	logger.SetLevel(logrus.InfoLevel)
	
	// Create orchestrator
	orchestrator := NewModuleOrchestrator(logger)
	
	ctx := context.Background()
	
	// Initialize and start
	if err := orchestrator.Initialize(ctx); err != nil {
		logger.WithError(err).Fatal("Failed to initialize orchestrator")
	}
	
	if err := orchestrator.Start(ctx); err != nil {
		logger.WithError(err).Fatal("Failed to start orchestrator")
	}
	
	defer orchestrator.Stop(ctx)
	
	// Create workflow engine
	workflowEngine := NewWorkflowEngine(orchestrator, logger)
	
	// Register default workflows
	if err := workflowEngine.CreateDefaultWorkflows(); err != nil {
		logger.WithError(err).Fatal("Failed to create default workflows")
	}
	
	// Demonstrate bidirectional communication
	demonstrateCommunication(orchestrator, workflowEngine, logger)
}

// demonstrateCommunication shows various communication patterns
func demonstrateCommunication(orchestrator *ModuleOrchestrator, workflowEngine *WorkflowEngine, logger *logrus.Logger) {
	logger.Info("=== Demonstrating Bidirectional Communication ===")
	
	// 1. Document creation with automatic learning tracking
	logger.Info("1. Creating research document...")
	docID, err := orchestrator.CreateResearchDocument(
		context.Background(),
		"Advanced Geometric Analysis",
		"This document explores the mathematical foundations of geometric deep learning",
		"ideas",
		"theory",
		"researcher_1",
	)
	if err != nil {
		logger.WithError(err).Error("Failed to create document")
	} else {
		logger.WithField("document_id", docID).Info("Document created successfully")
	}
	
	// 2. Geometric computation with progress tracking
	logger.Info("2. Computing geometric features...")
	features, err := orchestrator.ComputeGeometricFeatures(
		context.Background(),
		[][]float64{{1, 2, 3, 4}, {5, 6, 7, 8}, {9, 10, 11, 12}},
		"riemannian",
		"researcher_1",
	)
	if err != nil {
		logger.WithError(err).Error("Failed to compute features")
	} else {
		logger.WithField("features", features).Info("Geometric features computed")
	}
	
	// 3. Document search with activity logging
	logger.Info("3. Searching documents...")
	documents, err := orchestrator.SearchDocuments(
		context.Background(),
		"geometric analysis",
		"ideas",
		"researcher_1",
	)
	if err != nil {
		logger.WithError(err).Error("Failed to search documents")
	} else {
		logger.WithField("documents", documents).Info("Documents found")
	}
	
	// 4. Learning event recording
	logger.Info("4. Recording learning event...")
	err = orchestrator.RecordLearningEvent(
		context.Background(),
		"researcher_1",
		"completed",
		map[string]interface{}{
			"id":         "research_session_1",
			"objectType": "Activity",
			"definition": map[string]interface{}{
				"type":        "research_session",
				"description": "Completed geometric analysis research",
			},
		},
		"researcher_1",
	)
	if err != nil {
		logger.WithError(err).Error("Failed to record learning event")
	} else {
		logger.Info("Learning event recorded successfully")
	}
	
	// 5. System status check
	logger.Info("5. Checking system status...")
	status := orchestrator.GetSystemStatus(context.Background())
	logger.WithField("system_status", status).Info("Current system status")
	
	// 6. Workflow status check
	logger.Info("6. Checking workflow status...")
	workflows := workflowEngine.GetWorkflows()
	jobs := workflowEngine.GetActiveJobs()
	
	logger.WithFields(map[string]interface{}{
		"workflows":     len(workflows),
		"active_jobs":   len(jobs),
		"workflow_ids": getWorkflowIDs(workflows),
	}).Info("Workflow engine status")
	
	// Let the system process events
	time.Sleep(2 * time.Second)
	
	logger.Info("=== Bidirectional Communication Demo Complete ===")
}

// getWorkflowIDs extracts workflow IDs
func getWorkflowIDs(workflows map[string]*Workflow) []string {
	ids := make([]string, 0, len(workflows))
	for id := range workflows {
		ids = append(ids, id)
	}
	return ids
}