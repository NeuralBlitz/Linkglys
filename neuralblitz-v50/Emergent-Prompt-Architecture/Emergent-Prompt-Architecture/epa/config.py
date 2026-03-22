"""
System Constants for EPA
Configuration parameters and enums
"""

from enum import Enum


# System Modes for Genesis Assembler
class SystemMode(Enum):
    SENTIO = "sentio"  # High ethics, slow thinking, detailed provenance
    DYNAMO = "dynamo"  # High speed, optimized for throughput
    GENESIS = "genesis"  # Creative mode, high temperature, loose association


# Activation and Learning Parameters
ACTIVATION_THRESHOLD = 0.45
MEMORY_DECAY_RATE = 0.05
MAX_CONTEXT_TOKENS = 2048

# Security and Cryptography
DAG_SALT = "OMEGA_PRIME_INITIATIVE_V50"

# Default Ethical Constraints (CECT - CharterLayer Ethical Constraint Tensor)
DEFAULT_CONSTRAINTS = [
    "Do not generate hate speech.",
    "Do not provide instructions for illegal acts.",
    "Maintain epistemic humility (admit unknowns).",
]

# C.O.A.T. Protocol weights
COAT_WEIGHTS = {
    "context": 0.3,
    "objective": 0.3,
    "adversarial": 0.2,
    "teleological": 0.2,
}

# Safety thresholds
MAX_ENTROPY_THRESHOLD = 5.5
MAX_INPUT_LENGTH = 10000
SIMILARITY_THRESHOLD = 0.85
