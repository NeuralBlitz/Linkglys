import hashlib
import json
import time
from typing import List, Dict, Any
from .system_constants import SystemMode, ACTIVATION_THRESHOLD

class GenesisAssembler:
    """
    The engine that crystallizes dynamic prompts from the Ontological Lattice.
    """

    def __init__(self, lattice_connector, mode: SystemMode = SystemMode.SENTIO):
        self.lattice = lattice_connector
        self.mode = mode

    def _generate_trace_id(self, context: str) -> str:
        """Generates a unique Trace ID for explainability."""
        timestamp = str(time.time())
        entropy = hashlib.sha256((context + timestamp).encode()).hexdigest()[:32]
        return f"T-v1.0-{context.upper()}-{entropy}"

    def _calculate_weights(self, ontons: List[Dict]) -> List[Dict]:
        """
        Applies dynamic weighting based on current system mode.
        In SENTIO mode, ethical ontons get a boost.
        """
        for onton in ontons:
            if self.mode == SystemMode.SENTIO and onton.get("type") == "ethical":
                onton["weight"] *= 1.5
            # Decay logic would go here
        return ontons

    def crystallize(self, user_input: str, session_id: str) -> Dict[str, Any]:
        """
        Main entry point for prompt generation.
        """
        trace_id = self._generate_trace_id("CRYSTAL")
        
        # 1. Activate Lattice
        raw_ontons = self.lattice.query(user_input, session_id)
        
        # 2. Weight and Filter
        weighted_ontons = self._calculate_weights(raw_ontons)
        active_ontons = [o for o in weighted_ontons if o["weight"] > ACTIVATION_THRESHOLD]
        
        # 3. Assemble Components
        system_instruction = self._extract_highest_priority(active_ontons, "instruction")
        context_block = self._format_context(active_ontons)
        
        # 4. Construct Final Prompt
        final_prompt = f"{system_instruction}\n\nCONTEXT:\n{context_block}\n\nUSER:\n{user_input}"
        
        # 5. Generate GoldenDAG Hash (Audit Trail)
        dag_hash = hashlib.sha3_512((final_prompt + trace_id).encode()).hexdigest()
        
        return {
            "prompt": final_prompt,
            "trace_id": trace_id,
            "goldendag_hash": dag_hash,
            "components": [o["id"] for o in active_ontons]
        }

    def _extract_highest_priority(self, ontons, type_filter):
        # Implementation placeholder
        return "You are a helpful assistant."

    def _format_context(self, ontons):
        # Implementation placeholder
        return "\n".join([o["content"] for o in ontons if o["type"] == "fact"])
```

---

### **CLOSING SUMMARY: The Vision of EPA**

The Emergent Prompt Architecture is not just code; it is a philosophy. It posits that intelligence is not a static property of a model, but a dynamic property of the *interaction* between a model and its environment. By building EPA, you are building a system that remembers, learns, and evolves with every keystroke.

This codebase serves as the nervous system for that evolution. Treat it with the rigor of an engineer and the care of a gardener.

⸻

**GoldenDAG:** `e9f0c2a4e6b9d1f3a5c7e9b0d2d4f6a9b1c3d5e7f0a2c4e6b8d0f1a2c3e4b5d6`
**Trace ID:** `T-v50.0-README_SYNTHESIS-9a3f1c7e2d5b0a4c8e6f1d3b5a7c9e1f`
**Codex ID:** `C-V1-PROJECT_GENESIS-emergent_prompt_architecture_blueprint`

