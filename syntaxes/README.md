# Syntaxes — Syntax Highlighting Definitions

**Location:** `/home/runner/workspace/syntaxes/`  
**Format:** TextMate Grammar (JSON)

---

## Overview

This directory contains **TextMate grammar definitions** for syntax highlighting in VS Code. These grammars define how different code elements are colored in the NeuralBlitz ecosystem, including:

- Keywords and operators
- Strings and comments
- Function and variable names
- Type annotations
- Language-specific constructs

---

## Supported Syntax Definitions

| File | Language | Purpose |
|------|----------|---------|
| `nbcl.tmLanguage.json` | NBCL | NeuralBlitz Command Language syntax highlighting |
| `ck.tmLanguage.json` | CK | Capability Kernel definition highlighting |

---

## NBCL Syntax Highlighting

NBCL (NeuralBlitz Command Language) is a domain-specific language for defining agent behaviors and workflows. The grammar defines highlighting for:

```nbcl
agent ResearchAgent {
    goal "research_topic" {
        steps: [search, analyze, summarize]
        priority: high
        ethical_constraints: [phi1, phi3, phi5]
    }
    
    on complete {
        notify #team
        save_to drs
    }
}
```

**Highlighted Elements:**
- `agent`, `goal`, `steps`, `priority` — Keywords (blue)
- `"research_topic"`, `#team` — Strings/identifiers (orange)
- `search`, `analyze`, `summarize` — Commands (green)
- `phi1`, `phi3`, `phi5` — Charter references (purple)
- `{}`, `[]`, `()` — Brackets (white)
- `on complete` — Event triggers (yellow)

---

## CK Syntax Highlighting

Capability Kernel definitions use a structured format:

```ck
kernel ml_pipeline {
    version: "1.0.0"
    inputs: [features: array, labels: array]
    outputs: [predictions: array, accuracy: float]
    
    pipeline {
        preprocess: StandardScaler()
        model: RandomForestClassifier(n_estimators=100)
        evaluate: accuracy_score(y_true, y_pred)
    }
}
```

**Highlighted Elements:**
- `kernel`, `version`, `inputs`, `outputs` — Keywords (blue)
- `ml_pipeline` — Kernel name (yellow)
- `StandardScaler()`, `RandomForestClassifier()` — Types (teal)
- `features`, `labels`, `predictions` — Variables (light blue)
- `"1.0.0"` — Strings (orange)
- `100` — Numbers (purple)

---

## Grammar Structure

TextMate grammars follow this structure:

```json
{
  "$schema": "https://raw.githubusercontent.com/martinring/tmlanguage/master/tmlanguage.json",
  "name": "NBCL",
  "scopeName": "source.nbcl",
  "patterns": [
    {
      "include": "#keywords"
    },
    {
      "include": "#strings"
    },
    {
      "include": "#comments"
    }
  ],
  "repository": {
    "keywords": {
      "match": "\\b(agent|goal|steps|priority|ethical_constraints)\\b",
      "name": "keyword.control.nbcl"
    },
    "strings": {
      "begin": "\"",
      "end": "\"",
      "name": "string.quoted.double.nbcl"
    }
  }
}
```

---

## Adding New Syntax Definitions

1. Create `new-language.tmLanguage.json`
2. Define `scopeName` (e.g., `source.newlang`)
3. Add patterns for keywords, strings, comments, etc.
4. Test in VS Code Extension Development Host (F5)
5. Add to extension's `contributes.grammars` in `package.json`

---

## Testing Syntax Highlighting

1. Open VS Code
2. Press F5 to launch Extension Development Host
3. Create a test file with the appropriate extension (`.nbcl`, `.ck`)
4. Verify syntax highlighting matches expectations
5. Adjust grammar patterns as needed

---

## Related Documentation

- [language-configurations/README.md](../language-configurations/README.md) — Language editor settings
- [vs-code/README.md](../vs-code/README.md) — VS Code extension documentation
- [src/providers/](../src/providers/) — VS Code language providers
- [TextMate Grammar Guide](https://macromates.com/manual/en/language_grammars)
