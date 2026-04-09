# NeuralBlitz / OpenCode LRS — System Architecture

**Version:** 2.0.0  
**Last Updated:** April 9, 2026

---

## Overview

NeuralBlitz is a **multi-language, multi-component AI development platform** that combines active inference agents, cognitive consciousness engines, governance systems, and enterprise infrastructure into a unified ecosystem.

The platform is built on **FastAPI** (Python 3.11+) with supporting services in Go, Rust, Java, and TypeScript.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ React    │  │ React    │  │ Slack    │  │ VS Code  │           │
│  │ Dashboard│  │ Native   │  │ Bot      │  │ Extension│           │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘           │
│       │              │              │              │                 │
│       └──────────────┴──────────────┴──────────────┘                 │
│                            │                                         │
│                    HTTP / WebSocket / gRPC                           │
├────────────────────────────┼─────────────────────────────────────────┤
│                      API GATEWAY LAYER                               │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │              FastAPI Application (port 5000)                 │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │    │
│  │  │ JWT Auth │ │ Rate     │ │ Redis/   │ │ CORS     │       │    │
│  │  │ Middleware│ │ Limiter  │ │ LRU Cache│ │ Middleware│      │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │    │
│  │  │WebSocket │ │ Event    │ │Prometheus│ │ ML       │       │    │
│  │  │ Manager  │ │ Bus      │ │ Metrics  │ │ Pipeline │       │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │    │
│  └─────────────────────────────────────────────────────────────┘    │
├────────────────────────────┼─────────────────────────────────────────┤
│                     SERVICE LAYER                                    │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                │
│  │ LRS-Agents   │ │NeuralBlitz   │ │Multi-Agent   │                │
│  │ Framework    │ │ v50 Engine   │ │ Coordinator  │                │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘                │
│         │                │                │                          │
│  ┌──────┴───────┐ ┌──────┴───────┐ ┌──────┴───────┐                │
│  │Capability    │ │Governance    │ │Federated     │                │
│  │Kernels       │ │& Ethics      │ │Learning      │                │
│  └──────────────┘ └──────────────┘ └──────────────┘                │
├────────────────────────────┼─────────────────────────────────────────┤
│                   INFRASTRUCTURE LAYER                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐               │
│  │InfluxDB  │ │Timescale │ │Prometheus│ │ Grafana  │               │
│  │Telemetry │ │DB Metrics│ │Monitoring│ │Dashboards│               │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐               │
│  │ IoT Mesh │ │  IPFS    │ │ Edge     │ │Serverless│               │
│  │ (MQTT)   │ │ Storage  │ │Computing │ │ Deploy   │               │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘               │
├────────────────────────────┼─────────────────────────────────────────┤
│                      DATA LAYER                                      │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                │
│  │ SQLAlchemy   │ │ Vector DBs   │ │ File System  │                │
│  │ (SQLite/PG)  │ │(Chroma/      │ │ (Plugins,    │                │
│  │              │ │ Weaviate/    │ │  Models,     │                │
│  │              │ │ Pinecone)    │ │  Configs)    │                │
│  └──────────────┘ └──────────────┘ └──────────────┘                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### 1. API Gateway (`src/`)

The main application is a **FastAPI** server running on port 5000 with:

| Component | File | Purpose |
|-----------|------|---------|
| **App Factory** | `app_factory_v2.py` | Creates FastAPI app with all middleware |
| **Authentication** | `middleware/auth.py` | JWT auth with roles (Admin/Developer/Viewer/Agent) |
| **Rate Limiting** | `middleware/rate_limiter.py` | Token bucket with configurable profiles |
| **Caching** | `middleware/cache.py` | Redis backend with in-memory LRU fallback |
| **WebSocket** | `middleware/websocket.py` | Real-time connections with rooms |
| **Event Bus** | `middleware/event_bus.py` | Async pub/sub with priority queue |
| **Metrics** | `middleware/metrics.py` | Prometheus counters, gauges, histograms |
| **Database** | `middleware/database.py` | SQLAlchemy ORM with Repository pattern |
| **ML Pipeline** | `ml_pipeline.py` | scikit-learn classifiers, regressors, clustering |
| **Audio Processing** | `audio_processing.py` | FFT-based audio feature extraction |

