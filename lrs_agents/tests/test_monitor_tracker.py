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
            "prediction_errors": [0.1],
            "tool_history": [{"tool": "api_call"}],
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
                    "prediction_errors": [0.1],
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
                "prediction_errors": [],
                "tool_history": [],
                "adaptation_count": 0,
                "belief_state": {},
            }
        )
        tracker.track_state(
            {
                "precision": {"task": 0.8},
                "prediction_errors": [],
                "tool_history": [],
                "adaptation_count": 0,
                "belief_state": {},
            }
        )
        tracker.track_state(
            {
                "precision": {"task": 0.9},
                "prediction_errors": [],
                "tool_history": [],
                "adaptation_count": 0,
                "belief_state": {},
            }
        )

        trajectory = tracker.get_precision_trajectory("task")

        assert trajectory == [0.7, 0.8, 0.9]

    def test_get_precision_trajectory_missing(self):
        """Test getting precision for missing level"""
        tracker = LRSStateTracker()

        tracker.track_state(
            {
                "precision": {"task": 0.7},
                "prediction_errors": [],
                "tool_history": [],
                "adaptation_count": 0,
                "belief_state": {},
            }
        )

        trajectory = tracker.get_precision_trajectory("missing")

        assert trajectory == []

    def test_get_prediction_error_trajectory(self):
        """Test getting prediction error trajectory"""
        tracker = LRSStateTracker()

        tracker.track_state(
            {
                "precision": {},
                "prediction_errors": [0.1, 0.2],
                "tool_history": [],
                "adaptation_count": 0,
                "belief_state": {},
            }
        )
        tracker.track_state(
            {
                "precision": {},
                "prediction_errors": [0.15],
                "tool_history": [],
                "adaptation_count": 0,
                "belief_state": {},
            }
        )

        trajectory = tracker.get_prediction_error_trajectory()

        assert trajectory == [0.1, 0.2, 0.15]

    def test_get_adaptation_events(self):
        """Test getting adaptation events"""
        tracker = LRSStateTracker()

        tracker.track_state(
            {
                "precision": {},
                "prediction_errors": [],
                "tool_history": [],
                "adaptation_count": 1,
                "belief_state": {},
            }
        )
        tracker.track_state(
            {
                "precision": {},
                "prediction_errors": [],
                "tool_history": [],
                "adaptation_count": 2,
                "belief_state": {},
            }
        )
        tracker.track_state(
            {
                "precision": {},
                "prediction_errors": [],
                "tool_history": [],
                "adaptation_count": 2,
                "belief_state": {},
            }
        )

        events = tracker.get_adaptation_events()

        assert len(events) == 2

    def test_get_tool_execution_history(self):
        """Test getting tool execution history"""
        tracker = LRSStateTracker()

        tracker.track_state(
            {
                "precision": {},
                "prediction_errors": [],
                "tool_history": [{"tool": "a", "success": True}],
                "adaptation_count": 0,
                "belief_state": {},
            }
        )
        tracker.track_state(
            {
                "precision": {},
                "prediction_errors": [],
                "tool_history": [{"tool": "b", "success": False}],
                "adaptation_count": 0,
                "belief_state": {},
            }
        )

        history = tracker.get_tool_execution_history()

        assert len(history) == 2
        assert history[0]["tool"] == "a"
        assert history[1]["tool"] == "b"

    def test_get_statistics(self):
        """Test getting statistics"""
        tracker = LRSStateTracker()

        tracker.track_state(
            {
                "precision": {"task": 0.7},
                "prediction_errors": [0.3],
                "tool_history": [],
                "adaptation_count": 1,
                "belief_state": {},
            }
        )
        tracker.track_state(
            {
                "precision": {"task": 0.8},
                "prediction_errors": [0.2],
                "tool_history": [],
                "adaptation_count": 2,
                "belief_state": {},
            }
        )

        stats = tracker.get_statistics()

        assert stats["total_snapshots"] == 2
        assert stats["total_adaptations"] == 3
        assert stats["avg_prediction_error"] == 0.25

    def test_clear_history(self):
        """Test clearing history"""
        tracker = LRSStateTracker()

        tracker.track_state(
            {
                "precision": {},
                "prediction_errors": [],
                "tool_history": [],
                "adaptation_count": 0,
                "belief_state": {},
            }
        )
        tracker.clear_history()

        assert len(tracker.history) == 0

    def test_export_json(self):
        """Test exporting to JSON"""
        tracker = LRSStateTracker()

        tracker.track_state(
            {
                "precision": {"task": 0.8},
                "prediction_errors": [0.2],
                "tool_history": [{"tool": "test"}],
                "adaptation_count": 1,
                "belief_state": {"key": "value"},
            }
        )

        json_str = tracker.to_json()

        assert "precision" in json_str
        assert "task" in json_str


class TestLRSStateTrackerEdgeCases:
    """Test edge cases for LRSStateTracker."""

    def test_empty_history(self):
        """Test operations on empty history"""
        tracker = LRSStateTracker()

        assert tracker.get_precision_trajectory("task") == []
        assert tracker.get_adaptation_events() == []
        assert tracker.get_tool_execution_history() == []

    def test_missing_keys_in_state(self):
        """Test handling state with missing keys"""
        tracker = LRSStateTracker()

        tracker.track_state({})

        snapshot = tracker.history[0]
        assert snapshot.precision == {}
        assert snapshot.prediction_errors == []
        assert snapshot.tool_history == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
