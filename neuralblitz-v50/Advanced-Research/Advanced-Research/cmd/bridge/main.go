package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/sirupsen/logrus"
	"github.com/advanced-research/pkg/core"
)

// Example application demonstrating the bidirectional communication system
func main() {
	// Parse command line flags
	var (
		configPath = flag.String("config", "configs/bridge.yaml", "Path to configuration file")
		logLevel   = flag.String("log-level", "info", "Log level (debug, info, warn, error)")
		demoMode   = flag.Bool("demo", false, "Run in demonstration mode")
	)
	flag.Parse()

	// Setup logging
	logger := logrus.New()
	level, err := logrus.ParseLevel(*logLevel)
	if err != nil {
		log.Fatalf("Invalid log level: %v", err)
	}
	logger.SetLevel(level)

	logger.Info("=== Bidirectional Communication System Demo ===")

	// Create orchestrator
	orchestrator := core.NewModuleOrchestrator(logger)

	// Initialize system
	ctx := context.Background()
	logger.Info("Initializing system...")
	if err := orchestrator.Initialize(ctx); err != nil {
		logger.WithError(err).Fatal("Failed to initialize system")
	}

	// Start system
	logger.Info("Starting system...")
	if err := orchestrator.Start(ctx); err != nil {
		logger.WithError(err).Fatal("Failed to start system")
	}
	defer orchestrator.Stop(ctx)

	// Setup graceful shutdown
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	// Create workflow engine for advanced demos
	workflowEngine := core.NewWorkflowEngine(orchestrator, logger)
	if err := workflowEngine.CreateDefaultWorkflows(); err != nil {
		logger.WithError(err).Error("Failed to create default workflows")
	}

	// Run demonstrations or interactive mode
	if *demoMode {
		runDemonstrations(ctx, orchestrator, workflowEngine, logger)
	} else {
		runInteractiveMode(ctx, orchestrator, logger)
	}

	// Wait for shutdown signal
	<-sigChan
	logger.Info("Shutdown signal received, stopping system...")
}

// runDemonstrations shows system capabilities through automated examples
func runDemonstrations(ctx context.Context, orchestrator *core.ModuleOrchestrator, workflowEngine *core.WorkflowEngine, logger *logrus.Logger) {
	logger.Info("🚀 Running demonstration mode...")

	// Demo 1: Document creation with automatic tracking
	demonstrateDocumentCreation(ctx, orchestrator, logger)

	// Demo 2: Geometric computation with notifications
	demonstrateGeometricComputation(ctx, orchestrator, logger)

	// Demo 3: Cross-module communication
	demonstrateCrossModuleCommunication(ctx, orchestrator, logger)

	// Demo 4: Workflow automation
	demonstrateWorkflowAutomation(ctx, workflowEngine, logger)

	// Demo 5: System monitoring
	demonstrateSystemMonitoring(ctx, orchestrator, logger)

	logger.Info("✅ All demonstrations completed!")
}

// demonstrateDocumentCreation shows how document creation automatically triggers other modules
func demonstrateDocumentCreation(ctx context.Context, orchestrator *core.ModuleOrchestrator, logger *logrus.Logger) {
	logger.Info("\n--- Demo 1: Document Creation & Automatic Tracking ---")

	// Create research document
	logger.Info("Creating research document...")
	docID, err := orchestrator.CreateResearchDocument(
		ctx,
		"Advanced Machine Learning Research",
		"This document explores the mathematical foundations of deep learning, focusing on geometric interpretations of neural networks and their applications in natural language processing.",
		"ideas",
		"theory",
		"researcher_1",
	)

	if err != nil {
		logger.WithError(err).Error("Failed to create document")
		return
	}

	logger.WithField("document_id", docID).Info("✅ Document created successfully")

	// Wait a moment for event processing
	time.Sleep(500 * time.Millisecond)

	// Check system status to see the impact
	status := orchestrator.GetSystemStatus(ctx)
	logger.WithFields(logrus.Fields{
		"modules":   status["modules"],
		"timestamp": status["timestamp"],
	}).Info("System status after document creation")
}

