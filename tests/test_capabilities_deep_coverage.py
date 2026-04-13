"""Deep coverage tests for capability kernels and utility modules (corrected class names)."""

import pytest
import numpy as np


class TestFeatureEngineeringAutomationCK:
    """Cover ck_feature_engineering_automation.py (18%→target 60%)."""

    @pytest.fixture
    def fe(self):
        from src.capabilities.ck_feature_engineering_automation import FeatureEngineeringAutomationCK
        return FeatureEngineeringAutomationCK()

    def test_scale_features(self, fe):
        import pandas as pd
        df = pd.DataFrame({"a": [1.0, 2.0, 3.0, 4.0, 5.0]})
        result = fe.process({"data": df.to_dict(), "method": "standard"})
        assert "status" in result

    def test_encode_categorical(self, fe):
        import pandas as pd
        df = pd.DataFrame({"cat": ["a", "b", "a", "c"]})
        result = fe.process({"data": df.to_dict(), "method": "onehot"})
        assert "status" in result

    def test_select_features(self, fe):
        import pandas as pd
        df = pd.DataFrame({"a": [1.0, 2.0, 3.0], "b": [1.0, 1.0, 1.0]})
        result = fe.process({"data": df.to_dict(), "method": "variance"})
        assert "status" in result

    def test_invalid_method(self, fe):
        result = fe.process({"data": {}, "method": "nonexistent"})
        assert "error" in result or result.get("status") == "error"


class TestMalwareSignatureAnalyzer:
    """Cover malware_signature_analyzer_ck.py (21%→target 60%)."""

    @pytest.fixture
    def analyzer(self):
        from src.capabilities.malware_signature_analyzer_ck import MalwareSignatureAnalyzer
        return MalwareSignatureAnalyzer()

    def test_init(self, analyzer):
        assert analyzer.name is not None

    def test_analyze_file_nonexistent(self, analyzer):
        result = analyzer.analyze("/nonexistent/file.exe")
        assert "error" in result or result.get("status") == "error"

    def test_compute_hashes(self, analyzer, tmp_path):
        sample = tmp_path / "test.bin"
        sample.write_bytes(b"MZ" + b"\x00" * 100)
        result = analyzer.analyze(str(sample))
        assert "hashes" in result or "md5" in result or "status" in result

    def test_threat_level_enum(self):
        from src.capabilities.malware_signature_analyzer_ck import ThreatLevel
        assert ThreatLevel.SAFE is not None
        assert ThreatLevel.MALICIOUS is not None

    def test_verdict_dataclass(self):
        from src.capabilities.malware_signature_analyzer_ck import MalwareVerdict
        v = MalwareVerdict(file_path="/test", threat_level="safe", confidence=1.0)
        assert v.threat_level == "safe"


class TestNetworkAnomalyDetector:
    """Cover network_anomaly_detector_ck.py (66%→target 85%)."""

    @pytest.fixture
    def detector(self):
        from src.capabilities.network_anomaly_detector_ck import NetworkAnomalyDetector
        return NetworkAnomalyDetector()

    def test_init(self, detector):
        assert detector is not None

    def test_detect_anomaly(self, detector):
        X = np.random.randn(100, 5)
        result = detector.detect_anomaly(X)
        assert "anomalies" in result or "predictions" in result

    def test_update_baseline(self, detector):
        detector.update_baseline(np.random.randn(50, 4))
        assert detector.baseline is not None or detector._baseline is not None

    def test_get_stats(self, detector):
        stats = detector.get_stats()
        assert isinstance(stats, dict)


class TestQuadraticVotingCK:
    """Cover quadratic_voting_ck.py (60%→target 85%)."""

    @pytest.fixture
    def qv(self):
        from src.capabilities.quadratic_voting_ck import QuadraticVotingCK
        return QuadraticVotingCK()

    def test_init(self, qv):
        assert qv is not None

    def test_vote_cost_quadratic(self, qv):
        cost = qv.calculate_vote_cost({"option_a": 3})
        assert cost == 9.0  # 3^2 = 9

    def test_commit_vote(self, qv):
        session = qv.create_voting_session("test", ["a", "b"])
        sid = session["session_id"]
        result = qv.commit_vote(sid, {"a": 2}, "v1", "hash1")
        assert result is not None

    def test_finalize_voting(self, qv):
        session = qv.create_voting_session("finalize_test", ["x", "y"])
        sid = session["session_id"]
        qv.commit_vote(sid, {"x": 1}, "v1", "h1")
        result = qv.finalize_voting(sid)
        assert "results" in result


