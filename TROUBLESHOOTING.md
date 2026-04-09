# NeuralBlitz / OpenCode LRS — Troubleshooting Guide

**Last Updated:** April 9, 2026

---

## Quick Diagnostics

Run this to check system health:

```bash
# Check API health
curl -s http://localhost:5000/api/v2/health | python -m json.tool

# Check all services
curl -s http://localhost:5000/api/v2/stats | python -m json.tool

# Check Prometheus metrics
curl -s http://localhost:5000/metrics | head -20
```

---

## Common Issues

### Server Won't Start

#### Port 5000 Already in Use

**Symptoms:**
```
OSError: [Errno 98] Address already in use
```

**Solution:**
```bash
# Find what's using port 5000
lsof -ti:5000

# Kill the process
lsof -ti:5000 | xargs kill -9

# Or change port in src/main.py
uvicorn app_factory:app --reload --port 5001
```

#### Missing Dependencies

**Symptoms:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
# Install all dependencies
pip install -e ".[dev]"

# Or install specific extras
pip install fastapi uvicorn pydantic PyJWT
```

#### Import Errors

**Symptoms:**
```
ImportError: cannot import name 'create_app' from 'app_factory'
```

**Solution:**
```bash
# Ensure you're running from correct directory
cd /home/runner/workspace

# Add to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Or run module directly
python -m src.main
```

---

### Authentication Issues

#### 401 Unauthorized on All Endpoints

**Symptoms:**
```json
{"detail": "Not authenticated"}
```

**Solution:**
```bash
# Login first
curl -X POST http://localhost:5000/api/v2/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Use the access_token in subsequent requests
curl http://localhost:5000/api/v2/agents \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Invalid Credentials

**Symptoms:**
```json
{"detail": "Invalid credentials"}
```

**Solution:**
```bash
# Check default users are seeded
python -c "
from middleware.auth import user_store
print(user_store.list_users())
"

# Create admin user manually
python -c "
from middleware.auth import user_store, Role
user_store.create_user(
    username='admin',
    email='admin@neuralblitz.io',
    password='admin123',
    role=Role.ADMIN
)
"
```

#### JWT Secret Changed

**Symptoms:** All existing tokens invalid after restart

**Solution:**
```bash
# Set consistent JWT_SECRET in .env
echo 'JWT_SECRET=my-consistent-secret' >> .env

# Restart server
```

---

### Database Issues

#### Database Locked

**Symptoms:**
```
sqlite3.OperationalError: database is locked
```

**Solution:**
```bash
# Kill any processes using the database
lsof neuralblitz.db

# Delete and recreate
rm neuralblitz.db
python -c "from middleware.database import init_db; init_db()"
```

#### SQLAlchemy Migration Errors

**Symptoms:**
```
sqlalchemy.exc.OperationalError: no such table: users
```

**Solution:**
```bash
# Reinitialize database
python -c "
from middleware.database import init_db
init_db(ensure_tables=True)
"
```

---

### Redis/Caching Issues

#### Redis Connection Refused

**Symptoms:**
```
redis.exceptions.ConnectionError: Connection refused
```

**Solution:**
```bash
# Option 1: Start Redis
redis-server &

# Option 2: Unset REDIS_URL to use memory cache
unset REDIS_URL

# Option 3: Use Docker Redis
docker run -d -p 6379:6379 redis:latest
```

#### Cache Not Working

**Symptoms:** Every request is slow, no cache hits

**Solution:**
```bash
# Check cache backend
curl http://localhost:5000/api/v2/health | grep cache
# Should show "redis" or "memory"

# Check cache stats
curl http://localhost:5000/api/v2/stats | python -m json.tool
```

---

### WebSocket Issues

#### WebSocket Connection Fails

**Symptoms:**
```
WebSocket connection to 'ws://localhost:5000/ws/connect/test' failed
```

**Solution:**
```bash
# Verify WebSocket is enabled
curl http://localhost:5000/api/v2/health | grep websocket

# Test WebSocket
wscat -c ws://localhost:5000/ws/connect/test-client

# Check server logs for WebSocket errors
```

---

### Event Bus Issues

#### Events Not Being Processed

**Symptoms:** Events published but no handlers fire

**Solution:**
```bash
# Check event bus stats
curl http://localhost:5000/api/v2/events/stats

# Check dead letter queue
curl http://localhost:5000/api/v2/events/dead-letters

# List subscriptions
curl http://localhost:5000/api/v2/events/subscriptions

# Check event status
curl "http://localhost:5000/api/v2/events?status=failed"
```

---

### ML Pipeline Issues

#### Model Training Fails

**Symptoms:**
```json
{"detail": "Unknown task"}
```

**Solution:**
```bash
# Valid task types: classification, regression, clustering

# Train classifier
curl -X POST http://localhost:5000/api/v2/ml/train \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "model_name": "my-model",
    "model_type": "random_forest",
    "task": "classification",
    "features": [[1, 2], [3, 4], [5, 6]],
    "labels": [0, 1, 0]
  }'
```