// demonstrateGeometricComputation shows geometric feature computation
func demonstrateGeometricComputation(ctx context.Context, orchestrator *core.ModuleOrchestrator, logger *logrus.Logger) {
	logger.Info("\n--- Demo 2: Geometric Computation & Event Broadcasting ---")

	// Prepare sample data
	inputData := [][]float64{
		{1.0, 2.0, 3.0, 4.0},
		{5.0, 6.0, 7.0, 8.0},
		{9.0, 10.0, 11.0, 12.0},
		{13.0, 14.0, 15.0, 16.0},
	}

	logger.Info("Computing geometric features...")
	features, err := orchestrator.ComputeGeometricFeatures(
		ctx,
		inputData,
		"riemannian",
		"researcher_1",
	)

	if err != nil {
		logger.WithError(err).Error("Failed to compute features")
		return
	}

	logger.WithField("features", features).Info("✅ Geometric features computed")

	// Wait for event processing
	time.Sleep(500 * time.Millisecond)
}

// demonstrateCrossModuleCommunication shows direct communication between modules
func demonstrateCrossModuleCommunication(ctx context.Context, orchestrator *core.ModuleOrchestrator, logger *logrus.Logger) {
	logger.Info("\n--- Demo 3: Cross-Module Communication ---")

	// Search for documents (this will automatically log the search activity in LRS)
	logger.Info("Searching for documents...")
	documents, err := orchestrator.SearchDocuments(
		ctx,
		"machine learning",
		"ideas",
		"researcher_1",
	)

	if err != nil {
		logger.WithError(err).Error("Failed to search documents")
		return
	}

	logger.WithField("documents", documents).Info("✅ Documents found")

	// Record a custom learning event
	logger.Info("Recording custom learning event...")
	err = orchestrator.RecordLearningEvent(
		ctx,
		"researcher_1",
		"completed",
		map[string]interface{}{
			"id":         "demo_activity_001",
			"objectType": "Activity",
			"definition": map[string]interface{}{
				"type":        "demonstration",
				"description": "Completed bidirectional communication demo",
				"category":    "learning_progress",
			},
		},
		"researcher_1",
	)

	if err != nil {
		logger.WithError(err).Error("Failed to record learning event")
		return
	}

	logger.Info("✅ Learning event recorded")
}

// demonstrateWorkflowAutomation shows workflow execution
func demonstrateWorkflowAutomation(ctx context.Context, workflowEngine *core.WorkflowEngine, logger *logrus.Logger) {
	logger.Info("\n--- Demo 4: Workflow Automation ---")

	// Get available workflows
	workflows := workflowEngine.GetWorkflows()
	
	logger.WithField("workflows", len(workflows)).Info("Available workflows")
	
	for id, workflow := range workflows {
		logger.WithFields(logrus.Fields{
			"id":          id,
			"name":        workflow.Name,
			"description": workflow.Description,
			"steps":       len(workflow.Steps),
		}).Info("Workflow details")
	}

	// Show active jobs
	activeJobs := workflowEngine.GetActiveJobs()
	logger.WithField("active_jobs", len(activeJobs)).Info("Currently active workflow jobs")
}

// demonstrateSystemMonitoring shows system health and metrics
func demonstrateSystemMonitoring(ctx context.Context, orchestrator *core.ModuleOrchestrator, logger *logrus.Logger) {
	logger.Info("\n--- Demo 5: System Monitoring & Health Check ---")

	// Get comprehensive system status
	status := orchestrator.GetSystemStatus(ctx)

	if modules, ok := status["modules"].(map[string]interface{}); ok {
		logger.Info("📊 Module Status:")
		for name, moduleStatus := range modules {
			logger.WithFields(logrus.Fields{
				"module": name,
				"status": moduleStatus,
			}).Info("  •")
		}
	}

	if capabilities, ok := status["capabilities"].(map[string]interface{}); ok {
		logger.Info("🔧 Module Capabilities:")
		for name, caps := range capabilities {
			logger.WithFields(logrus.Fields{
				"module":      name,
				"capabilities": caps,
			}).Info("  •")
		}
	}

	logger.WithField("timestamp", status["timestamp"]).Info("📈 System health check completed")
}

