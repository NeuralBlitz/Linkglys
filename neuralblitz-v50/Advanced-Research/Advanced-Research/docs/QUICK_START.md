# Quick Start Guide

Get the bidirectional communication system running in **5 minutes**!

## 🚀 Quick Installation

### 1. Clone & Build
```bash
git clone <repository-url>
cd Advanced-Research
go mod tidy
go build -o bin/bridge ./cmd/bridge
```

### 2. Run Demo
```bash
./bin/bridge -demo
```

That's it! The system will demonstrate all capabilities automatically.

## 🎯 Interactive Mode

For hands-on experimentation:

```bash
./bin/bridge
```

Try these commands:
```bash
> create "My Research" "Content about AI" "ideas" "theory" "alice"
> compute "1,2,3,4" "eigenvalue" "alice"
> search "machine learning" "synthesis" "alice"
> status
```

## 📊 What You'll See

### Automated Demo Mode:
- ✅ Document creation with automatic LRS tracking
- ✅ Geometric computation with event broadcasting
- ✅ Cross-module communication
- ✅ Workflow automation
- ✅ System monitoring

### Interactive Mode:
- 📝 Create research documents
- 🔬 Compute geometric features
- 🔍 Search and retrieve documents
- 📈 Track learning progress
- 📊 Monitor system health

## 🔧 Key Features Demonstrated

### 1. Bidirectional Communication
```go
// Document creation → Automatic LRS tracking → NeuralBlitz notification
docID, _ := orchestrator.CreateResearchDocument(ctx, title, content, stage, docType, user)
```

### 2. Event-Driven Architecture
```go
// One event triggers multiple module responses
bridge.Broadcast(ctx, "document_created", documentInfo)
```

### 3. Workflow Automation
```go
// Multi-step processes across modules
workflow := &Workflow{
    Steps: []WorkflowStep{
        {Module: "opencode", Action: "create_document"},
        {Module: "neuralblitz", Action: "compute_features"},
        {Module: "lrs", Action: "record_progress"},
    },
}
```

## 📋 Configuration

### Development (default)
```yaml
bridge:
  max_concurrent_requests: 100
  default_timeout: 30s

modules:
  lrs:
    enabled: true
    endpoint: "http://localhost:8081/xapi/"
    
  opencode:
    enabled: true
    workspace: "dev-workspace"
    
  neuralblitz:
    enabled: true
    backend: "cpu"
```

### Production
```yaml
# See configs/production.yaml
# - Higher request limits
# - GPU backend for NeuralBlitz
# - External services
# - Monitoring enabled
```

## 🔍 Health Checks

Verify system is working:

```bash
curl http://localhost:8080/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "modules": {
    "lrs": "running",
    "opencode": "running", 
    "neuralblitz": "running"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 📈 Metrics

Access monitoring data:

```bash
curl http://localhost:8080/api/metrics
```

Key metrics:
- Request throughput
- Response times
- Module health
- Active workflows
- Event processing rates

## 🐳 Docker Quick Start

```bash
# Build image
docker build -t bidirectional-bridge .

# Run demo
docker run -p 8080:8080 bidirectional-bridge -demo

# Interactive mode
docker run -it -p 8080:8080 bidirectional-bridge
```

## ☸️ Kubernetes Deployment

```bash
# Deploy to Kubernetes
kubectl apply -f k8s/

# Check status
kubectl get pods -l app=bidirectional-bridge

# Access service
kubectl port-forward service/bridge-service 8080:8080
```

## 🔧 Next Steps

### For Developers:
1. **Read [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md)** - Full setup guide
2. **Review [API_REFERENCE.md](./API_REFERENCE.md)** - Complete API documentation  
3. **Check [EXAMPLES.md](./EXAMPLES.md)** - Copy-paste ready examples
4. **Understand [UNDERSTANDING_THE_SYSTEM.md](./UNDERSTANDING_THE_SYSTEM.md)** - Architecture concepts

### For Operations:
1. **Configure production settings** - Modify configs/production.yaml
2. **Set up monitoring** - Enable Prometheus/Jaeger integration
3. **Deploy with Kubernetes** - Use provided K8s manifests
4. **Monitor health checks** - Set up alerting on /api/health

### For Architects:
1. **Review [BIDIRECTIONAL_API_COMMUNICATION.md](./BIDIRECTIONAL_API_COMMUNICATION.md)** - Architecture decisions
2. **Plan integrations** - Design custom modules and workflows
3. **Scale deployment** - Plan horizontal scaling strategy
4. **Security hardening** - Implement access controls and audit logging

## 🆘 Common Issues & Solutions

| Problem | Solution |
|----------|----------|
| Module not responding | Check `curl http://localhost:8080/api/modules/status` |
| Request timeouts | Increase `default_timeout` in config |
| Event loss | Increase `event_buffer_size` |
| High memory usage | Reduce `max_concurrent_requests` |
| Connection refused | Verify all required services are running |

## 📚 Documentation Map

```
📖 Documentation/
├── 📋 README.md (this file)
├── 🚀 IMPLEMENTATION_GUIDE.md
├── 📚 API_REFERENCE.md  
├── 🏗️ BIDIRECTIONAL_API_COMMUNICATION.md
├── 🧠 UNDERSTANDING_THE_SYSTEM.md
└── 💡 EXAMPLES.md
```

## 🎯 Success Indicators

You're successfully running the system when you see:

```bash
=== Bidirectional Communication System Demo ===
Initializing system...
Starting system...
Module registered: lrs
Module registered: opencode  
Module registered: neuralblitz
All modules started successfully

--- Demo 1: Document Creation & Automatic Tracking ---
Creating research document...
✅ Document created successfully
System status after document creation

--- Demo 2: Geometric Computation & Event Broadcasting ---
Computing geometric features...
✅ Geometric features computed

✅ All demonstrations completed!
```

## 🎉 Congratulations!

You now have a fully functional bidirectional communication system with:

- ⚡ **Ultra-low latency** (<1ms in-process communication)
- 🔄 **Full bidirectional** communication between all modules
- 🎯 **Automatic workflow** orchestration
- 📊 **Built-in monitoring** and health checks
- 🛡️ **Production-ready** reliability and scalability

**Next:** Explore the full documentation to customize and extend the system for your specific needs!

---

*Need help? Check the full documentation directory or open an issue on GitHub.*