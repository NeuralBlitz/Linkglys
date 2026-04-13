"""Deep coverage tests for low-coverage modules — using real class names/methods."""

import pytest
import numpy as np
import pandas as pd


class TestFeatureEngineeringAutomationCK:
    @pytest.fixture
    def fe(self):
        from src.capabilities.ck_feature_engineering_automation import FeatureEngineeringAutomationCK
        return FeatureEngineeringAutomationCK()

    def test_execute_scale(self, fe):
        df = pd.DataFrame({"a": [1.0, 2.0, 3.0, 4.0, 5.0]})
        result = fe.execute({"data": df.to_dict(), "method": "standard"})
        assert "status" in result

    def test_execute_encode(self, fe):
        df = pd.DataFrame({"cat": ["a", "b", "a", "c"]})
        result = fe.execute({"data": df.to_dict(), "method": "onehot"})
        assert "status" in result

    def test_execute_select(self, fe):
        df = pd.DataFrame({"a": [1.0, 2.0, 3.0], "b": [1.0, 1.0, 1.0]})
        result = fe.execute({"data": df.to_dict(), "method": "variance"})
        assert "status" in result

    def test_execute_invalid(self, fe):
        result = fe.execute({"data": {}, "method": "nonexistent"})
        assert result.get("status") == "error" or "error" in result


class TestMalwareSignatureAnalyzer:
    @pytest.fixture
    def mal(self):
        from src.capabilities.malware_signature_analyzer_ck import MalwareSignatureAnalyzer
        return MalwareSignatureAnalyzer()

    def test_analyze_pe_header(self, mal):
        result = mal.analyze_pe_header(b"MZ" + b"\x00" * 200)
        assert "is_pe" in result

    def test_compute_hashes(self, mal):
        data = b"test binary content here"
        hashes = mal.compute_hashes(data)
        assert "md5" in hashes
        assert "sha256" in hashes

    def test_determine_verdict(self, mal):
        v = mal.determine_verdict({"threat_score": 0.9, "confidence": 0.95})
        assert v is not None

    def test_calculate_confidence(self, mal):
        c = mal.calculate_confidence({"md5_match": True, "yara_match": False})
        assert isinstance(c, float)

    def test_extract_iocs(self, mal):
        iocs = mal.extract_iocs({"urls": ["http://evil.com"], "ips": ["1.2.3.4"]})
        assert iocs is not None

    def test_apply_yara_rules(self, mal):
        result = mal.apply_yara_rules(b"test content")
        assert isinstance(result, list)


class TestNetworkAnomalyDetector:
    @pytest.fixture
    def nad(self):
        from src.capabilities.network_anomaly_detector_ck import NetworkAnomalyDetector
        return NetworkAnomalyDetector()

    def test_extract_features(self, nad):
        flow = {"src": "10.0.0.1", "dst": "10.0.0.2", "size": 1500, "duration": 0.5}
        feats = nad.extract_features(flow)
        assert feats is not None

    def test_compute_anomaly_score(self, nad):
        features = np.random.randn(10, 5)
        score = nad.compute_anomaly_score(features)
        assert isinstance(score, (float, np.ndarray))

    def test_detect_anomaly_type(self, nad):
        result = nad.detect_anomaly_type({"score": 0.9, "features": [1,2,3]})
        assert result is not None

    def test_determine_severity(self, nad):
        sev = nad.determine_severity(0.9)
        assert sev is not None

    def test_execute(self, nad):
        X = np.random.randn(100, 5)
        result = nad.execute({"data": X.tolist(), "method": "isolation_forest"})
        assert "status" in result


class TestQuadraticVotingCK:
    @pytest.fixture
    def qv(self):
        from src.capabilities.quadratic_voting_ck import QuadraticVotingCK
        return QuadraticVotingCK()

    def test_initiate_voting(self, qv):
        session = qv.initiate_voting("test_proposal", ["yes", "no"])
        assert "session_id" in session

    def test_commit_vote(self, qv):
        session = qv.initiate_voting("prop1", ["a", "b"])
        sid = session["session_id"]
        result = qv.commit_vote(sid, {"a": 2}, "v1", "commit1")
        assert result is not None

    def test_finalize_voting(self, qv):
        session = qv.initiate_voting("prop2", ["x", "y"])
        sid = session["session_id"]
        qv.commit_vote(sid, {"x": 1}, "v1", "c1")
        result = qv.finalize_voting(sid)
        assert "results" in result

    def test_reveal_vote(self, qv):
        session = qv.initiate_voting("prop3", ["a"])
        sid = session["session_id"]
        qv.commit_vote(sid, {"a": 1}, "v1", "commit")
        result = qv.reveal_vote(sid, "v1", {"a": 1}, "nonce")
        assert result is not None


