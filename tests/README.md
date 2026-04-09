# Tests

Comprehensive test suite for the NeuralBlitz AI system ecosystem. Contains 27+ test files and 7 subdirectories covering the LRS core, governance, neuralblitz-v50, IoT mesh, voice interface, capabilities, agents, cities, federated systems, integrations, and utilities.

## Overview

### Root-Level Test Files (27 files)

| File | Coverage Area |
|------|---------------|
| `test_lrs_core.py` | LRS (Learning Reasoning System) core functionality |
| `test_lrs_multi_agent.py` | Multi-agent LRS interactions |
| `test_neuralblitz_v50_core.py` | NeuralBlitz v50 core system |
| `test_agents.py` | Agent system tests |
| `test_capabilities.py` | Capability framework tests |
| `test_capability_kernels.py` | Capability kernel execution |
| `test_cities.py` | Smart city module tests |
| `test_federated_full.py` | Federated system integration tests |
| `test_governance_full.py` | Governance system end-to-end tests |
| `test_governance_modules.py` | Individual governance module tests |
| `test_integrations.py` | Cross-system integration tests |
| `test_iot_mesh_full.py` | IoT mesh system full test suite |
| `test_voice_interface_full.py` | Voice interface system tests |
| `test_app_factory.py` | Application factory tests |
| `test_simple_app.py` | Simple application smoke tests |
| `test_new_modules.py` | Tests for newly added modules |
| `test_utils.py` | Utility function tests |
| `conftest.py` | Pytest configuration, fixtures, and mocks |
| `__init__.py` | Package marker |

### Deep Source Tests

| File | Coverage Area |
|------|---------------|
| `test_src_agents_deep.py` | Deep tests for `src/agents/` |
| `test_src_capabilities_deep.py` | Deep tests for `src/capabilities/` |
| `test_src_federated_deep.py` | Deep tests for `src/federated/` |
| `test_src_governance_deep.py` | Deep tests for `src/governance/` |
| `test_src_integrations_deep.py` | Deep tests for `src/integrations/` |

### Test Subdirectories

| Directory | Contents |
|-----------|----------|
| `agents/` | Agent-specific test modules |
| `capabilities/` | Capability framework test modules |
| `cities/` | Smart city test modules |
| `federated/` | Federated learning and coordination tests |
| `governance/` | Governance policy and module tests |
| `integrations/` | Cross-component integration tests |
| `utils/` | Shared test utilities and helpers |

## Quick Start

### Run All Tests

```bash
# Run entire test suite
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=html

# Run with detailed output
pytest tests/ -v --tb=long

# Run in parallel (requires pytest-xdist)
pytest tests/ -n auto
```

### Run Specific Test Categories

```bash
# Core LRS tests
pytest tests/test_lrs_core.py tests/test_lrs_multi_agent.py -v

# Agent tests
pytest tests/test_agents.py tests/test_src_agents_deep.py -v

# Governance tests
pytest tests/test_governance_full.py tests/test_governance_modules.py tests/test_src_governance_deep.py -v

# Federated system tests
pytest tests/test_federated_full.py tests/test_src_federated_deep.py -v

# IoT mesh tests
pytest tests/test_iot_mesh_full.py -v

# Voice interface tests
pytest tests/test_voice_interface_full.py -v

# Integration tests
pytest tests/test_integrations.py tests/test_src_integrations_deep.py -v
```

### Run Subdirectory Tests

```bash
# Agent subdirectory tests
pytest tests/agents/ -v

# Capabilities subdirectory tests
pytest tests/capabilities/ -v

# Cities subdirectory tests
pytest tests/cities/ -v

# Federated subdirectory tests
pytest tests/federated/ -v

# Governance subdirectory tests
pytest tests/governance/ -v

# Integrations subdirectory tests
pytest tests/integrations/ -v

# Utilities subdirectory tests
pytest tests/utils/ -v
```

## Architecture & Components

### Test Configuration (`conftest.py`)

Shared pytest fixtures available across all test files:

| Fixture | Purpose |
|---------|---------|
| `mock_llm` | Mock LLM instance that returns predictable responses without API calls |
| `sample_belief_state` | Pre-built belief state dictionary for agent testing |
| `temp_dir` | Temporary directory (via `tmp_path`) for file operations |
| `mock_agent_config` | Standard agent configuration dictionary for test setups |
| `sample_tool_result` | Pre-built tool execution result with success/error fields |
| `suppress_import_warnings` | Autouse fixture that suppresses import-related deprecation warnings |

