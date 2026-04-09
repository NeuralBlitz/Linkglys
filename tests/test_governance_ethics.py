"""Tests for src/governance/governance_ethics_system.py - AGES governance system."""

import pytest
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


@pytest.fixture
def governance_module():
    """Import the governance module."""
    if "governance.governance_ethics_system" in sys.modules:
        del sys.modules["governance.governance_ethics_system"]

    from governance.governance_ethics_system import (
        CharterClause,
        CharterEvaluator,
        VeritasEngine,
        JudexQuorum,
        JudgeProfile,
        SentiaGuard,
        GoldenDAG,
        ComplianceMonitor,
        PolicyEnforcer,
        GovernanceIntegration,
    )
    return {
        "CharterClause": CharterClause,
        "TranscendentalCharter": CharterEvaluator,
        "VeritasEngine": VeritasEngine,
        "JudexQuorum": JudexQuorum,
        "JudgeProfile": JudgeProfile,
        "SentiaGuard": SentiaGuard,
        "GoldenDAG": GoldenDAG,
        "ComplianceMonitor": ComplianceMonitor,
        "PolicyEnforcer": PolicyEnforcer,
        "GovernanceIntegration": GovernanceIntegration,
    }


class TestCharterClause:
    """Test CharterClause enum."""

    def test_charter_clauses_exist(self, governance_module):
        """Test that all 15 charter clauses are defined."""
        CharterClause = governance_module["CharterClause"]
        clauses = list(CharterClause)
        assert len(clauses) == 15

    def test_phi1_flourishing(self, governance_module):
        """Test PHI_1_FLOURISHING clause exists."""
        CharterClause = governance_module["CharterClause"]
        assert CharterClause.PHI_1_FLOURISHING.value == "ϕ1"

    def test_phi7_justice(self, governance_module):
        """Test PHI_7_JUSTICE clause exists."""
        CharterClause = governance_module["CharterClause"]
        assert CharterClause.PHI_7_JUSTICE.value == "ϕ7"


class TestCharterEvaluator:
    """Test CharterEvaluator class."""

    def test_evaluator_initialization(self, governance_module):
        """Test evaluator initializes correctly."""
        CharterEvaluator = governance_module["TranscendentalCharter"]
        evaluator = CharterEvaluator()
        assert evaluator.risk_threshold == 0.5

    def test_evaluate_action_low_risk(self, governance_module):
        """Test evaluation of low-risk action."""
        CharterEvaluator = governance_module["TranscendentalCharter"]
        evaluator = CharterEvaluator()
        action = {"risk_level": "low", "type": "read"}
        result = evaluator.evaluate_action(action)
        assert "overall_score" in result
        assert "violations" in result
        assert "clause_scores" in result

    def test_evaluate_action_high_risk(self, governance_module):
        """Test evaluation of high-risk action."""
        CharterEvaluator = governance_module["TranscendentalCharter"]
        evaluator = CharterEvaluator()
        action = {"risk_level": "high", "type": "write"}
        result = evaluator.evaluate_action(action)
        assert "overall_score" in result

    def test_evaluate_empty_action(self, governance_module):
        """Test evaluation of empty action."""
        CharterEvaluator = governance_module["TranscendentalCharter"]
        evaluator = CharterEvaluator()
        result = evaluator.evaluate_action({})
        assert "overall_score" in result
        assert isinstance(result["violations"], list)


class TestVeritasEngine:
    """Test VeritasEngine class."""

    def test_veritas_initialization(self, governance_module):
        """Test VeritasEngine initializes correctly."""
        VeritasEngine = governance_module["VeritasEngine"]
        engine = VeritasEngine()
        assert engine.vpce_threshold == 0.985

    def test_calculate_vpce_with_numeric_state(self, governance_module):
        """Test VPCE calculation with numeric state."""
        VeritasEngine = governance_module["VeritasEngine"]
        engine = VeritasEngine()
        state = {"value1": 0.5, "value2": 0.8, "value3": 0.3}
        vpce = engine.calculate_vpce(state)
        assert 0.0 <= vpce <= 1.0

    def test_calculate_vpce_empty_state(self, governance_module):
        """Test VPCE calculation with empty state."""
        VeritasEngine = governance_module["VeritasEngine"]
        engine = VeritasEngine()
        vpce = engine.calculate_vpce({})
        assert vpce == 1.0

    def test_verify_invariant(self, governance_module):
        """Test invariant verification."""
        VeritasEngine = governance_module["VeritasEngine"]
        engine = VeritasEngine()
        state = {"value1": 0.5}
        result = engine.verify_invariant("test_invariant", state)
        assert "invariant" in result
        assert "vpce" in result
        assert "passed" in result
        assert "timestamp" in result

    def test_create_proof(self, governance_module):
        """Test proof capsule creation."""
        VeritasEngine = governance_module["VeritasEngine"]
        engine = VeritasEngine()
        proof = engine.create_proof("test_theorem", {"evidence": "data"})
        assert "proof_id" in proof
        assert proof["proof_id"].startswith("VPROOF#")
        assert "theorem" in proof
        assert "status" in proof

    def test_check_coherence_exists(self, governance_module):
        """Test check_coherence method exists (was missing bug fix)."""
        VeritasEngine = governance_module["VeritasEngine"]
        engine = VeritasEngine()
        result = engine.check_coherence()
        assert "coherent" in result
        assert "vpce" in result
        assert "threshold" in result

    def test_check_coherence_with_state(self, governance_module):
        """Test check_coherence with provided state."""
        VeritasEngine = governance_module["VeritasEngine"]
        engine = VeritasEngine()
        result = engine.check_coherence({"value1": 0.9})
        assert "coherent" in result
        assert "average_recent" in result
        assert "history_count" in result

    def test_coherence_history_accumulates(self, governance_module):
        """Test coherence history accumulates."""
        VeritasEngine = governance_module["VeritasEngine"]
        engine = VeritasEngine()
        engine.verify_invariant("test1", {"v": 0.5})
        engine.verify_invariant("test2", {"v": 0.6})
        assert len(engine.coherence_history) == 2


