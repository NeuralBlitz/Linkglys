package core

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"github.com/sirupsen/logrus"
)

// WorkflowEngine orchestrates complex workflows across multiple modules
type WorkflowEngine struct {
	orchestrator *ModuleOrchestrator
	workflows    map[string]*Workflow
	activeJobs   map[string]*WorkflowJob
	logger       *logrus.Logger
}

// Workflow defines a multi-step workflow
type Workflow struct {
	ID          string                 `json:"id"`
	Name        string                 `json:"name"`
	Description string                 `json:"description"`
	Steps       []WorkflowStep         `json:"steps"`
	Triggers    []WorkflowTrigger      `json:"triggers"`
	Metadata    map[string]interface{} `json:"metadata"`
}

// WorkflowStep represents a single step in a workflow
type WorkflowStep struct {
	ID         string                 `json:"id"`
	Name       string                 `json:"name"`
	Module     string                 `json:"module"`
	Action     string                 `json:"action"`
	Parameters map[string]interface{} `json:"parameters"`
	Conditions []WorkflowCondition    `json:"conditions"`
	Timeout    time.Duration          `json:"timeout"`
}

// WorkflowCondition represents a condition for workflow execution
type WorkflowCondition struct {
	Type      string      `json:"type"`
	Module    string      `json:"module"`
	Attribute string      `json:"attribute"`
	Operator  string      `json:"operator"`
	Value     interface{} `json:"value"`
}

// WorkflowTrigger defines when a workflow should start
type WorkflowTrigger struct {
	Type   string                 `json:"type"`
	Module string                 `json:"module"`
	Event  string                 `json:"event"`
	Filter map[string]interface{} `json:"filter"`
}

// WorkflowJob represents an active workflow execution
type WorkflowJob struct {
	ID        string                 `json:"id"`
	Workflow  *Workflow             `json:"workflow"`
	Context   map[string]interface{} `json:"context"`
	Status    string                 `json:"status"`
	StartTime time.Time              `json:"start_time"`
	EndTime   *time.Time            `json:"end_time,omitempty"`
	Results   map[string]interface{} `json:"results"`
}

// NewWorkflowEngine creates a new workflow engine
func NewWorkflowEngine(orchestrator *ModuleOrchestrator, logger *logrus.Logger) *WorkflowEngine {
	if logger == nil {
		logger = logrus.New()
	}
	
	return &WorkflowEngine{
		orchestrator: orchestrator,
		workflows:    make(map[string]*Workflow),
		activeJobs:   make(map[string]*WorkflowJob),
		logger:       logger,
	}
}

// RegisterWorkflow registers a new workflow
func (we *WorkflowEngine) RegisterWorkflow(workflow *Workflow) error {
	if _, exists := we.workflows[workflow.ID]; exists {
		return fmt.Errorf("workflow %s already registered", workflow.ID)
	}
	
	we.workflows[workflow.ID] = workflow
	
	// Setup triggers
	for _, trigger := range workflow.Triggers {
		we.setupTrigger(workflow.ID, trigger)
	}
	
	we.logger.WithFields(logrus.Fields{
		"workflow_id": workflow.ID,
		"name":       workflow.Name,
	}).Info("Workflow registered")
	
	return nil
}

// setupTrigger sets up event triggers for a workflow
func (we *WorkflowEngine) setupTrigger(workflowID string, trigger WorkflowTrigger) {
	// Get the module communicator
	comm, err := we.orchestrator.bridge.GetCommunicator(trigger.Module)
	if err != nil {
		we.logger.WithError(err).Error("Failed to get communicator for trigger")
		return
	}
	
	// Register event handler
	comm.RegisterHandler(trigger.Event, func(event Event) error {
		// Check filters
		if !we.checkTriggerFilter(trigger.Filter, event.Data) {
			return nil
		}
		
		// Start workflow
		go we.startWorkflow(workflowID, map[string]interface{}{
			"trigger_event": event,
			"trigger_data":  event.Data,
		})
		
		return nil
	})
}

