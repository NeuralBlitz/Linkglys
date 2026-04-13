#!/usr/bin/env python3
"""Prometheus Metrics — Real App Metrics Export
Exports application metrics in Prometheus exposition format for monitoring.
"""

import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from fastapi import Request
from fastapi.responses import PlainTextResponse


class MetricType(str, Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"


@dataclass
class MetricSample:
    name: str
    value: float
    labels: dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class Counter:
    """Monotonically increasing counter metric."""

    def __init__(self, name: str, description: str, label_names: list[str] = None):
        self.name = name
        self.description = description
        self.label_names = label_names or []
        self._values: dict[str, float] = {"": 0.0}
        self._lock = threading.Lock()

    def inc(self, value: float = 1.0, **labels) -> None:
        key = self._label_key(labels)
        with self._lock:
            self._values[key] = self._values.get(key, 0.0) + value

    def get(self, **labels) -> float:
        key = self._label_key(labels)
        return self._values.get(key, 0.0)

    def _label_key(self, labels: dict[str, str]) -> str:
        if not labels:
            return ""
        return ",".join(f"{k}={labels.get(k, '')}" for k in self.label_names)

    def _samples(self) -> list[MetricSample]:
        samples = []
        for key, value in self._values.items():
            labels = {}
            if key:
                parts = key.split(",")
                for p in parts:
                    if "=" in p:
                        k, v = p.split("=", 1)
                        labels[k] = v
            samples.append(MetricSample(name=self.name, value=value, labels=labels))
        return samples


class Gauge:
    """Gauge metric that can go up and down."""

    def __init__(self, name: str, description: str, label_names: list[str] = None):
        self.name = name
        self.description = description
        self.label_names = label_names or []
        self._values: dict[str, float] = {"": 0.0}
        self._lock = threading.Lock()

    def set(self, value: float, **labels) -> None:
        key = self._label_key(labels)
        with self._lock:
            self._values[key] = value

    def inc(self, value: float = 1.0, **labels) -> None:
        key = self._label_key(labels)
        with self._lock:
            self._values[key] = self._values.get(key, 0.0) + value

    def dec(self, value: float = 1.0, **labels) -> None:
        key = self._label_key(labels)
        with self._lock:
            self._values[key] = self._values.get(key, 0.0) - value

    def get(self, **labels) -> float:
        key = self._label_key(labels)
        return self._values.get(key, 0.0)

    def track_inprogress(self, **labels):
        """Context manager to track in-progress operations."""
        return _InprogressTracker(self, labels)

    def time(self, **labels):
        """Decorator/context manager to track duration."""
        return _Timer(self, labels)

    def _label_key(self, labels: dict[str, str]) -> str:
        if not labels:
            return ""
        return ",".join(f"{k}={labels.get(k, '')}" for k in self.label_names)

    def _samples(self) -> list[MetricSample]:
        samples = []
        for key, value in self._values.items():
            labels = {}
            if key:
                parts = key.split(",")
                for p in parts:
                    if "=" in p:
                        k, v = p.split("=", 1)
                        labels[k] = v
            samples.append(MetricSample(name=self.name, value=value, labels=labels))
        return samples


class Histogram:
    """Histogram metric for measuring distributions."""

    DEFAULT_BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, float("inf"))

    def __init__(self, name: str, description: str, buckets: tuple = None, label_names: list[str] = None):
        self.name = name
        self.description = description
        self.buckets = buckets or self.DEFAULT_BUCKETS
        self.label_names = label_names or []
        self._lock = threading.Lock()
        # Per-label-group storage
        self._data: dict[str, dict] = {"": {
            "bucket_counts": [0] * len(self.buckets),
            "sum": 0.0,
            "count": 0,
        }}

    def observe(self, value: float, **labels) -> None:
        key = self._label_key(labels)
        with self._lock:
            if key not in self._data:
                self._data[key] = {
                    "bucket_counts": [0] * len(self.buckets),
                    "sum": 0.0,
                    "count": 0,
                }
            data = self._data[key]
            data["sum"] += value
            data["count"] += 1
            for i, bound in enumerate(self.buckets):
                if value <= bound:
                    data["bucket_counts"][i] += 1

    def time(self, **labels):
        return _Timer(self, labels)

    def _label_key(self, labels: dict[str, str]) -> str:
        if not labels:
            return ""
        return ",".join(f"{k}={labels.get(k, '')}" for k in self.label_names)

    def _samples(self) -> list[MetricSample]:
        samples = []
        for key, data in self._data.items():
            labels = {}
            if key:
                parts = key.split(",")
                for p in parts:
                    if "=" in p:
                        k, v = p.split("=", 1)
                        labels[k] = v

            # Bucket samples
            cumulative = 0
            for i, bound in enumerate(self.buckets):
                cumulative += data["bucket_counts"][i]
                bucket_labels = {**labels, "le": str(bound) if bound != float("inf") else "+Inf"}
                samples.append(MetricSample(
                    name=f"{self.name}_bucket",
                    value=cumulative,
                    labels=bucket_labels,
                ))

            # Sum and count
            samples.append(MetricSample(name=f"{self.name}_sum", value=data["sum"], labels=labels))
            samples.append(MetricSample(name=f"{self.name}_count", value=data["count"], labels=labels))

        return samples


