# Middleware — FastAPI Middleware Layer

**Location:** `src/middleware/`
**Package:** `Linkglys Middleware Package`

---

## Overview

The middleware layer provides **cross-cutting concerns** for the FastAPI application: authentication, rate limiting, caching, WebSocket management, event-driven architecture, Prometheus metrics, database ORM, and health checks.

All components are exported through `__init__.py` for easy import:

```python
from middleware.auth import get_current_user, require_role, Role
from middleware.rate_limiter import rate_limit, RATE_LIMIT_PROFILES
from middleware.cache import cached, invalidate_cache
from middleware.websocket import ws_manager, emit_agent_status
from middleware.event_bus import emit, on_event, Event, EventPriority
from middleware.metrics import registry, prometheus_metrics_middleware
from middleware.database import get_db, Repository, init_db
```

---

## Components

### 1. Authentication (`auth.py` — 329 lines)

**Purpose:** JWT-based authentication with role-based access control.

**Key Features:**
- JWT token pairs (access + refresh)
- Password hashing (SHA-256 + salt)
- 4 roles: `ADMIN`, `DEVELOPER`, `VIEWER`, `AGENT`
- API key generation for service accounts
- Default users seeded on startup

**Key Classes & Functions:**
```python
class Role(Enum): ADMIN, DEVELOPER, VIEWER, AGENT
class User: user_id, username, email, role, hashed_password

user_store: UserStore  # In-memory user management
create_token_pair(user) → TokenPair  # Generate access + refresh tokens
decode_access_token(token) → dict  # Validate and decode JWT token
get_current_user(request) → User  # FastAPI dependency for auth
require_role(role) → User  # Role-based access dependency
```

**Usage:**
```python
from fastapi import Depends
from middleware.auth import get_current_active_user, require_role, Role

@app.get("/protected")
async def protected(user: User = Depends(get_current_active_user)):
    return {"message": f"Hello {user.username}"}

@app.delete("/admin-only")
async def admin_only(user: User = Depends(require_role(Role.ADMIN))):
    return {"message": "Admin action performed"}
```

### 2. Rate Limiter (`rate_limiter.py` — 180 lines)

**Purpose:** Token bucket rate limiting with configurable profiles.

**Key Features:**
- Token bucket algorithm
- Per-user and per-IP limiting
- 6 built-in profiles: default, strict, moderate, relaxed, api, webhook

**Usage:**
```python
from middleware.rate_limiter import rate_limit

@app.get("/api/data")
@rate_limit(profile="api")
async def get_data():
    return {"data": "..."}
```

### 3. Cache (`cache.py` — 220 lines)

**Purpose:** Response caching with Redis backend and in-memory LRU fallback.

**Key Features:**
- Redis backend (auto-detected)
- In-memory LRU cache (10,000 max entries) as fallback
- TTL support
- Pattern-based cache invalidation

**Usage:**
```python
from middleware.cache import cached, invalidate_cache

@app.get("/expensive-query")
@cached(ttl=300)  # Cache for 5 minutes
async def expensive_query():
    return {"result": "expensive computation"}

# Invalidate all keys matching pattern
await invalidate_cache("user:*")
```

### 4. WebSocket Manager (`websocket.py` — 250 lines)

**Purpose:** Real-time WebSocket connections with room support.

**Key Features:**
- Connection management with rooms
- Message types: agent_status, metrics, log, events
- Broadcast and per-client filtering
- Automatic cleanup on disconnect

**Usage:**
```python
from middleware.websocket import ws_manager, emit_agent_status

# Emit to all clients
await emit_agent_status("agent-1", "running", {"cpu": 0.5})

# Emit to specific room
await ws_manager.emit_to_room("agents", {"status": "updated"})
```

**WebSocket URL:** `ws://localhost:5000/ws/connect/{client_id}`

### 5. Event Bus (`event_bus.py` — 330 lines)

**Purpose:** Async pub/sub event system with priority queue and dead-letter handling.

**Key Features:**
- Priority levels: CRITICAL, HIGH, NORMAL, LOW, DEBUG
- Wildcard pattern subscriptions
- Retry with dead-letter queue (3 attempts max)
- TTL support (3600s default)

**Key Classes & Functions:**
```python
class Event: id, type, source, data, priority, status, timestamp
class EventPriority(Enum): CRITICAL=0, HIGH=1, NORMAL=2, LOW=3, DEBUG=4
class EventStatus(Enum): PENDING, PROCESSING, COMPLETED, FAILED, DEAD_LETTER

event_bus: EventBus  # Global event bus instance
emit(event_type, data, source, priority)  # Publish event
on_event(event_types)  # Decorator for event handlers
```

**Usage:**
```python
from middleware.event_bus import emit, on_event, EventPriority

# Publish event
await emit("agent.started", {"agent_id": "a1"}, source="api")

# Subscribe to events
@on_event(["agent.started", "agent.stopped"])
def handle_agent_event(event):
    print(f"Agent event: {event.type} - {event.data}")
```

### 6. Metrics (`metrics.py` — 280 lines)

**Purpose:** Prometheus metrics integration.

**Key Metrics:**
- `http_requests_total` (Counter) — Total HTTP requests
- `http_request_duration_seconds` (Histogram) — Request latency
- `agents_total` (Gauge) — Active agent count
- `db_query_duration_seconds` (Histogram) — Database query time

**Usage:**
```python
from middleware.metrics import http_requests_total, agents_total

# Increment counter
http_requests_total.labels(method="GET", endpoint="/agents").inc()

# Set gauge
agents_total.set(10)
```

**Endpoint:** `GET /metrics` — Prometheus scrape endpoint

### 7. Database (`database.py` — 300 lines)

**Purpose:** SQLAlchemy ORM with Repository pattern.

**Models:**
- `User` — User accounts
- `ApiKey` — API keys
- `Agent` — Agent registry
- `AgentMetric` — Agent metrics time-series
- `AgentEvent` — Agent events log
- `Plugin` — Plugin registry

**Key Classes:**
```python
class Repository:  # Generic CRUD repository
    def get(entity_type, entity_id)
    def list(entity_type, filters)
    def create(entity_type, data)
    def update(entity_type, entity_id, data)
    def delete(entity_type, entity_id)

get_db() → Session  # FastAPI dependency for DB session
init_db()  # Initialize database tables
```

### 8. Health Checker (`health.py` — 250 lines)

**Purpose:** Multi-component health checking.

**Components Checked:**
- Database connectivity
- Cache backend
- WebSocket manager
- Event bus
- ML pipeline
- Disk space
- Memory usage
- DNS resolution

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
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

## Testing

```bash
# Test middleware components
pytest tests/test_app_factory.py -v

# Test auth specifically
python -c "
from middleware.auth import user_store, Role
users = user_store.list_users()
print(f'Users: {len(users)}')
"
```

---

## Related Documentation

- [src/ README](../README.md) — Main application overview
- [API.md](../API.md) — Complete API reference
- [ARCHITECTURE.md](../../ARCHITECTURE.md) — System architecture
