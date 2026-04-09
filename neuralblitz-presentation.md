---
marp: true
theme: default
paginate: true
---

<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&family=Fira+Code:wght@400;500;700&display=swap');

:root {
  --color-background: #0d1117;
  --color-foreground: #c9d1d9;
  --color-heading: #58a6ff;
  --color-accent: #7ee787;
  --color-code-bg: #161b22;
  --color-border: #30363d;
  --font-default: 'Noto Sans JP', 'Hiragino Kaku Gothic ProN', 'Meiryo', sans-serif;
  --font-code: 'Fira Code', 'Consolas', 'Monaco', monospace;
}

section {
  background-color: var(--color-background);
  color: var(--color-foreground);
  font-family: var(--font-default);
  font-weight: 400;
  box-sizing: border-box;
  border-left: 4px solid var(--color-accent);
  position: relative;
  line-height: 1.6;
  font-size: 20px;
  padding: 56px;
}

h1, h2, h3, h4, h5, h6 {
  font-weight: 700;
  color: var(--color-heading);
  margin: 0;
  padding: 0;
  font-family: var(--font-code);
}

h1 {
  font-size: 52px;
  line-height: 1.3;
  text-align: left;
}

h1::before {
  content: '# ';
  color: var(--color-accent);
}

h2 {
  font-size: 38px;
  margin-bottom: 40px;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--color-border);
}

h2::before {
  content: '## ';
  color: var(--color-accent);
}

h3 {
  color: var(--color-foreground);
  font-size: 26px;
  margin-top: 32px;
  margin-bottom: 12px;
}

h3::before {
  content: '### ';
  color: var(--color-accent);
}

ul, ol {
  padding-left: 32px;
}

li {
  margin-bottom: 10px;
}

li::marker {
  color: var(--color-accent);
}

pre {
  background-color: var(--color-code-bg);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 16px;
  overflow-x: auto;
  font-family: var(--font-code);
  font-size: 16px;
  line-height: 1.5;
}

code {
  background-color: var(--color-code-bg);
  color: var(--color-accent);
  padding: 2px 6px;
  border-radius: 3px;
  font-family: var(--font-code);
  font-size: 0.9em;
}

pre code {
  background-color: transparent;
  padding: 0;
  color: var(--color-foreground);
}

footer {
  font-size: 14px;
  color: #8b949e;
  font-family: var(--font-code);
  position: absolute;
  left: 56px;
  right: 56px;
  bottom: 40px;
  text-align: right;
}

footer::before {
  content: '// ';
  color: var(--color-accent);
}

section.lead {
  border-left: 4px solid var(--color-accent);
  display: flex;
  flex-direction: column;
  justify-content: center;
}

section.lead h1 {
  margin-bottom: 24px;
}

section.lead p {
  font-size: 22px;
  color: var(--color-foreground);
  font-family: var(--font-code);
}

strong {
  color: var(--color-accent);
  font-weight: 700;
}
</style>

<!-- _class: lead -->

# NeuralBlitz Platform

AI Agent Ecosystem & Extension Framework

---

## Overview

NeuralBlitz is an **AI development platform** combining:

- **LRS-Agents**: Active inference agents with precision tracking
- **Plugin System**: Dynamic extension architecture
- **150+ Skills**: Pre-built AI capabilities
- **Multi-Frontend**: Web dashboard + mobile app
- **FastAPI Backend**: REST API on port 5000

---

## Core Architecture

```
┌─────────────────────────────────┐
│   Frontend (React / Expo)       │
├─────────────────────────────────┤
│   FastAPI Backend (Python)      │
│   ├── LRS-Agents Framework      │
│   ├── Plugin Registry           │
│   └── Multi-Agent Coordination  │
├─────────────────────────────────┤
│   AI Skills & Integrations      │
└─────────────────────────────────┘
```

---

## Plugin System

**Fully functional extension architecture:**

- **Dynamic discovery** from `./plugins/` directory
- **Hot loading/unloading** via `importlib`
- **Hook registration** & event emission
- **JSON persistence** for state

**Plugin types:**
- `ToolPlugin` — Commands, tools, APIs
- `LRSPlugin` — Precision tracking & inference
- `TUIPlugin` — Terminal visualizations

---

## Available Skills (150+)

**Development**: architecture-patterns, nodejs-backend, next-best-practices

**Testing**: e2e-testing, javascript-testing, vitest, qa-test-planner

**AI/ML**: ai-sdk, llm-evaluation, embedding-strategies, mcp-builder

**Design**: frontend-design, shadcn-ui, tailwind-design-system, ui-ux-pro-max

**Marketing**: copywriting, seo-audit, paid-ads, social-content

**Content**: docx, pdf, pptx, xlsx, baoyu-post-to-wechat, baoyu-post-to-x

---

## How to Build Extensions

**Create a new plugin:**

```python
from lrs.enterprise.opencode_plugin_architecture import ToolPlugin

class MyPlugin(ToolPlugin):
    def get_metadata(self):
        return PluginMetadata(
            name="my-plugin",
            version="1.0.0",
            description="My custom extension"
        )
    
    def initialize(self):
        # Setup logic
        pass
```

Drop in `plugins/` → auto-loaded!

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI, Uvicorn, Pydantic |
| **AI/LLM** | OpenAI, Anthropic, Google, Ollama |
| **Frontend** | React, Bun, Expo/React Native |
| **Testing** | pytest, pytest-asyncio |
| **Monitoring** | Docker, Prometheus, Grafana |
| **Vector DB** | ChromaDB, Pinecone, Weaviate |

---

## Key Directories

```
/home/runner/workspace/
├── lrs_agents/        # LRS-Agents framework
├── src/               # FastAPI application
├── plugins/           # Drop plugins here
├── .agents/skills/    # 150+ AI skills
├── neuralblitz-v50/   # Cognitive engine
├── neuralblitz-dashboard/  # React web UI
└── neuralblitz-mobile/     # Expo mobile app
```

---

## Getting Started

1. **Explore the codebase** — Understand LRS-Agents architecture
2. **Create a plugin** — Add `.py` file to `plugins/`
3. **Use skills** — Invoke AI capabilities via skill system
4. **Run the server** — `python src/main.py` on port 5000
5. **Build frontend** — Dashboard & mobile apps

---

<!-- _class: lead -->

# Questions?

Build your own extensions today!