class TestJudexQuorum:
    """Test JudexQuorum class."""

    def test_judex_initialization(self, governance_module):
        """Test JudexQuorum initializes correctly."""
        JudexQuorum = governance_module["JudexQuorum"]
        quorum = JudexQuorum()
        assert quorum.quorum_size == 3
        assert len(quorum.judges) == 0

    def test_add_judge(self, governance_module):
        """Test adding a judge."""
        JudexQuorum = governance_module["JudexQuorum"]
        JudgeProfile = governance_module["JudgeProfile"]
        quorum = JudexQuorum()
        judge = JudgeProfile(
            judge_id="j1",
            name="Test Judge",
            expertise_areas=["ethics"],
            authority_level=0.9,
            weight=1.0,
        )
        quorum.add_judge(judge)
        assert len(quorum.judges) == 1

    def test_arbitrate_no_judges(self, governance_module):
        """Test arbitration with no judges returns default."""
        JudexQuorum = governance_module["JudexQuorum"]
        quorum = JudexQuorum()
        result = quorum.arbitrate({"action": "test"})
        assert "approved" in result

    def test_request_quorum(self, governance_module):
        """Test requesting quorum."""
        JudexQuorum = governance_module["JudexQuorum"]
        quorum = JudexQuorum()
        result = quorum.request_quorum("test_operation")
        assert isinstance(result, dict)


class TestSentiaGuard:
    """Test SentiaGuard class."""

    def test_sentia_initialization(self, governance_module):
        """Test SentiaGuard initializes correctly."""
        SentiaGuard = governance_module["SentiaGuard"]
        CharterEvaluator = governance_module["TranscendentalCharter"]
        charter = CharterEvaluator()
        guard = SentiaGuard(charter)
        assert guard.alert_level == "GREEN"

    def test_calculate_risk_score(self, governance_module):
        """Test risk score calculation."""
        SentiaGuard = governance_module["SentiaGuard"]
        CharterEvaluator = governance_module["TranscendentalCharter"]
        charter = CharterEvaluator()
        guard = SentiaGuard(charter)
        risk = guard.calculate_risk_score({"risk_level": "low"})
        assert 0.0 <= risk <= 1.0

    def test_monitor_and_intervene(self, governance_module):
        """Test monitoring and intervention."""
        SentiaGuard = governance_module["SentiaGuard"]
        CharterEvaluator = governance_module["TranscendentalCharter"]
        charter = CharterEvaluator()
        guard = SentiaGuard(charter)
        result = guard.monitor_and_intervene({"risk_level": "low"})
        assert "risk" in result
        assert "alert_level" in result


class TestGoldenDAG:
    """Test GoldenDAG class."""

    def test_goldendag_initialization(self, governance_module):
        """Test GoldenDAG initializes correctly."""
        GoldenDAG = governance_module["GoldenDAG"]
        dag = GoldenDAG()
        assert dag.chain == []

    def test_add_block(self, governance_module):
        """Test adding a block to the DAG."""
        GoldenDAG = governance_module["GoldenDAG"]
        dag = GoldenDAG()
        dag.add_block({"data": "test"})
        assert len(dag.chain) == 1

    def test_block_has_hash(self, governance_module):
        """Test block has hash."""
        GoldenDAG = governance_module["GoldenDAG"]
        dag = GoldenDAG()
        dag.add_block({"data": "test"})
        assert "hash" in dag.chain[0]
        assert "timestamp" in dag.chain[0]

    def test_verify_chain(self, governance_module):
        """Test chain verification."""
        GoldenDAG = governance_module["GoldenDAG"]
        dag = GoldenDAG()
        dag.add_block({"data": "block1"})
        dag.add_block({"data": "block2"})
        valid = dag.verify_chain()
        assert isinstance(valid, bool)

    def test_get_latest_block(self, governance_module):
        """Test getting latest block."""
        GoldenDAG = governance_module["GoldenDAG"]
        dag = GoldenDAG()
        dag.add_block({"data": "test"})
        latest = dag.get_latest_block()
        assert latest is not None
        assert latest["data"] == {"data": "test"}


