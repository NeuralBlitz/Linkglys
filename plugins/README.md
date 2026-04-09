# Plugins — Extension System

**Location:** `/home/runner/workspace/plugins/`  
**Language:** Python 3.11+

---

## Overview

The plugin system provides a **hot-loadable extension architecture** for NeuralBlitz. Any Python file placed in the `plugins/` directory is automatically discovered and registered on server start.

Plugins can add new tools, commands, LRS integration points, or terminal visualizations without modifying the core application.

---

## Plugin Types

| Type | Base Class | Purpose |
|------|------------|---------|
| **ToolPlugin** | `ToolPlugin` | Add new commands, tools, or APIs |
| **LRSPlugin** | `LRSPlugin` | Add precision tracking and inference capabilities |
| **TUIPlugin** | `TUIPlugin` | Add terminal-based visualizations |

---

## Quick Start

### Create a Plugin

```python
# plugins/my_custom_tool.py
from lrs.enterprise.opencode_plugin_architecture import ToolPlugin, PluginMetadata

class MyCustomTool(ToolPlugin):
    """A custom tool plugin that demonstrates the plugin interface."""

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my-custom-tool",
            version="1.0.0",
            description="A custom tool for NeuralBlitz",
            author="Your Name",
            tags=["tool", "example"]
        )

    def initialize(self):
        """Called when the plugin is loaded."""
        self.logger.info("MyCustomTool initialized")

    async def execute(self, **kwargs) -> dict:
        """Execute the tool's main functionality."""
        return {
            "status": "success",
            "message": f"Executed with args: {kwargs}"
        }

    def get_commands(self) -> list:
        """Return available commands for this plugin."""
        return ["my-tool"]
```

### Install the Plugin

```bash
# Simply drop the file into plugins/
cp my_custom_tool.py plugins/

# Plugins are auto-discovered on server restart
# List installed plugins
curl http://localhost:5000/api/v2/plugins
```

### Use the Plugin

```bash
# Via API
curl -X POST http://localhost:5000/api/v2/plugins \
  -H "Content-Type: application/json" \
  -d '{"name": "my-custom-tool", "version": "1.0.0"}'

# Via LRS agent
from lrs_agents.lrs import create_lrs_agent
agent = create_lrs_agent(tools=[my_custom_tool])
```

---

## Plugin Architecture

```
┌──────────────────────────────────────┐
│         Plugin Registry               │
│  ┌──────────────────────────────┐   │
│  │  Discovery: plugins/*.py     │   │
│  │  Loading: importlib          │   │
│  │  Hot reload: supported       │   │
│  └──────────────────────────────┘   │
│              │                        │
│     ┌────────┴────────┐              │
│     ▼                 ▼              │
│  ToolPlugin        LRSPlugin         │
│  (commands)    (precision)           │
│                                      │
│     ┌──────────────────┐            │
│     │  JSON Persistence │            │
│     │  (plugin state)   │            │
│     └──────────────────┘            │
└──────────────────────────────────────┘
```

### Lifecycle

1. **Discovery** — Server scans `plugins/*.py` on startup
2. **Loading** — Each `.py` file is imported via `importlib`
3. **Initialization** — `initialize()` method called
4. **Registration** — Plugin commands/tools registered
5. **Execution** — Plugin runs when invoked
6. **State Persistence** — Plugin state saved to JSON
7. **Hot Unload** — Plugin removed from registry (if supported)

---

## Sample Plugins

### 1. `sample_lrs_plugin.py`

Demonstrates LRS integration with precision tracking:

```python
class SampleLRSPlugin(LRSPlugin):
    def get_metadata(self):
        return PluginMetadata(name="sample-lrs", version="1.0.0")

    def initialize(self):
        # Setup precision tracking
        pass

    async def execute(self, **kwargs):
        # LRS-specific logic
        return {"precision": 0.85}
```

### 2. `sample_tool_plugin.py`

Demonstrates tool registration:

```python
class SampleToolPlugin(ToolPlugin):
    def get_metadata(self):
        return PluginMetadata(name="sample-tool", version="1.0.0")

    def initialize(self):
        # Register tool commands
        pass

    async def execute(self, **kwargs):
        return {"tool_result": "success"}
```

---

## Plugin API

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v2/plugins` | List all installed plugins |
| `POST` | `/api/v2/plugins` | Install/register a plugin (admin only) |
| `DELETE` | `/api/v2/plugins/{name}` | Remove a plugin (admin only) |

### Plugin Metadata

```python
@dataclass
class PluginMetadata:
    name: str               # Unique plugin name
    version: str            # Semver version
    description: str        # Human-readable description
    author: str = ""        # Author name
    tags: list = None       # Categorization tags
    dependencies: list = None  # Required plugins
```

---

## Best Practices

1. **Keep it focused** — One responsibility per plugin
2. **Handle errors gracefully** — Don't crash the host
3. **Use logging** — `self.logger.info(...)` for debugging
4. **Version your plugin** — Use semver (`1.0.0`)
5. **Test in isolation** — Plugins should work independently
6. **Document dependencies** — List required packages
7. **Clean up resources** — Implement `shutdown()` if needed

---

## Testing

```bash
# List installed plugins
curl http://localhost:5000/api/v2/plugins

# Test a sample plugin
python -c "
import importlib.util
spec = importlib.util.spec_from_file_location('sample_lrs_plugin', 'plugins/sample_lrs_plugin.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
plugin = module.SampleLRSPlugin()
print(f'Plugin: {plugin.get_metadata().name}')
"
```

---

## Related Documentation

- [src/ README](src/README.md) — Main application overview
- [API.md](src/API.md) — Plugin API endpoints
- [LRS-Agents README](lrs_agents/README.md) — LRS integration context
- [ARCHITECTURE.md](ARCHITECTURE.md) — Plugin system architecture
