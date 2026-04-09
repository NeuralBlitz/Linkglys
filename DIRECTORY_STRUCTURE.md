# NeuralBlitz / OpenCode LRS — Directory Structure

**Last Updated:** April 9, 2026

---

## Overview

This document explains every directory in the project, what it contains, and how components relate to each other.

---

## Root-Level Structure

```
/home/runner/workspace/
├── 📄 README.md                          # Main project overview (887 lines)
├── 📄 ARCHITECTURE.md                    # System architecture (NEW)
├── 📄 DEVELOPMENT_SETUP.md               # Dev environment setup (NEW)
├── 📄 TESTING.md                         # Testing guide (NEW)
├── 📄 TROUBLESHOOTING.md                 # Common issues & solutions (NEW)
├── 📄 CONTRIBUTING.md                    # Contribution guidelines (EXPANDED)
├── 📄 DOCUMENTATION_AUDIT.md             # Documentation coverage audit
├── 📄 neuralblitz-presentation.md        # Marp slide deck presentation
├── 📄 OMEGA_CTOS_VISUALIZATION.txt       # Omega-Class Task Orchestration
│
├── 📦 package.json                       # Node.js package config (scripts, deps)
├── 📦 pyproject.toml                     # Python package config (deps, pytest, ruff)
├── 📦 docker-compose.yml                 # Monitoring stack (InfluxDB, TimescaleDB, Prometheus, Grafana)
├── 📦 tsconfig.json                      # TypeScript configuration
├── 📦 .gitignore                         # Git ignore patterns
├── 📦 .gitmodules                        # Git submodule references
├── 📦 .lrsgate                           # LRS gate configuration
│
├── 📂 src/                               # ⭐ MAIN APPLICATION — FastAPI backend
├── 📂 lrs_agents/                        # LRS Active Inference Framework
├── 📂 neuralblitz-v50/                   # Cognitive Consciousness Engine
├── 📂 neuralblitz-dashboard/             # React web dashboard
├── 📂 neuralblitz-mobile/                # React Native mobile app
├── 📂 neuralblitz_slack_bot/             # Slack bot integration
├── 📂 voice_interface/                   # Voice interface (Whisper + TTS)
├── 📂 iot_mesh_system/                   # MQTT-based IoT mesh
├── 📂 edge_computing/                    # Edge device deployments
├── 📂 serverless/                        # Serverless Framework config
├── 📂 serverless_deployments/            # Multi-cloud serverless (AWS, Azure, GCP)
├── 📂 Governance/                        # Ethics monitoring systems
├── 📂 CapabilityKernels/                 # Audio processing kernels
├── 📂 plugins/                           # Plugin system (hot-loadable)
├── 📂 tests/                             # Root-level test suite (27 files)
├── 📂 docs/                              # Technical documentation hub (43 files)
├── 📂 influxdb/                          # InfluxDB telemetry client
├── 📂 timescaledb/                       # TimescaleDB agent metrics
├── 📂 prometheus/                        # Prometheus monitoring config
├── 📂 ipfs_integration/                  # IPFS decentralized storage
├── 📂 schemas/                           # JSON schema definitions
├── 📂 reports/                           # Generated reports
├── 📂 language-configurations/           # VS Code language configs
├── 📂 syntaxes/                          # Syntax highlighting definitions
│
├── 📂 .agents/skills/                    # 150+ AI skill definitions
├── 📂 .github/                           # GitHub CI/CD workflows
├── 📂 .config/                           # Application configurations
├── 📂 .local/                            # Local skills and storage
├── 📂 _quarantine/                       # Experimental/quarantined code
└── 📂 vs-code/                           # VS Code extension
```

---

## Detailed Directory Breakdown

### `src/` — Main Application

The core FastAPI backend running on port 5000.

