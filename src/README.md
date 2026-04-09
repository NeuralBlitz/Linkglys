# src/ — NeuralBlitz Main Application

**Location:** `/home/runner/workspace/src/`  
**Language:** Python 3.11+ (FastAPI) + TypeScript (VS Code extension)  
**Port:** 5000

---

## Overview

This directory contains the **main FastAPI application** for NeuralBlitz. It serves as the central API gateway, integrating authentication, rate limiting, caching, WebSocket communication, event-driven architecture, Prometheus metrics, ML pipelines, and the plugin system.

---

## Quick Start

```bash
# Start the server
cd src && python3 main.py

# Server runs at http://localhost:5000
# API docs at http://localhost:5000/docs
```

---

## Directory Structure

```
src/
├── main.py                    # Entry point (uvicorn port 5000)
├── app_factory_v2.py          # Full FastAPI app with all middleware
├── ml_pipeline.py             # scikit-learn ML pipeline
├── audio_processing.py        # FFT audio feature extraction
│
├── 📂 middleware/              # FastAPI middleware layer
├── 📂 agents/                  # Autonomous agent systems
├── 📂 capabilities/            # Capability Kernels
├── 📂 cities/                  # Smart city systems
├── 📂 federated/               # Federated learning
├── 📂 governance/              # Ethics and governance
├── 📂 integrations/            # Vector database connectors
├── 📂 utils/                   # Infrastructure utilities
├── 📂 commands/                # VS Code NBCL commands (TS)
├── 📂 debugger/                # VS Code debug adapter (TS)
├── 📂 providers/               # VS Code language providers (TS)
└── 📂 util/                    # VS Code utilities (TS)
```

---

## Key Files

| File | Lines | Purpose |
|------|-------|---------|
| `main.py` | 11 | Entry point — creates app via `create_app()`, runs uvicorn on port 5000 |
| `app_factory_v2.py` | 461 | Full FastAPI app: auth, rate limiting, cache, WebSocket, events, metrics, ML, plugins |
| `ml_pipeline.py` | 387 | scikit-learn pipeline: classifiers, regressors, clustering, anomaly detection |
| `audio_processing.py` | ~350 | FFT audio features: RMS, MFCC, chroma, tempo, sound classification |

---

## Middleware Layer

The middleware stack processes requests in this order:

1. **CORS** — Cross-origin request handling
2. **Prometheus Metrics** — Request tracking
3. **Rate Limiter** — Token bucket algorithm
4. **JWT Auth** — Token validation (for protected endpoints)
5. **Cache** — Response caching (Redis or memory)
6. **Route Handler** — Business logic

See `middleware/README.md` for detailed middleware documentation.

---

## API Endpoints

### Authentication
- `POST /api/v2/auth/login` — Login with username/password
- `POST /api/v2/auth/register` — Register new user
- `POST /api/v2/auth/refresh` — Refresh access token
- `POST /api/v2/auth/api-key` — Generate API key
- `GET /api/v2/auth/me` — Get current user
- `GET /api/v2/auth/users` — List all users (admin only)

### Agents
- `GET /api/v2/agents` — List agents
- `POST /api/v2/agents` — Create agent
- `POST /api/v2/agents/{agent_id}/command` — Send command to agent
- `GET /api/v2/agents/{agent_id}/metrics` — Get agent metrics

### ML Pipeline
- `POST /api/v2/ml/train` — Train model (classification/regression)
- `POST /api/v2/ml/predict` — Run prediction
- `POST /api/v2/ml/cluster` — Cluster data (k-means/DBSCAN)
- `POST /api/v2/ml/anomalies` — Detect anomalies
- `GET /api/v2/ml/stats` — ML pipeline statistics

### Plugins
- `GET /api/v2/plugins` — List plugins
- `POST /api/v2/plugins` — Install plugin (admin)
- `DELETE /api/v2/plugins/{name}` — Remove plugin (admin)

### System
- `GET /api/v2/health` — Health check
- `GET /api/v2/stats` — System statistics
- `GET /api/v2/config` — Configuration details
- `GET /api/v2/events` — Event stream
- `GET /api/v2/events/dead-letters` — Dead letter queue
- `GET /api/v2/events/stats` — Event bus statistics
- `GET /metrics` — Prometheus metrics endpoint

### WebSocket
- `GET /ws/connect/{client_id}` — WebSocket connection

See [API.md](API.md) for complete API documentation with request/response examples.

---

## Architecture

```
┌─────────────────────────────────────────┐
│              Client Request              │
├─────────────────────────────────────────┤
│  CORS → Metrics → Rate Limit → Auth     │
├─────────────────────────────────────────┤
│            Route Handler                │
│  (Agent, ML, Plugin, Event, System)     │
├─────────────────────────────────────────┤
│         Event Bus + Database            │
├─────────────────────────────────────────┤
│              Response                   │
└─────────────────────────────────────────┘
```

---

## Testing

```bash
# Test from project root
pytest tests/ -v

# Test specific module
pytest tests/test_app_factory.py -v
pytest tests/test_simple_app.py -v
```

---

## Related Documentation

- [Middleware README](middleware/README.md) — Auth, cache, WebSocket, events
- [Agents README](agents/README.md) — Autonomous agent systems
- [Capabilities README](capabilities/README.md) — Capability Kernels
- [API.md](API.md) — Complete API reference
- [ARCHITECTURE.md](../../ARCHITECTURE.md) — System architecture overview
