"""
Onton - The fundamental semantic atom of EPA
Represents the smallest unit of meaning in the Ontological Lattice
"""

import hashlib
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class OntonType(Enum):
    """Types of Ontons in the system"""

    PERSONA = "persona"  # System identity/role
    INSTRUCTION = "instruction"  # Direct commands
    FACT = "fact"  # Verifiable information
    CONSTRAINT = "constraint"  # Rules and limitations
    ETHICAL = "ethical"  # Ethical guidelines
    MEMORY = "memory"  # Stored experiences
    CONTEXT = "context"  # Situational information


@dataclass
class Onton:
    """
    The Onton - atomic semantic unit in the EPA system
    """

    id: str
    content: str
    type: OntonType
    weight: float = 0.5
    decay_rate: float = 0.01
    associations: List[str] = field(default_factory=list)
    creation_time: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0
    truth_probability: float = 1.0
    emotional_valence: float = 0.0  # -1 (negative) to 1 (positive)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Generate ID if not provided"""
        if not self.id:
            self.id = self._generate_id()

    def _generate_id(self) -> str:
        """Generate unique ID for the Onton"""
        content_hash = hashlib.sha256(self.content.encode()).hexdigest()[:8]
        timestamp = str(int(time.time()))[-6:]
        return f"onton_{content_hash}_{timestamp}"

    def activate(self) -> float:
        """
        Activate the Onton and update its statistics
        Returns the current activation weight
        """
        self.last_accessed = time.time()
        self.access_count += 1

        # Apply decay based on time since last access
        time_since_access = time.time() - self.creation_time
        decay_factor = max(0.1, 1.0 - (self.decay_rate * time_since_access))

        return self.weight * decay_factor

    def reinforce(self, delta: float) -> None:
        """
        Reinforce the Onton with feedback
        Positive delta increases weight, negative decreases it
        """
        self.weight = max(0.0, min(1.0, self.weight + delta))
        self.truth_probability = max(
            0.0, min(1.0, self.truth_probability + delta * 0.1)
        )

    def decay(self) -> None:
        """Apply natural decay to the Onton"""
        self.weight = max(0.1, self.weight - self.decay_rate)

    def add_association(self, other_onton_id: str) -> None:
        """Add an association to another Onton"""
        if other_onton_id not in self.associations:
            self.associations.append(other_onton_id)

    def to_dict(self) -> Dict[str, Any]:
        """Convert Onton to dictionary representation"""
        return {
            "id": self.id,
            "content": self.content,
            "type": self.type.value,
            "weight": self.weight,
            "decay_rate": self.decay_rate,
            "associations": self.associations,
            "creation_time": self.creation_time,
            "last_accessed": self.last_accessed,
            "access_count": self.access_count,
            "truth_probability": self.truth_probability,
            "emotional_valence": self.emotional_valence,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Onton":
        """Create Onton from dictionary representation"""
        return cls(
            id=data["id"],
            content=data["content"],
            type=OntonType(data["type"]),
            weight=data.get("weight", 0.5),
            decay_rate=data.get("decay_rate", 0.01),
            associations=data.get("associations", []),
            creation_time=data.get("creation_time", time.time()),
            last_accessed=data.get("last_accessed", time.time()),
            access_count=data.get("access_count", 0),
            truth_probability=data.get("truth_probability", 1.0),
            emotional_valence=data.get("emotional_valence", 0.0),
            metadata=data.get("metadata", {}),
        )

    def __repr__(self) -> str:
        return f"Onton(id={self.id}, type={self.type.value}, weight={self.weight:.2f})"
