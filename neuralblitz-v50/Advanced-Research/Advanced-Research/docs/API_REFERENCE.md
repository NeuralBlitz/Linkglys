# API Reference - Bidirectional Communication System

## Core Interfaces

### ModuleInterface

All modules must implement this interface to participate in the bidirectional communication system.

```go
type ModuleInterface interface {
    // Lifecycle management
    Initialize(ctx context.Context) error
    Start(ctx context.Context) error
    Stop(ctx context.Context) error
    
    // Module information
    GetStatus() ModuleStatus
    GetName() string
    GetCapabilities() []string
    
    // Request handling
    HandleRequest(ctx context.Context, req *ModuleRequest) (*ModuleResponse, error)
}
```

**Usage Example:**
```go
type MyModule struct {
    name   string
    status ModuleStatus
    // ... other fields
}

func (m *MyModule) Initialize(ctx context.Context) error {
    // Initialize module resources
    m.status = StatusStarting
    // ... initialization logic
    m.status = StatusRunning
    return nil
}

func (m *MyModule) HandleRequest(ctx context.Context, req *ModuleRequest) (*ModuleResponse, error) {
    switch req.Type {
    case "my_action":
        return m.handleMyAction(ctx, req)
    default:
        return &ModuleResponse{
            Success: false,
            Error:   "unknown request type",
        }, nil
    }
}
```

### ModuleStatus

Enum representing the current state of a module.

```go
type ModuleStatus string

const (
    StatusStopped   ModuleStatus = "stopped"
    StatusStarting ModuleStatus = "starting"
    StatusRunning  ModuleStatus = "running"
    StatusStopping ModuleStatus = "stopping"
    StatusError    ModuleStatus = "error"
)
```

## Core Communication Components

### EventBus

Provides publish-subscribe messaging between modules.

```go
type EventBus struct {
    // Internal fields
}

// Methods
func NewEventBus(logger *logrus.Logger) *EventBus
func (eb *EventBus) Subscribe(eventType string, handler chan Event) error
func (eb *EventBus) Unsubscribe(eventType string, handler chan Event) error
func (eb *EventBus) Publish(ctx context.Context, event Event) error
func (eb *EventBus) RequestResponse(ctx context.Context, request Event, timeout time.Duration) (*Event, error)
```

**Usage Examples:**

```go
// Create event bus
eventBus := NewEventBus(logger)

// Subscribe to events
eventChan := make(chan Event, 100)
eventBus.Subscribe("document_created", eventChan)

// Publish events
event := Event{
    Type:   "document_created",
    Source: "opencode",
    Data:   documentInfo,
}
eventBus.Publish(ctx, event)

// Request-response pattern
response, err := eventBus.RequestResponse(ctx, requestEvent, 30*time.Second)
```

### Event

Represents a message passed between modules.

```go
type Event struct {
    ID        string                 `json:"id"`
    Type      string                 `json:"type"`
    Source    string                 `json:"source"`
    Target    string                 `json:"target,omitempty"`
    Data      map[string]interface{} `json:"data"`
    Timestamp time.Time              `json:"timestamp"`
    ReplyTo   string                 `json:"reply_to,omitempty"`
}
```

**Field Descriptions:**
- `ID`: Unique identifier for the event
- `Type`: Event type identifier (e.g., "document_created")
- `Source`: Module that generated the event
- `Target`: Specific target module (optional)
- `Data`: Event payload
- `Timestamp`: When the event was created
- `ReplyTo`: For request-response correlation

### BidirectionalBridge

Central coordination hub for all module communications.

```go
type BidirectionalBridge struct {
    // Internal fields
}

func NewBidirectionalBridge(logger *logrus.Logger) *BidirectionalBridge
func (bb *BidirectionalBridge) RegisterModule(module ModuleInterface) error
func (bb *BidirectionalBridge) SendRequest(ctx context.Context, req *ModuleRequest) (*ModuleResponse, error)
func (bb *BidirectionalBridge) Broadcast(ctx context.Context, source, eventType string, data map[string]interface{}) error
func (bb *BidirectionalBridge) GetModuleStatus() map[string]ModuleStatus
func (bb *BidirectionalBridge) GetModuleCapabilities() map[string][]string
func (bb *BidirectionalBridge) Close(ctx context.Context) error
```

**Usage Examples:**