**API Endpoints:**
- `POST /api/v2/auth/login` — User authentication
- `POST /api/v2/auth/register` — User registration
- `POST /api/v2/auth/refresh` — Token refresh
- `GET /api/v2/agents` — List agents
- `POST /api/v2/agents` — Create agent
- `POST /api/v2/ml/train` — Train ML model
- `POST /api/v2/ml/predict` — Run prediction
- `GET /api/v2/plugins` — List plugins
- `GET /api/v2/events` — Event stream
- `GET /api/v2/health` — Health check
- `GET /metrics` — Prometheus metrics
- `GET /ws/connect/{client_id}` — WebSocket connection

### 2. LRS-Agents (`lrs_agents/`)

**Active Inference Framework** based on the Free Energy Principle:

- **Precision Tracking**: Beta distribution confidence (α/β parameters)
- **Tool Lenses**: Bidirectional tool abstraction with automatic error tracking
- **Expected Free Energy**: G = Epistemic Value - Pragmatic Value
- **Multi-Agent Coordination**: Social precision tracking, turn-based execution
- **Integrations**: LangChain, OpenAI Assistants, AutoGPT

**Key Modules:**
- `lrs/core/` — Precision, lenses, registry, free energy
- `lrs/agents/` — Orchestrator, researcher, coder, tester, planner, critic
- `lrs/enterprise/` — Distributed orchestration, security, monitoring
- `lrs/monitoring/` — Performance tracking, health checks, structured logging
- `lrs/neuralblitz_integration/` — Bridge to NeuralBlitz v50

### 3. NeuralBlitz v50 (`neuralblitz-v50/`)

**Cognitive Consciousness Engine** implemented in 10+ languages:

| Language | Purpose |
|----------|---------|
| **Python** | Primary implementation with FastAPI |
| **Go** | High-performance cognitive engine |
| **Rust** | Memory-safe core with async support |
| **Java** | Enterprise-grade cognitive processing |
| **JavaScript** | Web integration and demos |

**Core Concepts:**
- **7-Dimensional Intent Vector**: φ₁-Dominance, φ₂-Harmony, φ₃-Creation, φ₄-Preservation, φ₅-Transformation, φ₆-Knowledge, φ₇-Connection
- **Consciousness Model**: Coherence, complexity, consciousness level tracking
- **Neural Processing**: Spiking networks, attention focus, working memory

**Sub-Projects:**
- `Emergent-Prompt-Architecture/` — Dynamic prompt evolution with C.O.A.T. protocol
- `ComputationalAxioms/` — Mathematical/crypto foundation (GoldenDAG, TraceID)
- `Advanced-Research/` — Quantum computing, dimensional processing, BCI

### 4. Agents (`src/agents/`)

Multi-layered autonomous agent systems:

| File | Lines | Description |
|------|-------|-------------|
| `advanced_autonomous_agent_framework.py` | 1,471 | Full AAF: goals, tools, memory, ethics |
| `multi_layered_multi_agent_system.py` | 795 | 5-tier hierarchy with batch processing |
| `distributed_mlmas.py` | 496 | Multi-node coordination |
| `autonomous_self_evolution_simplified.py` | 371 | Evolutionary self-improvement |

### 5. Capability Kernels (`src/capabilities/`)

Specialized processing modules:

| Kernel | Purpose |
|--------|---------|
| **Bioinformatics CK** | Sequence analysis, protein analysis (Biopython) |
| **Data Quality Assessment** | Missing values, outliers, distribution analysis |
| **Feature Engineering** | Automated scaling, encoding, selection |
| **ML Automated Pipeline** | Model selection, hyperparameter optimization |
| **Computer Vision CK** | Image processing kernels |
| **Malware Signature Analyzer** | Multi-hash signature matching, YARA rules |
| **Network Anomaly Detector** | Statistical baselines, ML-based detection |
| **NeuralBlitz Code Kernels** | AutoProgrammer, CodeReviewer, TestGenerator |
| **Quadratic Voting CK** | Sybil-resistant voting with cryptographic commitments |

### 6. Governance (`src/governance/` + `Governance/`)

**AGES — Advanced Governance & Ethics System:**