// checkTriggerFilter checks if trigger data matches the filter
func (we *WorkflowEngine) checkTriggerFilter(filter map[string]interface{}, data map[string]interface{}) bool {
	for key, expectedValue := range filter {
		if actualValue, exists := data[key]; !exists || actualValue != expectedValue {
			return false
		}
	}
	return true
}

// startWorkflow starts executing a workflow
func (we *WorkflowEngine) startWorkflow(workflowID string, context map[string]interface{}) {
	workflow, exists := we.workflows[workflowID]
	if !exists {
		we.logger.WithField("workflow_id", workflowID).Error("Workflow not found")
		return
	}
	
	// Create job
	jobID := fmt.Sprintf("job_%s_%d", workflowID, time.Now().Unix())
	job := &WorkflowJob{
		ID:        jobID,
		Workflow:  workflow,
		Context:   context,
		Status:    "running",
		StartTime: time.Now(),
		Results:   make(map[string]interface{}),
	}
	
	we.activeJobs[jobID] = job
	
	we.logger.WithFields(logrus.Fields{
		"job_id":     jobID,
		"workflow_id": workflowID,
	}).Info("Starting workflow job")
	
	// Execute steps
	err := we.executeWorkflowSteps(job)
	if err != nil {
		we.logger.WithFields(logrus.Fields{
			"job_id": jobID,
			"error":   err,
		}).Error("Workflow execution failed")
		job.Status = "failed"
	} else {
		job.Status = "completed"
		we.logger.WithField("job_id", jobID).Info("Workflow execution completed")
	}
	
	now := time.Now()
	job.EndTime = &now
}

// executeWorkflowSteps executes all steps in a workflow
func (we *WorkflowEngine) executeWorkflowSteps(job *WorkflowJob) error {
	for _, step := range job.Workflow.Steps {
		// Check conditions
		if !we.checkStepConditions(step.Conditions, job.Context) {
			we.logger.WithFields(logrus.Fields{
				"job_id": job.ID,
				"step":   step.Name,
			}).Debug("Step conditions not met, skipping")
			continue
		}
		
		// Execute step
		result, err := we.executeWorkflowStep(job, step)
		if err != nil {
			return fmt.Errorf("failed to execute step %s: %w", step.Name, err)
		}
		
		// Store result
		job.Results[step.ID] = result
		job.Context[fmt.Sprintf("step_%s_result", step.ID)] = result
		
		we.logger.WithFields(logrus.Fields{
			"job_id": job.ID,
			"step":   step.Name,
		}).Debug("Workflow step completed")
	}
	
	return nil
}

// checkStepConditions checks if step conditions are satisfied
func (we *WorkflowEngine) checkStepConditions(conditions []WorkflowCondition, context map[string]interface{}) bool {
	for _, condition := range conditions {
		if !we.checkCondition(condition, context) {
			return false
		}
	}
	return true
}

// checkCondition checks a single condition
func (we *WorkflowEngine) checkCondition(condition WorkflowCondition, context map[string]interface{}) bool {
	// This is a simplified implementation
	// In practice, would need more sophisticated condition evaluation
	
	// Check if attribute exists in context
	if value, exists := context[condition.Attribute]; exists {
		return we.compareValues(value, condition.Operator, condition.Value)
	}
	
	return false
}

// compareValues compares two values based on operator
func (we *WorkflowEngine) compareValues(actual interface{}, operator string, expected interface{}) bool {
	switch operator {
	case "equals":
		return actual == expected
	case "not_equals":
		return actual != expected
	case "greater_than":
		// Simplified numeric comparison
		if actualFloat, ok := actual.(float64); ok {
			if expectedFloat, ok := expected.(float64); ok {
				return actualFloat > expectedFloat
			}
		}
	case "less_than":
		// Simplified numeric comparison
		if actualFloat, ok := actual.(float64); ok {
			if expectedFloat, ok := expected.(float64); ok {
				return actualFloat < expectedFloat
			}
		}
	}
	
	return false
}