class _InprogressTracker:
    def __init__(self, gauge: Gauge, labels: dict[str, str]):
        self.gauge = gauge
        self.labels = labels

    def __enter__(self):
        self.gauge.inc(**self.labels)
        return self

    def __exit__(self, *args):
        self.gauge.dec(**self.labels)


class _Timer:
    def __init__(self, metric, labels: dict[str, str]):
        self.metric = metric
        self.labels = labels
        self.start = None

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args):
        if self.start:
            elapsed = time.perf_counter() - self.start
            self.metric.observe(elapsed, **self.labels)


# ──────────────────────────────────────────────────────────────
# Metrics Registry
# ──────────────────────────────────────────────────────────────

class MetricsRegistry:
    """Central registry for all application metrics."""

    def __init__(self):
        self._counters: dict[str, Counter] = {}
        self._gauges: dict[str, Gauge] = {}
        self._histograms: dict[str, Histogram] = {}

    def counter(self, name: str, description: str, label_names: list[str] = None) -> Counter:
        if name not in self._counters:
            self._counters[name] = Counter(name, description, label_names)
        return self._counters[name]

    def gauge(self, name: str, description: str, label_names: list[str] = None) -> Gauge:
        if name not in self._gauges:
            self._gauges[name] = Gauge(name, description, label_names)
        return self._gauges[name]

    def histogram(self, name: str, description: str, buckets: tuple = None, label_names: list[str] = None) -> Histogram:
        if name not in self._histograms:
            self._histograms[name] = Histogram(name, description, buckets, label_names)
        return self._histograms[name]

    def generate(self) -> str:
        """Generate Prometheus exposition format output."""
        lines = []

        for metric in list(self._counters.values()) + list(self._gauges.values()) + list(self._histograms.values()):
            # HELP
            lines.append(f"# HELP {metric.name} {metric.description}")
            # TYPE
            if isinstance(metric, Counter):
                lines.append(f"# TYPE {metric.name} counter")
            elif isinstance(metric, Gauge):
                lines.append(f"# TYPE {metric.name} gauge")
            elif isinstance(metric, Histogram):
                lines.append(f"# TYPE {metric.name} histogram")

            for sample in metric._samples():
                if sample.labels:
                    label_str = ",".join(f'{k}="{v}"' for k, v in sorted(sample.labels.items()))
                    lines.append(f"{sample.name}{{{label_str}}} {sample.value}")
                else:
                    lines.append(f"{sample.name} {sample.value}")

            lines.append("")

        return "\n".join(lines)

    def get_all(self) -> dict[str, Any]:
        return {
            "counters": {n: {k: v for k, v in c._values.items()} for n, c in self._counters.items()},
            "gauges": {n: {k: v for k, v in g._values.items()} for n, g in self._gauges.items()},
            "histograms": {n: dict(g._data) for n, g in self._histograms.items()},
        }


