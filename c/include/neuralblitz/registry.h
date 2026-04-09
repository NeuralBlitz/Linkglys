#ifndef NEURALBLITZ_REGISTRY_H
#define NEURALBLITZ_REGISTRY_H

#include "neuralblitz/types.h"

/* ──────────────────────────────────────────────────────────────
 * Tool Registry
 * Manages tool discovery, registration, and selection with
 * fallback chains and schema-based lookup.
 * ────────────────────────────────────────────────────────────── */

typedef struct {
    nb_tool_lens_t     tools[NB_MAX_TOOLS];
    nb_tool_schema_t   schemas[NB_MAX_TOOLS];
    int                count;
    /* Fallback chains: tool_index -> list of fallback indices */
    int                fallbacks[NB_MAX_TOOLS][NB_MAX_ARGS];
    int                fallback_count[NB_MAX_TOOLS];
    /* Usage statistics */
    int64_t            total_executions;
    double             total_latency;
} nb_tool_registry_t;

/* Initialize registry */
nb_status_t nb_registry_init(nb_tool_registry_t *reg);

/* Register a tool lens */
nb_status_t nb_registry_register(
    nb_tool_registry_t *reg,
    const nb_tool_lens_t *lens,
    const nb_tool_schema_t *schema
);

/* Find tool by name */
const nb_tool_lens_t* nb_registry_find(const nb_tool_registry_t *reg, const char *name);

/* Find tool by index */
const nb_tool_lens_t* nb_registry_get(const nb_tool_registry_t *reg, int index);

/* Discover tools compatible with a given intent and precision */
nb_status_t nb_registry_discover(
    const nb_tool_registry_t *reg,
    const nb_intent_t *intent,
    const nb_precision_t *precision,
    int *tool_indices,
    int max_results,
    int *result_count
);

/* Get fallback chain for a tool */
nb_status_t nb_registry_get_fallbacks(
    const nb_tool_registry_t *reg,
    int tool_index,
    const int **fallbacks,
    int *count
);

/* Add fallback for a tool */
nb_status_t nb_registry_add_fallback(
    nb_tool_registry_t *reg,
    int tool_index,
    int fallback_index
);

/* Update tool usage statistics */
nb_status_t nb_registry_update_stats(
    nb_tool_registry_t *reg,
    int tool_index,
    double duration_ms,
    bool success
);

/* List all registered tools */
nb_status_t nb_registry_list(
    const nb_tool_registry_t *reg,
    char (*names)[NB_MAX_NAME_LEN],
    int max_names,
    int *count
);

/* Get registry statistics */
nb_status_t nb_registry_stats(
    const nb_tool_registry_t *reg,
    int *tool_count,
    int *enabled_count,
    double *avg_latency
);

/* Clear registry */
nb_status_t nb_registry_clear(nb_tool_registry_t *reg);

#endif /* NEURALBLITZ_REGISTRY_H */
