#ifndef NEURALBLITZ_API_H
#define NEURALBLITZ_API_H

#include "neuralblitz/types.h"
#include "neuralblitz/precision.h"
#include "neuralblitz/intent.h"
#include "neuralblitz/free_energy.h"
#include "neuralblitz/cognitive.h"
#include "neuralblitz/lens.h"
#include "neuralblitz/registry.h"
#include "neuralblitz/agent.h"
#include "neuralblitz/multi_agent.h"
#include "neuralblitz/plugin.h"

/* ──────────────────────────────────────────────────────────────
 * NeuralBlitz C API — Public Interface
 * ────────────────────────────────────────────────────────────── */

/* Version */
#define NEURALBLITZ_VERSION_MAJOR 1
#define NEURALBLITZ_VERSION_MINOR 0
#define NEURALBLITZ_VERSION_PATCH 0

typedef struct {
    const char *version;
    const char *build_date;
    const char *compiler;
} nb_version_t;

/* Get library version info */
nb_version_t nb_version(void);

/* ──────────────────────────────────────────────────────────────
 * Core Engine
 * ────────────────────────────────────────────────────────────── */

typedef struct {
    nb_agent_system_t   agent_system;
    nb_multi_agent_t    multi_agent;
    nb_plugin_system_t  plugin_system;
    nb_tool_registry_t  registry;
    bool                initialized;
} nb_engine_t;

/* Initialize the full engine */
nb_status_t nb_engine_init(nb_engine_t *engine);

/* Shutdown engine */
nb_status_t nb_engine_shutdown(nb_engine_t *engine);

/* Register a tool */
nb_status_t nb_engine_register_tool(
    nb_engine_t *engine,
    const char *name,
    const char *version,
    nb_tool_forward_t forward,
    nb_tool_backward_t backward,
    void *context,
    const nb_tool_schema_t *schema
);

/* Create an agent */
nb_status_t nb_engine_create_agent(
    nb_engine_t *engine,
    const char *id,
    const char *name,
    const char *type
);

/* Run agent inference cycle */
nb_status_t nb_engine_infer(
    nb_engine_t *engine,
    const char *agent_id,
    const void *input,
    size_t input_size,
    nb_exec_result_t *result
);

/* Get engine status */
nb_status_t nb_engine_status(const nb_engine_t *engine, char *buf, size_t buf_size);

#endif /* NEURALBLITZ_API_H */