# Global registry
registry = MetricsRegistry()


# ──────────────────────────────────────────────────────────────
# Pre-defined Application Metrics
# ──────────────────────────────────────────────────────────────

# Request metrics
http_requests_total = registry.counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)
http_request_duration_seconds = registry.histogram(
    "http_request_duration_seconds", "HTTP request duration in seconds",
    label_names=["method", "endpoint"]
)
http_requests_in_progress = registry.gauge(
    "http_requests_in_progress", "HTTP requests currently being processed"
)

# Agent metrics
agents_total = registry.gauge("agents_total", "Total number of agents", ["status", "type"])
agent_execution_duration = registry.histogram(
    "agent_execution_duration_seconds", "Agent execution duration",
    label_names=["agent_id", "agent_type"]
)
agent_errors_total = registry.counter(
    "agent_errors_total", "Total agent errors", ["agent_id", "error_type"]
)

# Event bus metrics
events_published_total = registry.counter(
    "events_published_total", "Total events published", ["event_type"]
)
events_processed_total = registry.counter(
    "events_processed_total", "Total events processed", ["event_type", "status"]
)
event_processing_duration = registry.histogram(
    "event_processing_duration_seconds", "Event processing duration"
)

# Plugin metrics
plugins_total = registry.gauge("plugins_total", "Total plugins", ["status"])
plugin_load_duration = registry.histogram(
    "plugin_load_duration_seconds", "Plugin load duration"
)

# System metrics
system_uptime_seconds = registry.gauge("system_uptime_seconds", "System uptime in seconds")
system_memory_usage_bytes = registry.gauge("system_memory_usage_bytes", "System memory usage")
system_cpu_usage_percent = registry.gauge("system_cpu_usage_percent", "System CPU usage")

# Database metrics
db_query_duration_seconds = registry.histogram(
    "db_query_duration_seconds", "Database query duration",
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
    label_names=["table", "operation"]
)
db_connections_active = registry.gauge("db_connections_active", "Active database connections")

# Cache metrics
cache_hits_total = registry.counter("cache_hits_total", "Total cache hits", ["backend"])
cache_misses_total = registry.counter("cache_misses_total", "Total cache misses", ["backend"])

# WebSocket metrics
ws_connections_active = registry.gauge("ws_connections_active", "Active WebSocket connections")
ws_messages_sent_total = registry.counter("ws_messages_sent_total", "Total WebSocket messages sent")

# Set initial uptime
START_TIME = time.time()
system_uptime_seconds.set(0)


def update_system_metrics():
    """Update system-level metrics."""
    import psutil
    system_uptime_seconds.set(time.time() - START_TIME)
    mem = psutil.virtual_memory()
    system_memory_usage_bytes.set(mem.used)
    system_cpu_usage_percent.set(psutil.cpu_percent(interval=0))


# ──────────────────────────────────────────────────────────────
# FastAPI Integration
# ──────────────────────────────────────────────────────────────


async def prometheus_metrics_middleware(request: Request, call_next):
    """FastAPI middleware to collect HTTP metrics."""
    method = request.method
    endpoint = request.url.path

    http_requests_in_progress.inc()

    start = time.perf_counter()
    try:
        response = await call_next(request)
        status = response.status_code
    except Exception:
        status = 500
        raise
    finally:
        duration = time.perf_counter() - start
        http_requests_in_progress.dec()
        http_requests_total.inc(method=method, endpoint=endpoint, status=str(status))
        http_request_duration_seconds.observe(duration, method=method, endpoint=endpoint)

    return response


def metrics_endpoint() -> PlainTextResponse:
    """Generate Prometheus metrics endpoint response."""
    update_system_metrics()
    return PlainTextResponse(
        content=registry.generate(),
        media_type="text/plain",
    )
