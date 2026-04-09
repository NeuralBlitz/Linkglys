# Schemas — JSON Schema Definitions

**Location:** `/home/runner/workspace/schemas/`  
**Format:** JSON Schema

---

## Overview

This directory contains **JSON schema definitions** that validate data structures across the NeuralBlitz platform, including Capability Kernel contracts, deployment configurations, and cybersecurity registries.

---

## Directory Structure

```
schemas/
├── bioinformatics_ck_contracts.json       # Bioinformatics CK contract schema
├── capabilities/                          # CK capability schemas
│   ├── data_quality_assessment.json       # Data quality assessment schema
│   ├── feature_engineering_automation.json # Feature engineering schema
│   └── ml_automated_pipeline.json         # ML pipeline schema
├── cybersecurity_ck_registry.json         # Cybersecurity CK registry
├── deployments/                           # Deployment schemas
│   ├── deployment_goldendag.json          # GoldenDAG deployment schema
│   └── deployment_summary.py              # Deployment summary generator
└── voting_systems_report_metadata.json    # Voting systems metadata schema
```

---

## Schema Categories

### 1. Capability Kernel Contracts

Define the interface and metadata for capability kernels:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Capability Kernel Contract",
  "type": "object",
  "required": ["name", "version", "description", "inputs", "outputs"],
  "properties": {
    "name": {"type": "string", "pattern": "^[a-z_]+$"},
    "version": {"type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$"},
    "description": {"type": "string", "minLength": 10},
    "inputs": {"type": "array", "items": {"type": "object"}},
    "outputs": {"type": "array", "items": {"type": "object"}},
    "capabilities": {"type": "array", "items": {"type": "string"}},
    "dependencies": {"type": "array", "items": {"type": "string"}}
  }
}
```

### 2. Deployment Schemas

Define deployment configurations with GoldenDAG provenance:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Deployment GoldenDAG Schema",
  "type": "object",
  "required": ["deployment_id", "trace_id", "signature", "timestamp"],
  "properties": {
    "deployment_id": {"type": "string"},
    "trace_id": {"type": "string", "pattern": "^T-v50\\.0-.*"},
    "signature": {"type": "string"},
    "timestamp": {"type": "string", "format": "date-time"},
    "context": {"type": "string"},
    "data": {"type": "object"}
  }
}
```

### 3. Cybersecurity CK Registry

Define the registry structure for cybersecurity capability kernels:

```json
{
  "kernels": [
    {
      "name": "malware_signature_analyzer",
      "version": "1.0.0",
      "capabilities": ["signature_matching", "yara_rules", "behavioral_analysis"],
      "status": "active"
    }
  ]
}
```

---

## Using Schemas for Validation

### Python Validation

```python
import json
import jsonschema

# Load schema
with open("schemas/capabilities/ml_automated_pipeline.json") as f:
    schema = json.load(f)

# Validate data
data = {
    "name": "ml_pipeline",
    "version": "1.0.0",
    "description": "Automated ML pipeline",
    "inputs": [{"name": "features", "type": "array"}],
    "outputs": [{"name": "predictions", "type": "array"}]
}

jsonschema.validate(data, schema)
print("Data is valid!")
```

### Command Line

```bash
# Install jsonschema CLI
pip install jsonschema

# Validate a file against a schema
jsonschema -i data.json schemas/capabilities/ml_automated_pipeline.json
```

---

## Schema Reference

### Capabilities

| Schema | Purpose | Required Fields |
|--------|---------|----------------|
| `data_quality_assessment` | Data quality CK contract | name, version, inputs, outputs, quality_metrics |
| `feature_engineering_automation` | Feature engineering CK contract | name, version, transformations, selection_methods |
| `ml_automated_pipeline` | ML pipeline CK contract | name, version, model_types, evaluation_metrics |

### Deployments

| Schema | Purpose | Required Fields |
|--------|---------|----------------|
| `deployment_goldendag` | GoldenDAG deployment record | deployment_id, trace_id, signature, timestamp |

### Contracts

| Schema | Purpose | Required Fields |
|--------|---------|----------------|
| `bioinformatics_ck_contracts` | Bioinformatics CK contracts | name, version, sequence_types, analysis_methods |
| `cybersecurity_ck_registry` | Cybersecurity CK registry | kernels, version, last_updated |
| `voting_systems_report_metadata` | Voting systems metadata | version, report_date, voting_method |

---

## Adding New Schemas

1. Create JSON file in appropriate subdirectory
2. Follow Draft-07 JSON Schema standard
3. Include `$schema`, `title`, `type`, `required`, `properties`
4. Add validation examples
5. Test against existing data

---

## Related Documentation

- [src/capabilities/README.md](src/capabilities/README.md) — Capability Kernels
- [CapabilityKernels/README.md](CapabilityKernels/README.md) — Audio processing kernels
- [CK Contract Schema](src/capabilities/README.md#ck-contract-schema) — Schema specification
