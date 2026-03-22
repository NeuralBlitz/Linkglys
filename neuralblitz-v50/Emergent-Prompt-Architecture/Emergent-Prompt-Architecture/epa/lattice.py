"""
Ontological Lattice - The substrate of EPA
Manages the hypergraph knowledge base of Ontons
"""

import re
import math
import time
from typing import Dict, List, Set, Tuple, Any, Optional
from collections import defaultdict, deque

from .onton import Onton, OntonType
from .exceptions import LatticeException


class OntologicalLattice:
    """
    The Ontological Lattice - weighted hypergraph database
    Stores and manages Ontons with their relationships and dynamics
    """

    def __init__(self, memory_decay_rate: float = 0.05):
        self.ontons: Dict[str, Onton] = {}
        self.associations: Dict[str, Set[str]] = defaultdict(set)
        self.session_context: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.memory_decay_rate = memory_decay_rate
        self.immutable_anchors = {"ROOT_ETHICS", "MATH_AXIOMS", "SAFETY_CORE"}

    def add_onton(self, onton: Onton) -> None:
        """Add an Onton to the lattice"""
        if onton.id in self.ontons:
            raise LatticeException(f"Onton with ID {onton.id} already exists")

        self.ontons[onton.id] = onton

        # Create bidirectional associations
        for assoc_id in onton.associations:
            self.associations[onton.id].add(assoc_id)
            self.associations[assoc_id].add(onton.id)

    def get_onton(self, onton_id: str) -> Optional[Onton]:
        """Get an Onton by ID"""
        return self.ontons.get(onton_id)

    def query(self, input_text: str, session_id: str = "") -> List[Onton]:
        """
        Query the lattice with input text to activate relevant Ontons
        Returns list of activated Ontons sorted by activation weight
        """
        # Extract keywords and concepts from input
        keywords = self._extract_keywords(input_text)

        # Calculate activation scores for all Ontons
        activation_scores = []

        for onton_id, onton in self.ontons.items():
            score = self._calculate_activation_score(onton, keywords, session_id)
            if score > 0.1:  # Minimum activation threshold
                activation_scores.append((onton, score))

        # Sort by activation score (descending)
        activation_scores.sort(key=lambda x: x[1], reverse=True)

        # Apply activation to returned Ontons
        activated_ontons = []
        for onton, score in activation_scores:
            onton.activate()
            activated_ontons.append(onton)

        return activated_ontons

    def reinforce_ontons(
        self, onton_ids: List[str], feedback_score: float, reason: str = ""
    ) -> None:
        """
        Apply reinforcement to specified Ontons
        Positive feedback_score reinforces, negative weakens
        """
        for onton_id in onton_ids:
            if onton_id in self.ontons and onton_id not in self.immutable_anchors:
                self.ontons[onton_id].reinforce(feedback_score)

    def apply_decay(self) -> None:
        """Apply natural decay to all Ontons"""
        current_time = time.time()

        for onton in self.ontons.values():
            time_since_access = current_time - onton.last_accessed
            if time_since_access > 3600:  # 1 hour
                onton.decay()

    def get_associations(self, onton_id: str, depth: int = 1) -> Set[str]:
        """
        Get associated Ontons within specified depth
        Uses breadth-first search through association graph
        """
        if onton_id not in self.ontons:
            return set()

        visited = {onton_id}
        queue = deque([(onton_id, 0)])
        result = set()

        while queue:
            current_id, current_depth = queue.popleft()

            if current_depth > 0:
                result.add(current_id)

            if current_depth < depth:
                for assoc_id in self.associations[current_id]:
                    if assoc_id not in visited and assoc_id in self.ontons:
                        visited.add(assoc_id)
                        queue.append((assoc_id, current_depth + 1))

        return result

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from input text"""
        # Simple keyword extraction - can be enhanced with NLP
        words = re.findall(r"\b\w+\b", text.lower())
        # Filter out common stop words
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
        }
        return [word for word in words if word not in stop_words and len(word) > 2]

    def _calculate_activation_score(
        self, onton: Onton, keywords: List[str], session_id: str
    ) -> float:
        """
        Calculate activation score for an Onton based on input
        Considers semantic similarity, session context, and associations
        """
        base_score = 0.0

        # Semantic similarity with keywords
        onton_text = onton.content.lower()
        keyword_matches = sum(1 for keyword in keywords if keyword in onton_text)
        if keyword_matches > 0:
            base_score += (keyword_matches / len(keywords)) * 0.7

        # Session context boost
        if session_id and onton.id in self.session_context[session_id]:
            context_boost = self.session_context[session_id][onton.id]
            base_score += context_boost * 0.3

        # Association boost (activated neighbors increase score)
        assoc_boost = 0.0
        for assoc_id in onton.associations:
            if assoc_id in self.session_context.get(session_id, {}):
                assoc_boost += self.session_context[session_id][assoc_id] * 0.1

        base_score += min(assoc_boost, 0.2)

        # Apply Onton's weight and truth probability
        final_score = base_score * onton.weight * onton.truth_probability

        # Apply decay factor
        time_factor = math.exp(
            -self.memory_decay_rate * (time.time() - onton.last_accessed)
        )
        final_score *= time_factor

        return min(1.0, final_score)

    def update_session_context(
        self, session_id: str, active_ontons: List[Onton]
    ) -> None:
        """
        Update session context with currently active Ontons
        This creates temporal associations for future queries
        """
        current_time = time.time()
        context_decay = 0.9  # Decay factor for session context

        # Decay existing context
        for onton_id in list(self.session_context[session_id].keys()):
            self.session_context[session_id][onton_id] *= context_decay
            if self.session_context[session_id][onton_id] < 0.01:
                del self.session_context[session_id][onton_id]

        # Add new active Ontons
        for onton in active_ontons:
            activation_weight = onton.activate()
            self.session_context[session_id][onton.id] = activation_weight

    def get_statistics(self) -> Dict[str, Any]:
        """Get lattice statistics"""
        type_counts = defaultdict(int)
        total_weight = 0.0

        for onton in self.ontons.values():
            type_counts[onton.type.value] += 1
            total_weight += onton.weight

        return {
            "total_ontons": len(self.ontons),
            "type_distribution": dict(type_counts),
            "total_associations": sum(
                len(assoc) for assoc in self.associations.values()
            ),
            "average_weight": total_weight / len(self.ontons) if self.ontons else 0.0,
            "active_sessions": len(self.session_context),
        }

    def export_lattice(self) -> Dict[str, Any]:
        """Export lattice state for persistence"""
        return {
            "ontons": [onton.to_dict() for onton in self.ontons.values()],
            "associations": {k: list(v) for k, v in self.associations.items()},
            "session_context": dict(self.session_context),
        }

    def import_lattice(self, data: Dict[str, Any]) -> None:
        """Import lattice state from exported data"""
        # Import Ontons
        for onton_data in data.get("ontons", []):
            onton = Onton.from_dict(onton_data)
            self.ontons[onton.id] = onton

        # Import associations
        self.associations = defaultdict(set)
        for onton_id, assoc_list in data.get("associations", {}).items():
            self.associations[onton_id] = set(assoc_list)

        # Import session context
        self.session_context = defaultdict(dict)
        for session_id, context_data in data.get("session_context", {}).items():
            self.session_context[session_id] = context_data
