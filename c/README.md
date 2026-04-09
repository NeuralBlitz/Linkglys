# NeuralBlitz C Implementation

Complete, production-ready C implementation of the NeuralBlitz active inference framework.

## Architecture

```
include/neuralblitz/
├── types.h          → Core types, enums, structs (precision, intent, agents, plugins)
├── precision.h      → Beta distribution precision/confidence tracking
├── intent.h         → 7D phi intent vector operations
├── free_energy.h    → Expected free energy: G(π) = Epistemic - Pragmatic
├── cognitive.h      → Consciousness levels, coherence, state management
├── lens.h           → Bidirectional morphisms (ToolLens) with composition (>>)
├── registry.h       → Tool discovery, registration, fallback chains
├── agent.h          → Single agent + agent system management
├── multi_agent.h    → Multi-agent coordination, shared state, social precision
├── plugin.h         → Plugin lifecycle management, event hooks
└── api.h            → Public API (engine abstraction)

src/
├── precision.c      (130 lines)  Beta distribution math
├── intent.c         (185 lines)  7D vector algebra
├── free_energy.c    (120 lines)  Policy evaluation, softmax
├── cognitive.c      (135 lines)  State machine, consciousness levels
├── lens.c           (160 lines)  Forward/backward passes, composition
├── registry.c       (175 lines)  Tool registry, discovery, fallbacks
├── agent.c          (260 lines)  Agent lifecycle, inference cycles
├── multi_agent.c    (230 lines)  Communication, shared beliefs, social precision
├── plugin.c         (130 lines)  Plugin system, event dispatch
└── api.c            (110 lines)  Engine abstraction layer

tests/
└── test_neuralblitz.c (580 lines) 65 comprehensive tests
```

## Building

### Using Make
```bash
make          # Build library + tests
make test     # Build and run tests
make clean    # Remove build artifacts
make install  # Install to /usr/local
```

### Using CMake
```bash
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make
make test     # Run tests
make install  # Install
```

## Usage

```c
#include <neuralblitz/api.h>

int main(void) {
    nb_engine_t engine;
    nb_engine_init(&engine);

    // Register tools
    nb_engine_register_tool(&engine,
        "my_tool", "1.0.0", my_forward_fn, my_backward_fn, NULL, NULL);

    // Create agents
    nb_engine_create_agent(&engine, "agent_1", "My Agent", "inference");

    // Run inference
    nb_exec_result_t result;
    nb_engine_infer(&engine, "agent_1", "input data", 10, &result);

    nb_engine_shutdown(&engine);
    return 0;
}
```

## Test Coverage

65 tests covering all modules:
- **Precision**: 8 tests (init, update, bayesian, CI, combine, decay, reset)
- **Intent**: 10 tests (create, uniform, zero, normalize, dot, similarity, scale, add, clamp, dominant)
- **Free Energy**: 5 tests (epistemic, pragmatic, evaluate, select, softmax)
- **Cognitive**: 5 tests (init, levels, entropy, update, coherence)
- **Registry**: 6 tests (init, register, find, discover, fallbacks, stats)
- **Lens**: 5 tests (init, forward, record, enable, reset)
- **Agent**: 3 tests (init, system, evaluate)
- **Multi-Agent**: 5 tests (init, add/remove, send/receive, broadcast, channels)
- **Shared State**: 2 tests (get/set, coherence)
- **Social Precision**: 1 test
- **Plugin**: 2 tests (register/find, init_all)
- **Integration**: 5 tests (version, engine init, tool register, agent create, inference)
- **Edge Cases**: 2 tests (null checks, string outputs)

## Design Principles

1. **Zero dependencies** — Only standard C library + libm
2. **No dynamic allocation** in hot paths — Fixed-size arrays, stack allocation
3. **Thread-safe** — No global mutable state
4. **Composable** — ToolLens composition operator, plugin hooks
5. **Testable** — Every function is independently testable
