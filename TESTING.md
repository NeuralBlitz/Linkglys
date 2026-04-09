# Linkglys — Testing Guide

**Last Updated:** April 9, 2026

---

## Overview

This project uses **pytest** with async support for comprehensive testing across all components.

### Test Framework Stack

| Tool | Purpose |
|------|---------|
| **pytest** | Test runner |
| **pytest-asyncio** | Async test support |
| **pytest-cov** | Coverage reporting |
| **pytest-mock** | Mocking utilities |
| **pytest-benchmark** | Performance benchmarks |

---

## Running Tests

### Quick Test Suite

```bash
# Run all tests
pytest

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Run with short tracebacks
pytest --tb=short
```

### By Component

```bash
# Root-level tests (27 files)
pytest tests/ -v

# LRS-Agents tests
cd lrs_agents && pytest tests/ -v

# Specific component tests
pytest tests/agents/ -v
pytest tests/capabilities/ -v
pytest tests/cities/ -v
pytest tests/federated/ -v
pytest tests/governance/ -v
pytest tests/integrations/ -v
pytest tests/utils/ -v
```

### By Test Type

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Exclude slow tests
pytest -m "not slow"

# Performance benchmarks
pytest tests/performance/ -v --benchmark-only
```

### Coverage Reports

```bash
# Run with coverage
pytest --cov=src --cov-report=html

# Open coverage report
open htmlcov/index.html

# Terminal coverage summary
pytest --cov=src --cov-report=term-missing

# Fail if coverage below threshold
pytest --cov=src --cov-fail-under=80
```

---

## Test Structure

### Root-Level Tests (`tests/`)

```
tests/
├── test_agents.py              # Agent module loading tests
├── test_capabilities.py        # Capability kernel tests
├── test_cities.py              # Smart city system tests
├── test_governance_modules.py  # Governance module tests
├── test_lrs_core.py            # LRS core tests (precision, lens, registry)
├── test_neuralblitz_v50_core.py # NeuralBlitz v50 tests
├── test_edge_computing.py      # Edge computing tests
├── test_voice_interface_full.py # Voice interface tests
├── test_iot_mesh_full.py       # IoT mesh system tests
├── test_federated_full.py      # Federated learning tests
├── test_governance_full.py     # Governance system tests
├── test_simple_app.py          # Flask app tests
├── test_app_factory.py         # FastAPI app factory tests
├── agents/                     # Agent-specific tests
├── capabilities/               # Capability kernel tests
├── cities/                     # Smart city tests
├── federated/                  # Federated learning tests
├── governance/                 # Governance system tests
├── integrations/               # Vector DB integration tests
└── utils/                      # Utility module tests
```

### LRS-Agents Tests (`lrs_agents/tests/`)

```
lrs_agents/tests/
├── unit/                       # Unit tests
├── integration/                # Integration tests
├── e2e/                        # End-to-end tests
├── performance/                # Performance tests
├── stress/                     # Stress tests
└── security/                   # Security tests
```

---

## Writing Tests

### Test Conventions

All tests follow these conventions:

```python
import pytest
from src.module import ClassToTest

class TestClassName:
    """Tests for ClassToTest."""

    @pytest.fixture
    def instance(self):
        """Create test instance."""
        return ClassToTest()

    def test_method_does_thing(self, instance):
        """Test specific behavior."""
        result = instance.method()
        assert result == expected_value

    @pytest.mark.asyncio
    async def test_async_method(self, instance):
        """Test async behavior."""
        result = await instance.async_method()
        assert result is not None

    @pytest.mark.unit
    def test_unit_level(self, instance):
        """Mark as unit test."""
        pass

    @pytest.mark.slow
    def test_slow_operation(self, instance):
        """Mark as slow test."""
        pass
```

### Testing FastAPI Endpoints

```python
from fastapi.testclient import TestClient
from src.app_factory_v2 import create_app

client = TestClient(create_app())

