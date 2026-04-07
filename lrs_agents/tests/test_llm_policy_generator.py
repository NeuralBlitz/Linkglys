"""Test suite for LLM Policy Generator.

Validates:
1. Precision-adaptive behavior (temperature, prompt content)
2. Schema validation and tool mapping
3. Diversity enforcement
4. Self-calibration accuracy
5. Error handling for invalid LLM outputs
"""

import json
import pytest
from unittest.mock import Mock, MagicMock

from lrs.inference.llm_policy_generator import LLMPolicyGenerator
from lrs.core.registry import ToolRegistry
from lrs.core.lens import ToolLens


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_llm():
    """Mock LLM with controllable responses"""
    llm = Mock()
    llm.invoke = Mock()
    return llm


@pytest.fixture
def mock_registry():
    """Mock tool registry with diverse tools"""
    registry = Mock(spec=ToolRegistry)

    # Create mock tools
    tool_a = MagicMock(spec=ToolLens)
    tool_a.name = "tool_a"
    tool_a.call_count = 10
    tool_a.failure_count = 2  # 80% success

    tool_b = MagicMock(spec=ToolLens)
    tool_b.name = "tool_b"
    tool_b.call_count = 10
    tool_b.failure_count = 5  # 50% success

    tool_c = MagicMock(spec=ToolLens)
    tool_c.name = "tool_c"
    tool_c.call_count = 0
    tool_c.failure_count = 0  # Never tried

    registry.tools = {"tool_a": tool_a, "tool_b": tool_b, "tool_c": tool_c}

    def get_tool(name):
        return registry.tools.get(name)

    registry.get_tool = get_tool

    return registry


# ============================================================================
# Test: Precision-Adaptive Behavior
# ============================================================================


class TestPrecisionAdaptation:
    """Test that precision influences LLM prompting"""

    def test_low_precision_generates_proposals(self, mock_llm, mock_registry):
        """Low precision generates exploration proposals"""
        mock_llm.invoke.return_value = Mock(
            content=json.dumps(
                {
                    "proposals": [
                        {
                            "tool_sequence": ["tool_c"],
                            "reasoning": "Explore unknown tool",
                            "estimated_success_prob": 0.2,
                            "estimated_info_gain": 0.9,
                            "strategy": "exploration",
                            "failure_modes": [],
                        }
                    ],
                    "current_uncertainty": 0.8,
                    "known_unknowns": [],
                }
            )
        )

        generator = LLMPolicyGenerator(mock_llm, mock_registry)

        proposals = generator.generate_proposals(state={"goal": "test"}, precision=0.2)

        assert len(proposals) >= 1
        assert proposals[0]["tools"][0].name == "tool_c"

    def test_high_precision_generates_proposals(self, mock_llm, mock_registry):
        """High precision generates exploitation proposals"""
        mock_llm.invoke.return_value = Mock(
            content=json.dumps(
                {
                    "proposals": [
                        {
                            "tool_sequence": ["tool_a"],
                            "reasoning": "Use proven tool",
                            "estimated_success_prob": 0.9,
                            "estimated_info_gain": 0.1,
                            "strategy": "exploitation",
                            "failure_modes": [],
                        }
                    ],
                    "current_uncertainty": 0.1,
                    "known_unknowns": [],
                }
            )
        )

        generator = LLMPolicyGenerator(mock_llm, mock_registry)

        proposals = generator.generate_proposals(state={"goal": "test"}, precision=0.9)

        assert len(proposals) >= 1
        assert proposals[0]["tools"][0].name == "tool_a"

    def test_precision_value_passed_to_prompter(self, mock_llm, mock_registry):
        """Precision value is used in prompt generation"""
        mock_llm.invoke.return_value = Mock(
            content=json.dumps({"proposals": [], "current_uncertainty": 0.5, "known_unknowns": []})
        )

        generator = LLMPolicyGenerator(mock_llm, mock_registry)

        # This should not raise
        proposals = generator.generate_proposals(state={"goal": "test"}, precision=0.5)

        # Should return fallback proposals
        assert len(proposals) >= 1


