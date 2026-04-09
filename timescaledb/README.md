# TimescaleDB — Agent Metrics Time-Series

**Location:** `/home/runner/workspace/timescaledb/`  
**Version:** PostgreSQL 15 + TimescaleDB  
**Port:** 5432

---

## Overview

[TimescaleDB](https://www.timescale.com/) is a **time-series database built on PostgreSQL**. It stores agent performance metrics, execution logs, and event history with hypertable optimization for time-range queries.

---

## Components

| File | Purpose |
|------|---------|
| `timescaledb_agent_client.py` | Python client for writing/reading agent metrics |
| `init/01-init-schema.sql` | Schema initialization with hypertables |

---

## Quick Start

### Start with Docker Compose

```bash
# Start TimescaleDB
docker-compose up -d timescaledb

# Connect to database
psql -h localhost -U agent_user -d agent_metrics
# Password: set via POSTGRES_PASSWORD env var
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_DB` | `agent_metrics` | Database name |
| `POSTGRES_USER` | `agent_user` | Database user |
| `POSTGRES_PASSWORD` | *(required)* | Database password |

---

## Schema

The initialization script (`init/01-init-schema.sql`) creates:

### Hypertables

```sql
-- Agent metrics hypertable (time-partitioned)
CREATE TABLE agent_metrics (
    time TIMESTAMPTZ NOT NULL,
    agent_id VARCHAR(255) NOT NULL,
    metric_name VARCHAR(255) NOT NULL,
    metric_value DOUBLE PRECISION,
    metadata JSONB
);
SELECT create_hypertable('agent_metrics', 'time');

-- Agent events hypertable
CREATE TABLE agent_events (
    time TIMESTAMPTZ NOT NULL,
    agent_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(255) NOT NULL,
    event_data JSONB
);
SELECT create_hypertable('agent_events', 'time');
```

### Indexes

- `time DESC` — Fast time-range queries
- `agent_id, time DESC` — Per-agent time-series
- `metric_name, time DESC` — Per-metric queries

---

## Using the Agent Client

```python
from timescaledb.timescaledb_agent_client import TimescaleDBClient

client = TimescaleDBClient(
    host="localhost",
    port=5432,
    user="agent_user",
    password="your_password",
    database="agent_metrics"
)

# Write agent metric
client.write_metric(
    agent_id="agent-1",
    metric_name="cpu_usage",
    value=0.45,
    metadata={"host": "server-1"}
)

# Query time range
results = client.query_range(
    agent_id="agent-1",
    start="2026-04-09T00:00:00Z",
    end="2026-04-09T23:59:59Z",
    metric_name="cpu_usage"
)

# Get aggregated statistics
stats = client.get_stats(
    agent_id="agent-1",
    window="1h"
)
print(f"Average CPU: {stats.avg_cpu}")
print(f"P95 Latency: {stats.p95_latency}")
```

---

## Common Queries

```sql
-- Agent CPU usage over last hour
SELECT time_bucket('5 minutes', time) AS bucket, AVG(metric_value) AS avg_cpu
FROM agent_metrics
WHERE agent_id = 'agent-1'
  AND metric_name = 'cpu_usage'
  AND time > NOW() - INTERVAL '1 hour'
GROUP BY bucket
ORDER BY bucket;

-- Top 10 agents by request count
SELECT agent_id, COUNT(*) AS request_count
FROM agent_metrics
WHERE metric_name = 'requests_per_second'
  AND time > NOW() - INTERVAL '24 hours'
GROUP BY agent_id
ORDER BY request_count DESC
LIMIT 10;

-- Error rate over time
SELECT time_bucket('10 minutes', time) AS bucket,
       AVG(metric_value) AS avg_error_rate
FROM agent_metrics
WHERE metric_name = 'error_rate'
  AND time > NOW() - INTERVAL '1 hour'
GROUP BY bucket
ORDER BY bucket;
```

---

## Data Retention

TimescaleDB policies for automatic data cleanup:

```sql
-- Drop raw data older than 30 days
SELECT add_retention_policy('agent_metrics', INTERVAL '30 days');

-- Drop events older than 90 days
SELECT add_retention_policy('agent_events', INTERVAL '90 days');
```

---

## Testing

```bash
# Verify TimescaleDB is running
docker-compose ps timescaledb

# Test connection
psql -h localhost -U agent_user -d agent_metrics -c "SELECT extname FROM pg_extension WHERE extname = 'timescaledb';"

# Test client
python -c "
from timescaledb.timescaledb_agent_client import TimescaleDBClient
client = TimescaleDBClient(host='localhost', user='agent_user', password='your_password', database='agent_metrics')
client.write_metric('test-agent', 'test_metric', 1.0)
print('Metric written successfully')
"
```

---

## Related Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) — System architecture
- [InfluxDB README](influxdb/README.md) — Telemetry data
- [Prometheus README](prometheus/README.md) — System monitoring
- [Monitoring Stack](docker-compose.yml) — Docker Compose configuration
