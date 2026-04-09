# Prometheus — System Monitoring & Alerting

**Location:** `/home/runner/workspace/prometheus/`  
**Version:** Latest  
**Port:** 9090

---

## Overview

[Prometheus](https://prometheus.io/) is a **systems monitoring and alerting toolkit** that collects metrics from NeuralBlitz services, stores them in a time-series database, and triggers alerts based on configurable rules.

---

## Components

| File | Purpose |
|------|---------|
| `prometheus.yml` | Scrape configuration — which targets to monitor |
| `alerts.yml` | Alert rules — conditions that trigger notifications |
| `recording-rules.yml` | Pre-computed metrics for query performance |
| `prometheus_integration_client.py` | Python client for pushing metrics to Prometheus |

---

## Quick Start

### Start with Docker Compose

```bash
# Start Prometheus (and full monitoring stack)
docker-compose up -d prometheus

# Access Prometheus UI
open http://localhost:9090

# View targets
open http://localhost:9090/targets

# Query metrics
open http://localhost:9090/graph
```

---

## Scrape Configuration (`prometheus.yml`)

Prometheus scrapes metrics from the following targets:

| Target | Port | Metrics |
|--------|------|---------|
| **NeuralBlitz API** | 5000 | HTTP requests, latency, agent counts |
| **Node Exporter** | 9100 | Host CPU, memory, disk, network |
| **cAdvisor** | 8080 | Container CPU, memory, network, filesystem |
| **InfluxDB** | 8086 | InfluxDB internals |
| **Grafana** | 3000 | Grafana internals |

**Scrape interval:** 15 seconds (default)  
**Evaluation interval:** 15 seconds (for rules)

---

## Alert Rules (`alerts.yml`)

### System Alerts

| Alert | Condition | Severity | Description |
|-------|-----------|----------|-------------|
| **HighCPUUsage** | CPU > 80% for 5m | Warning | Node CPU usage is high |
| **HighMemoryUsage** | Memory > 85% for 5m | Warning | Node memory usage is high |
| **DiskSpaceLow** | Disk < 20% for 10m | Critical | Disk space is running low |
| **ServiceDown** | Target up == 0 for 1m | Critical | A monitored service is down |
| **HighErrorRate** | Error rate > 5% for 5m | Warning | API error rate is elevated |
| **HighLatency** | P95 latency > 1s for 5m | Warning | API response time is high |

### Agent Alerts

| Alert | Condition | Severity | Description |
|-------|-----------|----------|-------------|
| **AgentHighCPU** | Agent CPU > 70% for 5m | Warning | Individual agent using excessive CPU |
| **AgentCrashLoop** | Agent restarts > 3 in 10m | Critical | Agent is crash looping |
| **AgentQueueBacklog** | Queue depth > 1000 for 5m | Warning | Agent task queue is backing up |

---

## Recording Rules (`recording-rules.yml`)

Recording rules pre-compute expensive queries for faster dashboard loading:

| Rule Name | Expression | Purpose |
|-----------|------------|---------|
| `job:http_requests_total:rate5m` | `rate(http_requests_total[5m])` | Request rate per job |
| `job:http_request_duration:p95` | `histogram_quantile(0.95, rate(http_request_duration_bucket[5m]))` | P95 latency |
| `instance:cpu_usage:avg5m` | `avg by(instance)(rate(node_cpu_seconds_total[5m]))` | Average CPU per instance |
| `agent:error_rate:ratio5m` | `sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))` | Agent error rate |

---

## Using the Integration Client

```python
from prometheus.prometheus_integration_client import PrometheusIntegrationClient

client = PrometheusIntegrationClient(
    pushgateway_url="http://localhost:9091"
)

# Push custom metrics
client.push_metric(
    name="custom_agent_metric",
    value=42.0,
    metric_type="gauge",
    labels={"agent_id": "agent-1"}
)

# Push with timestamp
client.push_metric_with_timestamp(
    name="agent_performance",
    value=0.95,
    labels={"model": "v2.0"},
    timestamp=datetime.utcnow()
)
```

---

## Querying Prometheus

```python
import requests

# Query current value
response = requests.get(
    "http://localhost:9090/api/v1/query",
    params={"query": "up"}
)
print(response.json())

# Query range (time series)
response = requests.get(
    "http://localhost:9090/api/v1/query_range",
    params={
        "query": "http_requests_total",
        "start": "2026-04-09T00:00:00Z",
        "end": "2026-04-09T23:59:59Z",
        "step": "60s"
    }
)
```

---

## Metrics Catalog

### HTTP Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `http_requests_total` | Counter | Total HTTP requests by method, endpoint, status |
| `http_request_duration_seconds` | Histogram | Request latency distribution |
| `http_request_size_bytes` | Histogram | Request size distribution |
| `http_response_size_bytes` | Histogram | Response size distribution |

### Agent Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `agents_total` | Gauge | Number of active agents |
| `agent_execution_duration_seconds` | Histogram | Agent execution time |
| `agent_errors_total` | Counter | Agent execution failures |

### System Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `node_cpu_seconds_total` | Counter | CPU time used |
| `node_memory_Active_bytes` | Gauge | Active memory |
| `node_filesystem_avail_bytes` | Gauge | Available disk space |
| `container_cpu_usage_seconds_total` | Counter | Container CPU time |

---

## Grafana Integration

Prometheus is automatically configured as a Grafana data source when running `docker-compose up`.

1. Open Grafana: http://localhost:3000
2. Login: admin / your password
3. Go to **Dashboards** → Browse pre-configured dashboards
4. Use Prometheus as data source for custom panels

---

## Testing

```bash
# Verify Prometheus is running
curl http://localhost:9090/-/healthy
# Expected: "Prometheus Server is Healthy"

# Check targets
curl http://localhost:9090/api/v1/targets | python -m json.tool

# Test query
curl "http://localhost:9090/api/v1/query?query=up" | python -m json.tool

# Reload configuration
curl -X POST http://localhost:9090/-/reload
```

---

## Related Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) — System architecture
- [InfluxDB README](influxdb/README.md) — Telemetry data
- [TimescaleDB README](timescaledb/README.md) — Agent metrics
- [Monitoring Stack](docker-compose.yml) — Docker Compose configuration
- [Grafana](http://localhost:3000) — Visualization dashboards
