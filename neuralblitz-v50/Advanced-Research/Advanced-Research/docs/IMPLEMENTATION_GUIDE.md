# Implementation Guide - Bidirectional Communication System

## Quick Start

This guide will help you get the bidirectional communication system running in minutes.

### Prerequisites

- Go 1.19 or higher
- Access to the existing LRS, Opencode, and NeuralBlitz modules
- Basic understanding of Go programming concepts

### Installation

1. **Clone the Repository**
```bash
git clone <repository-url>
cd Advanced-Research
```

2. **Install Dependencies**
```bash
go mod tidy
```

3. **Build the System**
```bash
go build -o bin/bidirectional-bridge ./cmd/bridge
```

## Basic Usage

### 1. Simple Module Integration

```go
package main

import (
    "context"
    "log"
    "time"
    
    "github.com/advanced-research/pkg/core"
)

func main() {
    // Create logger
    logger := log.New(os.Stdout, "[BRIDGE] ", log.LstdFlags)
    
    // Create orchestrator
    orchestrator := core.NewModuleOrchestrator(logger)
    
    // Initialize
    ctx := context.Background()
    if err := orchestrator.Initialize(ctx); err != nil {
        log.Fatal("Failed to initialize:", err)
    }
    
    // Start
    if err := orchestrator.Start(ctx); err != nil {
        log.Fatal("Failed to start:", err)
    }
    defer orchestrator.Stop(ctx)
    
    // Use the system
    docID, err := orchestrator.CreateResearchDocument(
        ctx,
        "My First Research Paper",
        "This is my research content...",
        "ideas",
        "theory",
        "researcher_1",
    )
    
    if err != nil {
        log.Printf("Error creating document: %v", err)
    } else {
        log.Printf("Document created with ID: %s", docID)
    }
    
    // Keep running
    select {}
}
```

### 2. Custom Module Implementation

```go
package mymodule

import (
    "context"
    "fmt"
    "sync"
    
    "github.com/advanced-research/pkg/core"
)

type MyCustomModule struct {
    name       string
    status     core.ModuleStatus
    mutex      sync.RWMutex
    logger     *logrus.Logger
    dataStore  map[string]interface{}
}

func NewMyCustomModule(name string, logger *logrus.Logger) *MyCustomModule {
    return &MyCustomModule{
        name:      name,
        status:    core.StatusStopped,
        logger:    logger,
        dataStore: make(map[string]interface{}),
    }
}

func (m *MyCustomModule) Initialize(ctx context.Context) error {
    m.mutex.Lock()
    defer m.mutex.Unlock()
    
    m.status = core.StatusStarting
    m.logger.Info("Initializing custom module")
    
    // Initialize resources here
    // For example: database connections, file handles, etc.
    
    m.status = core.StatusRunning
    return nil
}

func (m *MyCustomModule) Start(ctx context.Context) error {
    m.mutex.Lock()
    defer m.mutex.Unlock()
    
    if m.status != core.StatusStarting {
        return fmt.Errorf("module must be initialized first")
    }
    
    m.status = core.StatusRunning
    m.logger.Info("Custom module started")
    return nil
}

func (m *MyCustomModule) Stop(ctx context.Context) error {
    m.mutex.Lock()
    defer m.mutex.Unlock()
    
    m.status = core.StatusStopping
    m.logger.Info("Stopping custom module")
    
    // Cleanup resources here
    
    m.status = core.StatusStopped
    return nil
}

func (m *MyCustomModule) GetStatus() core.ModuleStatus {
    m.mutex.RLock()
    defer m.mutex.RUnlock()
    return m.status
}

func (m *MyCustomModule) GetName() string {
    return m.name
}

func (m *MyCustomModule) GetCapabilities() []string {
    return []string{
        "store_data",
        "retrieve_data",
        "process_data",
        "notify_events",
    }
}

func (m *MyCustomModule) HandleRequest(ctx context.Context, req *core.ModuleRequest) (*core.ModuleResponse, error) {
    m.mutex.RLock()
    defer m.mutex.RUnlock()
    
    if m.status != core.StatusRunning {
        return nil, fmt.Errorf("module is not running")
    }
    
    switch req.Type {
    case "store_data":
        return m.handleStoreData(ctx, req)
    case "retrieve_data":
        return m.handleRetrieveData(ctx, req)
    case "process_data":
        return m.handleProcessData(ctx, req)
    default:
        return &core.ModuleResponse{
            ID:      req.ID,
            Type:    fmt.Sprintf("%s_response", req.Type),
            Source:  m.GetName(),
            Target:  req.Source,
            Success: false,
            Error:   fmt.Sprintf("unknown request type: %s", req.Type),
        }, nil
    }
}

func (m *MyCustomModule) handleStoreData(ctx context.Context, req *core.ModuleRequest) (*core.ModuleResponse, error) {
    key, ok := req.Data["key"].(string)
    if !ok {
        return &core.ModuleResponse{
            Success: false,
            Error:   "missing or invalid key parameter",
        }, nil
    }
    
    value := req.Data["value"]
    m.dataStore[key] = value
    
    m.logger.WithFields(logrus.Fields{
        "key":   key,
        "value": value,
    }).Info("Data stored")
    
    return &core.ModuleResponse{
        ID:      req.ID,
        Type:    "store_data_response",
        Source:  m.GetName(),
        Target:  req.Source,
        Success: true,
        Data: map[string]interface{}{
            "stored": true,
            "key":    key,
        },
    }, nil
}

func (m *MyCustomModule) handleRetrieveData(ctx context.Context, req *core.ModuleRequest) (*core.ModuleResponse, error) {
    key, ok := req.Data["key"].(string)
    if !ok {
        return &core.ModuleResponse{
            Success: false,
            Error:   "missing key parameter",
        }, nil
    }
    
    value, exists := m.dataStore[key]
    
    return &core.ModuleResponse{
        ID:      req.ID,
        Type:    "retrieve_data_response",
        Source:  m.GetName(),
        Target:  req.Source,
        Success: exists,
        Data: map[string]interface{}{
            "value":  value,
            "exists": exists,
        },
    }, nil
}

func (m *MyCustomModule) handleProcessData(ctx context.Context, req *core.ModuleRequest) (*core.ModuleResponse, error) {
    data := req.Data["data"]
    
    // Process the data (example: convert to uppercase string)
    processed := fmt.Sprintf("PROCESSED: %v", data)
    
    return &core.ModuleResponse{
        ID:      req.ID,
        Type:    "process_data_response",
        Source:  m.GetName(),
        Target:  req.Source,
        Success: true,
        Data: map[string]interface{}{
            "original":  data,
            "processed": processed,
        },
    }, nil
}
```

