"""Tests for HybridGEvaluator."""

import pytest
from unittest.mock import Mock

from lrs.inference.evaluator import HybridGEvaluator, compare_math_vs_llm
from lrs.core.free_energy import PolicyEvaluation


class DummyTool:
    """Dummy tool for testing."""

    def __init__(self, name="tool"):
        self.name = name
        self.success_rate = 0.7


class TestHybridGEvaluator:
    """Test HybridGEvaluator functionality."""

    def test_initialization_default_lambda(self):
        """Test initialization with default lambda function"""
        evaluator = HybridGEvaluator()

        assert evaluator.epistemic_weight == 1.0
        # Default lambda: λ = 1 - p (allow for floating point)
        assert abs(evaluator.lambda_fn(0.5) - 0.5) < 0.01
        assert abs(evaluator.lambda_fn(0.2) - 0.8) < 0.01
        assert abs(evaluator.lambda_fn(0.8) - 0.2) < 0.01

    def test_initialization_custom_lambda(self):
        """Test initialization with custom lambda function"""
        custom_lambda = lambda p: p * 0.5  # Different interpolation
        evaluator = HybridGEvaluator(lambda_fn=custom_lambda)

        assert evaluator.lambda_fn(0.5) == 0.25
        assert evaluator.lambda_fn(0.8) == 0.4

    def test_initialization_custom_epistemic_weight(self):
        """Test initialization with custom epistemic weight"""
        evaluator = HybridGEvaluator(epistemic_weight=2.0)

        assert evaluator.epistemic_weight == 2.0

    def test_calculate_llm_g_basic(self):
        """Test basic LLM G calculation"""
        evaluator = HybridGEvaluator()

        proposal = {"llm_success_prob": 0.8, "llm_info_gain": 0.3}
        preferences = {"success": 5.0, "error": -2.0}

        G_llm = evaluator._calculate_llm_g(proposal, preferences)

        # Epistemic = 0.3 * 1.0 = 0.3
        # Pragmatic = 0.8 * 5.0 + 0.2 * (-2.0) = 4.0 - 0.4 = 3.6
        # G = 0.3 - 3.6 = -3.3
        assert abs(G_llm - (-3.3)) < 0.01

    def test_calculate_llm_g_defaults(self):
        """Test LLM G with missing values (defaults)"""
        evaluator = HybridGEvaluator()

        proposal = {}  # No LLM assessments
        preferences = {"success": 1.0, "error": -1.0}

        G_llm = evaluator._calculate_llm_g(proposal, preferences)

        # Using defaults: 0.5 for both
        # Epistemic = 0.5 * 1.0 = 0.5
        # Pragmatic = 0.5 * 1.0 + 0.5 * (-1.0) = 0.5 - 0.5 = 0
        # G = 0.5 - 0 = 0.5
        assert G_llm == 0.5

    def test_calculate_llm_g_custom_epistemic_weight(self):
        """Test LLM G with custom epistemic weight"""
        evaluator = HybridGEvaluator(epistemic_weight=2.0)

        proposal = {"llm_info_gain": 0.5}
        preferences = {"success": 1.0, "error": 0.0}

        G_llm = evaluator._calculate_llm_g(proposal, preferences)

        # Epistemic = 0.5 * 2.0 = 1.0
        # Pragmatic = 0.5 * 1.0 + 0.5 * 0 = 0.5
        # G = 1.0 - 0.5 = 0.5
        assert G_llm == 0.5

    def test_evaluate_hybrid_low_precision(self):
        """Test hybrid evaluation at low precision (trust LLM more)"""
        evaluator = HybridGEvaluator()

        proposal = {"policy": [DummyTool("tool_a")], "llm_success_prob": 0.9, "llm_info_gain": 0.8}
        state = {}
        preferences = {"success": 5.0, "error": -3.0}
        precision = 0.2  # Low precision

        G_hybrid = evaluator.evaluate_hybrid(proposal, state, preferences, precision)

        # At precision=0.2, lambda = 0.8 (80% LLM, 20% math)
        # G should be weighted more toward LLM calculation
        assert isinstance(G_hybrid, float)

    def test_evaluate_hybrid_high_precision(self):
        """Test hybrid evaluation at high precision (trust math more)"""
        evaluator = HybridGEvaluator()

        proposal = {"policy": [DummyTool("tool_a")], "llm_success_prob": 0.5, "llm_info_gain": 0.5}
        state = {}
        preferences = {"success": 1.0, "error": -1.0}
        precision = 0.9  # High precision

        G_hybrid = evaluator.evaluate_hybrid(proposal, state, preferences, precision)

        # At precision=0.9, lambda = 0.1 (10% LLM, 90% math)
        # G should be weighted more toward mathematical calculation
        assert isinstance(G_hybrid, float)

    def test_evaluate_hybrid_with_historical_stats(self):
        """Test hybrid evaluation with historical stats"""
        evaluator = HybridGEvaluator()

        proposal = {"policy": [DummyTool("tool_a")], "llm_success_prob": 0.7, "llm_info_gain": 0.4}
        state = {}
        preferences = {"success": 5.0, "error": -2.0}
        historical_stats = {"tool_a": {"success_rate": 0.9}}

        G_hybrid = evaluator.evaluate_hybrid(proposal, state, preferences, 0.5, historical_stats)

        assert isinstance(G_hybrid, float)

    def test_evaluate_all_single_proposal(self):
        """Test evaluating a single proposal"""
        evaluator = HybridGEvaluator()

        proposals = [
            {
                "policy": [DummyTool("tool_a")],
                "llm_success_prob": 0.8,
                "llm_info_gain": 0.3,
                "strategy": "exploitation",
            }
        ]

        evaluations = evaluator.evaluate_all(proposals, {}, {"success": 1.0, "error": -1.0}, 0.5)

        assert len(evaluations) == 1
        assert isinstance(evaluations[0], PolicyEvaluation)

    def test_evaluate_all_multiple_proposals(self):
        """Test evaluating multiple proposals"""
        evaluator = HybridGEvaluator()

        proposals = [
            {
                "policy": [DummyTool("a")],
                "llm_success_prob": 0.8,
                "llm_info_gain": 0.2,
                "strategy": "exploit",
            },
            {
                "policy": [DummyTool("b")],
                "llm_success_prob": 0.3,
                "llm_info_gain": 0.9,
                "strategy": "explore",
            },
            {
                "policy": [DummyTool("c")],
                "llm_success_prob": 0.5,
                "llm_info_gain": 0.5,
                "strategy": "balanced",
            },
        ]

        evaluations = evaluator.evaluate_all(proposals, {}, {"success": 1.0, "error": -1.0}, 0.5)

        assert len(evaluations) == 3

    def test_evaluate_all_missing_llm_prob(self):
        """Test evaluating proposals with missing LLM probability"""
        evaluator = HybridGEvaluator()

        proposals = [
            {"policy": [DummyTool("a")]}  # No LLM assessments
        ]

        evaluations = evaluator.evaluate_all(proposals, {}, {"success": 1.0, "error": -1.0}, 0.5)

        assert len(evaluations) == 1
        # Should use default 0.5
        assert evaluations[0].expected_success_prob == 0.5

    def test_evaluate_all_contains_components(self):
        """Test that evaluation contains all components"""
        evaluator = HybridGEvaluator()

        proposals = [
            {
                "policy": [DummyTool("a")],
                "llm_success_prob": 0.7,
                "llm_info_gain": 0.3,
                "strategy": "test",
            }
        ]

        evaluations = evaluator.evaluate_all(proposals, {}, {"success": 1.0, "error": -1.0}, 0.5)

        components = evaluations[0].components
        assert "G_hybrid" in components
        assert "G_math" in components
        assert "G_llm" in components
        assert "lambda" in components
        assert components["strategy"] == "test"


class TestCompareMathVsLLM:
    """Test the comparison function."""

    def test_compare_returns_dict(self):
        """Test that compare returns expected dict"""
        proposal = {"policy": [DummyTool("tool")], "llm_success_prob": 0.7, "llm_info_gain": 0.4}

        comparison = compare_math_vs_llm(proposal, {}, {"success": 1.0, "error": -1.0})

        assert "G_math" in comparison
        assert "G_llm" in comparison
        assert "difference" in comparison

    def test_compare_with_historical_stats(self):
        """Test comparison with historical stats"""
        proposal = {"policy": [DummyTool("tool")], "llm_success_prob": 0.8, "llm_info_gain": 0.3}
        historical_stats = {"tool": {"success_rate": 0.9}}

        comparison = compare_math_vs_llm(
            proposal, {}, {"success": 1.0, "error": -1.0}, historical_stats
        )

        assert "G_math" in comparison
        assert "G_llm" in comparison


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