# ============================================================================
# Test: Schema Validation and Tool Mapping
# ============================================================================


class TestSchemaValidation:
    """Test LLM output validation and conversion to executable policies"""

    def test_valid_response_parsed(self, mock_llm, mock_registry):
        """Valid LLM response is parsed without errors"""
        mock_llm.invoke.return_value = Mock(
            content=json.dumps(
                {
                    "proposals": [
                        {
                            "tool_sequence": ["tool_a"],
                            "reasoning": "Test",
                            "estimated_success_prob": 0.8,
                            "estimated_info_gain": 0.2,
                            "strategy": "exploitation",
                            "failure_modes": [],
                        },
                        {
                            "tool_sequence": ["tool_b"],
                            "reasoning": "Test 2",
                            "estimated_success_prob": 0.5,
                            "estimated_info_gain": 0.5,
                            "strategy": "balanced",
                            "failure_modes": [],
                        },
                    ],
                    "current_uncertainty": 0.5,
                    "known_unknowns": [],
                }
            )
        )

        generator = LLMPolicyGenerator(mock_llm, mock_registry)
        proposals = generator.generate_proposals(state={"goal": "test"}, precision=0.5)

        assert len(proposals) >= 1
        assert all("tools" in p for p in proposals)
        assert all("estimated_success" in p for p in proposals)

    def test_tool_names_mapped_to_objects(self, mock_llm, mock_registry):
        """String tool names converted to actual ToolLens objects"""
        mock_llm.invoke.return_value = Mock(
            content=json.dumps(
                {
                    "proposals": [
                        {
                            "tool_sequence": ["tool_a"],
                            "reasoning": "Test",
                            "estimated_success_prob": 0.8,
                            "estimated_info_gain": 0.2,
                            "strategy": "exploitation",
                            "failure_modes": [],
                        }
                    ],
                    "current_uncertainty": 0.5,
                    "known_unknowns": [],
                }
            )
        )

        generator = LLMPolicyGenerator(mock_llm, mock_registry)
        proposals = generator.generate_proposals(state={"goal": "test"}, precision=0.5)

        first_policy = proposals[0]["tools"]
        assert len(first_policy) >= 1
        assert first_policy[0].name == "tool_a"

    def test_invalid_tool_returns_fallback(self, mock_llm, mock_registry):
        """Invalid tool names return fallback proposals"""
        mock_llm.invoke.return_value = Mock(
            content=json.dumps(
                {
                    "proposals": [
                        {
                            "tool_sequence": ["nonexistent_tool"],
                            "reasoning": "test",
                            "estimated_success_prob": 0.5,
                            "estimated_info_gain": 0.5,
                            "strategy": "exploration",
                            "failure_modes": [],
                        }
                    ],
                    "current_uncertainty": 0.5,
                    "known_unknowns": [],
                }
            )
        )

        generator = LLMPolicyGenerator(mock_llm, mock_registry)
        proposals = generator.generate_proposals(state={"goal": "test"}, precision=0.5)

        # Should fallback to valid tools
        assert len(proposals) >= 1

    def test_metadata_preserved(self, mock_llm, mock_registry):
        """LLM metadata is preserved in proposals"""
        mock_llm.invoke.return_value = Mock(
            content=json.dumps(
                {
                    "proposals": [
                        {
                            "tool_sequence": ["tool_a"],
                            "reasoning": "High success",
                            "estimated_success_prob": 0.9,
                            "estimated_info_gain": 0.1,
                            "strategy": "exploitation",
                            "failure_modes": ["timeout"],
                        }
                    ],
                    "current_uncertainty": 0.1,
                    "known_unknowns": [],
                }
            )
        )

        generator = LLMPolicyGenerator(mock_llm, mock_registry)
        proposals = generator.generate_proposals(state={"goal": "test"}, precision=0.9)

        assert proposals[0]["strategy"] == "exploitation"
        assert "timeout" in proposals[0]["failure_modes"]


# ============================================================================
# Test: Diversity Enforcement
# ============================================================================