// runInteractiveMode provides an interactive shell for manual testing
func runInteractiveMode(ctx context.Context, orchestrator *core.ModuleOrchestrator, logger *logrus.Logger) {
	logger.Info("\n🎮 Running in interactive mode")
	logger.Info("Available commands:")
	logger.Info("  create <title> <content> <stage> <type> <user>  - Create research document")
	logger.Info("  compute <data> <feature_type> <user>         - Compute geometric features")
	logger.Info("  search <query> <stage> <user>               - Search documents")
	logger.Info("  record <actor> <verb> <object> <user>       - Record learning event")
	logger.Info("  status                                      - Show system status")
	logger.Info("  help                                        - Show this help")
	logger.Info("  quit                                        - Exit")

	for {
		fmt.Print("\n> ")
		var input string
		fmt.Scanln(&input)

		if input == "quit" || input == "exit" {
			break
		}

		handleInteractiveCommand(ctx, input, orchestrator, logger)
	}
}

// handleInteractiveCommand processes user commands in interactive mode
func handleInteractiveCommand(ctx context.Context, input string, orchestrator *core.ModuleOrchestrator, logger *logrus.Logger) {
	// Simple command parsing (in production, use a proper CLI library)
	parts := []string{}
	current := ""
	for _, char := range input {
		if char == ' ' && current != "" {
			parts = append(parts, current)
			current = ""
		} else {
			current += string(char)
		}
	}
	if current != "" {
		parts = append(parts, current)
	}

	if len(parts) == 0 {
		return
	}

	command := parts[0]

	switch command {
	case "create":
		if len(parts) < 6 {
			logger.Error("Usage: create <title> <content> <stage> <type> <user>")
			return
		}
		docID, err := orchestrator.CreateResearchDocument(ctx, parts[1], parts[2], parts[3], parts[4], parts[5])
		if err != nil {
			logger.WithError(err).Error("Failed to create document")
		} else {
			logger.WithField("document_id", docID).Info("Document created")
		}

	case "compute":
		if len(parts) < 4 {
			logger.Error("Usage: compute <data> <feature_type> <user>")
			return
		}
		// Convert string to float array (simplified)
		inputData := [][]float64{{1, 2, 3, 4}} // Use mock data for demo
		features, err := orchestrator.ComputeGeometricFeatures(ctx, inputData, parts[2], parts[3])
		if err != nil {
			logger.WithError(err).Error("Failed to compute features")
		} else {
			logger.WithField("features", features).Info("Features computed")
		}

	case "search":
		if len(parts) < 4 {
			logger.Error("Usage: search <query> <stage> <user>")
			return
		}
		documents, err := orchestrator.SearchDocuments(ctx, parts[1], parts[2], parts[3])
		if err != nil {
			logger.WithError(err).Error("Failed to search documents")
		} else {
			logger.WithField("documents", documents).Info("Documents found")
		}

	case "record":
		if len(parts) < 5 {
			logger.Error("Usage: record <actor> <verb> <object> <user>")
			return
		}
		objectData := map[string]interface{}{
			"id":         "interactive_event",
			"objectType": "Activity",
			"definition": map[string]interface{}{
				"type":        "user_initiated",
				"description": parts[3],
			},
		}
		err := orchestrator.RecordLearningEvent(ctx, parts[1], parts[2], objectData, parts[4])
		if err != nil {
			logger.WithError(err).Error("Failed to record event")
		} else {
			logger.Info("Event recorded")
		}

	case "status":
		status := orchestrator.GetSystemStatus(ctx)
		logger.WithField("status", status).Info("System status")

	case "help":
		logger.Info("Available commands:")
		logger.Info("  create <title> <content> <stage> <type> <user>")
		logger.Info("  compute <data> <feature_type> <user>")
		logger.Info("  search <query> <stage> <user>")
		logger.Info("  record <actor> <verb> <object> <user>")
		logger.Info("  status")
		logger.Info("  help")
		logger.Info("  quit")

	default:
		logger.WithField("command", command).Error("Unknown command. Type 'help' for available commands.")
	}
}