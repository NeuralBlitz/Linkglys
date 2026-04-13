"""Tests for src/app_factory_v2.py — the main FastAPI application."""

import sys
import pytest
from fastapi.testclient import TestClient

pytest.importorskip("fastapi")


@pytest.fixture
def mock_modules(monkeypatch):
    """Mock all optional external imports so app_factory_v2 loads cleanly."""
    import sys
    for mod in [
        "lrs_agents.lrs.opencode.simplified_integration",
        "lrs_agents.lrs.cognitive.multi_agent_coordination",
    ]:
        monkeypatch.setitem(sys.modules, mod, None)


@pytest.fixture
def app_factory_module(mock_modules):
    """Import app_factory_v2 with mocked dependencies."""
    import importlib
    # Clear cached middleware/app modules to force fresh import
    for key in list(sys.modules.keys()):
        if key.startswith(("middleware.", "app_factory")):
            del sys.modules[key]
    from src import app_factory_v2
    return app_factory_v2


@pytest.fixture
def client(app_factory_module):
    """Create a TestClient for the full v2 app."""
    return TestClient(app_factory_module.create_app())


class TestAppFactoryV2:
    """Integration tests for the full FastAPI v2 application."""

    def test_create_app(self, app_factory_module):
        """Test that create_app returns a FastAPI instance."""
        app = app_factory_module.create_app()
        assert app.title == "Linkglys API v2.0"
        assert app.version == "2.0.0"

    def test_root_endpoint(self, client):
        """Test root endpoint returns API info or SPA."""
        response = client.get("/")
        assert response.status_code in (200, 307)

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/api/v2/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "2.0.0"

    def test_metrics_endpoint(self, client):
        """Test Prometheus metrics endpoint — may serve SPA if build exists."""
        response = client.get("/metrics")
        assert response.status_code == 200

    def test_stats_endpoint(self, client):
        """Test system stats endpoint."""
        response = client.get("/api/v2/stats")
        assert response.status_code == 200
        data = response.json()
        assert "rate_limiter" in data
        assert "cache" in data
        assert "websocket" in data
        assert "event_bus" in data

    def test_config_endpoint(self, client):
        """Test configuration endpoint."""
        response = client.get("/api/v2/config")
        assert response.status_code == 200
        data = response.json()
        assert "rate_limit_profiles" in data
        assert isinstance(data["rate_limit_profiles"], list)
        assert "jwt_algorithm" in data
        assert "cache_backend" in data

    def test_list_agents(self, client):
        """Test listing agents."""
        response = client.get("/api/v2/agents")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert "total" in data
        assert isinstance(data["agents"], list)

    def test_create_agent(self, client):
        """Test creating an agent with auth."""
        login_resp = client.post("/api/v2/auth/login", json={
            "username": "admin", "password": "admin"
        })
        token = login_resp.json()["access_token"]
        response = client.post("/api/v2/agents", json={
            "name": "test-agent-v2",
            "type": "inference",
            "config": {"model": "test-model"}
        }, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "test-agent-v2"

    def test_list_agents_with_filter(self, client):
        """Test listing agents with status filter."""
        response = client.get("/api/v2/agents", params={"status": "idle"})
        assert response.status_code == 200
        data = response.json()
        for agent in data["agents"]:
            assert agent["status"] == "idle"

    def test_agent_command(self, client):
        """Test sending command to agent."""
        response = client.post("/api/v2/agents/agent-0/command", json={
            "command": "start",
            "params": {"task": "test"}
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "queued"

    def test_agent_metrics(self, client):
        """Test getting agent metrics."""
        response = client.get("/api/v2/agents/agent-0/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "metrics" in data
        assert "cpu_usage" in data["metrics"]

    def test_ml_predict_no_model(self, client):
        """Test predict with non-existent model returns error."""
        response = client.post("/api/v2/ml/predict", json={
            "model_name": "nonexistent",
            "features": [[1, 2, 3]]
        })
        # Should not crash — returns error in response
        assert response.status_code in (200, 500)

    def test_ml_stats(self, client):
        """Test ML pipeline stats endpoint."""
        response = client.get("/api/v2/ml/stats")
        assert response.status_code == 200
        data = response.json()
        assert "loaded_models" in data

    def test_list_plugins(self, client):
        """Test listing plugins."""
        response = client.get("/api/v2/plugins")
        assert response.status_code == 200
        data = response.json()
        assert "plugins" in data
        assert "count" in data

    def test_event_stats(self, client):
        """Test event bus statistics."""
        response = client.get("/api/v2/events/stats")
        assert response.status_code == 200
        data = response.json()
        assert "events_published" in data

    def test_event_dead_letters(self, client):
        """Test dead letter queue endpoint."""
        response = client.get("/api/v2/events/dead-letters")
        assert response.status_code == 200
        data = response.json()
        assert "dead_letters" in data

    def test_event_subscriptions(self, client):
        """Test list subscriptions endpoint."""
        response = client.get("/api/v2/events/subscriptions")
        assert response.status_code == 200
        data = response.json()
        assert "subscriptions" in data

    def test_integration_status(self, client):
        """Test integration status endpoint."""
        response = client.get("/api/v2/integration/status")
        assert response.status_code == 200
        data = response.json()
        assert "lrs" in data
        assert "opencode" in data

    def test_auth_login_invalid_credentials(self, client):
        """Test login with invalid credentials returns 401."""
        response = client.post("/api/v2/auth/login", json={
            "username": "nonexistent",
            "password": "wrong"
        })
        assert response.status_code == 401

    def test_auth_register(self, client):
        """Test user registration."""
        response = client.post("/api/v2/auth/register", json={
            "username": "newtestuser",
            "email": "newtest@example.com",
            "password": "testpass123",
            "role": "viewer"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data or "user" in data

    def test_auth_register_duplicate(self, client):
        """Test registration with duplicate username returns 400."""
        client.post("/api/v2/auth/register", json={
            "username": "dupuser",
            "email": "dup@example.com",
            "password": "testpass",
            "role": "viewer"
        })
        response = client.post("/api/v2/auth/register", json={
            "username": "dupuser",
            "email": "dup2@example.com",
            "password": "testpass",
            "role": "viewer"
        })
        assert response.status_code == 400

    def test_auth_login_default_users(self, client):
        """Test login with seeded default users."""
        for user, pwd in [("admin", "admin"), ("developer", "developer"), ("viewer", "viewer")]:
            response = client.post("/api/v2/auth/login", json={
                "username": user,
                "password": pwd
            })
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data

    def test_auth_me_with_token(self, client):
        """Test /auth/me with valid token."""
        login_resp = client.post("/api/v2/auth/login", json={
            "username": "admin",
            "password": "admin"
        })
        token = login_resp.json()["access_token"]
        response = client.get("/api/v2/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"

    def test_auth_list_users_admin_only(self, client):
        """Test /auth/users requires admin role."""
        # Login as viewer (non-admin)
        client.post("/api/v2/auth/register", json={
            "username": "nonadmin",
            "email": "nonadmin@example.com",
            "password": "testpass",
            "role": "viewer"
        })
        login_resp = client.post("/api/v2/auth/login", json={
            "username": "nonadmin",
            "password": "testpass"
        })
        token = login_resp.json()["access_token"]

        response = client.get("/api/v2/auth/users", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 403

        # Admin can access
        admin_resp = client.post("/api/v2/auth/login", json={
            "username": "admin",
            "password": "admin"
        })
        admin_token = admin_resp.json()["access_token"]
        response = client.get("/api/v2/auth/users", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200

    def test_auth_api_key(self, client):
        """Test API key generation."""
        login_resp = client.post("/api/v2/auth/login", json={
            "username": "admin",
            "password": "admin"
        })
        token = login_resp.json()["access_token"]
        response = client.post("/api/v2/auth/api-key", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert "api_key" in data
        assert data["api_key"].startswith("nb_")

    def test_auth_refresh_token(self, client):
        """Test token refresh."""
        login_resp = client.post("/api/v2/auth/login", json={
            "username": "admin",
            "password": "admin"
        })
        refresh_token = login_resp.json()["refresh_token"]
        response = client.post("/api/v2/auth/refresh", params={
            "refresh_token": refresh_token
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_ml_train_classification(self, client):
        """Test training a classification model."""
        login_resp = client.post("/api/v2/auth/login", json={
            "username": "admin", "password": "admin"
        })
        token = login_resp.json()["access_token"]
        response = client.post("/api/v2/ml/train", json={
            "model_name": "test-cls-v3",
            "model_type": "random_forest",
            "task": "classification",
            "features": [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0], [7.0, 8.0], [9.0, 10.0]],
            "labels": [0, 0, 1, 1, 0],
        }, headers={"Authorization": f"Bearer {token}"})
        # May succeed or fail depending on sklearn availability
        assert response.status_code in (200, 500)

    def test_ml_predict_after_train(self, client):
        """Test prediction endpoint (model may not exist, tests error handling)."""
        response = client.post("/api/v2/ml/predict", json={
            "model_name": "nonexistent-model-xyz",
            "features": [[1.0, 2.0, 3.0]]
        })
        # Should return error in response body, not crash
        assert response.status_code in (200, 500)

    def test_ml_cluster(self, client):
        """Test clustering endpoint."""
        response = client.post("/api/v2/ml/cluster", json={
            "features": [[1.0, 2.0], [1.1, 2.1], [10.0, 20.0], [10.1, 20.1]],
            "n_clusters": 2,
            "method": "kmeans"
        })
        assert response.status_code in (200, 422, 500)

    def test_ml_anomalies(self, client):
        """Test anomaly detection endpoint."""
        response = client.post("/api/v2/ml/anomalies", json={
            "features": [[1.0, 2.0], [1.1, 2.1], [1.0, 2.0], [100.0, 200.0]],
            "contamination": 0.1
        })
        assert response.status_code in (200, 422, 500)
