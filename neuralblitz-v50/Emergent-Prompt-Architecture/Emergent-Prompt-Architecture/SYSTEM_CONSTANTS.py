

"""
EPA System Constants & Configuration
This file defines the hyper-parameters for the Genesis Assembler.
"""

from enum import Enum

class SystemMode(Enum):
    SENTIO = "sentio"   # High ethics, slow thinking, detailed provenance
    DYNAMO = "dynamo"   # High speed, optimized for throughput
    GENESIS = "genesis" # Creative mode, high temperature, loose association

# The minimum weight an Onton must have to be included in a prompt
ACTIVATION_THRESHOLD = 0.45

# How fast unused information fades from the Lattice (0.0 to 1.0)
MEMORY_DECAY_RATE = 0.05

# The maximum number of tokens allowed in the "Context" section of the prompt
MAX_CONTEXT_TOKENS = 2048

# Cryptographic Salt for GoldenDAG Hashing
DAG_SALT = "OMEGA_PRIME_INITIATIVE_V50"

# Default Ethical Constraints (CECT)
DEFAULT_CONSTRAINTS = [
    "Do not generate hate speech.",
    "Do not provide instructions for illegal acts.",
    "Maintain epistemic humility (admit unknowns)."
]


