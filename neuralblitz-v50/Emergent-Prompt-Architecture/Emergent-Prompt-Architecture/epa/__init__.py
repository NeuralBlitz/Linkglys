"""
EPA Core Module - Emergent Prompt Architecture
Implements the core components: Onton, Ontological Lattice, Genesis Assembler, and Feedback Engine
"""

from .onton import Onton
from .lattice import OntologicalLattice
from .assembler import GenesisAssembler
from .safety import SafetyValidator
from .feedback import FeedbackEngine
from .exceptions import *
from .config import SystemMode

__version__ = "1.0.0"
__all__ = [
    "Onton",
    "OntologicalLattice",
    "GenesisAssembler",
    "SafetyValidator",
    "FeedbackEngine",
    "SystemMode",
]
