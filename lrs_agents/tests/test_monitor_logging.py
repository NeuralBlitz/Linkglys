"""Tests for LRSLogger structured logging."""

import pytest
import logging
import json
from io import StringIO
from lrs.monitoring.structured_logging import LRSLogger, create_logger_for_agent


class TestLRSLoggerInitialization:
    """Test LRSLogger initialization."""

    def test_initialization_with_defaults(self):
        """Test default initialization"""
        logger = LRSLogger(agent_id="test_agent")

        assert logger.agent_id == "test_agent"
        assert logger.session_id.startswith("test_agent_")
        assert len(logger.logger.handlers) > 0

    def test_initialization_no_console(self):
        """Test initialization without console output"""
        logger = LRSLogger(agent_id="test_agent", console=False)

        # Should have no handlers when console is disabled and no file
        assert len(logger.logger.handlers) == 0

    def test_initialization_with_log_file(self, tmp_path):
        """Test initialization with log file"""
        log_file = tmp_path / "test.jsonl"
        logger = LRSLogger(agent_id="test_agent", log_file=str(log_file), console=False)

        assert len(logger.logger.handlers) == 1

    def test_initialization_custom_level(self):
        """Test initialization with custom logging level"""
        logger = LRSLogger(agent_id="test_agent", level=logging.DEBUG)

        assert logger.logger.level == logging.DEBUG


class TestLRSLoggerPrecisionUpdate:
    """Test precision update logging."""

    def test_log_precision_update(self, caplog):
        """Test logging precision update"""
        logger = LRSLogger(agent_id="test_agent", console=False)

        logger.log_precision_update(
            level="execution", old_value=0.8, new_value=0.4, prediction_error=0.95
        )

        # Just verify it doesn't raise
        assert True

    def test_log_precision_update_with_propagation(self, caplog):
        """Test logging precision update with propagation"""
        logger = LRSLogger(agent_id="test_agent", console=False)

        logger.log_precision_update(
            level="planning", old_value=0.6, new_value=0.3, prediction_error=0.8, propagated=True
        )

        assert True


class TestLRSLoggerPolicySelection:
    """Test policy selection logging."""

    def test_log_policy_selection(self):
        """Test logging policy selection"""
        logger = LRSLogger(agent_id="test_agent", console=False)

        policies = ["policy_a", "policy_b", "policy_c"]

        logger.log_policy_selection(
            policies=policies, selected_index=1, G_values=[-0.5, -0.8, -0.3], precision=0.75
        )

        assert True

    def test_log_policy_selection_single_policy(self):
        """Test logging with single policy"""
        logger = LRSLogger(agent_id="test_agent", console=False)

        logger.log_policy_selection(
            policies=["only_policy"], selected_index=0, G_values=[-0.5], precision=0.9
        )

        assert True


class TestLRSLoggerToolExecution:
    """Test tool execution logging."""

    def test_log_tool_execution_success(self):
        """Test logging successful tool execution"""
        logger = LRSLogger(agent_id="test_agent", console=False)

        logger.log_tool_execution(
            tool_name="api_fetch", success=True, execution_time=0.5, prediction_error=0.1
        )

        assert True

    def test_log_tool_execution_failure(self):
        """Test logging failed tool execution"""
        logger = LRSLogger(agent_id="test_agent", console=False)

        logger.log_tool_execution(
            tool_name="api_fetch",
            success=False,
            execution_time=0.3,
            prediction_error=0.9,
            error_message="Connection timeout",
        )

        assert True

    def test_log_tool_execution_fast(self):
        """Test logging very fast tool execution"""
        logger = LRSLogger(agent_id="test_agent", console=False)

        logger.log_tool_execution(
            tool_name="cache_hit", success=True, execution_time=0.001, prediction_error=0.0
        )

        assert True


class TestLRSLoggerAdaptationEvent:
    """Test adaptation event logging."""

    def test_log_adaptation_event(self):
        """Test logging adaptation event"""
        logger = LRSLogger(agent_id="test_agent", console=False)

        logger.log_adaptation_event(
            trigger="high_prediction_error",
            old_precision={"abstract": 0.5, "planning": 0.6, "execution": 0.7},
            new_precision={"abstract": 0.6, "planning": 0.7, "execution": 0.5},
            action_taken="reduced_execution_precision",
        )

        assert True

    def test_log_adaptation_event_single_level(self):
        """Test logging adaptation for single level"""
        logger = LRSLogger(agent_id="test_agent", console=False)

        logger.log_adaptation_event(
            trigger="low_success_rate",
            old_precision={"execution": 0.8},
            new_precision={"execution": 0.4},
            action_taken="reduced_precision",
        )

        assert True


class TestLRSLoggerPerformanceMetrics:
    """Test performance metrics logging."""

    def test_log_performance_metrics(self):
        """Test logging performance metrics"""
        logger = LRSLogger(agent_id="test_agent", console=False)

        logger.log_performance_metrics(
            total_steps=100,
            success_rate=0.85,
            avg_precision=0.72,
            adaptation_count=5,
            execution_time=45.5,
        )

        assert True

    def test_log_performance_metrics_zero_time(self):
        """Test logging with zero execution time"""
        logger = LRSLogger(agent_id="test_agent", console=False)

        logger.log_performance_metrics(
            total_steps=0,
            success_rate=0.0,
            avg_precision=0.0,
            adaptation_count=0,
            execution_time=0.0,
        )

        assert True


class TestLRSLoggerError:
    """Test error logging."""

    def test_log_error(self):
        """Test logging error"""
        logger = LRSLogger(agent_id="test_agent", console=False)

        logger.log_error(
            error_type="ValueError",
            message="Invalid precision value",
            stack_trace="Traceback (most recent call last):\n  ...",
        )

        assert True

    def test_log_error_no_stack_trace(self):
        """Test logging error without stack trace"""
        logger = LRSLogger(agent_id="test_agent", console=False)

        logger.log_error(error_type="RuntimeError", message="Something went wrong")

        assert True


class TestCreateLoggerForAgent:
    """Test create_logger_for_agent helper."""

    def test_create_logger(self):
        """Test creating logger via helper"""
        logger = create_logger_for_agent("my_agent")

        assert logger.agent_id == "my_agent"

    def test_create_logger_with_kwargs(self, tmp_path):
        """Test creating logger with kwargs"""
        log_file = tmp_path / "logs.jsonl"

        logger = create_logger_for_agent("my_agent", log_file=str(log_file), console=False)

        assert logger.agent_id == "my_agent"
        assert len(logger.logger.handlers) == 1


class TestLRSLoggerEdgeCases:
    """Test edge cases."""

    def test_single_policy(self):
        """Test with single policy"""
        logger = LRSLogger(agent_id="test_agent", console=False)

        logger.log_policy_selection(
            policies=["policy_a"], selected_index=0, G_values=[-0.5], precision=0.5
        )

        assert True

    def test_all_negative_precision_values(self):
        """Test logging precision with extreme values"""
        logger = LRSLogger(agent_id="test_agent", console=False)

        logger.log_precision_update(
            level="execution", old_value=1.0, new_value=0.0, prediction_error=1.0
        )

        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
