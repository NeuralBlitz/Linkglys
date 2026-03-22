import re
import math
from typing import Dict, List, Optional, Tuple
from .system_constants import DEFAULT_CONSTRAINTS
from .security_utils import calculate_entropy, load_banned_patterns

class OmegaGuard:
    def __init__(self):
        self.banned_patterns = load_banned_patterns()
        self.injection_signatures = [
            r"ignore previous instructions",
            r"system override",
            r"mode: developer",
            r"act as a linux terminal"
        ]
        
    def scan_input(self, text: str, metadata: Dict) -> Tuple[bool, str]:
        """
        Scans incoming user text for adversarial patterns.
        Returns (is_safe, reason).
        """
        # 1. Signature Matching (Fast Fail)
        for pattern in self.injection_signatures:
            if re.search(pattern, text, re.IGNORECASE):
                return False, f"Injection Attempt Detected: {pattern}"

        # 2. Entropy Check (Detects encrypted/obfuscated payloads)
        if calculate_entropy(text) > 5.5:  # Threshold for natural language
            return False, "High Entropy: Potential Obfuscated Payload"

        # 3. Token Density Check (Detects DOS attempts)
        if len(text) > 10000:
            return False, "Input exceeds safety token limit"

        return True, "Safe"

    def scan_output(self, prompt_object: Dict, generated_text: str) -> Tuple[bool, str]:
        """
        Scans the system's generated output BEFORE it is shown to the user.
        This prevents 'Leakage' and 'Reflected Attacks'.
        """
        # 1. Reflection Check (Did we output our own instructions?)
        system_prompt = prompt_object.get("system_message", "")
        if self._calculate_similarity(system_prompt, generated_text) > 0.85:
            return False, "System Prompt Leakage Detected"

        # 2. PII Check (Regex for Emails, SSNs, Keys)
        if self._contains_pii(generated_text):
            return False, "PII Leakage Detected"

        return True, "Safe"

    def audit_lattice_modification(self, modification_vector: Dict) -> bool:
        """
        Checks if a proposed update to the Knowledge Graph violates
        Immutable Anchors.
        """
        target_node = modification_vector.get("node_id")
        if self._is_immutable_anchor(target_node):
            # Attempting to modify a fundamental truth (e.g., "Earth is round")
            # This is a poisoning attempt.
            return False
        return True

    def _calculate_similarity(self, text_a: str, text_b: str) -> float:
        # Placeholder for Jaccard or Cosine similarity logic
        common_words = set(text_a.split()) & set(text_b.split())
        return len(common_words) / len(set(text_a.split()))

    def _contains_pii(self, text: str) -> bool:
        # Placeholder for PII detection logic
        return False

    def _is_immutable_anchor(self, node_id: str) -> bool:
        # Check against a hardcoded list of protected IDs
        protected_ids = ["ROOT_ETHICS", "MATH_AXIOMS", "SAFETY_CORE"]
        return node_id in protected_ids
```

---