| Component | Purpose |
|-----------|---------|
| **Transcendental Charter** | 15 ethical clauses (φ₁-φ₁₅) |
| **Veritas Engine** | Phase-coherence tracking |
| **Judex Quorum** | Multi-judge arbitration |
| **SentiaGuard** | LSTM-based ethical drift detection |
| **GoldenDAG Ledger** | Immutable audit trail |
| **Conscientia M3** | 14 correlated ethical metrics |

### 7. Federated Learning (`src/federated/`)

Privacy-preserving distributed ML:

- **Differential Privacy**: Gaussian noise, gradient clipping
- **Secure Aggregation**: Shamir secret sharing, Fernet encryption
- **PySyft Integration**: DP tensors, encrypted remote execution

### 8. Smart Cities (`src/cities/`)

Urban infrastructure optimization:

- **Traffic Optimization**: Flow control with reinforcement learning
- **Energy Management**: Renewable integration, load balancing
- **Safety Coordination**: Public safety systems
- **Unified Controller**: Multi-system orchestration

### 9. Integrations (`src/integrations/`)

Vector database connectors:

- **ChromaDB**: Local vector database with embedding support
- **Pinecone**: Cloud vector database with managed infrastructure
- **Weaviate**: Semantic vector search with GraphQL

### 10. Monitoring Stack

| Service | Port | Purpose |
|---------|------|---------|
| **InfluxDB** | 8086 | Time-series telemetry |
| **TimescaleDB** | 5432 | Agent metrics (PostgreSQL + hypertables) |
| **Prometheus** | 9090 | System monitoring with alerts |
| **Grafana** | 3000 | Visualization dashboards |
| **Node Exporter** | 9100 | Host metrics |
| **cAdvisor** | 8080 | Container metrics |

### 11. Infrastructure Components

| Component | Location | Purpose |
|-----------|----------|---------|
| **IoT Mesh System** | `iot_mesh_system/` | MQTT-based device networking |
| **IPFS Integration** | `ipfs_integration/` | Decentralized storage |
| **Edge Computing** | `edge_computing/` | Coral TPU, Jetson Nano, Raspberry Pi |
| **Serverless** | `serverless_deployments/` | AWS Lambda, Azure Functions, GCP Cloud Run |
| **Voice Interface** | `voice_interface/` | Whisper STT, TTS, command parsing |
| **Slack Bot** | `neuralblitz_slack_bot/` | Agent management via Slack |

### 12. Frontend Applications

| App | Tech | Location |
|-----|------|----------|
| **Dashboard** | React + Bun | `neuralblitz-dashboard/` |
| **Mobile** | React Native (Expo) | `neuralblitz-mobile/` |
| **VS Code Extension** | TypeScript | `vs-code/` |

---

## Data Flow

### Request Lifecycle

```
Client Request
    │
    ▼
┌─────────────────────┐
│  CORS Middleware     │ ← Allow cross-origin requests
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  Prometheus Metrics  │ ← Track request duration, status
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  Rate Limiter        │ ← Token bucket check
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  JWT Auth            │ ← Validate token (if protected endpoint)
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  Cache Check         │ ← Return cached response if available
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  Route Handler       │ ← Business logic execution
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  Event Emit          │ ← Publish event to bus
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  Response + Cache    │ ← Store response, return to client
└─────────────────────┘
```

### Event Bus Flow

```
Publisher → Event(priority, type, data)
    │
    ▼
┌─────────────────────┐
│  Event Bus Queue     │ ← Priority-ordered events
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  Subscriber Match    │ ← Pattern-based routing
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  Async Handler       │ ← With retry (3 attempts)
└──────────┬──────────┘
           ▼
    ┌──────┴──────┐
    ▼             ▼
 Success      Failed (3×)
    │             │
    ▼             ▼
 Completed    Dead Letter Queue
```

---

