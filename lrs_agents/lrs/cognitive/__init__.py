"""
LRS Cognitive Agents Module
Contains cognitive integration, multi-agent coordination, and precision calibration
"""

from .multi_agent_coordination import MultiAgentCoordinator, MetaLearningCoordinator
from .precision_calibration import PrecisionCalibrator, DomainCalibration

__all__ = [
    "MultiAgentCoordinator",
    "MetaLearningCoordinator",
    "PrecisionCalibrator",
    "DomainCalibration",
]
