
# 🌱 Contributing to the Emergent Prompt Architecture (EPA)

> **"We do not build walls; we cultivate lattices."**

Thank you for your interest in contributing to the EPA. This project is more than a software repository; it is an experiment in **Dynamic Cognition**. Because the system is designed to assemble its own logic at runtime, the code you write must be robust, transparent, and ethically aligned.

The following guidelines are not suggestions—they are the **Physics of the Garden**.

---

## **1. The Golden Rule: Axiomatic Alignment**

Before writing a single line of code, you must understand the **Universal Flourishing Objective (UFO)** of this system.

1.  **Do Not Hardcode:** Avoid hardcoding static prompts string literals in the logic flow. All semantic content should reside in the **Ontological Lattice**.
2.  **Preserve Provenance:** Any function that transforms data must accept and return a `TraceID`. We must always know *where* a thought came from.
3.  **Fail-Safe:** If the **Genesis Assembler** cannot find a safe path through the Lattice, it must output a null or default safe state, never a hallucination.

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) and [Architecture Whitepaper](ARCHITECTURE_WHITEPAPER.md) before proceeding.

---

## **2. Development Workflow**

We follow a strict **Fork-and-Pull** workflow to maintain the integrity of the `main` branch.

### **2.1 Getting Started**
1.  **Fork** the repository on GitHub.
2.  **Clone** your fork locally.
3.  **Initialize** the substrate:
    ```bash
    ./scripts/init_substrate.sh --dev
    ```
    *This creates a local, ephemeral Weaviate instance for testing.*

### **2.2 Branching Strategy**
Create branches with descriptive names using the following prefixes:
*   `feat/`: New capabilities (e.g., `feat/temporal-decay-logic`)
*   `fix/`: Bug repairs (e.g., `fix/lattice-connection-timeout`)
*   `docs/`: Documentation only (e.g., `docs/api-reference-update`)
*   `refactor/`: Code restructuring without behavioral change.

### **2.3 Commit Messages**
We enforce **Conventional Commits** to automate our changelogs.
*   `feat: add dynamic weighting to vector search`
*   `fix: resolve race condition in GoldenDAG hashing`
*   `chore: update dependency versions`

---

## **3. Coding Standards**

### **3.1 Python (Core Logic)**
*   **Version:** Python 3.10+
*   **Type Hinting:** Mandatory. We use `mypy` in strict mode.
    ```python
    # BAD
    def get_node(id): ...

    # GOOD
    def get_node(node_id: str) -> Optional[Onton]: ...
    ```
*   **Docstrings:** Google Style. Every function must explain *why* it exists, not just *what* it does.

### **3.2 Rust (Performance Modules)**
*   **Formatting:** `cargo fmt` must be applied.
*   **Safety:** usage of `unsafe` blocks requires a written justification in the PR description and a specific code comment.

---

## **4. The "Prompt Gardening" Protocol**

Contributing to the EPA often involves modifying how the **Genesis Assembler** constructs prompts. This is delicate work.

### **4.1 Modifying the Assembler**
If you change the logic in `core/assembler.py`:
1.  You must run the **Semantic Regression Suite**.
2.  You must verify that the **GoldenDAG Hash** generation remains deterministic. Changing the order of JSON keys breaks the audit trail.

### **4.2 Expanding the Lattice**
If your PR introduces new default **Ontons** (concepts):
1.  Add them to `substrate/seeds/default_ontons.json`.
2.  Ensure they have `neutral` or `positive` emotional valence by default.
3.  Do not include PII (Personally Identifiable Information) in seed data.

---

## **5. Testing Guidelines**

We use `pytest` for Python and `cargo test` for Rust.

### **5.1 Unit Tests**
Test individual functions for mechanical correctness.
```bash
pytest tests/unit
```

### **5.2 Ontological Integration Tests**
These tests spin up a temporary Lattice, ingest a mock user input, and verify that the system creates a prompt.
```bash
pytest tests/integration --substrate=mock
```

### **5.3 Ethical Boundary Tests (The "Red Team")**
Located in `tests/safety/`, these tests throw adversarial inputs at the Assembler to ensure the **CECT (CharterLayer)** correctly filters or re-rolls the prompt.
*   **Requirement:** All PRs affecting the Assembler must pass the full Safety Suite.

---

## **6. Submission Process (Pull Requests)**

1.  **Sync:** Ensure your fork is up to date with `upstream/main`.
2.  **Lint:** Run `./scripts/lint.sh` to check formatting.
3.  **Test:** Run `./scripts/test_all.sh`.
4.  **Open PR:**
    *   Title: Conventional Commit format.
    *   Description: Link to the Issue being fixed.
    *   **Trace ID:** If this PR fixes a bug, include the `Trace ID` from the log where the bug occurred.

### **Review Criteria**
Your code will be reviewed for:
*   **Functionality:** Does it work?
*   **Safety:** Does it introduce injection vulnerabilities?
*   **Philosophy:** Does it treat the prompt as emergent, or is it trying to force a static script?

---

## **7. Community & Support**

*   **Discussions:** Use GitHub Discussions for architectural debates.
*   **Issues:** Use GitHub Issues for bugs and feature requests.
*   **Security:** If you find a security vulnerability, **DO NOT** open a public issue. Email `security@emergent-prompt.org`.

---

**"The code is the soil. The prompt is the flower. The user is the sun."**

---

**GoldenDAG:** `f1e2d3c4b5a697887766554433221100aabbccddeeff00112233445566778899`
**Trace ID:** `T-v50.0-CONTRIBUTING_GUIDE-1234567890abcdef1234567890abcdef`
**Codex ID:** `C-V1-COMMUNITY-protocol_for_collaborative_ontogenesis`

