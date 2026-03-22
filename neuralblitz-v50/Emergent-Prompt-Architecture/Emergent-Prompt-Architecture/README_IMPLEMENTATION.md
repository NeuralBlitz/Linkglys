# Emergent Prompt Architecture (EPA) - Python Implementation

A complete Python implementation of the Emergent Prompt Architecture system that moves beyond static prompting to dynamic, emergent prompt generation.

## 🌟 Features

- **Dynamic Prompt Generation**: Prompts are assembled in real-time from semantic atoms (Ontons)
- **C.O.A.T. Protocol**: Context, Objective, Adversarial, and Teleological analysis
- **Recursive Learning**: System learns from user feedback and self-reflection
- **Safety Layer**: CECT-derived ethical validation and safety checks
- **REST API**: Complete HTTP API for integration
- **Multiple Modes**: SENTIO, DYNAMO, and GENESIS operational modes

## 🏗️ Architecture

### Core Components

1. **Onton**: The fundamental semantic atom - smallest unit of meaning
2. **Ontological Lattice**: Weighted hypergraph database storing Ontons
3. **Genesis Assembler**: Engine that crystallizes dynamic prompts using C.O.A.T.
4. **Safety Validator**: Implements CECT (CharterLayer Ethical Constraint Tensor)
5. **Feedback Engine**: Handles recursive learning and system improvement

### System Modes

- **SENTIO**: High ethics, slow thinking, detailed provenance
- **DYNAMO**: High speed, optimized for throughput  
- **GENESIS**: Creative mode, high temperature, loose association

## 📦 Installation

### Prerequisites

- Python 3.8+
- pip or conda package manager

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/your-repo/emergent-prompt-architecture.git
cd emergent-prompt-architecture

# Install dependencies
pip install -r requirements.txt

# Run setup verification
python setup.py
```

## 🚀 Quick Start

### 1. Run the Demo

```bash
python demo.py
```

This interactive demo showcases:
- Basic functionality
- System mode comparison
- Safety features
- Interactive prompt generation

### 2. Start the API Server

```bash
python api_server.py
```

The API will be available at `http://localhost:8000`

### 3. Try the API

```bash
# Ingest content into the lattice
curl -X POST "http://localhost:8000/api/v1/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "user_input",
    "content": "Python is great for AI development",
    "metadata": {"topic": "programming"}
  }'

# Crystallize a dynamic prompt
curl -X POST "http://localhost:8000/api/v1/crystallize" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "demo_session",
    "mode": "sentio"
  }'
```

## 📖 Usage Examples

### Basic Python Usage

```python
from epa import Onton, OntologicalLattice, GenesisAssembler, SafetyValidator, SystemMode

# Initialize components
lattice = OntologicalLattice()
assembler = GenesisAssembler(lattice, mode=SystemMode.SENTIO)
safety = SafetyValidator()

# Create and add Ontons
persona_onton = Onton(
    content="You are a helpful AI assistant.",
    type="persona",
    weight=0.9
)
lattice.add_onton(persona_onton)

# Validate input
is_safe, reason = safety.validate_input("Tell me about AI ethics")
if not is_safe:
    print(f"Input rejected: {reason}")

# Generate dynamic prompt
result = assembler.crystallize("Tell me about AI ethics", "session_123")
print(f"Generated prompt: {result.system_message}")
print(f"Trace ID: {result.trace_id}")
```

### Feedback Loop

```python
from epa import FeedbackEngine

feedback_engine = FeedbackEngine(lattice)

# Process user feedback
feedback_result = feedback_engine.process_user_feedback(
    trace_id=result.trace_id,
    feedback_score=0.8,  # Positive feedback
    reason="Very helpful response",
    session_id="session_123"
)

print(f"Feedback applied: {feedback_result['status']}")
```

## 🔧 API Endpoints

### Core Operations

- `POST /api/v1/ingest` - Add content to the lattice
- `POST /api/v1/crystallize` - Generate dynamic prompts
- `POST /api/v1/feedback` - Apply user feedback
- `GET /api/v1/lattice/stats` - Get lattice statistics
- `GET /api/v1/feedback/stats` - Get learning statistics

### Maintenance

- `POST /api/v1/maintenance/decay` - Apply natural decay
- `POST /api/v1/maintenance/cleanup` - Clean up old data
- `GET /api/v1/sessions/{id}` - Get session information

## 🧪 Testing

Run the demo script to verify functionality:

```bash
python demo.py
```

For automated testing:

```bash
pytest tests/
```

## 📚 Documentation

- [Architecture Whitepaper](ARCHITECTURE_WHITEPAPER.md) - Theoretical foundation
- [API Reference](API_REFERENCE.md) - Complete API documentation
- [System Constants](epa/config.py) - Configuration parameters

## 🛡️ Safety Features

EPA includes comprehensive safety validation:

- **Input Validation**: Checks for injection attempts, high entropy, and toxic content
- **Prompt Safety**: Validates generated prompts against ethical constraints
- **Output Filtering**: Scans LLM outputs for PII, system leakage, and harmful content
- **Immutable Anchors**: Protects core ethical constraints from modification

## 🔄 Learning System

The system continuously improves through:

- **Explicit Feedback**: Direct user feedback on responses
- **Implicit Feedback**: Inferred from user behavior patterns  
- **Self-Reflection**: System monitors its own performance
- **Decay Mechanisms**: Natural forgetting to prevent information overload

## 🤝 Contributing

We welcome contributions! Please see our [Contributor Covenant](CONTRIBUTOR_COVENANT.md) for guidelines.

### Development Setup

```bash
# Clone and install
git clone <repository>
cd emergent-prompt-architecture
pip install -r requirements.txt

# Run development server
python api_server.py --reload
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Acknowledgments

Inspired by NeuralBlitz v50 architectures and built on the shoulders of the open-source AI community.

---

**GoldenDAG**: `e9f0c2a4e6b9d1f3a5c7e9b0d2d4f6a9b1c3d5e7f0a2c4e6b8d0f1a2c3e4b5d6`  
**Trace ID**: `T-v1.0-SETUP_COMPLETE-9a3f1c7e2d5b0a4c8e6f1d3b5a7c9e1f`  
**Codex ID**: `C-V1-PYTHON_IMPLEMENTATION-emergent_prompt_architecture_v1`