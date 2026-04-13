"""Tests for src/middleware/health.py — Health Check System."""

import pytest
import asyncio
from unittest.mock import patch, MagicMock

pytest.importorskip("fastapi")


@pytest.fixture
def health_module():
    """Import health module fresh."""
    import importlib
    for key in list(__import__("sys").modules.keys()):
        if key.startswith("middleware.health"):
            del __import__("sys").modules[key]
    from src.middleware import health
    return health


class TestHealthStatus:
    def test_enum_values(self, health_module):
        assert health_module.HealthStatus.HEALTHY == "healthy"
        assert health_module.HealthStatus.DEGRADED == "degraded"
        assert health_module.HealthStatus.UNHEALTHY == "unhealthy"
        assert health_module.HealthStatus.UNKNOWN == "unknown"


class TestComponentHealth:
    def test_create_healthy(self, health_module):
        h = health_module.ComponentHealth(
            name="db",
            status=health_module.HealthStatus.HEALTHY,
            latency_ms=1.5,
            message="OK",
            details={"connections": 10},
        )
        assert h.name == "db"
        assert h.status == health_module.HealthStatus.HEALTHY
        assert h.latency_ms == 1.5
        assert h.details["connections"] == 10

    def test_create_unhealthy(self, health_module):
        h = health_module.ComponentHealth(
            name="cache",
            status=health_module.HealthStatus.UNHEALTHY,
            message="Connection refused",
        )
        assert h.status == health_module.HealthStatus.UNHEALTHY
        assert "refused" in h.message


class TestSystemHealth:
    def test_to_dict(self, health_module):
        sh = health_module.SystemHealth(
            status=health_module.HealthStatus.HEALTHY,
            components={
                "db": health_module.ComponentHealth(
                    name="db",
                    status=health_module.HealthStatus.HEALTHY,
                    latency_ms=2.0,
                ),
            },
            overall_uptime=100.5,
            checks_performed=5,
        )
        d = sh.to_dict()
        assert d["status"] == "healthy"
        assert "db" in d["components"]
        assert d["components"]["db"]["status"] == "healthy"
        assert d["components"]["db"]["latency_ms"] == 2.0
        assert d["overall_uptime"] == 100.5
        assert d["checks_performed"] == 5


class TestHealthChecker:
    @pytest.fixture
    def checker(self, health_module):
        return health_module.HealthChecker()

    def test_init(self, checker):
        assert checker._checks_performed == 0
        assert len(checker._history) == 0

    def test_get_history_empty(self, checker):
        history = checker.get_history(10)
        assert history == []

    def test_get_history_limited(self, checker):
        checker._history = [{"i": i} for i in range(200)]
        history = checker.get_history(50)
        assert len(history) == 50

    def test_get_history_all(self, checker):
        checker._history = [{"i": i} for i in range(10)]
        history = checker.get_history(100)
        assert len(history) == 10


class TestIndividualChecks:
    """Test individual async health check methods."""

    @pytest.fixture
    def checker(self, health_module):
        return health_module.HealthChecker()

    def test_check_database(self, checker, health_module):
        """Database check runs (module not installed = UNKNOWN)."""
        result = asyncio.get_event_loop().run_until_complete(
            checker._check_database()
        )
        assert result.name == "database"
        assert result.status in (
            health_module.HealthStatus.HEALTHY,
            health_module.HealthStatus.UNKNOWN,
            health_module.HealthStatus.UNHEALTHY,
        )

    def test_check_cache_memory(self, checker, health_module):
        """Memory cache should always work."""
        result = asyncio.get_event_loop().run_until_complete(
            checker._check_cache()
        )
        assert result.name == "cache"
        assert result.status == health_module.HealthStatus.HEALTHY

    def test_check_websocket(self, checker):
        result = asyncio.get_event_loop().run_until_complete(
            checker._check_websocket()
        )
        assert result.name == "websocket"

    def test_check_event_bus(self, checker):
        result = asyncio.get_event_loop().run_until_complete(
            checker._check_event_bus()
        )
        assert result.name == "event_bus"

    def test_check_ml_pipeline(self, checker):
        result = asyncio.get_event_loop().run_until_complete(
            checker._check_ml_pipeline()
        )
        assert result.name == "ml_pipeline"

    def test_check_disk_space(self, checker):
        result = asyncio.get_event_loop().run_until_complete(
            checker._check_disk_space()
        )
        assert result.name == "disk_space"

    def test_check_memory(self, checker):
        result = asyncio.get_event_loop().run_until_complete(
            checker._check_memory()
        )
        assert result.name == "memory"

    def test_check_external_api(self, checker):
        """External API check should handle network issues gracefully."""
        result = asyncio.get_event_loop().run_until_complete(
            checker._check_external_api()
        )
        assert result.name == "external_api"


class TestHealthCheckerCheckAll:
    """Test the full check_all method."""

    @pytest.fixture
    def checker(self, health_module):
        return health_module.HealthChecker()

    def test_check_all_returns_system_health(self, checker, health_module):
        result = asyncio.get_event_loop().run_until_complete(checker.check_all())
        assert isinstance(result, health_module.SystemHealth)
        # Status may be UNKNOWN (db not installed) or HEALTHY/DEGRADED/UNHEALTHY
        assert result.status in list(health_module.HealthStatus)
        assert len(result.components) > 0
        assert "database" in result.components
        assert "cache" in result.components
        assert "websocket" in result.components
        assert "event_bus" in result.components
        assert "ml_pipeline" in result.components
        assert result.checks_performed == 1

    def test_check_all_tracks_history(self, checker):
        asyncio.get_event_loop().run_until_complete(checker.check_all())
        asyncio.get_event_loop().run_until_complete(checker.check_all())
        assert len(checker._history) == 2

    def test_check_all_error_handling(self, checker, health_module):
        """Test that check_all handles component errors gracefully."""
        async def failing_check():
            raise RuntimeError("Simulated failure")

        with patch.object(checker, "_check_database", failing_check):
            result = asyncio.get_event_loop().run_until_complete(checker.check_all())
            # Should still complete, database component should be UNKNOWN
            assert "database" in result.components
            db = result.components["database"]
            assert db.status == health_module.HealthStatus.UNKNOWN
            assert "Simulated failure" in db.message


class TestHealthRouter:
    """Test FastAPI health router endpoints."""

    @pytest.fixture
    def client(self, health_module):
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(health_module.health_router)
        return TestClient(app)

    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "components" in data
        assert "timestamp" in data
        assert len(data["components"]) > 0

    def test_health_quick(self, client):
        response = client.get("/health/quick")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "uptime_seconds" in data
        assert data["status"] == "healthy"

    def test_health_history(self, client):
        response = client.get("/health/history")
        assert response.status_code == 200
        data = response.json()
        assert "history" in data
        assert isinstance(data["history"], list)

    def test_health_history_with_limit(self, client):
        response = client.get("/health/history?limit=10")
        assert response.status_code == 200