```
src/
├── main.py                              # Entry point — starts uvicorn on port 5000
├── server.py                            # Alternative server runner
├── app_factory.py                       # FastAPI v1 app factory (basic)
├── app_factory_v2.py                    # FastAPI v2 app factory (full — auth, cache, WebSocket, ML)
├── simple_app.py                        # Flask cognitive analysis UI (standalone)
├── ml_pipeline.py                       # scikit-learn ML pipeline (classifiers, regressors, clustering)
├── audio_processing.py                  # FFT audio feature extraction
│
├── 📂 middleware/                        # FastAPI middleware layer
│   ├── __init__.py                      # Package exports
│   ├── auth.py                          # JWT authentication (roles: Admin/Developer/Viewer/Agent)
│   ├── rate_limiter.py                  # Token bucket rate limiting
│   ├── cache.py                         # Redis + in-memory LRU cache
│   ├── websocket.py                     # WebSocket connection manager with rooms
│   ├── event_bus.py                     # Async pub/sub event bus
│   ├── metrics.py                       # Prometheus metrics (counters, gauges, histograms)
│   ├── database.py                      # SQLAlchemy ORM (User, Agent, Plugin models)
│   ├── health.py                        # Health check endpoint
│   └── task_queue.py                    # Background task queue
│
├── 📂 agents/                            # Autonomous agent systems
│   ├── advanced_autonomous_agent_framework.py  # Full AAF (1,471 lines) — goals, tools, memory, ethics
│   ├── multi_layered_multi_agent_system.py     # 5-tier agent hierarchy with batch processing
│   ├── distributed_mlmas.py                    # Multi-node coordination
│   └── autonomous_self_evolution_simplified.py # Evolutionary self-improvement
│
├── 📂 capabilities/                      # Capability Kernels (specialized processing)
│   ├── bioinformatics_ck.py             # Biopython sequence analysis
│   ├── ck_data_quality_assessment.py    # Missing values, outliers, distributions
│   ├── ck_feature_engineering_automation.py # Scaling, encoding, selection
│   ├── ck_ml_automated_pipeline.py      # Model selection, hyperparameter optimization
│   ├── cv_capability_kernels.py          # Computer vision kernels
│   ├── malware_signature_analyzer_ck.py # Multi-hash signature matching, YARA
│   ├── network_anomaly_detector_ck.py   # Statistical + ML anomaly detection
│   ├── neuralblitz_code_kernels.py      # AutoProgrammer, CodeReviewer, TestGenerator
│   └── quadratic_voting_ck.py           # Sybil-resistant quadratic voting
│
├── 📂 cities/                            # Smart city systems
│   ├── smart_city_traffic_optimization.py    # Traffic flow optimization
│   ├── smart_city_energy_management.py       # Energy grid management
│   ├── smart_city_safety_coordination.py     # Public safety coordination
│   └── smart_city_unified_controller.py      # Multi-system orchestration
│
├── 📂 federated/                         # Federated learning
│   ├── neuralblitz_federated_learning.py     # Core FL with differential privacy
│   ├── neuralblitz_federated_pysyft.py       # PySyft integration
│   └── test_neuralblitz_federated_learning.py
│
├── 📂 governance/                        # Ethics and governance
│   ├── governance_ethics_system.py      # AGES: Charter, Veritas, Judex, SentiaGuard, GoldenDAG
│   └── integrated_mas.py                # Combines MLMAS + AGES + Distributed
│
├── 📂 integrations/                      # Vector database connectors
│   ├── chromadb_integration.py          # ChromaDB local vector DB
│   ├── pinecone_integration.py          # Pinecone cloud vector DB
│   └── weaviate_integration.py          # Weaviate semantic search
│
├── 📂 utils/                             # Infrastructure utilities
│   ├── bci_security_implementation.py   # Brain-computer interface security
│   ├── blockchain_integration.py        # Blockchain provenance/audit
│   ├── dimensional_computing_demo.py    # Dimensional computing demos
│   ├── fault_tolerance_layer.py         # System fault tolerance
│   ├── network_topology_optimizer.py    # Network topology optimization
│   ├── neuro_symbiotic_demo.py          # Neuro-symbiotic computing
│   ├── quantum_foundation_demo.py       # Quantum computing demos
│   └── raft_consensus.py                # RAFT distributed consensus
│
├── 📂 commands/                          # VS Code NBCL commands (TypeScript)
│   └── nbclCommands.ts
│
├── 📂 debugger/                          # VS Code debug adapter (TypeScript)
│   ├── debugAdapter.ts
│   └── debugSession.ts
│
├── 📂 providers/                         # VS Code language providers (TypeScript)
│   ├── ckCompletionProvider.ts          # Capability Kernel completion
│   ├── nbclCompletionProvider.ts        # NBCL completion
│   ├── nbclDiagnosticProvider.ts        # NBCL diagnostics
│   ├── nbclDocumentSymbolProvider.ts    # Document symbols
│   └── nbclHoverProvider.ts             # Hover info
│
└── 📂 util/                              # VS Code utilities (TypeScript)
    ├── ckRegistry.ts                    # CK registry
    └── nbosClient.ts                    # NeuralBlitz OS client
```

