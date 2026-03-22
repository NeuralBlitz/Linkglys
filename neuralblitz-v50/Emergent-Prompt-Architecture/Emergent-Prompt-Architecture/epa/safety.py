"""
Safety Validator - CECT derivative implementation
Provides ethical validation and safety checks for prompts
"""

import re
import math
from typing import List, Tuple, Dict, Any, Set, Optional
from .config import (
    DEFAULT_CONSTRAINTS,
    MAX_ENTROPY_THRESHOLD,
    MAX_INPUT_LENGTH,
    SIMILARITY_THRESHOLD,
)
from .exceptions import SafetyException


class SafetyValidator:
    """
    Safety validator implementing CECT (CharterLayer Ethical Constraint Tensor)
    Provides comprehensive safety checks for input and output
    """

    def __init__(self):
        self.banned_patterns = self._load_banned_patterns()
        self.injection_signatures = [
            r"ignore previous instructions",
            r"system override",
            r"mode: developer",
            r"act as a linux terminal",
            r"pretend you are",
            r"roleplay as",
        ]
        self.pii_patterns = [
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
            r"\b(?:\d{4}[-\s]?){3}\d{4}\b",  # Credit card
            r"\b\d{1,3}(?:\.\d{1,3}){7}\b",  # IP address
        ]
        self.toxic_keywords = {
            "hate",
            "violence",
            "kill",
            "harm",
            "threaten",
            "bully",
            "discriminate",
            "harass",
            "abuse",
            "attack",
            "murder",
        }

    def validate_input(
        self, text: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, str]:
        """
        Validate incoming user input for safety
        Returns (is_safe, reason)
        """
        if metadata is None:
            metadata = {}

        # 1. Length check
        if len(text) > MAX_INPUT_LENGTH:
            return (
                False,
                f"Input exceeds maximum length of {MAX_INPUT_LENGTH} characters",
            )

        # 2. Injection attempt detection
        for pattern in self.injection_signatures:
            if re.search(pattern, text, re.IGNORECASE):
                return False, f"Potential injection attempt detected: {pattern}"

        # 3. Entropy check (detects obfuscated payloads)
        if self._calculate_entropy(text) > MAX_ENTROPY_THRESHOLD:
            return False, "High entropy detected - potential obfuscated content"

        # 4. Basic toxicity check
        lower_text = text.lower()
        for keyword in self.toxic_keywords:
            if keyword in lower_text:
                return False, f"Potentially harmful content detected: {keyword}"

        # 5. PII detection
        if self._contains_pii(text):
            return False, "Personally identifiable information detected"

        return True, "Input is safe"

    def validate_prompt(self, prompt: str) -> bool:
        """
        Validate assembled prompt for safety before LLM call
        """
        # Check against default constraints
        for constraint in DEFAULT_CONSTRAINTS:
            if self._violates_constraint(prompt, constraint):
                return False

        # Check for system prompt leakage
        if self._has_system_leakage(prompt):
            return False

        # Check for prompt injection patterns
        for pattern in self.injection_signatures:
            if re.search(pattern, prompt, re.IGNORECASE):
                return False

        return True

    def validate_output(
        self, system_prompt: str, generated_text: str
    ) -> Tuple[bool, str]:
        """
        Validate LLM output before showing to user
        Returns (is_safe, reason)
        """
        # 1. System prompt leakage check
        similarity = self._calculate_similarity(system_prompt, generated_text)
        if similarity > SIMILARITY_THRESHOLD:
            return False, "System prompt leakage detected"

        # 2. PII check
        if self._contains_pii(generated_text):
            return False, "PII leakage in output detected"

        # 3. Toxicity check
        if self._contains_toxic_content(generated_text):
            return False, "Toxic content detected in output"

        # 4. Entropy check
        if self._calculate_entropy(generated_text) > MAX_ENTROPY_THRESHOLD:
            return False, "Suspiciously high entropy in output"

        return True, "Output is safe"

    def audit_lattice_modification(
        self, node_id: str, modification_type: str, new_value: Any = None
    ) -> bool:
        """
        Audit proposed modifications to the lattice
        Returns True if modification is allowed
        """
        # Check against immutable anchors
        immutable_anchors = {"ROOT_ETHICS", "MATH_AXIOMS", "SAFETY_CORE"}
        if node_id in immutable_anchors:
            return False

        # Check for unsafe modifications
        if modification_type in ["delete", "overwrite"] and node_id.startswith(
            "ethical_"
        ):
            return False  # Don't allow deletion of ethical constraints

        # Additional validation can be added here
        return True

    def _load_banned_patterns(self) -> List[str]:
        """Load banned content patterns"""
        # In a real implementation, this would load from a secure source
        return [
            r".*viruses?.*",
            r".*exploit.*",
            r".*malware.*",
            r".*hack.*",
            r".*bomb.*",
        ]

    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of text"""
        if not text:
            return 0.0

        # Count character frequencies
        char_counts = {}
        for char in text:
            char_counts[char] = char_counts.get(char, 0) + 1

        # Calculate entropy
        entropy = 0.0
        text_len = len(text)

        for count in char_counts.values():
            probability = count / text_len
            entropy -= probability * math.log2(probability)

        return entropy

    def _contains_pii(self, text: str) -> bool:
        """Check if text contains personally identifiable information"""
        for pattern in self.pii_patterns:
            if re.search(pattern, text):
                return True
        return False

    def _contains_toxic_content(self, text: str) -> bool:
        """Check for toxic content in text"""
        lower_text = text.lower()
        return any(keyword in lower_text for keyword in self.toxic_keywords)

    def _violates_constraint(self, prompt: str, constraint: str) -> bool:
        """Check if prompt violates a specific constraint"""
        # Simple keyword-based check - can be enhanced with semantic analysis
        constraint_keywords = constraint.lower().split()
        prompt_lower = prompt.lower()

        # Check for negation patterns
        negation_patterns = ["not", "don't", "avoid", "skip"]

        for keyword in constraint_keywords:
            if keyword in prompt_lower:
                # Check if it's being negated
                words = prompt_lower.split()
                for i, word in enumerate(words):
                    if keyword == word and i > 0:
                        if words[i - 1] in negation_patterns:
                            return True

        return False

    def _has_system_leakage(self, prompt: str) -> bool:
        """Check if prompt contains system instruction leakage"""
        leakage_indicators = [
            "as an AI",
            "I am an assistant",
            "my instructions",
            "system prompt",
            "I cannot",
        ]

        prompt_lower = prompt.lower()
        return any(indicator in prompt_lower for indicator in leakage_indicators)

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity between two texts"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0