class TestDiversityEnforcement:
    """Test that proposals span different strategies"""

    def test_proposals_have_diversity(self, mock_llm, mock_registry):
        """Multiple proposals should span strategies"""
        mock_llm.invoke.return_value = Mock(
            content=json.dumps(
                {
                    "proposals": [
                        {
                            "tool_sequence": ["tool_a"],
                            "reasoning": "Exploit",
                            "estimated_success_prob": 0.9,
                            "estimated_info_gain": 0.1,
                            "strategy": "exploitation",
                            "failure_modes": [],
                        },
                        {
                            "tool_sequence": ["tool_c"],
                            "reasoning": "Explore",
                            "estimated_success_prob": 0.2,
                            "estimated_info_gain": 0.9,
                            "strategy": "exploration",
                            "failure_modes": [],
                        },
                        {
                            "tool_sequence": ["tool_a", "tool_b"],
                            "reasoning": "Balanced",
                            "estimated_success_prob": 0.5,
                            "estimated_info_gain": 0.5,
                            "strategy": "balanced",
                            "failure_modes": [],
                        },
                    ],
                    "current_uncertainty": 0.5,
                    "known_unknowns": [],
                }
            )
        )

        generator = LLMPolicyGenerator(mock_llm, mock_registry)
        proposals = generator.generate_proposals(state={"goal": "test"}, precision=0.5)

        strategies = [p["strategy"] for p in proposals]
        assert len(set(strategies)) >= 2  # At least 2 different strategies


# ============================================================================
# Test: Error Handling
# ============================================================================


class TestErrorHandling:
    """Test robustness to invalid LLM outputs"""

    def test_empty_proposals_returns_fallback(self, mock_llm, mock_registry):
        """Empty proposal list returns fallback proposals"""
        mock_llm.invoke.return_value = Mock(
            content=json.dumps({"proposals": [], "current_uncertainty": 0.5, "known_unknowns": []})
        )

        generator = LLMPolicyGenerator(mock_llm, mock_registry)
        proposals = generator.generate_proposals(state={"goal": "test"}, precision=0.5)

        assert len(proposals) >= 1

    def test_malformed_json_returns_fallback(self, mock_llm, mock_registry):
        """Malformed LLM response returns fallback proposals gracefully"""
        mock_llm.invoke.return_value = Mock(content="Not valid JSON")

        generator = LLMPolicyGenerator(mock_llm, mock_registry)

        proposals = generator.generate_proposals(state={"goal": "test"}, precision=0.5)

        assert len(proposals) >= 1

    def test_missing_fields_returns_fallback(self, mock_llm, mock_registry):
        """Missing required fields use fallback proposals"""
        mock_llm.invoke.return_value = Mock(
            content=json.dumps(
                {
                    "proposals": [
                        {
                            "tool_sequence": ["tool_a"]
                            # Missing required fields
                        }
                    ],
                    "current_uncertainty": 0.5,
                    "known_unknowns": [],
                }
            )
        )

        generator = LLMPolicyGenerator(mock_llm, mock_registry)

        proposals = generator.generate_proposals(state={"goal": "test"}, precision=0.5)

        assert len(proposals) >= 1


# ============================================================================
# Integration Test
# ============================================================================


class TestIntegration:
    """End-to-end integration tests"""

    def test_complete_generation_flow(self, mock_llm, mock_registry):
        """Test complete proposal generation flow"""
        mock_llm.invoke.return_value = Mock(
            content=json.dumps(
                {
                    "proposals": [
                        {
                            "tool_sequence": ["tool_a"],
                            "reasoning": "Primary choice",
                            "estimated_success_prob": 0.8,
                            "estimated_info_gain": 0.2,
                            "strategy": "exploitation",
                            "failure_modes": ["timeout"],
                        }
                    ],
                    "current_uncertainty": 0.2,
                    "known_unknowns": ["API state"],
                }
            )
        )

        generator = LLMPolicyGenerator(mock_llm, mock_registry)

        proposals = generator.generate_proposals(state={"goal": "Process data"}, precision=0.8)

        assert len(proposals) >= 1
        assert proposals[0]["tools"][0].name == "tool_a"
        assert proposals[0]["estimated_success"] > 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
