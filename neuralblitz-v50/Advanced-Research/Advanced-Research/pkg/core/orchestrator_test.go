package core

import (
	"context"
	"testing"
	"time"
)

// TestModuleOrchestrator demonstrates the bidirectional communication between modules
func TestModuleOrchestrator(t *testing.T) {
	// Create orchestrator
	orchestrator := NewModuleOrchestrator(nil)
	
	// Initialize
	ctx := context.Background()
	err := orchestrator.Initialize(ctx)
	if err != nil {
		t.Fatalf("Failed to initialize orchestrator: %v", err)
	}
	
	// Start
	err = orchestrator.Start(ctx)
	if err != nil {
		t.Fatalf("Failed to start orchestrator: %v", err)
	}
	
	defer orchestrator.Stop(ctx)
	
	// Test document creation
	docID, err := orchestrator.CreateResearchDocument(
		ctx,
		"Test Document",
		"This is a test document",
		"ideas",
		"theory",
		"test_user",
	)
	if err != nil {
		t.Errorf("Failed to create document: %v", err)
	}
	
	if docID == "" {
		t.Error("Expected document ID, got empty string")
	}
	
	// Test geometric computation
	features, err := orchestrator.ComputeGeometricFeatures(
		ctx,
		[]float64{1.0, 2.0, 3.0, 4.0},
		"eigenvalue",
		"test_user",
	)
	if err != nil {
		t.Errorf("Failed to compute geometric features: %v", err)
	}
	
	if features == nil {
		t.Error("Expected features, got nil")
	}
	
	// Test document search
	documents, err := orchestrator.SearchDocuments(
		ctx,
		"test query",
		"ideas",
		"test_user",
	)
	if err != nil {
		t.Errorf("Failed to search documents: %v", err)
	}
	
	if documents == nil {
		t.Error("Expected documents, got nil")
	}
	
	// Test learning event recording
	err = orchestrator.RecordLearningEvent(
		ctx,
		"test_user",
		"completed",
		map[string]interface{}{
			"id":         "test_activity",
			"objectType": "Activity",
			"definition": map[string]interface{}{
				"type": "test",
			},
		},
		"test_user",
	)
	if err != nil {
		t.Errorf("Failed to record learning event: %v", err)
	}
	
	// Get system status
	status := orchestrator.GetSystemStatus(ctx)
	if status == nil {
		t.Error("Expected system status, got nil")
	}
	
	t.Log("System status:", status)
}

// ExampleUsage demonstrates how to use the bidirectional communication system
func ExampleUsage() {
	orchestrator := NewModuleOrchestrator(nil)
	ctx := context.Background()
	
	// Initialize and start
	orchestrator.Initialize(ctx)
	orchestrator.Start(ctx)
	defer orchestrator.Stop(ctx)
	
	// Create a collaborative research session
	go func() {
		// Create a research document
		docID, _ := orchestrator.CreateResearchDocument(
			ctx,
			"Neural Network Research",
			"Research on attention mechanisms",
			"ideas",
			"theory",
			"researcher_1",
		)
		
		// Perform geometric analysis
		features, _ := orchestrator.ComputeGeometricFeatures(
			ctx,
			[][]float64{{1, 2, 3, 4}, {5, 6, 7, 8}},
			"riemannian",
			"researcher_1",
		)
		
		// Search related documents
		_, _ = orchestrator.SearchDocuments(
			ctx,
			"attention mechanisms",
			"ideas",
			"researcher_1",
		)
		
		// Record learning progress
		_ = orchestrator.RecordLearningEvent(
			ctx,
			"researcher_1",
			"analyzed",
			map[string]interface{}{
				"id":         docID,
				"objectType": "Activity",
				"definition": map[string]interface{}{
					"type":     "research_analysis",
					"features": features,
				},
			},
			"researcher_1",
		)
	}()
	
	// Let the system run
	time.Sleep(2 * time.Second)
}