# Agents — Autonomous Agent Systems

**Location:** `src/agents/`  
**Language:** Python 3.11+

---

## Overview

This directory contains **multi-layered autonomous agent systems** based on the NeuralBlitz v20.0 "Apical Synthesis" architecture. These agents operate with goal decomposition, self-reflection, ethical constraints, memory systems, and real-time adaptation.

---

## Files

### 1. `advanced_autonomous_agent_framework.py` (1,471 lines)

**The most comprehensive agent framework in the project.**

**Architecture:**
```
┌────────────────────────────────────────────────┐
│             AutonomousAgent                     │
│  ┌──────────┐ ┌──────────┐ ┌───────────────┐  │
│  │GoalManager│ │ToolManager│ │CommunicationMgr│ │
│  └──────────┘ └──────────┘ └───────────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌───────────────┐  │
│  │MemorySystem│ │MetaCogityEngine│ │EthicalConstraints│ │
│  └──────────┘ └──────────┘ └───────────────┘  │
└────────────────────────────────────────────────┘
```

**Key Components:**
- **GoalManager** — Goal decomposition, hierarchical planning, dependency resolution
- **ToolManager** — Tool registration, execution, error handling
- **CommunicationManager** — Inter-agent messaging, negotiation
- **MemorySystem** — Episodic (experience), Semantic (knowledge), Working (short-term) memory
- **MetaCognitiveEngine** — Self-reflection, strategy adjustment, learning
- **EthicalConstraintSystem** — Charter compliance, safety guardrails

**Agent States:** `IDLE`, `THINKING`, `ACTING`, `LEARNING`, `REFLECTING`, `PLANNING`, `COMMUNICATING`, `WAITING`, `ERROR`

### 2. `multi_layered_multi_agent_system.py` (795 lines)

**5-tier agent hierarchy with batch processing.**

**Architecture:**
- **AgentCluster** — Group of agents with load balancing
- **AutonomousAgent** — Individual agent with ethical constraint engine
- **MetaCognitiveLayer** — System evolution and optimization
- **BatchProcessor** — Dependency-resolved batch execution
- **EthicalGovernance** — Charter compliance checks

**Capacity:** 50,000+ processing stages with distributed coordination.

### 3. `distributed_mlmas.py` (496 lines)

**Multi-node coordination for distributed systems.**

**Key Components:**
- **Node** — Compute node with capability registry
- **DistributedScheduler** — Task scheduling with node scoring
- **FaultTolerance** — Node failure detection and recovery
- **CrossClusterCommunication** — Inter-cluster message routing

**Features:** Load balancing, fault tolerance, network-aware task distribution.

### 4. `autonomous_self_evolution_simplified.py` (371 lines)

**Evolutionary self-improvement system.**

**Key Components:**
- **EvolutionaryPressure** — Fitness evaluation, selection pressure
- **SelfModification** — Code modification with risk assessment
- **CapabilityTracking** — Learning, reasoning, creativity, wisdom, compassion
- **TranscendenceProgress** — Progress toward technological singularity

---

## Usage Example

```python
from src.agents.advanced_autonomous_agent_framework import AutonomousAgent

# Create agent
agent = AutonomousAgent(
    name="research-agent",
    capabilities=["research", "analysis", "reporting"]
)

# Set goal
agent.set_goal("Research quantum computing applications")

# Execute
result = await agent.execute()
print(f"Goal completed: {result.completed}")
print(f"Steps taken: {len(result.steps)}")
print(f"Tools used: {result.tools_used}")
```

---

## Testing

```bash
# Test agent module loading
pytest tests/agents/ -v

# Test specific agent
python -c "
from src.agents.advanced_autonomous_agent_framework import AutonomousAgent
agent = AutonomousAgent(name='test')
print(f'Agent state: {agent.state.value}')
"
```

---

## Related Documentation

- [src/ README](../README.md) — Main application overview
- [LRS-Agents README](../../lrs_agents/README.md) — Active Inference framework
- [ARCHITECTURE.md](../../ARCHITECTURE.md) — System architecture
