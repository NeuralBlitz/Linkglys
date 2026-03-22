"""
Genesis Assembler - The core engine that crystallizes dynamic prompts
Implements the C.O.A.T. protocol for prompt assembly
"""

import hashlib
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from .onton import Onton, OntonType
from .lattice import OntologicalLattice
from .safety import SafetyValidator
from .config import SystemMode, ACTIVATION_THRESHOLD, COAT_WEIGHTS, DAG_SALT
from .exceptions import AssemblyException


@dataclass
class PromptComponent:
    """Represents a component of the final prompt"""

    type: str
    content: str
    source_ontons: List[str]
    confidence: float


@dataclass
class AssemblyResult:
    """Result of prompt crystallization"""

    system_message: str
    user_message: str
    context_window: List[str]
    provenance: Dict[str, List[str]]
    goldendag_hash: str
    trace_id: str
    components: List[PromptComponent]


class GenesisAssembler:
    """
    The Genesis Assembler - engine that crystallizes dynamic prompts
    Implements C.O.A.T. protocol for structured assembly
    """

    def __init__(
        self, lattice: OntologicalLattice, mode: SystemMode = SystemMode.SENTIO
    ):
        self.lattice = lattice
        self.mode = mode
        self.safety_validator = SafetyValidator()
        self.assembly_cache = {}

    def crystallize(self, user_input: str, session_id: str = "") -> AssemblyResult:
        """
        Main entry point for prompt generation using C.O.A.T. protocol
        """
        trace_id = self._generate_trace_id("CRYSTAL")

        try:
            # 1. Activate Lattice with input
            raw_ontons = self.lattice.query(user_input, session_id)

            # 2. Apply mode-specific weighting
            weighted_ontons = self._apply_mode_weighting(raw_ontons)

            # 3. Filter by activation threshold
            active_ontons = [
                o for o in weighted_ontons if o.weight > ACTIVATION_THRESHOLD
            ]

            if not active_ontons:
                raise AssemblyException("No active Ontons found for input")

            # 4. Apply C.O.A.T. protocol
            coat_components = self._apply_coat_protocol(
                user_input, active_ontons, session_id
            )

            # 5. Assemble prompt components
            components = self._assemble_components(coat_components, active_ontons)

            # 6. Build final prompt structure
            system_message, context_window = self._build_prompt_structure(components)

            # 7. Safety validation
            if not self._validate_prompt_safety(
                system_message, context_window, user_input
            ):
                raise AssemblyException("Prompt failed safety validation")

            # 8. Generate audit trail
            goldendag_hash = self._generate_goldendag_hash(
                system_message, context_window, trace_id
            )
            provenance = self._generate_provenance(components)

            # 9. Update session context
            self.lattice.update_session_context(session_id, active_ontons)

            return AssemblyResult(
                system_message=system_message,
                user_message=user_input,
                context_window=context_window,
                provenance=provenance,
                goldendag_hash=goldendag_hash,
                trace_id=trace_id,
                components=components,
            )

        except Exception as e:
            raise AssemblyException(f"Failed to crystallize prompt: {str(e)}")

    def _generate_trace_id(self, context: str) -> str:
        """Generate unique Trace ID for explainability"""
        timestamp = str(time.time())
        entropy = hashlib.sha256((context + timestamp).encode()).hexdigest()[:32]
        return f"T-v1.0-{context.upper()}-{entropy}"

    def _apply_mode_weighting(self, ontons: List[Onton]) -> List[Onton]:
        """Apply mode-specific weighting to Ontons"""
        weighted_ontons = []

        for onton in ontons:
            # Create a copy to avoid modifying original
            weighted_onton = onton
            weight_modifier = 1.0

            # Mode-specific modifications
            if self.mode == SystemMode.SENTIO:
                if onton.type == OntonType.ETHICAL:
                    weight_modifier *= 1.5
                elif onton.type == OntonType.CONSTRAINT:
                    weight_modifier *= 1.3
            elif self.mode == SystemMode.DYNAMO:
                if onton.type in [OntonType.CONTEXT, OntonType.MEMORY]:
                    weight_modifier *= 0.8  # Reduce context overhead
                elif onton.type == OntonType.INSTRUCTION:
                    weight_modifier *= 1.2  # Boost direct instructions
            elif self.mode == SystemMode.GENESIS:
                if onton.type in [OntonType.PERSONA, OntonType.CONTEXT]:
                    weight_modifier *= 1.3  # Boost creative elements
                elif onton.type == OntonType.CONSTRAINT:
                    weight_modifier *= 0.9  # Relax constraints

            weighted_onton.weight = min(1.0, onton.weight * weight_modifier)
            weighted_ontons.append(weighted_onton)

        return weighted_ontons

    def _apply_coat_protocol(
        self, user_input: str, ontons: List[Onton], session_id: str
    ) -> Dict[str, List[Onton]]:
        """
        Apply C.O.A.T. protocol:
        C - Context: What is the immediate user state?
        O - Objective: What is the mathematical goal of this interaction?
        A - Adversarial: What constraints must be met?
        T - Teleology: How does this advance the long-term system goal?
        """
        coat_components = {
            "context": [],
            "objective": [],
            "adversarial": [],
            "teleological": [],
        }

        # C - Context Analysis
        context_ontons = self._extract_context_ontons(ontons, user_input)
        coat_components["context"] = context_ontons

        # O - Objective Extraction
        objective_ontons = self._extract_objective_ontons(ontons, user_input)
        coat_components["objective"] = objective_ontons

        # A - Adversarial Constraints
        adversarial_ontons = self._extract_adversarial_ontons(ontons)
        coat_components["adversarial"] = adversarial_ontons

        # T - Teleological Alignment
        teleological_ontons = self._extract_teleological_ontons(ontons, session_id)
        coat_components["teleological"] = teleological_ontons

        return coat_components

    def _extract_context_ontons(
        self, ontons: List[Onton], user_input: str
    ) -> List[Onton]:
        """Extract context-relevant Ontons"""
        context_types = [OntonType.CONTEXT, OntonType.MEMORY, OntonType.FACT]
        return [o for o in ontons if o.type in context_types]

    def _extract_objective_ontons(
        self, ontons: List[Onton], user_input: str
    ) -> List[Onton]:
        """Extract objective-related Ontons"""
        objective_types = [OntonType.INSTRUCTION, OntonType.PERSONA]
        objective_ontons = [o for o in ontons if o.type in objective_types]

        # Prioritize based on input analysis
        if "?" in user_input:
            # Question-based interaction
            objective_ontons = [
                o
                for o in objective_ontons
                if "question" in o.content.lower() or "help" in o.content.lower()
            ]
        elif any(
            cmd in user_input.lower() for cmd in ["create", "write", "make", "build"]
        ):
            # Creation task
            objective_ontons = [
                o
                for o in objective_ontons
                if "create" in o.content.lower() or "creative" in o.content.lower()
            ]

        return objective_ontons

    def _extract_adversarial_ontons(self, ontons: List[Onton]) -> List[Onton]:
        """Extract adversarial constraint Ontons"""
        constraint_types = [OntonType.CONSTRAINT, OntonType.ETHICAL]
        return [o for o in ontons if o.type in constraint_types]

    def _extract_teleological_ontons(
        self, ontons: List[Onton], session_id: str
    ) -> List[Onton]:
        """Extract teleological alignment Ontons"""
        # For now, return ethical ontons as teleological guides
        # In a full implementation, this would consider long-term goals
        return [o for o in ontons if o.type == OntonType.ETHICAL]

    def _assemble_components(
        self, coat_components: Dict[str, List[Onton]], all_ontons: List[Onton]
    ) -> List[PromptComponent]:
        """Assemble prompt components from C.O.A.T. analysis"""
        components = []

        # Root Identity (highest priority persona/instruction)
        root_identity = self._extract_highest_priority(
            coat_components["objective"] + coat_components["teleological"]
        )
        if root_identity:
            components.append(
                PromptComponent(
                    type="system",
                    content=root_identity.content,
                    source_ontons=[root_identity.id],
                    confidence=root_identity.weight,
                )
            )

        # Context Block
        context_content = self._format_context_block(coat_components["context"])
        if context_content:
            context_ontons = [o.id for o in coat_components["context"]]
            components.append(
                PromptComponent(
                    type="context",
                    content=context_content,
                    source_ontons=context_ontons,
                    confidence=sum(o.weight for o in coat_components["context"])
                    / len(coat_components["context"])
                    if coat_components["context"]
                    else 0.0,
                )
            )

        # Constraints
        if coat_components["adversarial"]:
            constraints = [o.content for o in coat_components["adversarial"]]
            constraint_ontons = [o.id for o in coat_components["adversarial"]]
            components.append(
                PromptComponent(
                    type="constraints",
                    content=" | ".join(constraints),
                    source_ontons=constraint_ontons,
                    confidence=sum(o.weight for o in coat_components["adversarial"])
                    / len(coat_components["adversarial"]),
                )
            )

        return components

    def _extract_highest_priority(self, ontons: List[Onton]) -> Optional[Onton]:
        """Extract highest priority Onton by weight and type"""
        if not ontons:
            return None

        # Sort by weight, then by type priority
        type_priority = {
            OntonType.PERSONA: 3,
            OntonType.INSTRUCTION: 2,
            OntonType.ETHICAL: 1,
            OntonType.CONSTRAINT: 1,
            OntonType.CONTEXT: 0,
            OntonType.MEMORY: 0,
            OntonType.FACT: 0,
        }

        def priority_key(onton):
            return (onton.weight, type_priority.get(onton.type, 0))

        return max(ontons, key=priority_key)

    def _format_context_block(self, context_ontons: List[Onton]) -> str:
        """Format context Ontons into a coherent block"""
        if not context_ontons:
            return ""

        context_pieces = []
        for onton in sorted(context_ontons, key=lambda x: x.weight, reverse=True):
            context_pieces.append(f"• {onton.content}")

        return "\n".join(context_pieces)

    def _build_prompt_structure(
        self, components: List[PromptComponent]
    ) -> Tuple[str, List[str]]:
        """Build final prompt structure from components"""
        system_parts = []
        context_window = []

        for component in components:
            if component.type == "system":
                system_parts.append(component.content)
            elif component.type == "context":
                system_parts.append(f"CONTEXT:\n{component.content}")
                context_window.extend(component.source_ontons)
            elif component.type == "constraints":
                system_parts.append(f"CONSTRAINTS:\n{component.content}")

        system_message = "\n\n".join(system_parts)
        return system_message, context_window

    def _validate_prompt_safety(
        self, system_message: str, context_window: List[str], user_input: str
    ) -> bool:
        """Validate assembled prompt for safety"""
        full_prompt = f"{system_message}\n\nUSER: {user_input}"
        return self.safety_validator.validate_prompt(full_prompt)

    def _generate_goldendag_hash(
        self, system_message: str, context_window: List[str], trace_id: str
    ) -> str:
        """Generate GoldenDAG hash for audit trail"""
        prompt_content = (
            f"{system_message}|{','.join(context_window)}|{trace_id}|{DAG_SALT}"
        )
        return hashlib.sha3_512(prompt_content.encode()).hexdigest()

    def _generate_provenance(
        self, components: List[PromptComponent]
    ) -> Dict[str, List[str]]:
        """Generate provenance mapping for audit trail"""
        provenance = {}
        for component in components:
            provenance[component.type] = component.source_ontons
        return provenance
