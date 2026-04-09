# Federated Learning — Privacy-Preserving Distributed ML

**Location:** `src/federated/`  
**Language:** Python 3.11+

---

## Overview

Federated Learning enables **privacy-preserving distributed machine learning** where models are trained across multiple devices/nodes without sharing raw data. This implementation includes differential privacy, secure aggregation, and PySyft integration.

---

## Components

### 1. Core Federated Learning (`neuralblitz_federated_learning.py` — 756 lines)

**Architecture:**
```
┌────────────────────────────────────────────────┐
│          FederatedLearningSystem                │
│  ┌──────────────────┐ ┌──────────────────────┐ │
│  │DifferentialPrivacy│ │SecureAggregation     │ │
│  │Mechanism         │ │Protocol              │ │
│  └──────────────────┘ └──────────────────────┘ │
│  ┌──────────────────┐ ┌──────────────────────┐ │
│  │PrivacyAccountant │ │DistributedTraining   │ │
│  │                  │ │Coordinator           │ │
│  └──────────────────┘ └──────────────────────┘ │
└────────────────────────────────────────────────┘
```

**Key Components:**

#### DifferentialPrivacyMechanism
- **Gaussian noise injection** — Add calibrated noise to gradients
- **Gradient clipping** — Bound gradient norms for privacy
- **Privacy budget tracking** — Track ε (epsilon) privacy budget

#### SecureAggregationProtocol
- **Shamir secret sharing** — Split gradients into shares
- **Fernet encryption** — Encrypt gradient transmissions
- **Secure aggregation** — Aggregate without revealing individual gradients

#### PrivacyAccountant
- **Moments accountant** — Track privacy budget across rounds
- **ε-δ privacy guarantees** — Formal differential privacy bounds

#### DistributedTrainingCoordinator
- **Node registration** — Register participating nodes
- **Round coordination** — Coordinate training rounds
- **Model aggregation** — Aggregate model updates from nodes

**Integrations:** DRS-F (Federated DRS), CECT (Charter-Ethical Constraint Tensor), NBHS-512 (hashing), QEC-CK (Quantum Error Correction)

### 2. PySyft Integration (`neuralblitz_federated_pysyft.py` — 460 lines)

**Purpose:** Production-grade federated learning using PySyft.

**Features:**
- **DP Tensors** — Differentially private tensor operations
- **Encrypted Remote Execution** — Run computations on remote workers
- **HybridFederatedSystem** — Combines custom FL with PySyft fallback
- **Virtual Workers** — Simulate federated nodes locally

**Usage:**
```python
from src.federated.neuralblitz_federated_pysyft import HybridFederatedSystem

system = HybridFederatedSystem()

# Train federated model
model = system.train_federated(
    data_partitions=node_data,
    rounds=100,
    privacy_epsilon=1.0
)

# Evaluate
accuracy = system.evaluate(model, test_data)
```

---

## Privacy Guarantees

| Parameter | Value | Meaning |
|-----------|-------|---------|
| **ε (epsilon)** | 1.0 | Privacy budget — lower = more private |
| **δ (delta)** | 1e-5 | Failure probability |
| **Noise multiplier** | 1.0 | Gaussian noise scale |
| **Clipping norm** | 1.0 | Max gradient norm |

---

## Testing

```bash
# Test federated learning modules
pytest tests/federated/ -v

# Full test
pytest tests/test_federated_full.py -v

# Test module loading
python -c "
from src.federated.neuralblitz_federated_learning import DistributedTrainingCoordinator
coordinator = DistributedTrainingCoordinator()
print(f'Active nodes: {len(coordinator.nodes)}')
"
```

---

## Related Documentation

- [src/ README](../README.md) — Main application overview
- [Federated Learning Report](../../docs/FEDERATED_LEARNING_REPORT.md)
- [Governance README](../governance/README.md) — Ethics compliance for FL
