# NeuralBlitz / OpenCode LRS — Development Setup Guide

**Last Updated:** April 9, 2026

---

## Prerequisites

### Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| **Python** | 3.11+ | Backend runtime |
| **Node.js** | 18+ | Frontend tooling |
| **Bun** | Latest | Dashboard build tool |
| **Docker** | 20.10+ | Containerization |
| **Docker Compose** | 2.0+ | Multi-container orchestration |
| **Git** | 2.30+ | Version control |

### Recommended (Optional)

| Software | Purpose |
|----------|---------|
| **Go** | NeuralBlitz v50 Go implementation |
| **Rust** | NeuralBlitz v50 Rust implementation |
| **Java 17+** | NeuralBlitz v50 Java implementation |
| **PostgreSQL 15+** | Production database (SQLite used in dev) |
| **Redis** | Production cache backend (memory fallback in dev) |

---

## Quick Start (5 Minutes)

### 1. Clone the Repository

```bash
git clone https://github.com/NeuralBlitz/opencode-lrs-agents-nbx
cd opencode-lrs-agents-nbx
```

### 2. Install Python Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e ".[dev]"
```

### 3. Set Environment Variables

```bash
# Create .env file
cat > .env << 'EOF'
JWT_SECRET=your-secret-key-change-in-production
DATABASE_URL=sqlite:///./neuralblitz.db
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
EOF
```

### 4. Start the API Server

```bash
# Option A: Using npm/bun scripts
bun start
# or
npm start

# Option B: Direct Python
cd src && python3 main.py

# Option C: With uvicorn directly
uvicorn src.app_factory_v2:app --reload --port 5000
```

### 5. Verify It's Running

```bash
# Health check
curl http://localhost:5000/api/v2/health

# API docs (Swagger UI)
open http://localhost:5000/docs

# Alternative docs (ReDoc)
open http://localhost:5000/redoc
```

**You should see:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "uptime_seconds": 12345,
  "components": {
    "auth": "enabled",
    "rate_limiting": "enabled",
    "cache": "memory",
    "websocket": "enabled",
    "event_bus": "enabled",
    "metrics": "prometheus",
    "ml_pipeline": "enabled"
  }
}
```

---

## Full Development Environment

### 1. Start Monitoring Stack (Docker Compose)

```bash
# Start all monitoring services
docker-compose up -d

# Verify services
docker-compose ps

# View logs
docker-compose logs -f influxdb
docker-compose logs -f timescaledb
docker-compose logs -f prometheus
docker-compose logs -f grafana
```

**Services available:**
| Service | URL | Credentials |
|---------|-----|-------------|
| **InfluxDB** | http://localhost:8086 | admin / your password |
| **TimescaleDB** | localhost:5432 | agent_user / your password |
| **Prometheus** | http://localhost:9090 | No auth |
| **Grafana** | http://localhost:3000 | admin / your password |
| **Node Exporter** | http://localhost:9100/metrics | No auth |
| **cAdvisor** | http://localhost:8080 | No auth |

### 2. Start LRS-Agents (Optional)

```bash
cd lrs_agents

# Install in development mode
pip install -e ".[all]"

# Run tests to verify setup
pytest tests/ -v --tb=short
```

### 3. Start NeuralBlitz v50 (Optional)

```bash
cd neuralblitz-v50

# Python implementation
cd python && pip install -e .

# Or Go implementation
cd go && go build ./cmd/neuralblitz

# Or Rust implementation
cd rust && cargo build
```

### 4. Start Frontend Dashboard (Optional)

```bash
cd neuralblitz-dashboard

# Install dependencies
bun install

# Start dev server
bun run dev
# Dashboard available at http://localhost:3000
```

### 5. Start Mobile App (Optional)

```bash
cd neuralblitz-mobile

# Install dependencies
bun install

# Start Expo
bun run start
# Scan QR code with Expo Go app
```

---

## IDE Setup

### VS Code (Recommended)

The project includes a **VS Code extension** in `vs-code/` with:

- **NBCL Language Support** — NeuralBlitz Command Language
- **Capability Kernel Completion** — Auto-complete for CK calls
- **Diagnostic Provider** — Lint NBCL files
- **Debug Adapter** — Debug agent execution