### 3. Registering Custom Module

```go
func main() {
    logger := logrus.New()
    
    // Create orchestrator
    orchestrator := core.NewModuleOrchestrator(logger)
    
    // Create custom module
    customModule := mymodule.NewMyCustomModule("my_custom_module", logger)
    
    // Get access to bridge to register manually (if needed)
    bridge := orchestrator.GetBridge()
    bridge.RegisterModule(customModule)
    
    // Initialize and start
    ctx := context.Background()
    orchestrator.Initialize(ctx)
    orchestrator.Start(ctx)
    defer orchestrator.Stop(ctx)
    
    // Now you can send requests to your custom module
    req := &core.ModuleRequest{
        Type:   "store_data",
        Source: "main",
        Target: "my_custom_module",
        Data: map[string]interface{}{
            "key":   "test_key",
            "value": "test_value",
        },
    }
    
    response, err := bridge.SendRequest(ctx, req)
    if err != nil {
        log.Printf("Error: %v", err)
    } else {
        log.Printf("Response: %+v", response)
    }
}
```

## Advanced Features

### 1. Workflow Automation

```go
func setupCustomWorkflow(engine *core.WorkflowEngine) error {
    // Define a custom workflow
    customWorkflow := &core.Workflow{
        ID:          "data_processing_workflow",
        Name:        "Data Processing Workflow",
        Description: "Stores data, processes it, and notifies users",
        Steps: []core.WorkflowStep{
            {
                ID:     "store_input",
                Name:   "Store Input Data",
                Module: "my_custom_module",
                Action: "store_data",
                Parameters: map[string]interface{}{
                    "auto_key": true,
                },
                Timeout: 10 * time.Second,
            },
            {
                ID:     "process_stored",
                Name:   "Process Stored Data",
                Module: "my_custom_module",
                Action: "process_data",
                Conditions: []core.WorkflowCondition{
                    {
                        Type:     "result",
                        Module:   "my_custom_module",
                        Attribute: "store_data_response.success",
                        Operator: "equals",
                        Value:    true,
                    },
                },
                Timeout: 30 * time.Second,
            },
            {
                ID:     "notify_completion",
                Name:   "Notify Completion",
                Module: "opencode",
                Action: "create_document",
                Parameters: map[string]interface{}{
                    "title":     "Processing Complete",
                    "content":   "Data processing workflow completed successfully",
                    "stage":     "implementation",
                    "doc_type":  "analysis",
                },
                Timeout: 15 * time.Second,
            },
        },
        Triggers: []core.WorkflowTrigger{
            {
                Type:   "event",
                Module: "orchestrator",
                Event:  "data_processing_requested",
            },
        },
    }
    
    return engine.RegisterWorkflow(customWorkflow)
}
```

### 2. Event-Driven Communication

