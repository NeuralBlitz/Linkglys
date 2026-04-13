#!/usr/bin/env python3
"""Health Check System — Real Service Monitoring
Monitors all components: database, cache, Redis, WebSocket, event bus, ML pipeline, external services.
"""

import socket
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from fastapi import APIRouter


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ComponentHealth:
    name: str
    status: HealthStatus
    latency_ms: float = 0.0
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    checked_at: float = field(default_factory=time.time)


@dataclass
class SystemHealth:
    status: HealthStatus
    components: dict[str, ComponentHealth]
    overall_uptime: float
    checks_performed: int
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "components": {k: {
                "status": v.status.value,
                "latency_ms": round(v.latency_ms, 2),
                "message": v.message,
                "details": v.details,
                "checked_at": datetime.fromtimestamp(v.checked_at, tz=UTC).isoformat(),
            } for k, v in self.components.items()},
            "overall_uptime": round(self.overall_uptime, 2),
            "checks_performed": self.checks_performed,
            "timestamp": datetime.fromtimestamp(self.timestamp, tz=UTC).isoformat(),
        }


class HealthChecker:
    """Comprehensive health checker for all system components."""

    def __init__(self):
        self._start_time = time.time()
        self._checks_performed = 0
        self._history: list[dict[str, Any]] = []
        self._max_history = 1000

    async def check_all(self) -> SystemHealth:
        """Run all health checks and return system health."""
        components = {}

        # Run all checks in parallel
        checks = {
            "database": self._check_database(),
            "cache": self._check_cache(),
            "websocket": self._check_websocket(),
            "event_bus": self._check_event_bus(),
            "ml_pipeline": self._check_ml_pipeline(),
            "disk_space": self._check_disk_space(),
            "memory": self._check_memory(),
            "external_api": self._check_external_api(),
        }

        for name, coro in checks.items():
            try:
                components[name] = await coro
            except Exception as e:
                components[name] = ComponentHealth(
                    name=name,
                    status=HealthStatus.UNKNOWN,
                    message=f"Check failed: {str(e)}",
                )

        self._checks_performed += 1

        # Determine overall status
        statuses = [c.status for c in components.values()]
        if HealthStatus.UNHEALTHY in statuses:
            overall = HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            overall = HealthStatus.DEGRADED
        elif all(s == HealthStatus.HEALTHY for s in statuses):
            overall = HealthStatus.HEALTHY
        else:
            overall = HealthStatus.UNKNOWN

        health = SystemHealth(
            status=overall,
            components=components,
            overall_uptime=time.time() - self._start_time,
            checks_performed=self._checks_performed,
        )

        # Store in history
        self._history.append(health.to_dict())
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        return health

    async def _check_database(self) -> ComponentHealth:
        start = time.time()
        try:
            from middleware.database import DBUser, SessionLocal
            db = SessionLocal()
            count = db.query(DBUser).count()
            db.close()
            latency = (time.time() - start) * 1000
            return ComponentHealth(
                name="database",
                status=HealthStatus.HEALTHY,
                latency_ms=latency,
                message=f"Connected, {count} users",
                details={"user_count": count},
            )
        except ImportError:
            return ComponentHealth(name="database", status=HealthStatus.UNKNOWN, message="Database module not installed")
        except Exception as e:
            return ComponentHealth(
                name="database",
                status=HealthStatus.UNHEALTHY,
                latency_ms=(time.time() - start) * 1000,
                message=str(e),
            )

    async def _check_cache(self) -> ComponentHealth:
        start = time.time()
        try:
            from middleware.cache import cache
            cache.set("_health_check", "ok", ttl=5)
            result = cache.get("_health_check")
            latency = (time.time() - start) * 1000
            if result == "ok":
                return ComponentHealth(
                    name="cache",
                    status=HealthStatus.HEALTHY,
                    latency_ms=latency,
                    message=f"{'Redis' if cache._use_redis else 'Memory'} cache working",
                    details={"backend": "redis" if cache._use_redis else "memory"},
                )
            return ComponentHealth(name="cache", status=HealthStatus.DEGRADED, message="Cache read mismatch")
        except Exception as e:
            return ComponentHealth(
                name="cache",
                status=HealthStatus.UNHEALTHY,
                message=str(e),
            )

    async def _check_websocket(self) -> ComponentHealth:
        try:
            from middleware.websocket import ws_manager
            count = ws_manager.get_connected_count()
            return ComponentHealth(
                name="websocket",
                status=HealthStatus.HEALTHY,
                message=f"{count} active connections",
                details={"active_connections": count, "rooms": ws_manager.get_rooms()},
            )
        except Exception as e:
            return ComponentHealth(name="websocket", status=HealthStatus.UNKNOWN, message=str(e))

    async def _check_event_bus(self) -> ComponentHealth:
        try:
            from middleware.event_bus import event_bus
            stats = event_bus.get_stats()
            return ComponentHealth(
                name="event_bus",
                status=HealthStatus.HEALTHY,
                message=f"{stats['events_published']} events published",
                details=stats,
            )
        except Exception as e:
            return ComponentHealth(name="event_bus", status=HealthStatus.UNKNOWN, message=str(e))

    async def _check_ml_pipeline(self) -> ComponentHealth:
        try:
            from ml_pipeline import ml_pipeline
            stats = ml_pipeline.get_stats()
            return ComponentHealth(
                name="ml_pipeline",
                status=HealthStatus.HEALTHY,
                message=f"{len(stats['loaded_models'])} models loaded",
                details=stats,
            )
        except Exception as e:
            return ComponentHealth(name="ml_pipeline", status=HealthStatus.UNKNOWN, message=str(e))

    async def _check_disk_space(self) -> ComponentHealth:
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            usage_pct = (used / total) * 100
            if usage_pct > 95:
                status = HealthStatus.UNHEALTHY
            elif usage_pct > 85:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.HEALTHY
            return ComponentHealth(
                name="disk_space",
                status=status,
                message=f"{usage_pct:.1f}% used ({free / 1e9:.1f} GB free)",
                details={"total_gb": total / 1e9, "used_gb": used / 1e9, "free_gb": free / 1e9, "usage_pct": usage_pct},
            )
        except Exception as e:
            return ComponentHealth(name="disk_space", status=HealthStatus.UNKNOWN, message=str(e))

    async def _check_memory(self) -> ComponentHealth:
        try:
            import psutil
            mem = psutil.virtual_memory()
            if mem.percent > 95:
                status = HealthStatus.UNHEALTHY
            elif mem.percent > 85:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.HEALTHY
            return ComponentHealth(
                name="memory",
                status=status,
                message=f"{mem.percent:.1f}% used ({mem.available / 1e9:.1f} GB available)",
                details={
                    "total_gb": mem.total / 1e9,
                    "available_gb": mem.available / 1e9,
                    "usage_pct": mem.percent,
                }
            )
        except Exception as e:
            return ComponentHealth(name="memory", status=HealthStatus.UNKNOWN, message=str(e))

    async def _check_external_api(self) -> ComponentHealth:
        """Check connectivity to an external service."""
        start = time.time()
        try:
            # Check DNS resolution
            socket.getaddrinfo("google.com", 443)
            latency = (time.time() - start) * 1000
            return ComponentHealth(
                name="external_api",
                status=HealthStatus.HEALTHY,
                latency_ms=latency,
                message="DNS resolution working",
            )
        except Exception as e:
            return ComponentHealth(
                name="external_api",
                status=HealthStatus.DEGRADED,
                message=str(e),
            )

    def get_history(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._history[-limit:]


# Global health checker
health_checker = HealthChecker()


# ──────────────────────────────────────────────────────────────
# FastAPI Integration
# ──────────────────────────────────────────────────────────────

health_router = APIRouter(tags=["health"])


@health_router.get("/health")
async def health_check():
    return (await health_checker.check_all()).to_dict()


@health_router.get("/health/quick")
async def quick_health():
    """Quick health check without full component verification."""
    return {
        "status": "healthy",
        "uptime_seconds": round(time.time() - health_checker._start_time, 2),
        "checks_performed": health_checker._checks_performed,
    }


@health_router.get("/health/history")
async def health_history(limit: int = 50):
    return {"history": health_checker.get_history(limit)}