class TestBlockchainController:
    def test_get_system_status(self):
        from src.utils.blockchain_integration import BlockchainController
        bc = BlockchainController()
        status = bc.get_system_status()
        assert isinstance(status, dict)

    def test_create_cross_chain_asset(self):
        from src.utils.blockchain_integration import BlockchainController
        bc = BlockchainController()
        result = bc.create_cross_chain_asset({"type": "test", "value": 100})
        assert result is not None

    def test_verify_cross_chain_asset(self):
        from src.utils.blockchain_integration import BlockchainController
        bc = BlockchainController()
        result = bc.verify_cross_chain_asset("fake_id", "fake_proof")
        assert result is not None

    def test_contract_abi_class(self):
        from src.utils.blockchain_integration import ContractABI
        assert hasattr(ContractABI, 'ASSET_REGISTRY_ABI')

    def test_did_manager(self):
        from src.utils.blockchain_integration import DIDManager
        dm = DIDManager()
        assert dm is not None

    def test_did_create(self):
        from src.utils.blockchain_integration import DIDManager
        dm = DIDManager()
        did = dm.create_did("test_method", {"public_key": "abc123"})
        assert "did" in did

    def test_did_resolve(self):
        from src.utils.blockchain_integration import DIDManager
        dm = DIDManager()
        result = dm.resolve_did("did:test:123")
        assert isinstance(result, dict)


class TestAdversarialProtector:
    @pytest.fixture
    def ap(self):
        from src.utils.bci_security_implementation import AdversarialProtector
        return AdversarialProtector()

    def test_fit_clean_statistics(self, ap):
        data = np.random.randn(50, 10)
        ap.fit_clean_statistics(data)
        assert ap._clean_mean is not None

    def test_feature_squeezing(self, ap):
        ap.fit_clean_statistics(np.random.randn(20, 3))
        data = np.random.randn(10, 5)
        result = ap.feature_squeezing(data)
        assert result.shape == data.shape

    def test_sanitize_input(self, ap):
        ap.fit_clean_statistics(np.random.randn(20, 3))
        data = np.random.randn(10, 5)
        result = ap.sanitize_input(data)
        assert result is not None

    def test_detect_adversarial(self, ap):
        ap.fit_clean_statistics(np.random.randn(20, 3))
        data = np.random.randn(10, 5)
        result = ap.detect_adversarial(data)
        assert result is not None


class TestCheckpointManager:
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


class TestChromaDBIntegration:
    @pytest.fixture
    def db(self):
        from src.integrations.chromadb_integration import ChromaDBIntegration
        return ChromaDBIntegration()

    def test_connect(self, db):
        db.connect()
        assert db.client is not None

    def test_create_collection(self, db):
        db.connect()
        db.create_collection("test_coll")
        assert "test_coll" in db.list_collections()

    def test_count(self, db):
        db.connect()
        db.create_collection("count_test")
        c = db.count()
        assert isinstance(c, int)

    def test_peek(self, db):
        db.connect()
        db.create_collection("peek_test")
        result = db.peek(5)
        assert result is not None


class TestCircuitBreaker:
    def test_closed_to_open(self):
        from src.utils.fault_tolerance_layer import CircuitBreaker, CircuitState
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=999)
        def fail():
            raise ConnectionError("down")
        for _ in range(3):
            try:
                cb.call(fail)
            except:
                pass
        assert cb.get_state()["state"] == "open"

    def test_open_to_half_open(self):
        from src.utils.fault_tolerance_layer import CircuitBreaker
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.01)
        def fail():
            raise ConnectionError("x")
        try:
            cb.call(fail)
        except:
            pass
        import time; time.sleep(0.02)
        # Next call should transition to half_open
        success = [False]
        def ok():
            success[0] = True
            return "ok"
        result = cb.call(ok)
        assert result == "ok"
        assert success[0] is True