class TestBlockchainController:
    """Cover blockchain_integration.py (30%→target 60%)."""

    def test_controller_init(self):
        from src.utils.blockchain_integration import BlockchainController
        bc = BlockchainController()
        assert bc is not None

    def test_compute_hash(self):
        from src.utils.blockchain_integration import BlockchainController
        bc = BlockchainController()
        h = bc.compute_transaction_hash({"a": 1})
        assert isinstance(h, str)
        assert len(h) == 64

    def test_merkle_root(self):
        from src.utils.blockchain_integration import BlockchainController
        bc = BlockchainController()
        root = bc.create_merkle_tree(["tx1", "tx2", "tx3"])
        assert isinstance(root, str)

    def test_contract_abi(self):
        from src.utils.blockchain_integration import ContractABI
        assert ContractABI is not None

    def test_did_manager(self):
        from src.utils.blockchain_integration import DIDManager
        dm = DIDManager()
        assert dm is not None


class TestAdversarialProtector:
    """Cover bci_security_implementation.py (23%→target 60%)."""

    def test_init(self):
        from src.utils.bci_security_implementation import AdversarialProtector
        ap = AdversarialProtector()
        assert ap is not None

    def test_detect_adversarial(self):
        from src.utils.bci_security_implementation import AdversarialProtector
        ap = AdversarialProtector()
        result = ap.detect_adversarial(np.random.randn(10, 5))
        assert result is not None

    def test_auth_result_dataclass(self):
        from src.utils.bci_security_implementation import AuthResult
        ar = AuthResult(success=True, confidence=0.9)
        assert ar.success is True


class TestCheckpointManager:
    """Cover fault_tolerance_layer.py — CheckpointManager."""

    def test_create_and_restore(self):
        from src.utils.fault_tolerance_layer import CheckpointManager
        cm = CheckpointManager()
        cp = cm.create_checkpoint({"task": "running"}, {"node": "active"})
        restored = cm.restore_checkpoint(cp.checkpoint_id)
        assert restored["task_states"] == {"task": "running"}

    def test_verify_chain(self):
        from src.utils.fault_tolerance_layer import CheckpointManager
        cm = CheckpointManager()
        cm.create_checkpoint({"a": 1}, {"b": 2})
        assert cm.verify_checkpoint_chain() is True


class TestAdaptiveTopologyManager:
    """Cover network_topology_optimizer.py (20%→target 60%)."""

    def test_init(self):
        from src.utils.network_topology_optimizer import AdaptiveTopologyManager
        atm = AdaptiveTopologyManager("node_0")
        assert atm.node_id == "node_0"

    def test_add_node(self):
        from src.utils.network_topology_optimizer import AdaptiveTopologyManager, NodeAddress
        atm = AdaptiveTopologyManager("n0")
        atm.add_node(NodeAddress("n1", "10.0.0.1", 8080))
        assert "n1" in atm.routing_table

    def test_xor_distance(self):
        from src.utils.network_topology_optimizer import AdaptiveTopologyManager
        atm = AdaptiveTopologyManager("n0")
        d = atm._xor_distance("n0", "n1")
        assert isinstance(d, int)

    def test_kbucket(self):
        from src.utils.network_topology_optimizer import KBucket, NodeAddress
        b = KBucket(0, 100)
        n = NodeAddress("test", "10.0.0.1", 8080)
        assert b.add(n) is True

    def test_get_topology_stats(self):
        from src.utils.network_topology_optimizer import AdaptiveTopologyManager
        atm = AdaptiveTopologyManager("n0")
        stats = atm.get_topology_stats()
        assert "node_id" in stats