// executeWorkflowStep executes a single workflow step
func (we *WorkflowEngine) executeWorkflowStep(job *WorkflowJob, step WorkflowStep) (interface{}, error) {
	ctx := context.Background()
	
	// Set timeout if specified
	if step.Timeout > 0 {
		var cancel context.CancelFunc
		ctx, cancel = context.WithTimeout(ctx, step.Timeout)
		defer cancel()
	}
	
	switch step.Module {
	case "opencode":
		return we.executeOpencodeStep(ctx, job, step)
	case "neuralblitz":
		return we.executeNeuralBlitzStep(ctx, job, step)
	case "lrs":
		return we.executeLRSStep(ctx, job, step)
	default:
		return nil, fmt.Errorf("unknown module: %s", step.Module)
	}
}

// executeOpencodeStep executes a step in the opencode module
func (we *WorkflowEngine) executeOpencodeStep(ctx context.Context, job *WorkflowJob, step WorkflowStep) (interface{}, error) {
	switch step.Action {
	case "create_document":
		title, _ := step.Parameters["title"].(string)
		if title == "" {
			title = fmt.Sprintf("Auto-generated: %s", job.Workflow.Name)
		}
		
		content, _ := step.Parameters["content"].(string)
		if content == "" {
			content = job.Workflow.Description
		}
		
		stage, _ := step.Parameters["stage"].(string)
		if stage == "" {
			stage = "ideas"
		}
		
		docType, _ := step.Parameters["doc_type"].(string)
		if docType == "" {
			docType = "theory"
		}
		
		user, _ := step.Parameters["user"].(string)
		if user == "" {
			user = "workflow_system"
		}
		
		return we.orchestrator.CreateResearchDocument(ctx, title, content, stage, docType, user)
		
	case "search_documents":
		query, _ := step.Parameters["query"].(string)
		if query == "" {
			query = job.Workflow.Name
		}
		
		stage, _ := step.Parameters["stage"].(string)
		user, _ := step.Parameters["user"].(string)
		if user == "" {
			user = "workflow_system"
		}
		
		return we.orchestrator.SearchDocuments(ctx, query, stage, user)
		
	default:
		return nil, fmt.Errorf("unknown opencode action: %s", step.Action)
	}
}

// executeNeuralBlitzStep executes a step in the neuralblitz module
func (we *WorkflowEngine) executeNeuralBlitzStep(ctx context.Context, job *WorkflowJob, step WorkflowStep) (interface{}, error) {
	switch step.Action {
	case "compute_features":
		inputData := step.Parameters["input_data"]
		if inputData == nil {
			inputData = []float64{1.0, 2.0, 3.0, 4.0}
		}
		
		featureType, _ := step.Parameters["feature_type"].(string)
		if featureType == "" {
			featureType = "eigenvalue"
		}
		
		user, _ := step.Parameters["user"].(string)
		if user == "" {
			user = "workflow_system"
		}
		
		return we.orchestrator.ComputeGeometricFeatures(ctx, inputData, featureType, user)
		
	default:
		return nil, fmt.Errorf("unknown neuralblitz action: %s", step.Action)
	}
}

// executeLRSStep executes a step in the LRS module
func (we *WorkflowEngine) executeLRSStep(ctx context.Context, job *WorkflowJob, step WorkflowStep) (interface{}, error) {
	actor, _ := step.Parameters["actor"].(string)
	if actor == "" {
		actor = "workflow_system"
	}
	
	verb, _ := step.Parameters["verb"].(string)
	if verb == "" {
		verb = "executed"
	}
	
	objectData, _ := step.Parameters["object"].(map[string]interface{})
	if objectData == nil {
		objectData = map[string]interface{}{
			"id":         job.ID,
			"objectType": "Activity",
			"definition": map[string]interface{}{
				"type":  "workflow_execution",
				"name":  job.Workflow.Name,
			},
		}
	}
	
	user, _ := step.Parameters["user"].(string)
	if user == "" {
		user = "workflow_system"
	}
	
	err := we.orchestrator.RecordLearningEvent(ctx, actor, verb, objectData, user)
	if err != nil {
		return nil, err
	}
	
	return map[string]interface{}{
		"event_recorded": true,
		"timestamp":      time.Now().Format(time.RFC3339),
	}, nil
}

