"""
Feedback Engine - Implements recursive learning and feedback mechanisms
Handles user feedback and system self-reflection for continuous improvement
"""

import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .onton import Onton, OntonType
from .lattice import OntologicalLattice
from .assembler import AssemblyResult
from .exceptions import TraceException


class FeedbackType(Enum):
    """Types of feedback supported"""

    USER_EXPLICIT = "user_explicit"  # Direct user feedback
    USER_IMPLICIT = "user_implicit"  # Inferred from user behavior
    SYSTEM_SELF = "system_self"  # System self-reflection
    PERFORMANCE = "performance"  # Performance metrics


@dataclass
class FeedbackSignal:
    """Represents a feedback signal for learning"""

    trace_id: str
    feedback_type: FeedbackType
    score: float  # -1.0 to 1.0
    reason: str
    timestamp: float
    metadata: Dict[str, Any]
    affected_ontons: List[str]
    session_id: str = ""


class FeedbackEngine:
    """
    Feedback Engine - handles recursive learning and system improvement
    Implements feedback loops for both user and system-based learning
    """

    def __init__(self, lattice: OntologicalLattice):
        self.lattice = lattice
        self.feedback_history: List[FeedbackSignal] = []
        self.learning_rate = 0.1
        self.decay_factor = 0.95

    def process_user_feedback(
        self,
        trace_id: str,
        feedback_score: float,
        reason: str = "",
        session_id: str = "",
    ) -> Dict[str, Any]:
        """
        Process explicit user feedback for a previous interaction
        """
        if not -1.0 <= feedback_score <= 1.0:
            raise TraceException("Feedback score must be between -1.0 and 1.0")

        # Find the assembly result for this trace
        affected_ontons = self._find_ontons_by_trace_id(trace_id)

        # Create feedback signal
        feedback = FeedbackSignal(
            trace_id=trace_id,
            feedback_type=FeedbackType.USER_EXPLICIT,
            score=feedback_score,
            reason=reason,
            timestamp=time.time(),
            metadata={"source": "user_explicit"},
            affected_ontons=affected_ontons,
            session_id=session_id,
        )

        # Apply learning
        learning_result = self._apply_feedback(feedback)

        # Store feedback
        self.feedback_history.append(feedback)

        return {
            "status": "feedback_applied",
            "onton_updates": learning_result,
            "affected_count": len(affected_ontons),
            "feedback_id": len(self.feedback_history),
        }

    def infer_implicit_feedback(
        self, user_behavior: Dict[str, Any], session_id: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        Infer implicit feedback from user behavior patterns
        """
        # Analyze user behavior patterns
        feedback_signals = []

        # Check for repeated queries (confusion)
        if user_behavior.get("repeated_queries", 0) > 2:
            feedback_signals.append(
                FeedbackSignal(
                    trace_id=user_behavior.get("last_trace_id", ""),
                    feedback_type=FeedbackType.USER_IMPLICIT,
                    score=-0.3,
                    reason="User repeated queries - potential confusion",
                    timestamp=time.time(),
                    metadata={"behavior": "repeated_queries"},
                    affected_ontons=self._find_ontons_by_trace_id(
                        user_behavior.get("last_trace_id", "")
                    ),
                    session_id=session_id,
                )
            )

        # Check for rapid acceptance (helpful response)
        if user_behavior.get("rapid_acceptance", False):
            feedback_signals.append(
                FeedbackSignal(
                    trace_id=user_behavior.get("last_trace_id", ""),
                    feedback_type=FeedbackType.USER_IMPLICIT,
                    score=0.4,
                    reason="User rapidly accepted response",
                    timestamp=time.time(),
                    metadata={"behavior": "rapid_acceptance"},
                    affected_ontons=self._find_ontons_by_trace_id(
                        user_behavior.get("last_trace_id", "")
                    ),
                    session_id=session_id,
                )
            )

        # Apply feedback if any signals were generated
        if feedback_signals:
            results = []
            for feedback in feedback_signals:
                result = self._apply_feedback(feedback)
                results.append(result)
                self.feedback_history.append(feedback)

            return {
                "status": "implicit_feedback_applied",
                "signals_processed": len(feedback_signals),
                "results": results,
            }

        return None

    def system_self_reflection(
        self, assembly_result: AssemblyResult, performance_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Perform system self-reflection based on performance metrics
        """
        feedback_signals = []

        # Analyze response length efficiency
        if performance_metrics.get("response_efficiency", 1.0) < 0.5:
            feedback_signals.append(
                FeedbackSignal(
                    trace_id=assembly_result.trace_id,
                    feedback_type=FeedbackType.SYSTEM_SELF,
                    score=-0.2,
                    reason="Low response efficiency detected",
                    timestamp=time.time(),
                    metadata={
                        "metric": "response_efficiency",
                        "value": performance_metrics.get("response_efficiency"),
                    },
                    affected_ontons=assembly_result.context_window,
                )
            )

        # Analyze component confidence
        avg_confidence = sum(c.confidence for c in assembly_result.components) / len(
            assembly_result.components
        )
        if avg_confidence < 0.6:
            feedback_signals.append(
                FeedbackSignal(
                    trace_id=assembly_result.trace_id,
                    feedback_type=FeedbackType.SYSTEM_SELF,
                    score=-0.1,
                    reason="Low component confidence in assembly",
                    timestamp=time.time(),
                    metadata={"metric": "avg_confidence", "value": avg_confidence},
                    affected_ontons=[
                        onton_id
                        for component in assembly_result.components
                        for onton_id in component.source_ontons
                    ],
                )
            )

        # Apply self-reflection feedback
        results = []
        for feedback in feedback_signals:
            result = self._apply_feedback(feedback)
            results.append(result)
            self.feedback_history.append(feedback)

        return {
            "status": "self_reflection_complete",
            "signals_generated": len(feedback_signals),
            "results": results,
        }

    def get_feedback_statistics(self) -> Dict[str, Any]:
        """Get statistics about feedback and learning"""
        if not self.feedback_history:
            return {
                "total_feedback": 0,
                "feedback_types": {},
                "average_score": 0.0,
                "learning_trend": "stable",
            }

        # Calculate statistics
        total_feedback = len(self.feedback_history)
        feedback_by_type = {}
        scores = []

        for feedback in self.feedback_history:
            feedback_type = feedback.feedback_type.value
            feedback_by_type[feedback_type] = feedback_by_type.get(feedback_type, 0) + 1
            scores.append(feedback.score)

        # Calculate learning trend (recent vs overall)
        recent_feedback = (
            self.feedback_history[-10:]
            if len(self.feedback_history) >= 10
            else self.feedback_history
        )
        recent_avg = sum(f.score for f in recent_feedback) / len(recent_feedback)
        overall_avg = sum(scores) / len(scores)

        if recent_avg > overall_avg + 0.1:
            trend = "improving"
        elif recent_avg < overall_avg - 0.1:
            trend = "declining"
        else:
            trend = "stable"

        return {
            "total_feedback": total_feedback,
            "feedback_types": feedback_by_type,
            "average_score": overall_avg,
            "learning_trend": trend,
            "recent_average": recent_avg,
        }

    def _find_ontons_by_trace_id(self, trace_id: str) -> List[str]:
        """
        Find Ontons associated with a specific trace ID
        In a full implementation, this would query a trace database
        """
        # For now, return empty list - would need trace tracking system
        return []

    def _apply_feedback(self, feedback: FeedbackSignal) -> Dict[str, str]:
        """
        Apply feedback to affected Ontons in the lattice
        """
        updates = {}

        for onton_id in feedback.affected_ontons:
            onton = self.lattice.get_onton(onton_id)
            if onton and onton_id not in self.lattice.immutable_anchors:
                # Calculate reinforcement value
                reinforcement = feedback.score * self.learning_rate

                # Apply feedback based on type
                if feedback.feedback_type == FeedbackType.USER_EXPLICIT:
                    onton.reinforce(reinforcement)
                    updates[onton_id] = f"reinforced by {reinforcement:.3f}"
                elif feedback.feedback_type == FeedbackType.USER_IMPLICIT:
                    # Weaker reinforcement for implicit feedback
                    onton.reinforce(reinforcement * 0.5)
                    updates[onton_id] = (
                        f"implicitly reinforced by {reinforcement * 0.5:.3f}"
                    )
                elif feedback.feedback_type == FeedbackType.SYSTEM_SELF:
                    # Self-reflection feedback
                    onton.reinforce(reinforcement * 0.3)
                    updates[onton_id] = f"self-reflected by {reinforcement * 0.3:.3f}"

        return updates

    def cleanup_old_feedback(self, max_age_days: int = 30) -> int:
        """
        Clean up old feedback signals to prevent memory bloat
        """
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 3600

        initial_count = len(self.feedback_history)
        self.feedback_history = [
            feedback
            for feedback in self.feedback_history
            if current_time - feedback.timestamp < max_age_seconds
        ]

        return initial_count - len(self.feedback_history)