```go
func setupEventHandlers(communicator *core.ModuleCommunicator) {
    // Handle document creation events
    communicator.RegisterHandler("document_created", func(event core.Event) error {
        log.Printf("Document created: %+v", event.Data)
        
        // Automatically analyze new documents
        if title, ok := event.Data["title"].(string); ok {
            // Trigger analysis workflow
            return communicator.Broadcast(ctx, "analysis_requested", map[string]interface{}{
                "document_title": title,
                "auto_trigger":   true,
            })
        }
        
        return nil
    })
    
    // Handle computation completion events
    communicator.RegisterHandler("computation_completed", func(event core.Event) error {
        log.Printf("Computation completed: %+v", event.Data)
        
        // Store results
        return communicator.SendMessage(ctx, "my_custom_module", "store_data", map[string]interface{}{
            "key":   fmt.Sprintf("computation_%s", event.ID),
            "value": event.Data["results"],
        })
    })
}
```

### 3. Custom Middleware

```go
type LoggingMiddleware struct {
    logger *logrus.Logger
}

func (lm *LoggingMiddleware) Handle(next core.RequestHandler) core.RequestHandler {
    return func(req *core.ModuleRequest) (*core.ModuleResponse, error) {
        start := time.Now()
        
        lm.logger.WithFields(logrus.Fields{
            "request_id": req.ID,
            "type":       req.Type,
            "source":     req.Source,
            "target":     req.Target,
        }).Info("Request started")
        
        response, err := next(req)
        
        duration := time.Since(start)
        
        lm.logger.WithFields(logrus.Fields{
            "request_id": req.ID,
            "duration":   duration,
            "success":    response != nil && response.Success,
            "error":      err,
        }).Info("Request completed")
        
        return response, err
    }
}

// Apply middleware to module
func (m *MyCustomModule) HandleRequest(ctx context.Context, req *core.ModuleRequest) (*core.ModuleResponse, error) {
    middleware := &LoggingMiddleware{logger: m.logger}
    handler := func(req *core.ModuleRequest) (*core.ModuleResponse, error) {
        return m.actualHandleRequest(ctx, req)
    }
    
    return middleware.Handle(handler)(req)
}
```

## Testing

### Unit Testing Module

```go
package mymodule_test

import (
    "context"
    "testing"
    
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
    "github.com/advanced-research/pkg/core"
)

func TestMyCustomModule_StoreData(t *testing.T) {
    logger := logrus.New()
    module := NewMyCustomModule("test_module", logger)
    
    // Initialize module
    ctx := context.Background()
    require.NoError(t, module.Initialize(ctx))
    require.NoError(t, module.Start(ctx))
    defer module.Stop(ctx)
    
    // Test store data request
    req := &core.ModuleRequest{
        ID:     "test_req_1",
        Type:   "store_data",
        Source: "test",
        Target: "test_module",
        Data: map[string]interface{}{
            "key":   "test_key",
            "value": "test_value",
        },
    }
    
    response, err := module.HandleRequest(ctx, req)
    
    // Assertions
    require.NoError(t, err)
    assert.NotNil(t, response)
    assert.True(t, response.Success)
    assert.Equal(t, "store_data_response", response.Type)
    assert.Equal(t, true, response.Data["stored"])
    assert.Equal(t, "test_key", response.Data["key"])
}

func TestMyCustomModule_RetrieveData(t *testing.T) {
    logger := logrus.New()
    module := NewMyCustomModule("test_module", logger)
    
    ctx := context.Background()
    require.NoError(t, module.Initialize(ctx))
    require.NoError(t, module.Start(ctx))
    defer module.Stop(ctx)
    
    // First store some data
    storeReq := &core.ModuleRequest{
        Type:   "store_data",
        Data: map[string]interface{}{
            "key":   "retrieve_test_key",
            "value": "retrieve_test_value",
        },
    }
    _, err := module.HandleRequest(ctx, storeReq)
    require.NoError(t, err)
    
    // Then retrieve it
    retrieveReq := &core.ModuleRequest{
        ID:     "test_req_2",
        Type:   "retrieve_data",
        Source: "test",
        Target: "test_module",
        Data: map[string]interface{}{
            "key": "retrieve_test_key",
        },
    }
    
    response, err := module.HandleRequest(ctx, retrieveReq)
    
    // Assertions
    require.NoError(t, err)
    assert.NotNil(t, response)
    assert.True(t, response.Success)
    assert.Equal(t, "retrieve_test_value", response.Data["value"])
    assert.Equal(t, true, response.Data["exists"])
}
```

### Integration Testing

