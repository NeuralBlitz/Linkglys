# Bidirectional Communication Examples

This directory contains practical examples demonstrating the bidirectional communication system capabilities.

## Example Applications

### 1. Basic Integration (`basic_integration.go`)
Shows the simplest way to set up and use the communication system.

```go
// Create orchestrator and perform basic operations
orchestrator := core.NewModuleOrchestrator(logger)
orchestrator.Initialize(ctx)
orchestrator.Start(ctx)

// Create document (automatically tracked in LRS)
docID := orchestrator.CreateResearchDocument(ctx, title, content, stage, docType, user)

// Compute features (notifies other modules)
features := orchestrator.ComputeGeometricFeatures(ctx, data, featureType, user)
```

### 2. Custom Module Implementation (`custom_module_example.go`)
Demonstrates how to create a new module that integrates with the system.

```go
type AnalyticsModule struct {
    name    string
    status  core.ModuleStatus
    // ... other fields
}

func (am *AnalyticsModule) HandleRequest(ctx context.Context, req *core.ModuleRequest) (*core.ModuleResponse, error) {
    switch req.Type {
    case "analyze_usage":
        return am.analyzeUsage(ctx, req)
    case "generate_report":
        return am.generateReport(ctx, req)
    // ... other actions
    }
}
```

### 3. Workflow Automation (`workflow_examples.go`)
Shows complex multi-step workflows across modules.

```go
researchWorkflow := &core.Workflow{
    Name: "Automated Research Pipeline",
    Steps: []core.WorkflowStep{
        {Module: "opencode", Action: "create_document"},
        {Module: "neuralblitz", Action: "compute_features"},
        {Module: "lrs", Action: "record_progress"},
    },
    Triggers: []core.WorkflowTrigger{
        {Event: "research_requested"},
    },
}
```

### 4. Event-Driven Architecture (`event_driven_example.go`)
Demonstrates pub/sub patterns and reactive programming.

```go
// Setup event handlers
communicator.RegisterHandler("document_created", func(event core.Event) error {
    // Automatically analyze new documents
    return triggerAnalysis(event.Data["document_id"])
})

communicator.RegisterHandler("computation_completed", func(event core.Event) error {
    // Store computation results
    return storeResults(event.Data["results"])
})
```

### 5. Advanced Error Handling (`error_handling_example.go`)
Shows comprehensive error handling and recovery patterns.

```go
// Retry with exponential backoff
response, err := bridge.SendRequestWithRetry(ctx, req, &RetryPolicy{
    MaxAttempts: 3,
    Backoff:     time.Second,
    Multiplier:  2.0,
})

// Circuit breaker pattern
circuit := NewCircuitBreaker("neuralblitz", 5, time.Minute)
response, err := circuit.Execute(func() (*core.ModuleResponse, error) {
    return bridge.SendRequest(ctx, req)
})
```

## Running Examples

### Prerequisites
```bash
cd Advanced-Research
go mod tidy
```

### Run Individual Examples
```bash
# Basic integration demo
go run examples/basic_integration.go

# Custom module example
go run examples/custom_module_example.go

# Workflow examples
go run examples/workflow_examples.go

# Event-driven examples
go run examples/event_driven_example.go

# Error handling examples
go run examples/error_handling_example.go
```

### Run with Main Application
```bash
# Demo mode (automated demonstrations)
go run cmd/bridge/main.go -demo

# Interactive mode (manual commands)
go run cmd/bridge/main.go

# With custom configuration
go run cmd/bridge/main.go -config configs/custom.yaml -log-level debug
```

## Configuration Examples

### Development Configuration (`configs/development.yaml`)
```yaml
bridge:
  max_concurrent_requests: 50
  default_timeout: 10s
  event_buffer_size: 1000

modules:
  lrs:
    enabled: true
    endpoint: "http://localhost:8081/xapi/"
    batch_size: 5
    
  opencode:
    enabled: true
    workspace: "dev-workspace"
    local_path: "./dev-docs"
    
  neuralblitz:
    enabled: true
    backend: "cpu"
    manifold_type: "euclidean"

logging:
  level: "debug"
  format: "text"
```