// GetActiveJobs returns all active workflow jobs
func (we *WorkflowEngine) GetActiveJobs() map[string]*WorkflowJob {
	// Return a copy to avoid external modification
	jobs := make(map[string]*WorkflowJob)
	for id, job := range we.activeJobs {
		jobs[id] = job
	}
	return jobs
}

// GetWorkflows returns all registered workflows
func (we *WorkflowEngine) GetWorkflows() map[string]*Workflow {
	// Return a copy to avoid external modification
	workflows := make(map[string]*Workflow)
	for id, workflow := range we.workflows {
		workflows[id] = workflow
	}
	return workflows
}

// CreateDefaultWorkflows creates some default workflows
func (we *WorkflowEngine) CreateDefaultWorkflows() error {
	// Research workflow
	researchWorkflow := &Workflow{
		ID:          "research_workflow",
		Name:        "Research Document Creation",
		Description: "Creates research documents with automatic analysis",
		Steps: []WorkflowStep{
			{
				ID:     "create_doc",
				Name:   "Create Research Document",
				Module: "opencode",
				Action: "create_document",
				Parameters: map[string]interface{}{
					"stage":    "ideas",
					"doc_type": "theory",
				},
				Timeout: 30 * time.Second,
			},
			{
				ID:     "analyze_doc",
				Name:   "Analyze with Geometric Features",
				Module: "neuralblitz",
				Action: "compute_features",
				Parameters: map[string]interface{}{
					"feature_type": "riemannian",
				},
				Timeout: 60 * time.Second,
			},
			{
				ID:     "record_progress",
				Name:   "Record Learning Progress",
				Module: "lrs",
				Action: "record_learning_event",
				Parameters: map[string]interface{}{
					"verb": "completed",
				},
				Timeout: 10 * time.Second,
			},
		},
		Triggers: []WorkflowTrigger{
			{
				Type:   "event",
				Module: "orchestrator",
				Event:  "research_requested",
			},
		},
	}
	
	// Computational analysis workflow
	computationalWorkflow := &Workflow{
		ID:          "computational_analysis",
		Name:        "Computational Analysis",
		Description: "Performs geometric computation and records results",
		Steps: []WorkflowStep{
			{
				ID:     "compute",
				Name:   "Compute Geometric Features",
				Module: "neuralblitz",
				Action: "compute_features",
				Parameters: map[string]interface{}{
					"feature_type": "riemannian",
				},
				Timeout: 60 * time.Second,
			},
			{
				ID:     "search_related",
				Name:   "Search Related Documents",
				Module: "opencode",
				Action: "search_documents",
				Parameters: map[string]interface{}{
					"stage": "synthesis",
				},
				Timeout: 30 * time.Second,
			},
			{
				ID:     "record_activity",
				Name:   "Record Computation Activity",
				Module: "lrs",
				Action: "record_learning_event",
				Parameters: map[string]interface{}{
					"verb": "computed",
				},
				Timeout: 10 * time.Second,
			},
		},
		Triggers: []WorkflowTrigger{
			{
				Type:   "event",
				Module: "orchestrator",
				Event:  "computation_requested",
			},
		},
	}
	
	// Register workflows
	if err := we.RegisterWorkflow(researchWorkflow); err != nil {
		return fmt.Errorf("failed to register research workflow: %w", err)
	}
	
	if err := we.RegisterWorkflow(computationalWorkflow); err != nil {
		return fmt.Errorf("failed to register computational workflow: %w", err)
	}
	
	return nil
}