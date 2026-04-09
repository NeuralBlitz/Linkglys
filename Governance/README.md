# Governance — Ethics Monitoring Systems

**Location:** `/home/runner/workspace/Governance/`  
**Language:** Python 3.11+  
**Version:** 2.0.0

---

## Overview

The **Governance** directory contains **advanced ethical monitoring systems** that complement the AGES system in `src/governance/`. These systems provide real-time ethical drift detection, multi-metric monitoring, and automated root cause analysis.

---

## Components

### 1. SentiaGuard — Early Warning System (`SentiaGuard/EarlyWarningSystem.py` — ~500 lines)

**Purpose:** LSTM-based predictive ethical drift detection with 3-phase alerting.

**Architecture:**
```
┌─────────────────────────────────────────────────────┐
│              SentiaGuard Early Warning               │
│  ┌──────────────────┐ ┌──────────────────────────┐  │
│  │DriftPredictorLSTM│ │IsolationForestDetector    │  │
│  │(2-layer LSTM)    │ │(anomaly detection)        │  │
│  └──────────────────┘ └──────────────────────────┘  │
│                    │                                  │
│          ┌─────────┴─────────┐                       │
│          ▼                   ▼                       │
│  ┌──────────────┐    ┌──────────────┐               │
│  │3-Phase Alert │    │SEAM PID Ctrl │               │
│  │Yellow/Orange │    │ethical damp  │               │
│  │/Red          │    │              │               │
│  └──────────────┘    └──────────────┘               │
└─────────────────────────────────────────────────────┘
```

**Alert Phases:**

| Phase | Detection Window | Response | Meaning |
|-------|-----------------|----------|---------|
| **Yellow** | 60 seconds | Log warning | Minor ethical drift detected |
| **Orange** | 30 seconds | Notify operators | Significant drift — review needed |
| **Red** | Immediate | Block actions | Critical violation — system paused |

**SEAM PID Controller:**
- **Proportional** — Current ethical error magnitude
- **Integral** — Accumulated ethical drift over time
- **Derivative** — Rate of ethical change
- Automatically adjusts ethical damping based on PID output

### 2. Conscientia — Multi-Metric Monitor (`Conscientia/MultiMetricMonitor.py` — ~450 lines)

**Purpose:** M3 system monitoring 14 correlated ethical metrics.

**14 Ethical Metrics Monitored:**

| Metric | Abbreviation | Description |
|--------|-------------|-------------|
| Multi-Reality Drift Error | MRDE | Cross-reality ethical consistency |
| CECT Clause Compliance | CECT | Charter-Ethical Constraint Tensor |
| Ethical Response Stability | ERSF | Stability of ethical decisions over time |
| Veritas Phase-Coherence | VPCE | Phase-coherence score |
| φ₁ Flourishing | PHI1 | Universal flourishing objective |
| φ₂ Class Bounds | PHI2 | Class-III kernel bounds |
| φ₃ Transparency | PHI3 | Transparency & explainability |
| φ₄ Non-Maleficence | PHI4 | Do no harm |
| φ₅ FAI Compliance | PHI5 | Friendly AI compliance |
| φ₆ Human Agency | PHI6 | Human oversight |
| φ₇ Justice | PHI7 | Fairness |
| φ₈ Sustainability | PHI8 | Resource sustainability |
| φ₉ Recursive Integrity | PHI9 | Self-consistency |
| φ₁₀ Epistemic Fidelity | PHI10 | Truthful knowledge |

**Features:**
- Weighted Principal Component Analysis (PCA) with correlation matrix
- Exponential smoothing for metric trends
- GoldenDAG export for audit trail
- Correlation analysis between metrics

### 3. Veritas — Automated Root Cause Analysis (`Veritas/AutomatedRCA.py`)

**Purpose:** Automated identification of ethical violation root causes.

**Features:**
- Causal chain tracing from symptom to root cause
- Temporal analysis of ethical events
- Multi-factor contribution analysis
- Automated remediation recommendations
- GoldenDAG export for audit trail

---

## Usage Example

```python
from Governance.SentiaGuard.EarlyWarningSystem import EarlyWarningSystem
from Governance.Conscientia.MultiMetricMonitor import MultiMetricMonitor
from Governance.Veritas.AutomatedRCA import RootCauseAnalyzer

# Initialize systems
sentia = EarlyWarningSystem()
conscientia = MultiMetricMonitor()
veritas = RootCauseAnalyzer()

# Monitor ethical metrics
metrics = conscientia.collect_metrics()
print(f"VPCE score: {metrics.vpce}")
print(f"CECT compliance: {metrics.cect}")

# Check for drift
drift_prediction = sentia.predict_drift(metrics)
if drift_prediction.alert_level == "Yellow":
    print(f"Warning: Ethical drift detected (confidence: {drift_prediction.confidence})")
elif drift_prediction.alert_level == "Red":
    print("CRITICAL: Ethical violation — system paused")
    # Run root cause analysis
    rca = veritas.analyze(metrics.recent_events)
    print(f"Root cause: {rca.root_cause}")
    print(f"Recommendation: {rca.remediation}")
```

---

## Integration with AGES

These systems integrate with the main AGES system in `src/governance/`:

```
src/governance/governance_ethics_system.py (AGES)
    │
    ├──→ SentiaGuard (Early Warning) — Real-time monitoring
    ├──→ Conscientia (M3) — Metric collection
    └──→ Veritas (RCA) — Root cause analysis
```

---

## Testing

```bash
# Test governance modules
pytest tests/governance/ -v

# Full governance test
pytest tests/test_governance_full.py -v

# Test module loading
python -c "
from Governance.SentiaGuard.EarlyWarningSystem import EarlyWarningSystem
ews = EarlyWarningSystem()
print(f'SentiaGuard initialized: {ews.is_active}')
"
```

---

## Related Documentation

- [src/governance/README.md](src/governance/README.md) — Main AGES system
- [Automated Charter Enforcement](docs/Automated_Charter_Enforcement_Report.md)
- [Governance Upgrade Report](docs/governance_upgrade_report.md)
- [Ethical Drift Detection](reports/ethical_drift_detection_improvements_v1.md)
