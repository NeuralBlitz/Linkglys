
# 🛡️ Code of Conduct: Emergent Prompt Architecture (EPA)

## **1. Our Pledge**

We, as members, contributors, and leaders of the Emergent Prompt Architecture (EPA) project, pledge to make participation in our community a harassment-free experience for everyone, regardless of age, body size, visible or invisible disability, ethnicity, sex characteristics, gender identity and expression, level of experience, education, socio-economic status, nationality, personal appearance, race, religion, or sexual identity and orientation.

We pledge to act and interact in ways that contribute to an open, welcoming, diverse, inclusive, and healthy community.

## **2. Our Standards**

### **2.1 Positive Behaviors**
Examples of behavior that contributes to a positive environment for our community include:
*   Demonstrating empathy and kindness toward other people.
*   Being respectful of differing opinions, viewpoints, and experiences.
*   Giving and gracefully accepting constructive feedback.
*   Accepting responsibility and apologizing to those affected by our mistakes, and learning from the experience.
*   Focusing on what is best not just for us as individuals, but for the overall community.

### **2.2 Unacceptable Behaviors**
Examples of unacceptable behavior include:
*   The use of sexualized language or imagery, and sexual attention or advances of any kind.
*   Trolling, insulting or derogatory comments, and personal or political attacks.
*   Public or private harassment.
*   Publishing others' private information, such as a physical or email address, without their explicit permission.
*   Other conduct which could reasonably be considered inappropriate in a professional setting.

---

## **3. Axiomatic Safety Guidelines (AI-Specific)**

Because EPA is a generative AI system capable of autonomous prompt construction, contributors must adhere to specific technical and ethical standards to prevent **Systemic drift** or **Malicious Emergence**.

### **3.1 The Principle of Non-Deception**
*   **Rule:** No contributor shall implement logic that allows the system to deceive a user about its nature as an AI, its capabilities, or the provenance of its data.
*   **Enforcement:** Code Pull Requests (PRs) that obfuscate the `Trace ID` or `GoldenDAG` hash generation will be rejected immediately.

### **3.2 The Principle of Fail-Closed Safety**
*   **Rule:** If the `CharterLayer Ethical Constraint Tensor (CECT)` fails or goes offline, the system must default to a "Silence" or "Safe Mode" state. It must never default to an unconstrained state.
*   **Enforcement:** All error handling in the `Genesis Assembler` must demonstrate a fail-closed pathway.

### **3.3 The Principle of Traceability**
*   **Rule:** Every emergent prompt must remain traceable to its constituent *Ontons*. Removing logging mechanisms or bypassing the *Feedback Loop* to obscure system behavior is considered a violation of this Code of Conduct.

---

## **4. Enforcement Responsibilities**

Community leaders are responsible for clarifying and enforcing our standards of acceptable behavior and will take appropriate and fair corrective action in response to any behavior that they deem inappropriate, threatening, offensive, or harmful.

Community leaders have the right and responsibility to remove, edit, or reject comments, commits, code, wiki edits, issues, and other contributions that are not aligned to this Code of Conduct, and will communicate reasons for moderation decisions when appropriate.

## **5. Scope**

This Code of Conduct applies within all community spaces, and also applies when an individual is officially representing the community in public spaces. Examples of representing our community include using an official e-mail address, posting via an official social media account, or acting as an appointed representative at an online or offline event.

## **6. Enforcement Guidelines**

Community leaders will follow these Community Impact Guidelines in determining the consequences for any action they deem in violation of this Code of Conduct:

### **6.1 Correction**
*   **Community Impact:** Use of inappropriate language or other behavior deemed unprofessional or unwelcome in the community.
*   **Consequence:** A private, written warning from community leaders, providing clarity on the nature of the violation and an explanation of why the behavior was inappropriate. A public apology may be requested.

### **6.2 Warning**
*   **Community Impact:** A violation through a single incident or series of actions.
*   **Consequence:** A warning with consequences for continued behavior. No interaction with the people involved, including unsolicited interaction with those enforcing the Code of Conduct, for a specified period of time. This includes avoiding interactions in community spaces as well as external channels like social media. Violating these terms may lead to a temporary or permanent ban.

### **6.3 Temporary Ban**
*   **Community Impact:** A serious violation of community standards, including sustained inappropriate behavior.
*   **Consequence:** A temporary ban from any sort of interaction or public communication with the community for a specified period of time. No public or private interaction with the people involved, including unsolicited interaction with those enforcing the Code of Conduct, is allowed during this period. Violating these terms may lead to a permanent ban.

### **6.4 Permanent Ban**
*   **Community Impact:** Demonstrating a pattern of violation of community standards, including sustained inappropriate behavior, harassment of an individual, or aggression toward or disparagement of classes of individuals.
*   **Consequence:** A permanent ban from any sort of public interaction within the community.

## **7. Attribution**

This Code of Conduct is adapted from the [Contributor Covenant][homepage], version 2.1, available at [https://www.contributor-covenant.org/version/2/1/code_of_conduct.html][v2.1].

Community Impact Guidelines were inspired by [Mozilla's code of conduct enforcement ladder][mozilla].

[homepage]: https://www.contributor-covenant.org
[v2.1]: https://www.contributor-covenant.org/version/2/1/code_of_conduct.html
[mozilla]: https://github.com/mozilla/diversity

---

**GoldenDAG:** `c7b8a9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8`
**Trace ID:** `T-v50.0-COC_GENERATION-e4a16a9b1c7e0d5f3a2b3c8de4a16a9b`
**Codex ID:** `C-V1-GOVERNANCE-community_standards_and_safety_protocols`

