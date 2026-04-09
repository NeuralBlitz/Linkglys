# InfluxDB — Time-Series Telemetry

**Location:** `/home/runner/workspace/influxdb/`  
**Version:** InfluxDB 2.7  
**Port:** 8086

---

## Overview

[InfluxDB](https://www.influxdata.com/) is a **time-series database** used for collecting and storing telemetry data from NeuralBlitz agents and system components. It provides high-write-throughput for timestamped metrics with built-in downsampling and retention policies.

---

## Components

| File | Purpose |
|------|---------|
| `influxdb_telemetry_client.py` | Python client for writing telemetry data to InfluxDB |
| `config/influxdb.conf` | InfluxDB configuration file |
| `init/` | Database initialization scripts |

---

## Quick Start

### Start with Docker Compose

```bash
# Start InfluxDB (and other monitoring services)
docker-compose up -d influxdb

# Access InfluxDB UI
open http://localhost:8086
# Default credentials: admin / your password (set via INFLUXDB_ADMIN_PASSWORD env var)
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `INFLUXDB_DB` | `telemetry` | Database name |
| `INFLUXDB_ADMIN_USER` | `admin` | Admin username |
| `INFLUXDB_ADMIN_PASSWORD` | *(required)* | Admin password |
| `INFLUXDB_USER` | `telemetry_user` | Regular user |
| `INFLUXDB_USER_PASSWORD` | `telemetry_pass` | Regular user password |
| `INFLUXDB_ORG` | `neuralblitz` | Organization name |
| `INFLUXDB_BUCKET` | `system_metrics` | Default bucket |
| `INFLUXDB_ADMIN_TOKEN` | *(required)* | Admin API token |

---

## Using the Telemetry Client

```python
from influxdb.influxdb_telemetry_client import TelemetryClient

client = TelemetryClient(
    url="http://localhost:8086",
    token="your-token",
    org="neuralblitz",
    bucket="system_metrics"
)

# Write telemetry data
client.write_metric(
    measurement="agent_performance",
    tags={"agent_id": "agent-1", "status": "running"},
    fields={"cpu_usage": 0.45, "memory_mb": 256, "requests_per_second": 12.5},
    timestamp=datetime.utcnow()
)

# Query data
results = client.query(
    query='''
    from(bucket: "system_metrics")
      |> range(start: -1h)
      |> filter(fn: (r) => r._measurement == "agent_performance")
    '''
)
```

---

## Data Model

### Measurements

| Measurement | Tags | Fields |
|-------------|------|--------|
| `agent_performance` | agent_id, status | cpu_usage, memory_mb, requests_per_second, avg_latency_ms, error_rate |
| `system_health` | component, host | uptime_seconds, active_connections, queue_depth |
| `api_requests` | method, endpoint, status_code | duration_ms, request_size, response_size |
| `ml_pipeline` | model_name, task | training_time, accuracy, loss |

---

## Configuration

The `config/influxdb.conf` file configures:

```ini
[http]
  enabled = true
  bind-address = ":8086"

[storage]
  wal-fsync-delay = "100ms"
  cache-max-memory-size = 1073741824  # 1GB
```

---

## Retention Policies

| Policy | Duration | Shard Duration | Purpose |
|--------|----------|----------------|---------|
| `autogen` | Infinite | 168h (7 days) | Raw metrics |
| `downsampled_1h` | 90 days | 24h | Hourly aggregates |
| `downsampled_1d` | 1 year | 168h | Daily aggregates |

---

## Testing

```bash
# Verify InfluxDB is running
curl http://localhost:8086/health

# Test telemetry client
python -c "
from influxdb.influxdb_telemetry_client import TelemetryClient
client = TelemetryClient(url='http://localhost:8086', token='your-token', org='neuralblitz', bucket='system_metrics')
client.write_metric('test_measurement', {'test': 'true'}, {'value': 1.0})
print('Metric written successfully')
"
```

---

## Related Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) — System architecture
- [Prometheus README](prometheus/README.md) — Monitoring with Prometheus
- [TimescaleDB README](timescaledb/README.md) — Agent metrics in PostgreSQL
- [Monitoring Stack](docker-compose.yml) — Docker Compose monitoring configuration