```go
// Create and configure bridge
bridge := NewBidirectionalBridge(logger)

// Register modules
bridge.RegisterModule(lrsAdapter)
bridge.RegisterModule(opencodeAdapter)
bridge.RegisterModule(neuralblitzAdapter)

// Send direct requests
req := &ModuleRequest{
    Type:   "create_document",
    Source: "orchestrator",
    Target: "opencode",
    Data:   documentData,
}
response, err := bridge.SendRequest(ctx, req)

// Broadcast events
bridge.Broadcast(ctx, "system_shutdown", map[string]interface{}{
    "reason": "maintenance",
})
```

### ModuleRequest & ModuleResponse

Structures for request-response communication.

```go
type ModuleRequest struct {
    ID        string                 `json:"id"`
    Type      string                 `json:"type"`
    Source    string                 `json:"source"`
    Target    string                 `json:"target"`
    Data      map[string]interface{} `json:"data"`
    Timestamp time.Time              `json:"timestamp"`
    Timeout   time.Duration          `json:"timeout"`
}

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
```

## Module Adapters

### LRSModuleAdapter

Adapts the Learning Record Store for bidirectional communication.

```go
type LRSModuleAdapter struct {
    // Internal fields
}

func NewLRSModuleAdapter(client interface{}, logger *logrus.Logger) *LRSModuleAdapter
func (lrs *LRSModuleAdapter) SetCommunicator(communicator *ModuleCommunicator)
```

**Supported Request Types:**
- `record_learning_event`: Record user learning activities
- `get_learning_records`: Retrieve stored learning data
- `flush_records`: Force immediate record storage

**Example Usage:**
```go
// Record learning event
req := &ModuleRequest{
    Type:   "record_learning_event",
    Target: "lrs",
    Data: map[string]interface{}{
        "actor": map[string]interface{}{
            "account": map[string]interface{}{
                "homePage": "advanced-research",
                "name":     "user_123",
            },
        },
        "verb": "completed",
        "object": map[string]interface{}{
            "id": "activity_456",
            "objectType": "Activity",
        },
    },
}

response, err := bridge.SendRequest(ctx, req)
```

### OpencodeModuleAdapter

Adapts the Research Documentation system.

```go
type OpencodeModuleAdapter struct {
    // Internal fields
}

func NewOpencodeModuleAdapter(client interface{}, logger *logrus.Logger) *OpencodeModuleAdapter
func (oc *OpencodeModuleAdapter) SetCommunicator(communicator *ModuleCommunicator)
```

**Supported Request Types:**
- `create_document`: Create new research document
- `search_documents`: Search existing documents
- `update_document`: Modify document content
- `get_document`: Retrieve specific document
- `get_project_structure`: Get project organization

**Example Usage:**
```go
// Create document
req := &ModuleRequest{
    Type:   "create_document",
    Target: "opencode",
    Data: map[string]interface{}{
        "title":     "My Research Paper",
        "content":   "Research content here...",
        "stage":     "ideas",
        "doc_type":  "theory",
        "tags":      []string{"ai", "research"},
    },
}

response, err := bridge.SendRequest(ctx, req)
docID := response.Data["document_id"].(string)
```

### NeuralBlitzModuleAdapter

Adapts the Geometric Computation engine.

```go
type NeuralBlitzModuleAdapter struct {
    // Internal fields
}

func NewNeuralBlitzModuleAdapter(engine interface{}, logger *logrus.Logger) *NeuralBlitzModuleAdapter
func (nb *NeuralBlitzModuleAdapter) SetCommunicator(communicator *ModuleCommunicator)
```

**Supported Request Types:**
- `compute_geometric_features`: Calculate mathematical features
- `optimize_on_manifold`: Perform geometric optimization
- `get_layer`: Retrieve layer information
- `riemannian_attention`: Apply attention mechanisms
- `manifold_convolution`: Perform geometric convolutions

**Example Usage:**
```go
// Compute geometric features
req := &ModuleRequest{
    Type:   "compute_geometric_features",
    Target: "neuralblitz",
    Data: map[string]interface{}{
        "input_data":   [][]float64{{1,2,3,4}, {5,6,7,8}},
        "feature_type": "riemannian",
    },
}

response, err := bridge.SendRequest(ctx, req)
features := response.Data["features"]
```

