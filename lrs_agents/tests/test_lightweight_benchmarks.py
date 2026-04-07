"""Tests for lightweight benchmark utilities."""

import random

import pytest

from lrs.benchmarking.lightweight_benchmarks import (
    BasicSearchTool,
    CalculatorTool,
    FileReadTool,
    LightweightChaosBenchmark,
    LightweightChaosEnvironment,
    LightweightFileTool,
    LightweightGAIABenchmark,
    LightweightShellTool,
)
from lrs.opencode.lightweight_lrs import (
    LightweightFreeEnergyCalculator,
    LightweightPolicySelector,
    LightweightPrecisionParameters,
)


def test_lightweight_precision_parameters_adapt_threshold():
    """Precision should request adaptation when below threshold."""
    params = LightweightPrecisionParameters(adaptation_threshold=0.45)
    for _ in range(10):
        params.update(0.95)

    assert params.should_adapt()


def test_lightweight_free_energy_calculator_handles_empty_policy():
    """Empty policies should return zero epistemic/pragmatic values."""
    calculator = LightweightFreeEnergyCalculator()

    assert calculator.calculate_epistemic_value([]) == 0.0
    assert calculator.calculate_pragmatic_value([], {"success": 1.0}) == 0.0


def test_policy_selector_rejects_empty_evaluations():
    """Policy selector should reject empty input."""
    with pytest.raises(ValueError):
        LightweightPolicySelector.precision_weighted_selection([])


def test_lightweight_chaos_environment_locks_and_resets(monkeypatch, tmp_path):
    """Chaos environment should lock on chaos tick and reset cleanly."""
    env = LightweightChaosEnvironment(
        root_dir=str(tmp_path), chaos_interval=1, lock_probability=1.0
    )
    env.setup()

    monkeypatch.setattr("lrs.benchmarking.lightweight_benchmarks.random.random", lambda: 0.0)
    monkeypatch.setattr(env, "_set_permissions", lambda readable: None)
    env.tick()

    assert env.is_locked()

    env.reset()
    assert not env.is_locked()


def test_lightweight_shell_tool_forced_failure(monkeypatch, tmp_path):
    """Shell tool should report failure when environment is locked."""
    env = LightweightChaosEnvironment(root_dir=str(tmp_path))
    env.setup()
    env.locked = True

    monkeypatch.setattr("lrs.benchmarking.lightweight_benchmarks.random.random", lambda: 0.0)

    tool = LightweightShellTool(env)
    result = tool.execute("echo ok")

    assert not result["success"]
    assert "error" in result


def test_lightweight_file_tool_locked(tmp_path):
    """File tool should return an error when locked."""
    env = LightweightChaosEnvironment(root_dir=str(tmp_path))
    env.setup()
    env.locked = True

    tool = LightweightFileTool(env)
    result = tool.execute(env.key_path)

    assert not result["success"]
    assert result["error"] == "File locked"


def test_lightweight_gaia_tool_selection():
    """GAIA benchmark should select the right tools for tasks."""
    benchmark = LightweightGAIABenchmark()
    tasks = benchmark.create_simple_tasks()

    calc_tools = benchmark._get_tools_for_task(tasks[1])
    read_tools = benchmark._get_tools_for_task(tasks[2])
    search_tools = benchmark._get_tools_for_task(tasks[0])

    assert isinstance(calc_tools[0], CalculatorTool)
    assert isinstance(read_tools[0], FileReadTool)
    assert isinstance(search_tools[0], BasicSearchTool)


def test_lightweight_gaia_run_task_deterministic(monkeypatch):
    """Run task should be deterministic when random is fixed."""
    benchmark = LightweightGAIABenchmark()
    task = benchmark.create_simple_tasks()[0]

    monkeypatch.setattr("lrs.benchmarking.lightweight_benchmarks.random.random", lambda: 0.95)
    result = benchmark.run_task(task)

    assert result["success"]
    assert result["difficulty"] == "easy"


def test_lightweight_chaos_single_trial_success(monkeypatch):
    """Chaos benchmark should succeed when environment stays unlocked."""
    monkeypatch.setattr("lrs.benchmarking.lightweight_benchmarks.random.random", lambda: 0.99)
    benchmark = LightweightChaosBenchmark()

    result = benchmark.run_single_trial(max_steps=5)

    assert result["success"]
    assert result["steps"] >= 1
    assert "tool_stats" in result
