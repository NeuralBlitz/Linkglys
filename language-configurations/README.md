# Language Configurations — VS Code Language Settings

**Location:** `/home/runner/workspace/language-configurations/`  
**Purpose:** VS Code language-specific editor settings

---

## Overview

This directory contains **VS Code language configuration files** that define editor behavior for different programming languages used in the NeuralBlitz project. These configurations control:

- Comment syntax (`//`, `#`, `/* */`)
- Bracket pairs (`{}`, `[]`, `()`)
- Auto-closing pairs
- Auto-surrounding pairs
- Word pattern regexes
- Indentation rules
- Folding markers

---

## Supported Languages

| Language | File | Purpose |
|----------|------|---------|
| **Python** | `python-language-configuration.json` | NeuralBlitz backend, LRS-Agents |
| **TypeScript** | `typescript-language-configuration.json` | VS Code extension, mobile app |
| **JavaScript** | `javascript-language-configuration.json` | Dashboard, scripts |
| **Go** | `go-language-configuration.json` | NeuralBlitz v50 Go implementation |
| **Rust** | `rust-language-configuration.json` | NeuralBlitz v50 Rust implementation |
| **Java** | `java-language-configuration.json` | NeuralBlitz v50 Java implementation |

---

## Configuration Structure

Example Python configuration:

```json
{
  "comments": {
    "lineComment": "#",
    "blockComment": ["\"\"\"", "\"\"\""]
  },
  "brackets": [
    ["{", "}"],
    ["[", "]"],
    ["(", ")"]
  ],
  "autoClosingPairs": [
    { "open": "{", "close": "}" },
    { "open": "[", "close": "]" },
    { "open": "(", "close": ")" },
    { "open": "\"", "close": "\"", "notIn": ["string"] },
    { "open": "'", "close": "'", "notIn": ["string"] }
  ],
  "surroundingPairs": [
    { "open": "{", "close": "}" },
    { "open": "[", "close": "]" },
    { "open": "(", "close": ")" },
    { "open": "\"", "close": "\"" },
    { "open": "'", "close": "'" }
  ],
  "folding": {
    "markers": {
      "start": "^\\s*#\\s*region\\b",
      "end": "^\\s*#\\s*endregion\\b"
    }
  }
}
```

---

## How to Add a New Language

1. Create file: `new-language-language-configuration.json`
2. Define comment syntax, brackets, auto-closing pairs
3. Add to VS Code extension's `contributes.languages` in `package.json`
4. Test in Extension Development Host (F5)

---

## Usage

These configurations are loaded by VS Code automatically when editing files of the corresponding language. They improve the editing experience by enabling:

- Automatic comment insertion with `Ctrl+/`
- Auto-closing brackets and quotes
- Smart indentation
- Code folding with region markers
- Word selection patterns

---

## Related Documentation

- [syntaxes/README.md](../syntaxes/README.md) — Syntax highlighting definitions
- [vs-code/README.md](../vs-code/README.md) — VS Code extension documentation
- [VS Code Docs](https://code.visualstudio.com/api/language-extensions/language-configuration-guide)