## Orchestration Layer

### ModuleOrchestrator

High-level coordination between all modules.

```go
type ModuleOrchestrator struct {
    // Internal fields
}

func NewModuleOrchestrator(logger *logrus.Logger) *ModuleOrchestrator
func (mo *ModuleOrchestrator) Initialize(ctx context.Context) error
func (mo *ModuleOrchestrator) Start(ctx context.Context) error
func (mo *ModuleOrchestrator) Stop(ctx context.Context) error

// High-level operations
func (mo *ModuleOrchestrator) CreateResearchDocument(ctx context.Context, title, content, stage, docType, user string) (string, error)
func (mo *ModuleOrchestrator) ComputeGeometricFeatures(ctx context.Context, inputData interface{}, featureType, user string) (interface{}, error)
func (mo *ModuleOrchestrator) SearchDocuments(ctx context.Context, query, stage, user string) (interface{}, error)
func (mo *ModuleOrchestrator) RecordLearningEvent(ctx context.Context, actor, verb string, objectData map[string]interface{}, user string) error
func (mo *ModuleOrchestrator) GetSystemStatus(ctx context.Context) map[string]interface{}
```

**Example Usage:**
```go
// Create orchestrator
orchestrator := NewModuleOrchestrator(logger)
orchestrator.Initialize(ctx)
orchestrator.Start(ctx)

// High-level document creation
docID, err := orchestrator.CreateResearchDocument(
    ctx,
    "Advanced AI Research",
    "Content about artificial intelligence...",
    "ideas",
    "theory",
    "researcher_1",
)

// This automatically:
// 1. Creates document in Opencode
// 2. Records learning event in LRS
// 3. Notifies other modules
```

### WorkflowEngine

Manages multi-step automated workflows across modules.

```go
type WorkflowEngine struct {
    // Internal fields
}

func NewWorkflowEngine(orchestrator *ModuleOrchestrator, logger *logrus.Logger) *WorkflowEngine
func (we *WorkflowEngine) RegisterWorkflow(workflow *Workflow) error
func (we *WorkflowEngine) GetActiveJobs() map[string]*WorkflowJob
func (we *WorkflowEngine) GetWorkflows() map[string]*Workflow
```

### Workflow Structures

```go
type Workflow struct {
    ID          string                 `json:"id"`
    Name        string                 `json:"name"`
    Description string                 `json:"description"`
    Steps       []WorkflowStep         `json:"steps"`
    Triggers    []WorkflowTrigger      `json:"triggers"`
    Metadata    map[string]interface{} `json:"metadata"`
}

type WorkflowStep struct {
    ID         string                 `json:"id"`
    Name       string                 `json:"name"`
    Module     string                 `json:"module"`
    Action     string                 `json:"action"`
    Parameters map[string]interface{} `json:"parameters"`
    Conditions []WorkflowCondition    `json:"conditions"`
    Timeout    time.Duration          `json:"timeout"`
}

type WorkflowTrigger struct {
    Type   string                 `json:"type"`
    Module string                 `json:"module"`
    Event  string                 `json:"event"`
    Filter map[string]interface{} `json:"filter"`
}
```

**Example Workflow Definition:**
```go
researchWorkflow := &Workflow{
    ID:          "automated_research",
    Name:        "Automated Research Workflow",
    Description: "Creates document, analyzes it, and records progress",
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
            ID:     "analyze_content",
            Name:   "Analyze with Geometric Features",
            Module: "neuralblitz",
            Action: "compute_geometric_features",
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

workflowEngine.RegisterWorkflow(researchWorkflow)
```

## Module Communicator

Provides communication capabilities for individual modules.

```go
type ModuleCommunicator struct {
    // Internal fields
}

func NewModuleCommunicator(moduleName string, eventBus *EventBus, logger *logrus.Logger) *ModuleCommunicator
func (mc *ModuleCommunicator) RegisterHandler(eventType string, handler func(Event) error) error
func (mc *ModuleCommunicator) SendMessage(ctx context.Context, targetModule, eventType string, data map[string]interface{}) error
func (mc *ModuleCommunicator) Request(ctx context.Context, targetModule, eventType string, data map[string]interface{}, timeout time.Duration) (*Event, error)
func (mc *ModuleCommunicator) Broadcast(ctx context.Context, eventType string, data map[string]interface{}) error
func (mc *ModuleCommunicator) GetModuleName() string
```

