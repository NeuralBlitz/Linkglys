# Linkglys API v2.0 — Complete API Reference

**Base URL:** `http://localhost:5000`
**Version:** 2.0.0
**Interactive Docs:** [Swagger UI](http://localhost:5000/docs) | [ReDoc](http://localhost:5000/redoc)

---

## Authentication

All protected endpoints require a JWT token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

### Obtain Token

```bash
curl -X POST http://localhost:5000/api/v2/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

## Endpoints

### Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/v2/auth/login` | ❌ | Login with username/password |
| `POST` | `/api/v2/auth/register` | ❌ | Register new user |
| `POST` | `/api/v2/auth/refresh` | ❌ | Refresh access token |
| `POST` | `/api/v2/auth/api-key` | ✅ | Generate API key |
| `GET` | `/api/v2/auth/me` | ✅ | Get current user info |
| `GET` | `/api/v2/auth/users` | ✅ Admin | List all users |

#### POST /api/v2/auth/login

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Response (401):**
```json
{
  "detail": "Invalid credentials"
}
```

#### POST /api/v2/auth/register

**Request:**
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "securepass",
  "role": "viewer"
}
```

**Roles:** `admin`, `developer`, `viewer`, `agent`

#### POST /api/v2/auth/api-key

Generate a new API key for service accounts.

**Response:**
```json
{
  "api_key": "nb_sk_...",
  "message": "Save this key — it won't be shown again"
}
```

---

### Agents

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/v2/agents` | ❌ | List agents |
| `POST` | `/api/v2/agents` | ✅ | Create agent |
| `POST` | `/api/v2/agents/{agent_id}/command` | ❌ | Send command to agent |
| `GET` | `/api/v2/agents/{agent_id}/metrics` | ❌ | Get agent metrics |

#### GET /api/v2/agents

**Query Parameters:**
- `status` (optional) — Filter by status: `idle`, `running`, `error`
- `limit` (default: 50) — Maximum results

**Response:**
```json
{
  "agents": [
    {
      "id": "agent-0",
      "name": "Agent 0",
      "status": "idle",
      "type": "inference"
    }
  ],
  "total": 10
}
```

#### POST /api/v2/agents

**Request:**
```json
{
  "name": "research-agent",
  "type": "inference",
  "config": {
    "model": "claude-sonnet-4",
    "temperature": 0.7
  }
}
```

**Response:**
```json
{
  "id": "agent-1234",
  "name": "research-agent",
  "type": "inference",
  "status": "idle",
  "config": {"model": "claude-sonnet-4", "temperature": 0.7}
}
```

#### POST /api/v2/agents/{agent_id}/command

**Request:**
```json
{
  "command": "start",
  "params": {"task": "research quantum computing"}
}
```

**Response:**
```json
{
  "agent_id": "agent-1234",
  "command": "start",
  "status": "queued"
}
```

#### GET /api/v2/agents/{agent_id}/metrics

**Query Parameters:**
- `window` (default: `1h`) — Time window: `1h`, `6h`, `24h`, `7d`

**Response:**
```json
{
  "agent_id": "agent-1234",
  "window": "1h",
  "metrics": {
    "cpu_usage": 0.45,
    "memory_mb": 256,
    "requests_per_second": 12.5,
    "avg_latency_ms": 45,
    "error_rate": 0.02
  }
}
```

---

### ML Pipeline

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/v2/ml/train` | ✅ | Train ML model |
| `POST` | `/api/v2/ml/predict` | ❌ | Run prediction |
| `POST` | `/api/v2/ml/cluster` | ❌ | Cluster data |
| `POST` | `/api/v2/ml/anomalies` | ❌ | Detect anomalies |
| `GET` | `/api/v2/ml/stats` | ❌ | ML pipeline stats |

#### POST /api/v2/ml/train

**Request:**
```json
{
  "model_name": "my-classifier",
  "model_type": "random_forest",
  "task": "classification",
  "features": [[1, 2], [3, 4], [5, 6]],
  "labels": [0, 1, 0],
  "params": {"n_estimators": 100}
}
```

**Supported model_types:**
- `random_forest`, `svm`, `mlp` (classification)
- `gradient_boosting` (regression)
- `kmeans`, `dbscan` (clustering)
- `isolation_forest` (anomaly detection)

**Response:**
```json
{
  "model_name": "my-classifier",
  "accuracy": 0.95,
  "training_time_ms": 120,
  "status": "trained"
}
```

#### POST /api/v2/ml/predict

**Request:**
```json
{
  "model_name": "my-classifier",
  "features": [[1, 2]]
}
```

**Response:**
```json
{
  "prediction": [0],
  "probability": [0.85, 0.15],
  "model": "my-classifier"
}
```

#### POST /api/v2/ml/cluster

**Request:**
```json
{
  "features": [[1, 2], [3, 4], [5, 6]],
  "n_clusters": 3,
  "method": "kmeans"
}
```

**Supported methods:** `kmeans`, `dbscan`

**Response:**
```json
{
  "clusters": [0, 1, 2],
  "centroids": [[...], [...], [...]],
  "method": "kmeans"
}
```

#### POST /api/v2/ml/anomalies

**Request:**
```json
{
  "features": [[1, 2], [100, 200], [3, 4]],
  "contamination": 0.1
}
```

**Response:**
```json
{
  "anomalies": [-1, 1, -1],
  "contamination": 0.1,
  "method": "isolation_forest"
}
```

#### GET /api/v2/ml/stats

**Response:**
```json
{
  "models": ["my-classifier", "my-regressor"],
  "total_models": 2,
  "total_predictions": 1500
}
```

---

### Plugins

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/v2/plugins` | ❌ | List plugins |
| `POST` | `/api/v2/plugins` | ✅ Admin | Install plugin |
| `DELETE` | `/api/v2/plugins/{name}` | ✅ Admin | Remove plugin |

