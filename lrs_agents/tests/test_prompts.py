"""Tests for prompts module."""

import pytest
from lrs.inference.prompts import (
    MetaCognitivePrompter,
    PromptContext,
    StrategyMode,
)


class TestStrategyMode:
    """Test StrategyMode enum."""

    def test_exploitation_mode(self):
        """Test exploitation mode value"""
        assert StrategyMode.EXPLOITATION.value == "exploit"

    def test_exploration_mode(self):
        """Test exploration mode value"""
        assert StrategyMode.EXPLORATION.value == "explore"

    def test_balanced_mode(self):
        """Test balanced mode value"""
        assert StrategyMode.BALANCED.value == "balanced"


class TestPromptContext:
    """Test PromptContext dataclass."""

    def test_creation(self):
        """Test creating prompt context"""
        context = PromptContext(
            precision=0.7,
            recent_errors=[0.1, 0.2],
            available_tools=["tool1", "tool2"],
            goal="Test goal",
            state={"key": "value"},
            tool_history=[{"tool": "test"}],
        )

        assert context.precision == 0.7
        assert len(context.recent_errors) == 2
        assert len(context.available_tools) == 2


class TestMetaCognitivePrompter:
    """Test MetaCognitivePrompter class."""

    def test_initialization_default(self):
        """Test default initialization"""
        prompter = MetaCognitivePrompter()

        assert prompter.high_precision_threshold == 0.7
        assert prompter.low_precision_threshold == 0.4
        assert prompter.high_error_threshold == 0.7

    def test_initialization_custom(self):
        """Test custom thresholds"""
        prompter = MetaCognitivePrompter(
            high_precision_threshold=0.8, low_precision_threshold=0.3, high_error_threshold=0.6
        )

        assert prompter.high_precision_threshold == 0.8
        assert prompter.low_precision_threshold == 0.3

    def test_generate_prompt_high_precision(self):
        """Test prompt generation with high precision"""
        prompter = MetaCognitivePrompter()

        context = PromptContext(
            precision=0.9,
            recent_errors=[0.1],
            available_tools=["api_tool"],
            goal="Fetch data",
            state={},
            tool_history=[],
        )

        prompt = prompter.generate_prompt(context)

        assert "EXPLOITATION" in prompt
        assert "0.9" in prompt
        assert "api_tool" in prompt

    def test_generate_prompt_low_precision(self):
        """Test prompt generation with low precision"""
        prompter = MetaCognitivePrompter()

        context = PromptContext(
            precision=0.2,
            recent_errors=[0.9, 0.8],
            available_tools=["api_tool", "cache_tool"],
            goal="Fetch data",
            state={},
            tool_history=[],
        )

        prompt = prompter.generate_prompt(context)

        assert "EXPLORATION" in prompt
        assert "0.2" in prompt

    def test_generate_prompt_medium_precision(self):
        """Test prompt generation with medium precision"""
        prompter = MetaCognitivePrompter()

        context = PromptContext(
            precision=0.5,
            recent_errors=[0.3, 0.4],
            available_tools=["tool1", "tool2", "tool3"],
            goal="Process data",
            state={},
            tool_history=[],
        )

        prompt = prompter.generate_prompt(context)

        assert "BALANCED" in prompt

    def test_determine_mode_exploitation(self):
        """Test mode determination for high precision"""
        prompter = MetaCognitivePrompter()

        mode = prompter._determine_mode(0.9)

        assert mode == StrategyMode.EXPLOITATION

    def test_determine_mode_exploration(self):
        """Test mode determination for low precision"""
        prompter = MetaCognitivePrompter()

        mode = prompter._determine_mode(0.2)

        assert mode == StrategyMode.EXPLORATION

    def test_determine_mode_balanced(self):
        """Test mode determination for medium precision"""
        prompter = MetaCognitivePrompter()

        mode = prompter._determine_mode(0.5)

        assert mode == StrategyMode.BALANCED

    def test_build_header(self):
        """Test header generation"""
        prompter = MetaCognitivePrompter()

        header = prompter._build_header()

        assert "Active Inference" in header
        assert "Free Energy" in header

    def test_build_precision_info(self):
        """Test precision info generation"""
        prompter = MetaCognitivePrompter()

        info = prompter._build_precision_info(0.8, StrategyMode.EXPLOITATION)

        assert "0.8" in info
        assert "HIGH" in info

    def test_build_strategy_guidance_exploitation(self):
        """Test exploitation guidance"""
        prompter = MetaCognitivePrompter()

        context = PromptContext(
            precision=0.9, recent_errors=[], available_tools=[], goal="", state={}, tool_history=[]
        )

        guidance = prompter._build_strategy_guidance(StrategyMode.EXPLOITATION, context)

        assert "EXPLOITATION" in guidance

    def test_build_strategy_guidance_exploration(self):
        """Test exploration guidance"""
        prompter = MetaCognitivePrompter()

        context = PromptContext(
            precision=0.2, recent_errors=[], available_tools=[], goal="", state={}, tool_history=[]
        )

        guidance = prompter._build_strategy_guidance(StrategyMode.EXPLORATION, context)

        assert "EXPLORATION" in guidance

    def test_build_error_analysis(self):
        """Test error analysis generation"""
        prompter = MetaCognitivePrompter()

        analysis = prompter._build_error_analysis([0.8, 0.9])

        assert "0.8" in analysis or "high" in analysis.lower()

    def test_build_tool_context(self):
        """Test tool context generation"""
        prompter = MetaCognitivePrompter()

        context = prompter._build_tool_context(["tool1", "tool2"])

        assert "tool1" in context
        assert "tool2" in context

    def test_build_goal_description(self):
        """Test goal description generation"""
        prompter = MetaCognitivePrompter()

        desc = prompter._build_goal_description("Test goal")

        assert "Test goal" in desc

    def test_build_output_format(self):
        """Test output format generation"""
        prompter = MetaCognitivePrompter()

        fmt = prompter._build_output_format()

        assert "proposal" in fmt.lower() or "policy" in fmt.lower()

    def test_build_diversity_requirements(self):
        """Test diversity requirements generation"""
        prompter = MetaCognitivePrompter()

        reqs = prompter._build_diversity_requirements()

        assert len(reqs) > 0

    def test_build_calibration_instructions(self):
        """Test calibration instructions generation"""
        prompter = MetaCognitivePrompter()

        instructions = prompter._build_calibration_instructions()

        assert len(instructions) > 0


