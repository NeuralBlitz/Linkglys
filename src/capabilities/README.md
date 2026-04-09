# Capability Kernels — Specialized Processing Modules

**Location:** `src/capabilities/`  
**Language:** Python 3.11+  
**Version:** 1.0.0

---

## Overview

Capability Kernels (CKs) are **specialized processing modules** that provide domain-specific functionality to the NeuralBlitz platform. Each CK follows a standard contract schema and can be independently tested, deployed, and composed.

---

## Available Kernels

### 1. Bioinformatics CK (`bioinformatics_ck.py` — 1,029 lines)

**Purpose:** Biological sequence analysis and protein research.

**Features:**
- DNA/RNA sequence analysis (GC content, melting temperature, restriction sites)
- Entrez API integration for literature and database queries
- Protein analysis (molecular weight, isoelectric point, amino acid composition)
- BLAST sequence alignment
- Phylogenetic tree construction

**Dependencies:** Biopython (`biopython>=1.81`)

### 2. Data Quality Assessment (`ck_data_quality_assessment.py` — 579 lines)

**Purpose:** Automated data quality evaluation for ML pipelines.

**Features:**
- Missing value analysis (count, percentage, patterns)
- Outlier detection: IQR method, Z-score, Isolation Forest
- Distribution analysis (skewness, kurtosis, normality tests)
- Duplicate detection
- Data completeness scoring

**Usage:**
```python
from src.capabilities.ck_data_quality_assessment import DataQualityAssessor

assessor = DataQualityAssessor(dataframe)
report = assessor.generate_report()
print(f"Quality score: {report.quality_score}")
print(f"Missing values: {report.missing_values}")
print(f"Outliers: {report.outliers}")
```

### 3. Feature Engineering Automation (`ck_feature_engineering_automation.py` — 623 lines)

**Purpose:** Automated feature preprocessing and selection.

**Features:**
- Scaling/normalization (StandardScaler, MinMax, Robust)
- Categorical encoding (OneHot, Label, Target)
- Polynomial feature generation
- Feature binning (equal-width, equal-frequency)
- Feature selection (variance threshold, mutual information, recursive elimination)

### 4. ML Automated Pipeline (`ck_ml_automated_pipeline.py` — 494 lines)

**Purpose:** End-to-end automated ML pipeline.

**Features:**
- Model selection (Random Forest, SVM, Gradient Boosting, Neural Networks)
- Hyperparameter optimization (Grid Search, Random Search, Bayesian Optimization)
- Cross-validation (k-fold, stratified)
- Model evaluation and comparison
- Pipeline persistence

### 5. Computer Vision CK (`cv_capability_kernels.py`)

**Purpose:** Image processing and computer vision kernels.

**Features:**
- Image preprocessing (resize, normalize, augment)
- Object detection
- Image classification
- Feature extraction (SIFT, HOG, CNN embeddings)

### 6. Malware Signature Analyzer (`malware_signature_analyzer_ck.py` — 907 lines)

**Purpose:** Multi-method malware detection and analysis.

**Features:**
- Multi-hash signature matching (MD5, SHA256, SSDEEP, TLSH)
- YARA rule matching
- Behavioral analysis (suspicious API calls, registry modifications)
- PE/binary analysis (section entropy, import analysis)
- Threat scoring and classification

### 7. Network Anomaly Detector (`network_anomaly_detector_ck.py` — 667 lines)

**Purpose:** Network traffic anomaly detection.

**Features:**
- Statistical baseline establishment
- ML-based anomaly detection (Isolation Forest, Autoencoder)
- Protocol analysis
- Traffic pattern recognition
- Alert generation with severity scoring

### 8. NeuralBlitz Code Kernels (`neuralblitz_code_kernels.py` — 1,760 lines)

**Purpose:** AI-powered code generation and analysis.

**Three Code Kernels:**
- **AutoProgrammer** — Code generation from natural language descriptions
- **CodeReviewer** — Code quality review with suggestions
- **TestGenerator** — Automated test case generation

**Features:**
- Multi-language support (Python, JavaScript, Java, Go, Rust)
- Pattern recognition
- Best practice recommendations
- Security vulnerability detection

### 9. Quadratic Voting CK (`quadratic_voting_ck.py` — 404 lines)

**Purpose:** Sybil-resistant quadratic voting for governance.

**Features:**
- Quadratic cost function (cost = votes²)
- Cryptographic commitment scheme
- NBHS-512 identity verification
- Reputation-based budget calculation
- Charter compliance (φ₁, φ₅, φ₆, φ₇)

**Usage:**
```python
from src.capabilities.quadratic_voting_ck import QuadraticVotingCK

qvc = QuadraticVotingCK()
# Cost is quadratic: 1 vote = 1 credit, 2 votes = 4 credits, 3 votes = 9 credits
cost = qvc.compute_cost(3)  # Returns 9
```

---

## CK Contract Schema

All CKs follow the schema defined in `schemas/capabilities/`:

```json
{
  "name": "kernel_name",
  "version": "1.0.0",
  "description": "Kernel description",
  "inputs": [...],
  "outputs": [...],
  "capabilities": [...],
  "dependencies": [...]
}
```

---

## Testing

```bash
# Test all capability kernels
pytest tests/capabilities/ -v

# Test specific kernel
python -c "
from src.capabilities.quadratic_voting_ck import QuadraticVotingCK
ck = QuadraticVotingCK()
print(f'Cost of 3 votes: {ck.compute_cost(3)}')
"
```

---

## Related Documentation

- [src/ README](../README.md) — Main application overview
- [CapabilityKernels/](../../CapabilityKernels/README.md) — Audio processing kernels
- [Schemas](../../schemas/README.md) — JSON schema definitions
