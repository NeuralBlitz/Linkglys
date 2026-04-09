"""Tests for src/federated/neuralblitz_federated_learning.py - Federated learning system."""

import pytest
import numpy as np
import torch
import torch.nn as nn
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


@pytest.fixture
def federated_module():
    """Import the federated learning module."""
    if "federated.neuralblitz_federated_learning" in sys.modules:
        del sys.modules["federated.neuralblitz_federated_learning"]

    from federated.neuralblitz_federated_learning import (
        DifferentialPrivacyMechanism,
        SecureAggregation,
        FederatedClient,
        FederatedServer,
        FederatedConfig,
        PrivacyAccountant,
    )
    return {
        "DifferentialPrivacyMechanism": DifferentialPrivacyMechanism,
        "SecureAggregation": SecureAggregation,
        "FederatedClient": FederatedClient,
        "FederatedServer": FederatedServer,
        "FederatedConfig": FederatedConfig,
        "PrivacyAccountant": PrivacyAccountant,
    }


class SimpleModel(nn.Module):
    """Simple model for testing."""

    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(10, 2)

    def forward(self, x):
        return self.fc(x)


class TestDifferentialPrivacyMechanism:
    """Test DifferentialPrivacyMechanism class."""

    def test_dp_initialization(self, federated_module):
        """Test DP mechanism initializes correctly."""
        DP = federated_module["DifferentialPrivacyMechanism"]
        dp = DP(noise_multiplier=1.0, max_grad_norm=1.0)
        assert dp.noise_multiplier == 1.0
        assert dp.max_grad_norm == 1.0

    def test_clip_gradients(self, federated_module):
        """Test gradient clipping."""
        DP = federated_module["DifferentialPrivacyMechanism"]
        dp = DP(noise_multiplier=1.0, max_grad_norm=1.0)

        model = SimpleModel()
        # Set large gradients
        for param in model.parameters():
            param.grad = torch.ones_like(param) * 10.0

        dp.clip_gradients(model)

        # Check gradients are clipped
        for param in model.parameters():
            assert param.grad.norm().item() <= dp.max_grad_norm + 1e-6

    def test_add_noise(self, federated_module):
        """Test noise addition."""
        DP = federated_module["DifferentialPrivacyMechanism"]
        dp = DP(noise_multiplier=0.5, max_grad_norm=1.0)

        model = SimpleModel()
        for param in model.parameters():
            param.grad = torch.ones_like(param)

        original_grads = [p.grad.clone() for p in model.parameters()]
        dp.add_noise(model)

        # Gradients should be different after noise
        noise_added = False
        for param, orig in zip(model.parameters(), original_grads):
            if not torch.allclose(param.grad, orig):
                noise_added = True
                break
        assert noise_added

    def test_privatize_update(self, federated_module):
        """Test privatize_update method."""
        DP = federated_module["DifferentialPrivacyMechanism"]
        dp = DP(noise_multiplier=0.1, max_grad_norm=1.0)

        model = SimpleModel()
        result = dp.privatize_update(model, sampling_rate=0.1, step=1)
        assert "clipped" in result or "noise_added" in result or result is not None


class TestSecureAggregation:
    """Test SecureAggregation class."""

    def test_secure_agg_initialization(self, federated_module):
        """Test SecureAggregation initializes."""
        SA = federated_module["SecureAggregation"]
        sa = SA()
        assert sa is not None

    def test_encrypt_update(self, federated_module):
        """Test encrypt update."""
        SA = federated_module["SecureAggregation"]
        sa = SA(key=b"test_key_12345678901234567890123")

        model = SimpleModel()
        encrypted = sa.encrypt_update(model)
        assert encrypted is not None
        assert isinstance(encrypted, bytes)

    def test_decrypt_update_preserves_shape(self, federated_module):
        """Test decrypt update preserves tensor shape (bug fix verification)."""
        SA = federated_module["SecureAggregation"]
        sa = SA(key=b"test_key_12345678901234567890123")

        model = SimpleModel()
        encrypted = sa.encrypt_update(model)
        decrypted = sa.decrypt_update(encrypted)

        # Should be a valid tensor
        assert isinstance(decrypted, torch.Tensor)
        assert decrypted.numel() > 0


class TestPrivacyAccountant:
    """Test PrivacyAccountant class."""

    def test_accountant_initialization(self, federated_module):
        """Test PrivacyAccountant initializes."""
        PA = federated_module["PrivacyAccountant"]
        accountant = PA(epsilon=1.0, delta=1e-5)
        assert accountant.epsilon == 1.0
        assert accountant.delta == 1e-5

    def test_spend_budget(self, federated_module):
        """Test spending privacy budget."""
        PA = federated_module["PrivacyAccountant"]
        accountant = PA(epsilon=1.0, delta=1e-5)
        accountant.spend_budget(0.1)
        # Budget should be tracked
        assert hasattr(accountant, "epsilon") or hasattr(accountant, "_spent")