class TestMetaCognitivePrompterEdgeCases:
    """Test edge cases for MetaCognitivePrompter."""

    def test_empty_tools_list(self):
        """Test with empty tools list"""
        prompter = MetaCognitivePrompter()

        context = PromptContext(
            precision=0.5,
            recent_errors=[],
            available_tools=[],
            goal="Test",
            state={},
            tool_history=[],
        )

        prompt = prompter.generate_prompt(context)

        assert len(prompt) > 0

    def test_empty_recent_errors(self):
        """Test with no recent errors"""
        prompter = MetaCognitivePrompter()

        context = PromptContext(
            precision=0.5,
            recent_errors=[],
            available_tools=["tool1"],
            goal="Test",
            state={},
            tool_history=[],
        )

        prompt = prompter.generate_prompt(context)

        assert len(prompt) > 0

    def test_boundary_precision_high(self):
        """Test at high precision boundary"""
        prompter = MetaCognitivePrompter()

        mode = prompter._determine_mode(0.7)

        assert mode == StrategyMode.EXPLOITATION

    def test_boundary_precision_low(self):
        """Test at low precision boundary - 0.4 is at or below threshold so EXPLORATION"""
        prompter = MetaCognitivePrompter()

        mode = prompter._determine_mode(0.4)

        # 0.4 <= 0.4 (low_precision_threshold) returns EXPLORATION
        assert mode == StrategyMode.EXPLORATION


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_create_adaptive_prompt(self):
        """Test create_adaptive_prompt convenience function"""
        from lrs.inference.prompts import create_adaptive_prompt

        prompt = create_adaptive_prompt(goal="Test goal", tools=["tool1", "tool2"], precision=0.5)

        assert len(prompt) > 0
        assert "Test goal" in prompt
        assert "tool1" in prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