```go
func TestModuleIntegration(t *testing.T) {
    logger := logrus.New()
    
    // Create test orchestrator
    orchestrator := core.NewModuleOrchestrator(logger)
    
    ctx := context.Background()
    require.NoError(t, orchestrator.Initialize(ctx))
    require.NoError(t, orchestrator.Start(ctx))
    defer orchestrator.Stop(ctx)
    
    // Test document creation with automatic tracking
    docID, err := orchestrator.CreateResearchDocument(
        ctx,
        "Integration Test Document",
        "This is an integration test",
        "ideas",
        "theory",
        "test_user",
    )
    
    require.NoError(t, err)
    assert.NotEmpty(t, docID)
    
    // Test geometric computation
    features, err := orchestrator.ComputeGeometricFeatures(
        ctx,
        []float64{1, 2, 3, 4, 5},
        "eigenvalue",
        "test_user",
    )
    
    require.NoError(t, err)
    assert.NotNil(t, features)
    
    // Verify system status
    status := orchestrator.GetSystemStatus(ctx)
    assert.NotNil(t, status)
    assert.Contains(t, status["modules"], "lrs")
    assert.Contains(t, status["modules"], "opencode")
    assert.Contains(t, status["modules"], "neuralblitz")
}
```

## Deployment

### Docker Configuration

```dockerfile
# Dockerfile
FROM golang:1.19-alpine AS builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN go build -o bin/bridge ./cmd/bridge

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/

COPY --from=builder /app/bin/bridge .
COPY --from=builder /app/configs ./configs

CMD ["./bridge"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  bridge:
    build: .
    ports:
      - "8080:8080"
    environment:
      - LOG_LEVEL=info
      - LRS_ENDPOINT=http://lrs:8080/xapi/
      - OPENCODE_WORKSPACE=test-workspace
      - NEURALBLITZ_BACKEND=cpu
    depends_on:
      - lrs
      - opencode
      - neuralblitz
    volumes:
      - ./configs:/app/configs

  lrs:
    image: lrs-service:latest
    ports:
      - "8081:8080"
    environment:
      - DATABASE_URL=postgres://user:pass@postgres:5432/lrs

  opencode:
    image: opencode-service:latest
    ports:
      - "8082:8080"
    volumes:
      - ./research-docs:/app/docs

  neuralblitz:
    image: neuralblitz-service:latest
    ports:
      - "8083:8080"
    environment:
      - BACKEND=cpu

  postgres:
    image: postgres:13
    environment:
      - POSTGRES_DB=lrs
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bidirectional-bridge
spec:
  replicas: 3
  selector:
    matchLabels:
      app: bidirectional-bridge
  template:
    metadata:
      labels:
        app: bidirectional-bridge
    spec:
      containers:
      - name: bridge
        image: bridge-service:latest
        ports:
        - containerPort: 8080
        env:
        - name: LRS_ENDPOINT
          value: "http://lrs-service:8080/xapi/"
        - name: OPENCODE_WORKSPACE
          value: "production"
        - name: NEURALBLITZ_BACKEND
          value: "cuda"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: bridge-service
spec:
  selector:
    app: bidirectional-bridge
  ports:
  - protocol: TCP
    port: 8080
    targetPort: 8080
  type: LoadBalancer
```

## Performance Tuning

### Configuration Optimization

```yaml
# High-performance configuration
bridge:
  max_concurrent_requests: 500
  default_timeout: 10s
  event_buffer_size: 10000
  retry_attempts: 5
  retry_backoff: 500ms
  health_check_interval: 15s

modules:
  lrs:
    batch_size: 50
    timeout: 15s
    
  opencode:
    timeout: 30s
    auto_commit: true
    
  neuralblitz:
    backend: "cuda"
    tensor_ops_threads: 8
    max_batch_size: 64
```

### Monitoring Setup

```go
// Prometheus metrics integration
import (
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promhttp"
)

var (
    requestDuration = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name: "bridge_request_duration_seconds",
            Help: "Time spent processing requests",
        },
        []string{"module", "type"},
    )
    
    requestTotal = prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "bridge_requests_total",
            Help: "Total number of requests",
        },
        []string{"module", "type", "status"},
    )
)

func init() {
    prometheus.MustRegister(requestDuration)
    prometheus.MustRegister(requestTotal)
}

// In request handler
func (b *Bridge) handleRequest(req *ModuleRequest) (*ModuleResponse, error) {
    start := time.Now()
    defer func() {
        duration := time.Since(start).Seconds()
        requestDuration.WithLabelValues(req.Target, req.Type).Observe(duration)
    }()
    
    response, err := processRequest(req)
    
    status := "success"
    if err != nil || (response != nil && !response.Success) {
        status = "error"
    }
    requestTotal.WithLabelValues(req.Target, req.Type, status).Inc()
    
    return response, err
}
```

This implementation guide provides everything needed to understand, implement, test, and deploy the bidirectional communication system effectively.