### `lrs_agents/` — LRS Active Inference Framework

AI agents based on Free Energy Principle. See `lrs_agents/README.md` for full details.

```
lrs_agents/
├── README.md                            # Main documentation (931 lines)
├── pyproject.toml                       # Package configuration
├── 📂 lrs/                              # Core LRS package
│   ├── 📂 core/                         # Precision, lenses, free energy
│   ├── 📂 agents/                       # Orchestrator, coder, tester, planner, etc.
│   ├── 📂 enterprise/                   # Distributed, security, monitoring
│   ├── 📂 monitoring/                   # Performance, health checks, logging
│   ├── 📂 neuralblitz_integration/      # Bridge to NeuralBlitz v50
│   └── 📂 integration/                  # LangChain, OpenAI, AutoGPT adapters
├── 📂 integration-bridge/               # OpenCode ↔ LRS bridge (separate sub-project)
├── 📂 docs/                             # Tutorials (8 Jupyter notebooks), logs, phase reports
├── 📂 tests/                            # Unit, integration, e2e, performance, stress, security
├── 📂 docker/                           # Dockerfile, docker-compose.yml, entrypoint.sh
├── 📂 k8s/                              # Kubernetes manifests
├── 📂 deploy/                           # Deployment scripts
└── 📂 .github/workflows/                # CI, docs, publish, test
```

### `neuralblitz-v50/` — Cognitive Consciousness Engine

Multi-language cognitive engine. See `neuralblitz-v50/README.md` for full details.

```
neuralblitz-v50/
├── README.md                            # Main documentation (842 lines)
├── 📂 python/                           # Python implementation
│   └── 📂 neuralblitz/                  # Core package (minimal, advanced, production engines)
├── 📂 go/                               # Go implementation
├── 📂 rust/                             # Rust implementation
├── 📂 java/                             # Java implementation
├── 📂 js/                               # JavaScript implementation
├── 📂 c/                                # C implementation
├── 📂 cpp/                              # C++ implementation
├── 📂 haskell/                          # Haskell implementation
├── 📂 scala/                            # Scala implementation
├── 📂 ocaml/                            # OCaml implementation
├── 📂 reasonml/                         # ReasonML implementation
├── 📂 Emergent-Prompt-Architecture/     # Dynamic prompt evolution (532 files)
├── 📂 Advanced-Research/                # Quantum, dimensional, BCI research
├── 📂 ComputationalAxioms/              # Mathematical/crypto foundation
├── 📂 docker/                           # Docker configurations (Go, Python, Rust)
├── 📂 k8s/                              # Kubernetes deployments
├── 📂 sql/                              # Database schemas and migrations
├── 📂 scripts/                          # Deployment and utility scripts
├── 📂 monitoring/                       # Prometheus configuration
├── 📂 notebooks/                        # Jupyter notebooks
├── 📂 examples/                         # Example code
├── 📂 lib/                              # Bash and NixOS libraries
└── 📂 .github/workflows/                # Build, docs, minimal, test
```

### `neuralblitz-dashboard/` — React Web Dashboard

```
neuralblitz-dashboard/
├── package.json                         # React package config
├── 📂 components/
│   ├── AgentMonitoring.js               # Agent status monitoring
│   ├── DashboardHeader.js               # Dashboard header component
│   ├── DimensionalComputing.js          # Dimensional computing metrics
│   ├── EthicsCompliance.js              # Ethics compliance dashboard
│   └── RealTimeMetrics.js               # Real-time performance metrics
├── 📂 public/
│   └── README.md
├── App.js                               # Main app with routing
└── index.js                             # Entry point
```

### `neuralblitz-mobile/` — React Native Mobile App

```
neuralblitz-mobile/
├── package.json                         # React Native package config
├── 📂 navigation/
│   └── AppNavigator.tsx                 # React Navigation setup
├── 📂 screens/
│   ├── AgentControlScreen.tsx           # Agent management screen
│   ├── NotificationsScreen.tsx          # Notifications screen
│   └── VoiceCommandScreen.tsx           # Voice command screen
├── 📂 services/
│   ├── ApiService.ts                    # REST API client
│   ├── NotificationService.ts           # Push notifications
│   └── VoiceService.ts                  # Voice commands
└── App.tsx                              # Root component
```