def test_health_endpoint():
    response = client.get("/api/v2/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_auth_requires_token():
    response = client.get("/api/v2/agents")
    assert response.status_code == 401  # Unauthorized

def test_create_agent_with_auth():
    # Login first
    login_response = client.post("/api/v2/auth/login", json={
        "username": "admin",
        "password": "password"
    })
    token = login_response.json()["access_token"]

    # Create agent with token
    response = client.post("/api/v2/agents", json={
        "name": "test-agent",
        "type": "inference"
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
```

### Testing Agents

```python
from src.agents.advanced_autonomous_agent_framework import AutonomousAgent

class TestAutonomousAgent:
    @pytest.fixture
    def agent(self):
        return AutonomousAgent(name="test-agent")

    def test_agent_starts_idle(self, agent):
        assert agent.state.value == "idle"

    def test_agent_can_plan(self, agent):
        plan = agent.plan("simple task")
        assert plan is not None
        assert len(plan.steps) > 0
```

### Testing Capability Kernels

```python
from src.capabilities.quadratic_voting_ck import QuadraticVotingCK

class TestQuadraticVotingCK:
    @pytest.fixture
    def ck(self):
        return QuadraticVotingCK()

    def test_compute_vote_cost(self, ck):
        # Cost = votes²
        assert ck.compute_cost(1) == 1
        assert ck.compute_cost(2) == 4
        assert ck.compute_cost(3) == 9
```

---

## Test Configuration

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts = -v --tb=short --strict-markers
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

### pyproject.toml (Coverage)

```toml
[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/__pycache__/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
]
```

---

## CI/CD Testing

### GitHub Actions

Tests run automatically on:
- Every push to `main` branch
- Every pull request
- Scheduled daily runs

**Workflows:**
- `.github/workflows/ci.yml` — Main CI pipeline
- `lrs_agents/.github/workflows/test.yml` — LRS-Agents tests
- `neuralblitz-v50/.github/workflows/test.yml` — NeuralBlitz v50 tests

### Running CI Locally

```bash
# Simulate CI locally
ruff check src/ tests/
black --check src/ tests/
mypy src/
pytest tests/ -v --cov=src --cov-fail-under=80
```

---

## Performance Testing

### Benchmarks

```bash
# Run performance tests
pytest tests/performance/ -v --benchmark-only

# Compare against baseline
pytest tests/performance/ -v --benchmark-compare

# Generate performance report
pytest tests/performance/ -v --benchmark-json=benchmarks.json
```

### Load Testing

```bash
# LRS-Agents load tests
cd lrs_agents
pytest tests/stress/ -v

# API load testing with wrk
wrk -t4 -c100 -d30s http://localhost:5000/api/v2/health
```

---

## Debugging Tests

### Verbose Output

```bash
# Show print statements
pytest -v -s

# Show local variables on failure
pytest -l

# Show extra test info
pytest --tb=long
```

### Debug Single Test

```bash
# Run specific test
pytest tests/test_lrs_core.py::TestPrecision::test_update_precision -v

# Drop into debugger on failure
pytest tests/ -v --pdb
```

### Coverage Debugging

```bash
# See which lines are NOT covered
pytest --cov=src --cov-report=term-missing

# Highlight missing lines
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

---

## Test Categories

### Auto-Adapting Module Tests

Root-level tests use **auto-adapting** pattern:

```python
def test_module_loads():
    """Verify module can be imported and classes exist."""
    from src.module import SomeClass
    assert SomeClass is not None
    instance = SomeClass()
    assert instance is not None
```

These tests verify:
1. Module can be imported
2. Expected classes exist
3. Classes can be instantiated
4. Basic functionality works

### Functional Tests

LRS-Agents has deeper functional tests:

```python
def test_agent_adapts_on_failure():
    """Agent should explore alternatives when tools fail."""
    agent = create_lrs_agent(tools=[failing_tool, working_tool])
    result = agent.invoke({"messages": [...]})
    assert result["tool_used"] == "working_tool"
```

---

## Testing Checklist

Before submitting a PR:

- [ ] All existing tests pass: `pytest tests/ -v`
- [ ] New tests written for changes
- [ ] Coverage above 80%: `pytest --cov=src`
- [ ] Linting passes: `ruff check src/ tests/`
- [ ] Type checking passes: `mypy src/`
- [ ] Code formatted: `black src/ tests/`
- [ ] No slow tests in CI (or marked with `@pytest.mark.slow`)

---

## Common Test Issues

| Issue | Solution |
|-------|----------|
| **ModuleNotFoundError** | Add project root to `PYTHONPATH` |
| **Async tests not running** | Ensure `@pytest.mark.asyncio` decorator |
| **Tests pass locally, fail in CI** | Check environment variables, use mocks |
| **Coverage too low** | Add tests for untested branches |
| **Tests too slow** | Mark with `@pytest.mark.slow`, use `-m "not slow"` |
| **Database locked** | Use SQLite in-memory: `sqlite:///` |
| **Redis not available** | Mock Redis or use memory cache |

---

## Test Statistics

| Component | Test Files | Approx. Tests | Coverage |
|-----------|-----------|---------------|----------|
| **Root tests/** | 27 | ~100+ | ~60% |
| **LRS-Agents** | 50+ | ~350+ | ~95% |
| **NeuralBlitz v50** | 20+ | ~100+ | ~70% |
| **Integration Bridge** | 5+ | ~30+ | ~80% |
| **Total** | **100+** | **~600+** | **~75%** |

---

*For more information on testing individual components, see their respective README files.*