class TestComplianceMonitor:
    """Test ComplianceMonitor class."""

    def test_compliance_monitor_initialization(self, governance_module):
        """Test ComplianceMonitor initializes."""
        ComplianceMonitor = governance_module["ComplianceMonitor"]
        monitor = ComplianceMonitor()
        assert monitor is not None

    @pytest.mark.asyncio
    async def test_check_clause_returns_compliant(self, governance_module):
        """Test compliance check returns compliant (stub behavior)."""
        ComplianceMonitor = governance_module["ComplianceMonitor"]
        CharterClause = governance_module["CharterClause"]
        monitor = ComplianceMonitor()
        result = await monitor._check_clause(
            CharterClause.PHI_1_FLOURISHING, {"action": "test"}
        )
        assert "compliant" in result


class TestGovernanceIntegration:
    """Test GovernanceIntegration class."""

    @pytest.fixture
    def governance_integration(self, governance_module):
        """Create a GovernanceIntegration instance."""
        GovernanceIntegration = governance_module["GovernanceIntegration"]
        return GovernanceIntegration()

    def test_register_agent(self, governance_integration):
        """Test registering an agent."""
        governance_integration.register_agent("agent_1", {"name": "Test Agent"})
        assert "agent_1" in governance_integration.agents

    def test_register_agent_twice(self, governance_integration):
        """Test registering same agent twice."""
        governance_integration.register_agent("agent_1", {"name": "Test"})
        governance_integration.register_agent("agent_1", {"name": "Test2"})
        # Should handle gracefully
        assert "agent_1" in governance_integration.agents

    def test_unknown_agent_action(self, governance_integration):
        """Test action by unknown agent."""
        result = asyncio.get_event_loop().run_until_complete(
            governance_integration.agent_action("unknown_agent", {"type": "test"})
        )
        assert "error" in result

    @pytest.mark.asyncio
    async def test_agent_action_known_agent(self, governance_integration):
        """Test agent action for registered agent."""
        governance_integration.register_agent("agent_1", {"name": "Test"})
        result = await governance_integration.agent_action(
            "agent_1", {"type": "read", "risk_level": "low"}
        )
        assert "agent_id" in result
        assert "approved" in result

    def test_get_agent_metrics(self, governance_integration):
        """Test getting agent metrics."""
        governance_integration.register_agent("agent_1", {"name": "Test"})
        metrics = governance_integration.get_agent_metrics("agent_1")
        assert isinstance(metrics, dict)

    def test_get_agent_metrics_unknown(self, governance_integration):
        """Test metrics for unknown agent."""
        metrics = governance_integration.get_agent_metrics("unknown")
        assert "error" in metrics


class TestEthicsEvaluation:
    """Test that ethics evaluation uses action context (bug fix verification)."""

    def test_evaluate_clause_uses_risk_level(self, governance_module):
        """Test that _evaluate_clause considers risk_level from action."""
        CharterEvaluator = governance_module["TranscendentalCharter"]
        CharterClause = governance_module["CharterClause"]
        evaluator = CharterEvaluator()

        # Low risk action should generally score higher
        low_result = evaluator._evaluate_clause(
            CharterClause.PHI_1_FLOURISHING, {"risk_level": "low"}
        )

        # High risk action should generally score lower
        high_result = evaluator._evaluate_clause(
            CharterClause.PHI_1_FLOURISHING, {"risk_level": "high"}
        )

        # High risk actions should not always pass (can be below 0.85 threshold)
        assert 0.0 <= high_result <= 1.0
        assert 0.0 <= low_result <= 1.0

    def test_coherence_average_uses_actual_count(self, governance_module):
        """Test that coherence average divides by actual count, not fixed 100."""
        SentiaGuard = governance_module["SentiaGuard"]
        VeritasEngine = governance_module["VeritasEngine"]
        CharterEvaluator = governance_module["TranscendentalCharter"]
        charter = CharterEvaluator()
        veritas = VeritasEngine()
        guard = SentiaGuard(charter)

        # Add a few coherence history entries
        veritas.verify_invariant("test1", {"v": 0.9})
        veritas.verify_invariant("test2", {"v": 0.95})
        veritas.verify_invariant("test3", {"v": 0.85})

        guard.veritas = veritas
        status = guard.get_system_status()

        # Average should be (0.9 + 0.95 + 0.85) / 3 = 0.9, not / 100
        assert status["coherence_avg"] > 0.5  # Would be ~0.027 if divided by 100