### `neuralblitz_slack_bot/` — Slack Integration

```
neuralblitz_slack_bot/
├── README.md                            # Bot documentation (215 lines)
├── bot.py                               # Main bot application (slash commands)
├── command_handlers.py                  # Command logic
├── interactive_handlers.py              # Modal and button handlers
├── event_handlers.py                    # Real-time event processing
├── config.py                            # Configuration
└── test_bot.py                          # Tests
```

### `voice_interface/` — Voice Interface

```
voice_interface/
├── voice_interface.py                   # Complete voice interface (Whisper STT + TTS)
├── test_simple.py                       # Simple tests
├── examples.py                          # Usage examples
├── REPORT.md                            # Technical report
├── IMPLEMENTATION_SUMMARY.md            # Implementation summary
├── QUICKSTART.md                        # Quick start guide
└── requirements.txt                     # Python dependencies
```

### `iot_mesh_system/` — IoT Mesh Networking

```
iot_mesh_system/
├── iot_mesh_core.py                     # Core IoT system (MQTT, device registry, automation)
├── iot_mesh_unified.py                  # Unified IoT mesh system
├── mqtt_broker.py                       # MQTT broker manager
├── device_discovery.py                  # mDNS + SSDP device discovery
├── automation_engine.py                 # Rule engine and scene management
├── database.py                          # SQLite device database
├── docker-compose.yml                   # Docker deployment
├── Dockerfile                           # Docker image
├── config/mosquitto.conf                # Mosquitto MQTT config
├── IOT_MESH_REPORT.md                   # Technical report
├── requirements.txt                     # Python dependencies
└── test_iot_mesh.py                     # Tests
```

### `edge_computing/` — Edge Device Deployments

```
edge_computing/
├── jetson_nano_inference.py             # NVIDIA Jetson Nano deployment
├── coral_tpu_inference.py               # Google Coral TPU deployment
├── 📂 deployment/
│   └── edge_deployment.py               # Unified edge deployment manager
├── 📂 raspberry_pi/
│   └── deploy_raspberry_pi.sh           # Raspberry Pi deployment script
└── 📂 (platform READMEs)
```

### `serverless/` and `serverless_deployments/` — Multi-Cloud Serverless

```
serverless/
├── README.md                            # Serverless deployment guide (515 lines)
├── 📂 src/
│   └── lambda_handler.py                # AWS Lambda handler
├── serverless.yml                       # Serverless Framework config
├── deploy.sh                            # Deployment script
└── requirements.txt

serverless_deployments/
├── README.md                            # Multi-cloud overview
├── SERVERLESS_DEPLOYMENT_REPORT.md      # Deployment report
├── 📂 aws_lambda/                       # AWS Lambda (SAM template, inference handler)
├── 📂 azure_functions/                  # Azure Functions (audit, governance, inference)
└── 📂 google_cloud_run/                 # GCP Cloud Run (Docker, Terraform)
```

### `Governance/` — Ethics Monitoring Systems

```
Governance/
├── 📂 SentiaGuard/
│   └── EarlyWarningSystem.py            # LSTM-based ethical drift detection
├── 📂 Conscientia/
│   └── MultiMetricMonitor.py            # 14 correlated ethical metrics
└── 📂 Veritas/
    └── AutomatedRCA.py                  # Root cause analysis
```

### `CapabilityKernels/` — Audio Processing Kernels

```
CapabilityKernels/
├── realtime_analyzer_ck.py              # Real-time audio analysis
├── realtime_analyzer_ck.json            # CK metadata/contract
├── sound_classifier_ck.py               # Sound classification kernel
├── sound_classifier_ck.json
├── speech_recognizer_ck.py              # Speech recognition kernel
└── speech_recognizer_ck.json
```

### `plugins/` — Plugin System

```
plugins/
├── sample_lrs_plugin.py                 # Sample LRS plugin
└── sample_tool_plugin.py                # Sample tool plugin
# Drop any .py file here → auto-loaded on server start
```

### `tests/` — Root-Level Test Suite