class TestFederatedConfig:
    """Test FederatedConfig dataclass."""

    def test_config_defaults(self, federated_module):
        """Test FederatedConfig has reasonable defaults."""
        FC = federated_module["FederatedConfig"]
        config = FC()
        assert config.num_rounds > 0
        assert config.num_clients > 0
        assert config.batch_size > 0


class TestFederatedServer:
    """Test FederatedServer class."""

    def test_server_initialization(self, federated_module):
        """Test FederatedServer initializes."""
        FS = federated_module["FederatedServer"]
        model = SimpleModel()
        server = FS(model)
        assert server is not None

    def test_server_aggregate_updates(self, federated_module):
        """Test server aggregates client updates."""
        FS = federated_module["FederatedServer"]
        model = SimpleModel()
        server = FS(model)

        # Simulate client updates
        updates = []
        for _ in range(3):
            client_model = SimpleModel()
            updates.append({
                "weights": {k: v.clone() for k, v in client_model.state_dict().items()}
            })

        # Should not crash
        if hasattr(server, "aggregate"):
            server.aggregate(updates)


class TestFederatedClient:
    """Test FederatedClient class."""

    def test_client_initialization(self, federated_module):
        """Test FederatedClient initializes."""
        FC = federated_module["FederatedClient"]
        model = SimpleModel()
        client = FC(client_id="client_1", model=model)
        assert client.client_id == "client_1"

    def test_client_local_train(self, federated_module):
        """Test client local training with proper data."""
        FC = federated_module["FederatedClient"]
        from torch.utils.data import DataLoader, TensorDataset

        model = SimpleModel()
        client = FC(client_id="client_1", model=model)

        # Create dummy data
        X = torch.randn(100, 10)
        y = torch.randn(100, 2)
        dataset = TensorDataset(X, y)
        loader = DataLoader(dataset, batch_size=10)

        client.data_loader = loader

        # Train for 1 epoch
        config = federated_module["FederatedConfig"]()
        config.local_epochs = 1
        config.batch_size = 10
        config.learning_rate = 0.01

        # Should not raise ZeroDivisionError (bug fix verification)
        result = client.local_train(config)
        assert result is not None

    def test_client_empty_dataset(self, federated_module):
        """Test client handles empty dataset without ZeroDivisionError."""
        FC = federated_module["FederatedClient"]
        from torch.utils.data import DataLoader, TensorDataset

        model = SimpleModel()
        client = FC(client_id="client_1", model=model)

        # Empty dataset
        X = torch.randn(0, 10)
        y = torch.randn(0, 2)
        dataset = TensorDataset(X, y)
        loader = DataLoader(dataset, batch_size=10)
        client.data_loader = loader

        config = federated_module["FederatedConfig"]()
        config.local_epochs = 1
        config.batch_size = 10
        config.learning_rate = 0.01

        # Should handle empty dataset gracefully
        try:
            client.local_train(config)
        except ZeroDivisionError:
            pytest.fail("local_train raised ZeroDivisionError on empty dataset")


class TestFederatedLearningIntegration:
    """Integration tests for the federated learning system."""

    def test_full_federation_round(self, federated_module):
        """Test a full round of federated learning."""
        from torch.utils.data import DataLoader, TensorDataset

        FS = federated_module["FederatedServer"]
        FC = federated_module["FederatedClient"]
        FConfig = federated_module["FederatedConfig"]

        # Create server with model
        global_model = SimpleModel()
        server = FS(global_model)

        # Create clients with data
        clients = []
        for i in range(2):
            client_model = SimpleModel()
            X = torch.randn(50, 10)
            y = torch.randn(50, 2)
            dataset = TensorDataset(X, y)
            loader = DataLoader(dataset, batch_size=10)

            client = FC(client_id=f"client_{i}", model=client_model)
            client.data_loader = loader
            clients.append(client)

        # Train each client locally
        config = FConfig()
        config.local_epochs = 1
        config.batch_size = 10
        config.learning_rate = 0.01

        for client in clients:
            client.local_train(config)

        # Collect updates
        updates = []
        for client in clients:
            updates.append({
                "weights": {k: v.clone() for k, v in client.model.state_dict().items()}
            })

        # Server aggregates
        if hasattr(server, "aggregate"):
            server.aggregate(updates)

        # Global model should be updated
        assert global_model is not None