## Security Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Security Layers                       │
│                                                          │
│  Layer 1: JWT Authentication                             │
│  ├── Token pairs (access + refresh)                      │
│  ├── Role-based access (Admin/Developer/Viewer/Agent)    │
│  ├── API key support for service accounts                │
│  └── Password hashing (SHA-256 + salt)                   │
│                                                          │
│  Layer 2: Rate Limiting                                  │
│  ├── Token bucket algorithm                              │
│  ├── Per-user / per-IP profiles                          │
│  └── Configurable profiles (strict, moderate, relaxed)   │
│                                                          │
│  Layer 3: Governance & Ethics                            │
│  ├── Charter compliance (15 clauses)                     │
│  ├── Ethical drift detection (LSTM)                      │
│  └── GoldenDAG audit trail                               │
│                                                          │
│  Layer 4: Infrastructure Security                        │
│  ├── CORS configuration                                  │
│  ├── Input validation (Pydantic)                         │
│  └── Container isolation (Docker)                        │
└─────────────────────────────────────────────────────────┘
```

---

## Deployment Architecture

### Local Development
```
src/main.py → Uvicorn → FastAPI (port 5000)
```

### Docker Compose (Monitoring Stack)
```yaml
Services: influxdb, timescaledb, prometheus, grafana, node-exporter, cadvisor
Network: tsdb-network (bridge)
Volumes: Persistent data per service
```

### Kubernetes (Production)
```
Namespace: neuralblitz
Deployments: lrs-agents, neuralblitz-v50, integration-bridge
Services: ClusterIP + Ingress
HPA: 5-20 replicas based on CPU/memory
ConfigMaps: Environment configuration
Secrets: API keys, JWT secrets
```

### Serverless (Multi-Cloud)
```
AWS Lambda → SAM template + inference handler
Azure Functions → audit, governance, inference handlers
GCP Cloud Run → Docker container + Terraform
```

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI, Uvicorn, Python 3.11+ |
| **AI/LLM** | LRS-Agents, OpenAI, Anthropic, Google, Ollama |
| **ML** | scikit-learn, PySyft, NumPy |
| **Database** | SQLAlchemy (SQLite/PostgreSQL), ChromaDB, Pinecone, Weaviate |
| **Cache** | Redis (with in-memory LRU fallback) |
| **Monitoring** | Prometheus, Grafana, InfluxDB, TimescaleDB |
| **Frontend** | React (Bun), React Native (Expo) |
| **Testing** | pytest, pytest-asyncio, pytest-cov |
| **Deployment** | Docker, Kubernetes, AWS Lambda, Azure Functions, GCP Cloud Run |
| **CI/CD** | GitHub Actions |
| **Other Languages** | Go, Rust, Java, TypeScript, JavaScript |

---

## Key Design Patterns

| Pattern | Implementation |
|---------|---------------|
| **Factory** | `create_app()` in `app_factory_v2.py` |
| **Repository** | `Repository` class in `middleware/database.py` |
| **Pub/Sub** | `EventBus` in `middleware/event_bus.py` |
| **Middleware Chain** | FastAPI middleware stack |
| **Plugin** | Hot-loadable Python modules from `plugins/` |
| **Circuit Breaker** | In `lrs_agents/integration-bridge/` |
| **Strategy** | Rate limit profiles, ML model selection |
| **Observer** | Event subscribers, WebSocket rooms |
| **Dependency Injection** | FastAPI `Depends()` for auth, DB |

---

## File Structure Summary

```
/home/runner/workspace/
├── src/                          # Main FastAPI application
│   ├── main.py                   # Entry point (uvicorn port 5000)
│   ├── app_factory_v2.py        # Full app with all middleware
│   ├── middleware/               # Auth, cache, WebSocket, events, metrics
│   ├── agents/                   # Autonomous agent systems
│   ├── capabilities/             # Capability kernels
│   ├── cities/                   # Smart city systems
│   ├── federated/                # Federated learning
│   ├── governance/               # Ethics system
│   ├── integrations/             # Vector DB connectors
│   └── utils/                    # Infrastructure utilities
├── lrs_agents/                   # LRS active inference framework
├── neuralblitz-v50/              # Cognitive consciousness engine
├── neuralblitz-dashboard/        # React web dashboard
├── neuralblitz-mobile/           # React Native mobile app
├── neuralblitz_slack_bot/        # Slack integration
├── voice_interface/              # Voice interface (Whisper + TTS)
├── iot_mesh_system/              # MQTT device mesh
├── edge_computing/               # Edge device deployments
├── serverless_deployments/       # Multi-cloud serverless
├── Governance/                   # Ethics monitoring systems
├── CapabilityKernels/            # Audio processing kernels
├── plugins/                      # Plugin system
├── tests/                        # Root-level test suite
├── docs/                         # Technical documentation hub
└── docker-compose.yml            # Monitoring stack
```

---

*This architecture document provides a complete overview of how all components fit together. For detailed component documentation, see individual READMEs in each directory.*