#### scikit-learn Not Installed

**Symptoms:**
```
ModuleNotFoundError: No module named 'sklearn'
```

**Solution:**
```bash
pip install scikit-learn numpy
```

---

### Docker/Monitoring Issues

#### Docker Compose Won't Start

**Symptoms:**
```
ERROR: for influxdb  Cannot start service
```

**Solution:**
```bash
# Check Docker is running
docker ps

# Remove stale containers
docker-compose down -v
docker-compose up -d

# Check individual service logs
docker-compose logs influxdb
docker-compose logs timescaledb
```

#### Prometheus Not Scraping Metrics

**Symptoms:** No metrics at http://localhost:9090

**Solution:**
```bash
# Verify prometheus.yml is mounted
docker exec prometheus-monitor cat /etc/prometheus/prometheus.yml

# Reload Prometheus config
curl -X POST http://localhost:9090/-/reload

# Check Prometheus targets
open http://localhost:9090/targets
```

#### Grafana Dashboards Empty

**Symptoms:** No data in Grafana

**Solution:**
```bash
# Verify data source is configured
curl http://localhost:3000/api/datasources \
  -u admin:your_password

# Check Prometheus is reachable from Grafana
docker exec grafana-dashboard wget -qO- http://prometheus:9090/-/healthy
```

---

### Plugin System Issues

#### Plugin Not Loading

**Symptoms:** Plugin file in `plugins/` but not showing in API

**Solution:**
```bash
# Check plugin file syntax
python -m py_compile plugins/my_plugin.py

# Verify plugin naming (no underscore prefix)
ls plugins/*.py

# Restart server to reload plugins
```

---

### LRS-Agents Issues

#### Agent Not Adapting

**Symptoms:** Agent keeps failing without trying alternatives

**Solution:**
```python
# Check precision threshold
from lrs.core.precision import PrecisionParameters
p = PrecisionParameters()
print(p.value)  # Should start at 0.5

# Precision drops on failure, triggers adaptation at < 0.4
# If not adapting, check if prediction_error is being set correctly
```

#### Tool Failures Not Tracked

**Symptoms:** Precision not updating

**Solution:**
```python
# Ensure tools return ExecutionResult with prediction_error
from lrs.core.lens import ExecutionResult

# On success
return ExecutionResult(success=True, value=data, prediction_error=0.1)

# On failure
return ExecutionResult(success=False, value=None, prediction_error=0.9)
```

---

### NeuralBlitz v50 Issues

#### Import Errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'neuralblitz'
```

**Solution:**
```bash
# Install neuralblitz package
cd neuralblitz-v50/python && pip install -e .

# Or add to Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)/neuralblitz-v50/python
```

---

### Performance Issues

#### API Response Slow

**Diagnosis:**
```bash
# Check rate limiter stats
curl http://localhost:5000/api/v2/stats | python -m json.tool

# Check cache hit rate
# Low hit rate = cache not being utilized

# Check ML pipeline load
curl http://localhost:5000/api/v2/ml/stats
```

**Solutions:**
1. Enable Redis caching: `export REDIS_URL=redis://localhost:6379/0`
2. Check rate limit profile — may be too restrictive
3. Profile slow endpoints with `time curl ...`

#### High Memory Usage

**Diagnosis:**
```bash
# Check Python process memory
ps aux | grep python

# Check Docker container memory
docker stats
```

**Solutions:**
1. Reduce cache size in `middleware/cache.py`
2. Use Redis instead of in-memory cache
3. Limit agent count in `src/agents/`

---

### Testing Issues

#### Tests Fail with ModuleNotFoundError

**Solution:**
```bash
# Add project root to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Or run pytest with path
PYTHONPATH=. pytest tests/ -v
```

#### Async Tests Not Running

**Solution:**
```bash
# Ensure pytest-asyncio is installed
pip install pytest-asyncio

# Check pytest.ini has asyncio_mode = auto
```

---

## Getting Help

### Logs

```bash
# API server logs (stdout)
# Start with verbose logging
uvicorn src.app_factory_v2:app --reload --log-level debug

# Docker service logs
docker-compose logs -f

# LRS-Agents logs
cd lrs_agents && pytest tests/ -v --log-cli-level=INFO
```

### System Information

When reporting issues, include:

```bash
# Python version
python --version

# Installed packages
pip list

# System info
uname -a

# Docker version
docker --version
docker-compose --version
```

### Common Debug Commands

```bash
# Test database connectivity
python -c "from middleware.database import get_db; print('DB OK')"

# Test Redis
python -c "import redis; r = redis.Redis(); print(r.ping())"

# Test imports
python -c "from src.app_factory_v2 import create_app; print('Import OK')"

# Run health check
curl -s http://localhost:5000/api/v2/health | python -m json.tool
```
