# Utils — Infrastructure Utilities

**Location:** `src/utils/`  
**Language:** Python 3.11+

---

## Overview

This directory contains **infrastructure utility modules** that provide supporting functionality across the NeuralBlitz platform. These modules are used by multiple components but don't fit into a specific domain category.

---

## Modules

### 1. BCI Security (`bci_security_implementation.py`)

**Purpose:** Brain-Computer Interface security implementation.

**Features:**
- Neural data encryption
- Signal authentication
- Privacy-preserving BCI protocols
- Neural data integrity verification

### 2. Blockchain Integration (`blockchain_integration.py`)

**Purpose:** Blockchain integration for provenance and audit trails.

**Features:**
- Transaction recording on blockchain
- Provenance tracking for AI outputs
- Immutable audit logs
- Smart contract interaction
- Cross-chain support

### 3. Dimensional Computing Demo (`dimensional_computing_demo.py`)

**Purpose:** Demonstration of multi-dimensional processing.

**Features:**
- Hyperdimensional data representation
- Cross-dimensional transformations
- M-theory inspired computing
- String vibration mode processing

### 4. Fault Tolerance Layer (`fault_tolerance_layer.py`)

**Purpose:** System-level fault tolerance and recovery.

**Features:**
- Failure detection and isolation
- Automatic failover
- Graceful degradation
- Recovery procedures
- Circuit breaker patterns

### 5. Network Topology Optimizer (`network_topology_optimizer.py`)

**Purpose:** Optimize network topology for performance and reliability.

**Features:**
- Topology discovery and mapping
- Optimal routing calculation
- Bottleneck identification
- Redundancy planning
- Load distribution optimization

### 6. Neuro-Symbiotic Demo (`neuro_symbiotic_demo.py`)

**Purpose:** Demonstration of neuro-symbiotic computing.

**Features:**
- Human-AI symbiotic interaction
- Neural signal processing
- Adaptive response generation
- Cognitive state tracking

### 7. Quantum Foundation Demo (`quantum_foundation_demo.py`)

**Purpose:** Quantum computing foundation demonstrations.

**Features:**
- Quantum circuit simulation
- Quantum algorithm implementation
- Quantum-classical hybrid computing
- Quantum state visualization

### 8. RAFT Consensus (`raft_consensus.py`)

**Purpose:** RAFT distributed consensus algorithm implementation.

**Features:**
- Leader election
- Log replication
- Safety guarantees
- Cluster membership changes
- Network partition handling

**Algorithm:** RAFT (Replication And Fault Tolerance)
- Leader-based consensus
- Strong leader for log management
- Safety: election restriction prevents commit from previous term

---

## Usage Examples

### Fault Tolerance
```python
from src.utils.fault_tolerance_layer import FaultToleranceLayer

ftl = FaultToleranceLayer()

# Execute with fault tolerance
result = await ftl.execute_with_retry(
    operation=my_function,
    max_retries=3,
    backoff_factor=2
)
```

### RAFT Consensus
```python
from src.utils.raft_consensus import RAFTConsensus

consensus = RAFTConsensus(
    node_id="node-1",
    peers=["node-2", "node-3"]
)

# Propose value
await consensus.propose({"key": "value"})

# Get consensus value
value = await consensus.read("key")
```

---

## Testing

```bash
# Test utility modules
pytest tests/utils/ -v

# Test module loading
python -c "
from src.utils.raft_consensus import RAFTConsensus
print('RAFT Consensus module loaded')
"
```

---

## Related Documentation

- [src/ README](../README.md) — Main application overview
- [Fault Tolerance Report](../../docs/fault_tolerance_report.md)
- [Network Topology Report](../../docs/network_topology_report.md)
- [Consensus Mechanisms](../../docs/consensus_mechanisms_report.md)