#### GET /api/v2/plugins

**Response:**
```json
{
  "plugins": [
    {
      "name": "sample_lrs_plugin",
      "path": "plugins/sample_lrs_plugin.py",
      "size_bytes": 1234,
      "modified": 1712620800.0
    }
  ],
  "count": 1
}
```

---

### Event Bus

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/v2/events` | ❌ | Get events |
| `GET` | `/api/v2/events/dead-letters` | ❌ | Get dead letter queue |
| `GET` | `/api/v2/events/stats` | ❌ | Event bus statistics |
| `GET` | `/api/v2/events/subscriptions` | ❌ | List subscriptions |

#### GET /api/v2/events

**Query Parameters:**
- `event_type` (optional) — Filter by type
- `status` (optional) — Filter by status: `pending`, `processing`, `completed`, `failed`, `dead_letter`
- `limit` (default: 100) — Maximum results

**Response:**
```json
{
  "events": [
    {
      "id": "uuid-1",
      "type": "agent.started",
      "source": "api",
      "data": {"agent_id": "agent-1"},
      "status": "completed",
      "timestamp": 1712620800.0
    }
  ]
}
```

#### GET /api/v2/events/stats

**Response:**
```json
{
  "total_events": 1500,
  "pending": 5,
  "processing": 2,
  "completed": 1480,
  "failed": 10,
  "dead_letters": 3,
  "subscribers": 15
}
```

---

### System

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/v2/health` | ❌ | Health check |
| `GET` | `/api/v2/stats` | ❌ | System statistics |
| `GET` | `/api/v2/config` | ❌ | Configuration details |
| `GET` | `/api/v2/integration/status` | ❌ | Integration status |
| `GET` | `/metrics` | ❌ | Prometheus metrics |

#### GET /api/v2/health

**Response:**
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

#### GET /api/v2/stats

**Response:**
```json
{
  "rate_limiter": {"requests_limited": 150, "total_requests": 10000},
  "cache": {"hits": 500, "misses": 100, "hit_rate": 0.83},
  "websocket": {"active_connections": 15, "rooms": 3},
  "event_bus": {"total_events": 1500, "pending": 5}
}
```

#### GET /api/v2/config

**Response:**
```json
{
  "rate_limit_profiles": ["default", "strict", "moderate", "relaxed", "api", "webhook"],
  "jwt_algorithm": "HS256",
  "cache_backend": "memory",
  "ml_models": 2
}
```

---

## WebSocket

**URL:** `ws://localhost:5000/ws/connect/{client_id}`

### Message Types

| Type | Description |
|------|-------------|
| `agent_status` | Agent status changes |
| `metrics` | Performance metrics updates |
| `log` | Log entries |
| `events` | Event bus events |

### Connection Example

```javascript
const ws = new WebSocket('ws://localhost:5000/ws/connect/dashboard');

ws.onopen = () => {
  console.log('Connected to NeuralBlitz');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data.type, data.payload);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

---

## Error Responses

| Status Code | Meaning |
|-------------|---------|
| `400` | Bad Request — Invalid input |
| `401` | Unauthorized — Missing or invalid token |
| `403` | Forbidden — Insufficient permissions |
| `404` | Not Found — Resource doesn't exist |
| `500` | Internal Server Error — Server-side error |

**Error Format:**
```json
{
  "detail": "Error description"
}
```

---

## Rate Limiting

| Profile | Requests/Minute | Use Case |
|---------|-----------------|----------|
| `default` | 60 | General API access |
| `strict` | 10 | Sensitive operations |
| `moderate` | 30 | Standard access |
| `relaxed` | 120 | High-volume access |
| `api` | 1000 | Programmatic access |
| `webhook` | 300 | Webhook callbacks |

---

## Roles & Permissions

| Role | Permissions |
|------|-------------|
| **ADMIN** | read, write, delete, admin, deploy, configure |
| **DEVELOPER** | read, write, deploy |
| **VIEWER** | read |
| **AGENT** | read, write |

---

## Related Documentation

- [src/README.md](README.md) — Main application overview
- [middleware/README.md](middleware/README.md) — Middleware components
- [ARCHITECTURE.md](../../ARCHITECTURE.md) — System architecture
- [DEVELOPMENT_SETUP.md](../../DEVELOPMENT_SETUP.md) — Environment setup
- [Interactive Swagger UI](http://localhost:5000/docs)