```
tests/
├── test_agents.py                       # Agent module loading
├── test_capabilities.py                 # Capability kernel loading
├── test_cities.py                       # Smart city module loading
├── test_governance_modules.py           # Governance module loading
├── test_lrs_core.py                     # LRS core (precision, lens, registry)
├── test_neuralblitz_v50_core.py         # NeuralBlitz v50 loading
├── test_edge_computing.py               # Edge computing loading
├── test_voice_interface_full.py         # Voice interface loading
├── test_iot_mesh_full.py                # IoT mesh loading
├── test_federated_full.py               # Federated learning loading
├── test_governance_full.py              # Governance loading
├── test_simple_app.py                   # Flask app tests
├── test_app_factory.py                  # FastAPI app factory tests
├── 📂 agents/                           # Agent-specific tests
├── 📂 capabilities/                     # Capability kernel tests
├── 📂 cities/                           # Smart city tests
├── 📂 federated/                        # Federated learning tests
├── 📂 governance/                       # Governance tests
├── 📂 integrations/                     # Vector DB integration tests
└── 📂 utils/                            # Utility module tests
```

### `docs/` — Technical Documentation Hub

```
docs/
├── README.md                            # Documentation hub index (208 lines)
├── AGENTS.md                            # Agent guidelines (3,271 lines)
├── API_REFERENCE.md                     # API documentation (742 lines)
├── INSTALLATION.md                      # Setup instructions (456 lines)
├── [40+ technical reports]              # Blockchain, quantum, edge computing, etc.
└── Yea.md                               # Placeholder
```

### `influxdb/`, `timescaledb/`, `prometheus/` — Monitoring Stack

```
influxdb/
├── influxdb_telemetry_client.py         # Telemetry client
├── config/influxdb.conf                 # InfluxDB configuration
└── init/                                # Initialization scripts

timescaledb/
├── timescaledb_agent_client.py          # TimescaleDB agent client
└── init/01-init-schema.sql              # Schema with hypertables

prometheus/
├── prometheus.yml                       # Scrape configuration
├── alerts.yml                           # Alert rules
├── recording-rules.yml                  # Recording rules
└── prometheus_integration_client.py     # Python metrics push client
```

### Other Directories

```
ipfs_integration/
├── ipfs_manager.py                      # IPFS storage, cache, pinning managers
├── __init__.py
├── requirements.txt
└── REPORT.md

schemas/
├── 📂 capabilities/                     # CK JSON schemas
├── 📂 deployments/                      # Deployment schemas
├── bioinformatics_ck_contracts.json
├── cybersecurity_ck_registry.json
└── voting_systems_report_metadata.json

reports/
├── ethical_drift_detection_improvements_v1.md
├── autonomous_self_evolution_upgrades_report.py
├── mlmas_upgrades_report.py
└── stage_clusters_5000_9999_deployment.py

language-configurations/                 # VS Code language-specific settings
syntaxes/                                # Syntax highlighting definitions (TextMate)
vs-code/                                 # VS Code extension (see src/commands/, src/debugger/, etc.)
.agents/skills/                          # 150+ AI skill definitions (SKILL.md files)
.github/                                 # GitHub workflows (dependabot.yml)
.config/                                 # Application configurations (matplotlib)
.local/                                  # Local skills and opencode storage
_quarantine/                             # Experimental/quarantined code
```

---

## Component Relationships

```
src/main.py
    │
    ├──→ app_factory_v2.py (FastAPI app)
    │       ├──→ middleware/ (auth, cache, WebSocket, events, metrics)
    │       ├──→ agents/ (autonomous systems)
    │       ├──→ capabilities/ (processing kernels)
    │       ├──→ cities/ (smart city systems)
    │       ├──→ federated/ (federated learning)
    │       ├──→ governance/ (ethics system)
    │       ├──→ integrations/ (vector DBs)
    │       └──→ ml_pipeline.py (scikit-learn)
    │
    ├──→ lrs_agents/ (optional import)
    │       └──→ LRS integration, multi-agent coordination
    │
    └──→ neuralblitz-v50/ (optional import)
            └──→ Cognitive engine, consciousness model

neuralblitz-dashboard/ → Fetches from src/ API
neuralblitz-mobile/    → Fetches from src/ API
neuralblitz_slack_bot/ → Fetches from src/ API

docker-compose.yml → InfluxDB + TimescaleDB + Prometheus + Grafana
```

---

*This document provides a complete map of the project. For component-specific documentation, see individual README files in each directory.*