The configuration adds `src/` to `sys.path` for imports, enabling direct testing of source modules.

### Test Categories

**Core System Tests** — Test the foundational LRS (Learning Reasoning System) including belief states, adaptation loops, and multi-agent coordination.

**Governance Tests** — Validate governance modules, policy enforcement, rule evaluation, and compliance checking across full and module-level scopes.

**Federated Tests** — Cover federated learning coordination, distributed training, model aggregation, and cross-node synchronization.

**Agent Tests** — Exercise agent lifecycle, tool usage, planning, multi-agent collaboration, and deep source-level behavior.

**Capability Tests** — Validate the capability kernel system, skill registration, execution pipelines, and capability composition.

**City Tests** — Test smart city modules including infrastructure management, resource allocation, and urban analytics.

**IoT Mesh Tests** — Full integration tests for the IoT device mesh system (MQTT, discovery, automation, persistence).

**Voice Interface Tests** — End-to-end tests for voice input processing, speech recognition, intent extraction, and response generation.

**Integration Tests** — Cross-component tests verifying that subsystems work together correctly (LRS + agents, governance + federated, etc.).

### Test Patterns

```python
# Typical test structure using shared fixtures
class TestAgentBehavior:
    def test_agent_initialization(self, mock_agent_config, mock_llm):
        agent = Agent(config=mock_agent_config, llm=mock_llm)
        assert agent.name == "test_agent"
        assert agent.state == "initialized"

    def test_agent_tool_usage(self, mock_llm, sample_tool_result):
        mock_llm.invoke.return_value = sample_tool_result
        agent = Agent(llm=mock_llm)
        result = agent.execute_tool("test_tool")
        assert result["success"] is True
```

## Features

- **27+ root test files** covering all major system components
- **7 subdirectories** with organized, domain-specific test modules
- **5 deep source test files** for thorough `src/` directory validation
- **Shared fixtures** via `conftest.py` — mock LLM, belief states, agent configs, tool results
- **Full and module-level tests** — both end-to-end integration and unit-level module tests
- **IoT mesh integration tests** — dedicated full test suite for the IoT subsystem
- **Voice interface tests** — end-to-end voice processing pipeline coverage
- **Federated system tests** — distributed training and coordination validation
- **Governance tests** — policy enforcement and compliance at both full and module levels
- **Auto-suppressed warnings** — import deprecation warnings filtered to reduce noise

## API / Usage Examples

### Running Individual Tests

```bash
# Run a specific test function
pytest tests/test_lrs_core.py::test_belief_state_update -v

# Run a specific test class
pytest tests/test_agents.py::TestAgentLifecycle -v

# Run tests matching a keyword
pytest tests/ -k "governance" -v
pytest tests/ -k "federated" -v
```

### Running with Coverage

```bash
# Full coverage report
pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# Coverage for specific module
pytest tests/ --cov=src.agents --cov-report=html

# Coverage with minimum threshold
pytest tests/ --cov=src --cov-fail-under=80
```

### Running with Markers

```bash
# Run only unit tests (if marked)
pytest tests/ -m unit -v

# Run only integration tests (if marked)
pytest tests/ -m integration -v

# Run slow tests separately
pytest tests/ -m slow -v
```

### Debugging Failing Tests

```bash
# Drop into debugger on failure
pytest tests/test_lrs_core.py --pdb

# Show local variables on failure
pytest tests/test_lrs_core.py -v --tb=short

# Capture print output
pytest tests/test_lrs_core.py -v -s
```

## Testing

### Dependencies

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-asyncio pytest-mock

# Optional: parallel test execution
pip install pytest-xdist

# Optional: test reporting
pip install pytest-html
```

### CI/CD Integration

```bash
# Typical CI command
pytest tests/ -v --cov=src --cov-fail-under=70 --junitxml=test-results.xml

# With parallel execution
pytest tests/ -n auto --cov=src --cov-fail-under=70
```

## Related Documentation

- [ARCHITECTURE.md](../ARCHITECTURE.md) — Overall system architecture
- [DEVELOPMENT_SETUP.md](../DEVELOPMENT_SETUP.md) — Development environment setup
- [../iot_mesh_system/](../iot_mesh_system/) — IoT Mesh system (has its own test suite)
- [../ipfs_integration/](../ipfs_integration/) — IPFS integration module
- [../reports/](../reports/) — Analytical reports and deployment scripts
- [conftest.py](./conftest.py) — Shared pytest fixtures and configuration