**Install:**
```bash
cd vs-code
npm install
npm run compile
# Press F5 to launch Extension Development Host
```

**Recommended Extensions:**
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "dbaeumer.vscode-eslint",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode"
  ]
}
```

### PyCharm

- Set Python interpreter to project virtualenv
- Configure test runner to pytest
- Enable coverage reporting

---

## Code Quality

### Run All Checks

```bash
# Linting
ruff check src/ lrs_agents/ tests/

# Type checking
mypy src/ lrs_agents/

# Code formatting
black src/ lrs_agents/ tests/

# Run tests
pytest tests/ -v --cov=src --cov-report=html

# View coverage
open htmlcov/index.html
```

### Pre-Commit Hooks

```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## Database Setup

### Development (SQLite — Default)

No setup needed. SQLite database is created automatically at `./neuralblitz.db`.

### Production (PostgreSQL)

```bash
# Set environment variable
export DATABASE_URL=postgresql://user:pass@host:5432/neuralblitz

# Initialize database
python -c "from middleware.database import init_db; init_db()"
```

### TimescaleDB (Agent Metrics)

```bash
# Start with docker-compose
docker-compose up -d timescaledb

# Schema is auto-applied from timescaledb/init/01-init-schema.sql

# Verify
psql -h localhost -U agent_user -d agent_metrics -c "\dt"
```

---

## Cache Setup

### Development (In-Memory LRU — Default)

No setup needed. Cache uses in-memory LRU with 10,000 max entries.

### Production (Redis)

```bash
# Install Redis
# macOS: brew install redis && brew services start redis
# Linux: sudo apt install redis-server

# Set environment variable
export REDIS_URL=redis://localhost:6379/0

# Verify connection
redis-cli ping
# → PONG
```

The application automatically detects Redis and switches from memory to Redis backend.

---

## Plugin Development

### Create a Plugin

```python
# plugins/my_plugin.py
from lrs.enterprise.opencode_plugin_architecture import ToolPlugin
from lrs.enterprise.opencode_plugin_architecture import PluginMetadata

class MyPlugin(ToolPlugin):
    def get_metadata(self):
        return PluginMetadata(
            name="my-plugin",
            version="1.0.0",
            description="My custom extension"
        )

    def initialize(self):
        # Setup logic
        pass

    async def execute(self, **kwargs):
        # Plugin logic
        return {"result": "success"}
```

### Test Your Plugin

```bash
# List plugins
curl http://localhost:5000/api/v2/plugins

# Plugin is auto-discovered from plugins/ directory
```

---

## Common Development Workflows

### Add a New API Endpoint

1. Open `src/app_factory_v2.py`
2. Add route under the `api` router:
```python
@api.get("/my-new-endpoint")
async def my_new_endpoint():
    return {"message": "Hello World"}
```
3. Test: `curl http://localhost:5000/api/v2/my-new-endpoint`

### Add a New Capability Kernel

1. Create file in `src/capabilities/my_ck.py`
2. Implement kernel class
3. Add JSON contract in `schemas/capabilities/my_ck.json`
4. Test: `pytest tests/capabilities/ -v`

### Add a New Agent

1. Create file in `src/agents/my_agent.py`
2. Implement agent class
3. Test: `pytest tests/agents/ -v`

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Port 5000 already in use** | `lsof -ti:5000 | xargs kill` or change port in `main.py` |
| **Import errors** | Run `pip install -e ".[dev]"` from project root |
| **Redis connection refused** | Start Redis: `redis-server` or remove `REDIS_URL` to use memory cache |
| **Database locked** | Delete `neuralblitz.db` and restart |
| **Docker permission denied** | `sudo usermod -aG docker $USER` then logout/login |
| **Tests fail with module not found** | Add project root to `PYTHONPATH`: `export PYTHONPATH=$PYTHONPATH:$(pwd)` |

---

## Next Steps

- Read the [Architecture Guide](ARCHITECTURE.md) for system overview
- Read the [API Reference](docs/API_REFERENCE.md) for endpoint details
- Read the [Testing Guide](TESTING.md) for test procedures
- Read component-specific READMEs in each directory