### Production Configuration (`configs/production.yaml`)
```yaml
bridge:
  max_concurrent_requests: 500
  default_timeout: 30s
  event_buffer_size: 10000

modules:
  lrs:
    enabled: true
    endpoint: "${LRS_ENDPOINT}"
    batch_size: 50
    
  opencode:
    enabled: true
    workspace: "${OPENCODE_WORKSPACE}"
    
  neuralblitz:
    enabled: true
    backend: "cuda"
    manifold_type: "riemannian"

monitoring:
  prometheus:
    enabled: true
    port: 9090
    
  jaeger:
    enabled: true
    endpoint: "${JAEGER_ENDPOINT}"
```

## Testing Examples

### Unit Tests
```bash
# Run all tests
go test ./...

# Run specific test
go test -v ./pkg/core -run TestModuleRequest

# Run with coverage
go test -cover ./pkg/core
```

### Integration Tests
```bash
# Run integration tests
go test -tags=integration ./tests/integration

# Test against real modules
INTEGRATION_TEST=true go test ./tests/integration
```

### Performance Tests
```bash
# Run benchmarks
go test -bench=. ./pkg/core

# Load testing
go run tests/load_test.go
```

## Monitoring Examples

### Prometheus Metrics
```go
// Custom metrics
var (
    requestDuration = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name: "bridge_request_duration_seconds",
            Help: "Request processing time",
        },
        []string{"module", "type", "status"},
    )
    
    activeWorkflows = prometheus.NewGauge(
        prometheus.GaugeOpts{
            Name: "bridge_active_workflows",
            Health: "Number of currently active workflows",
        },
    )
)

// Expose metrics endpoint
http.Handle("/metrics", promhttp.Handler())
http.ListenAndServe(":9090", nil)
```

### Health Checks
```go
// Comprehensive health endpoint
func (b *Bridge) HealthHandler(w http.ResponseWriter, r *http.Request) {
    health := map[string]interface{}{
        "status": "healthy",
        "timestamp": time.Now(),
        "modules": b.GetModuleStatus(),
        "version": b.GetVersion(),
    }
    
    json.NewEncoder(w).Encode(health)
}
```

## Debugging Examples

### Request Tracing
```go
// Add correlation ID to all requests
func (b *Bridge) SendRequest(ctx context.Context, req *ModuleRequest) (*ModuleResponse, error) {
    correlationID := generateCorrelationID()
    ctx = context.WithValue(ctx, "correlation_id", correlationID)
    
    logger.WithFields(logrus.Fields{
        "correlation_id": correlationID,
        "request_id":     req.ID,
        "type":          req.Type,
    }).Debug("Sending request")
    
    // ... process request
}
```

### Event Logging
```go
// Structured event logging
func (m *MyModule) logEvent(eventType string, data map[string]interface{}) {
    logger.WithFields(logrus.Fields{
        "module":     m.GetName(),
        "event_type": eventType,
        "data":       data,
        "timestamp":  time.Now(),
    }).Info("Module event")
}
```

## Best Practices Illustrated

### 1. Error Handling
- Always check error returns
- Use structured error types
- Implement retry mechanisms
- Log with context

### 2. Resource Management
- Use context for cancellation
- Implement proper cleanup
- Monitor resource usage
- Handle graceful shutdown

### 3. Performance
- Use connection pooling
- Implement caching where appropriate
- Monitor metrics
- Profile bottlenecks

### 4. Security
- Validate all inputs
- Use secure communication
- Implement rate limiting
- Log security events

## Advanced Scenarios

### 1. Hot Module Reloading
```go
// Reload module without system restart
func (b *Bridge) ReloadModule(moduleName string) error {
    // Stop old module
    // Load new implementation
    // Register with bridge
    // Resume operations
}
```

### 2. Dynamic Workflow Creation
```go
// Create workflows from configuration
func createWorkflowFromConfig(config WorkflowConfig) *core.Workflow {
    // Parse configuration
    // Build workflow steps
    // Register triggers
    // Return workflow
}
```

### 3. Multi-Tenant Support
```go
// Isolate communication per tenant
func (b *Bridge) CreateTenantBridge(tenantID string) *TenantBridge {
    // Create isolated communication channel
    // Register tenant-specific modules
    // Return tenant bridge
}
```

These examples provide practical, copy-paste ready code for implementing common patterns and use cases with the bidirectional communication system.