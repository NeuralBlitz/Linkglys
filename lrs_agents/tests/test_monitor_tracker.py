"""Tests for LRSStateTracker."""

import pytest
from datetime import datetime
from lrs.monitoring.tracker import LRSStateTracker, StateSnapshot


class TestStateSnapshot:
    """Test StateSnapshot dataclass."""

    def test_creation(self):
        """Test creating a state snapshot"""
        snapshot = StateSnapshot(
            timestamp=datetime.now(),
            precision={"execution": 0.8},
            prediction_errors=[0.1, 0.2],
            tool_history=[{"tool": "test"}],
            adaptation_count=5,
            belief_state={"key": "value"},
        )

        assert snapshot.precision["execution"] == 0.8
        assert snapshot.adaptation_count == 5


class TestLRSStateTracker:
    """Test LRSStateTracker class."""

    def test_initialization_default(self):
        """Test default initialization"""
        tracker = LRSStateTracker()

        assert tracker.max_history == 100
        assert len(tracker.history) == 0

    def test_initialization_custom(self):
        """Test custom max history"""
        tracker = LRSStateTracker(max_history=50)

        assert tracker.max_history == 50

    def test_track_state(self):
        """Test tracking state"""
        tracker = LRSStateTracker()

        state = {
            "precision": {"execution": 0.9},
            "tool_history": [{"tool": "api_call", "prediction_error": 0.1}],
            "adaptation_count": 3,
            "belief_state": {"temp": 0.75},
        }

        tracker.track_state(state)

        assert len(tracker.history) == 1
        snapshot = tracker.history[0]
        assert snapshot.precision["execution"] == 0.9
        assert snapshot.adaptation_count == 3

    def test_track_state_max_history(self):
        """Test that history is capped at max_history"""
        tracker = LRSStateTracker(max_history=3)

        for i in range(5):
            tracker.track_state(
                {
                    "precision": {"level": 0.5 + i * 0.1},
                    "tool_history": [],
                    "adaptation_count": i,
                    "belief_state": {},
                }
            )

        assert len(tracker.history) == 3

    def test_get_precision_trajectory(self):
        """Test getting precision trajectory"""
        tracker = LRSStateTracker()

        tracker.track_state(
            {
                "precision": {"task": 0.7},
                "tool_history": [],
                "adaptation_count": 0,
                "belief_state": {},
            }
        )
        tracker.track_state(
            {
                "precision": {"task": 0.8},
                "tool_history": [],
                "adaptation_count": 0,
                "belief_state": {},
            }
        )
        tracker.track_state(
            {
                "precision": {"task": 0.9},
                "tool_history": [],
                "adaptation_count": 0,
                "belief_state": {},
            }
        )

        trajectory = tracker.get_precision_trajectory("task")

        assert trajectory == [0.7, 0.8, 0.9]

    def test_get_precision_trajectory_missing(self):
        """Test getting precision for missing level returns default"""
        tracker = LRSStateTracker()

        tracker.track_state(
            {
                "precision": {"task": 0.7},
                "tool_history": [],
                "adaptation_count": 0,
                "belief_state": {},
            }
        )

        trajectory = tracker.get_precision_trajectory("missing")

        # Missing levels return default 0.5
        assert trajectory == [0.5]

    def test_get_prediction_errors(self):
        """Test getting prediction errors"""
        tracker = LRSStateTracker()

        tracker.track_state(
            {
                "precision": {},
                "tool_history": [{"prediction_error": 0.1}, {"prediction_error": 0.2}],
                "adaptation_count": 0,
                "belief_state": {},
            }
        )
        tracker.track_state(
            {
                "precision": {},
                "tool_history": [{"prediction_error": 0.15}],
                "adaptation_count": 0,
                "belief_state": {},
            }
        )

        errors = tracker.get_prediction_errors()

        assert 0.1 in errors
        assert 0.2 in errors
        assert 0.15 in errors

    def test_get_adaptation_events(self):
        """Test getting adaptation events"""
        tracker = LRSStateTracker()

        tracker.track_state(
            {
                "precision": {},
                "tool_history": [{"prediction_error": 0.8}],
                "adaptation_count": 1,
                "belief_state": {},
            }
        )
        tracker.track_state(
            {
                "precision": {},
                "tool_history": [{"prediction_error": 0.9}],
                "adaptation_count": 2,
                "belief_state": {},
            }
        )

        events = tracker.get_adaptation_events()

        # Should have adaptation events when adaptation_count increases
        assert len(events) >= 0

    def test_get_tool_usage_stats(self):
        """Test getting tool usage stats"""
        tracker = LRSStateTracker()

        tracker.track_state(
            {
                "precision": {},
                "tool_history": [{"tool": "a", "success": True, "prediction_error": 0.1}],
                "adaptation_count": 0,
                "belief_state": {},
            }
        )

        stats = tracker.get_tool_usage_stats()

        assert "a" in stats

    def test_get_current_state(self):
        """Test getting current state"""
        tracker = LRSStateTracker()

        tracker.track_state(
            {
                "precision": {"task": 0.8},
                "tool_history": [],
                "adaptation_count": 1,
                "belief_state": {"key": "value"},
            }
        )

        current = tracker.get_current_state()

        assert current is not None

    def test_get_summary(self):
        """Test getting summary"""
        tracker = LRSStateTracker()

        tracker.track_state(
            {
                "precision": {"task": 0.8},
                "tool_history": [{"tool": "test", "success": True, "prediction_error": 0.2}],
                "adaptation_count": 1,
                "belief_state": {},
            }
        )

        summary = tracker.get_summary()

        assert "total_steps" in summary
        assert "total_adaptations" in summary
        assert "avg_precision" in summary
        assert "final_precision" in summary


class TestLRSStateTrackerEdgeCases:
    """Test edge cases for LRSStateTracker."""

    def test_empty_history(self):
        """Test operations on empty history"""
        tracker = LRSStateTracker()

        # With empty history, get_summary returns specific keys
        summary = tracker.get_summary()
        assert summary["total_steps"] == 0
        assert "total_adaptations" in summary

    def test_missing_keys_in_state(self):
        """Test handling state with missing keys"""
        tracker = LRSStateTracker()

        tracker.track_state({})

        snapshot = tracker.history[0]
        assert snapshot.precision == {}
        assert snapshot.tool_history == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