**Example Usage:**
```go
// In module adapter setup
communicator := NewModuleCommunicator("mymodule", eventBus, logger)

// Register event handlers
communicator.RegisterHandler("data_updated", func(event Event) error {
    // Handle data update event
    return nil
})

// Send messages to other modules
err := communicator.SendMessage(ctx, "othermodule", "process_data", map[string]interface{}{
    "data": myData,
})

// Broadcast to all modules
err = communicator.Broadcast(ctx, "status_update", map[string]interface{}{
    "status": "running",
})
```

## Error Handling

### Standard Error Responses

All modules return standardized error responses:

```go
type ErrorResponse struct {
    Code      string                 `json:"code"`
    Message   string                 `json:"message"`
    Details   map[string]interface{} `json:"details,omitempty"`
    Timestamp time.Time              `json:"timestamp"`
}
```

### Common Error Codes

| Code | Description | Example |
|------|-------------|---------|
| `MODULE_NOT_FOUND` | Target module doesn't exist | Requesting from non-existent module |
| `MODULE_NOT_RUNNING` | Target module is not active | Module stopped or error state |
| `INVALID_REQUEST` | Malformed request data | Missing required fields |
| `TIMEOUT` | Request exceeded timeout | Long-running computation |
| `PERMISSION_DENIED` | Insufficient permissions | Security policy violation |
| `INTERNAL_ERROR` | Module internal failure | Database connection error |

### Error Handling Pattern

```go
func handleRequest(req *ModuleRequest) (*ModuleResponse, error) {
    // Validate request
    if req.Data == nil {
        return &ModuleResponse{
            Success: false,
            Error:   "INVALID_REQUEST: missing data field",
        }, nil
    }
    
    // Process with timeout
    ctx, cancel := context.WithTimeout(ctx, req.Timeout)
    defer cancel()
    
    result, err := processRequest(ctx, req.Data)
    if err != nil {
        return &ModuleResponse{
            Success: false,
            Error:   fmt.Sprintf("INTERNAL_ERROR: %v", err),
        }, nil
    }
    
    return &ModuleResponse{
        Success: true,
        Data:    result,
    }, nil
}
```

## Configuration

### Bridge Configuration

```yaml
bridge:
  max_concurrent_requests: 100
  default_timeout: 30s
  event_buffer_size: 1000
  retry_attempts: 3
  retry_backoff: 1s
  health_check_interval: 30s
```

### Module Configuration

```yaml
modules:
  lrs:
    enabled: true
    endpoint: "http://lrs:8080/xapi/"
    username: "lrs_user"
    password: "lrs_pass"
    batch_size: 10
    timeout: 30s
    
  opencode:
    enabled: true
    workspace: "research-workspace"
    git_repo: "https://github.com/research/docs.git"
    local_path: "./research-docs"
    auto_commit: true
    timeout: 60s
    
  neuralblitz:
    enabled: true
    backend: "cpu"  # cpu, cuda, mps
    manifold_type: "riemannian"
    dimension: 64
    curvature: 1.0
    timeout: 120s
```

## Monitoring & Metrics

### System Status API

```go
type SystemStatus struct {
    Modules      map[string]ModuleStatus `json:"modules"`
    Capabilities map[string][]string     `json:"capabilities"`
    Statistics  SystemStatistics       `json:"statistics"`
    Timestamp    time.Time            `json:"timestamp"`
}

type SystemStatistics struct {
    TotalRequests            int64 `json:"total_requests"`
    SuccessfulRequests       int64 `json:"successful_requests"`
    FailedRequests         int64 `json:"failed_requests"`
    AverageResponseTime    float64 `json:"average_response_time_ms"`
    EventsPublished        int64 `json:"events_published"`
    EventsProcessed       int64 `json:"events_processed"`
    ActiveWorkflows       int64 `json:"active_workflows"`
    CompletedWorkflows    int64 `json:"completed_workflows"`
}
```

### Health Check Endpoints

```bash
# Overall system health
GET /api/health

# Individual module status
GET /api/modules/{module}/health

# System metrics
GET /api/metrics

# Active workflows
GET /api/workflows/active
```

This API reference provides comprehensive documentation for implementing and using the bidirectional communication system effectively.