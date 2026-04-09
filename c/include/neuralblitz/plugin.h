#ifndef NEURALBLITZ_PLUGIN_H
#define NEURALBLITZ_PLUGIN_H

#include "neuralblitz/types.h"

/* ──────────────────────────────────────────────────────────────
 * Plugin System
 * Dynamic plugin discovery, loading, lifecycle management,
 * and event hooks.
 * ────────────────────────────────────────────────────────────── */

typedef struct {
    nb_plugin_t       plugins[NB_MAX_PLUGINS];
    int               count;
    /* Event handler chains */
    nb_event_handler_t handlers[NB_MAX_PLUGINS];
    int               handler_count;
} nb_plugin_system_t;

/* Initialize plugin system */
nb_status_t nb_plugin_system_init(nb_plugin_system_t *ps);

/* Register a plugin */
nb_status_t nb_plugin_system_register(
    nb_plugin_system_t *ps,
    const nb_plugin_t *plugin
);

/* Unregister a plugin */
nb_status_t nb_plugin_system_unregister(nb_plugin_system_t *ps, const char *name);

/* Initialize all registered plugins */
nb_status_t nb_plugin_system_init_all(nb_plugin_system_t *ps, void *ctx);

/* Shutdown all plugins */
nb_status_t nb_plugin_system_shutdown_all(nb_plugin_system_t *ps);

/* Enable/disable a plugin */
nb_status_t nb_plugin_system_enable(nb_plugin_system_t *ps, const char *name, bool enabled);

/* Find plugin by name */
const nb_plugin_t* nb_plugin_system_find(const nb_plugin_system_t *ps, const char *name);

/* List all plugins */
nb_status_t nb_plugin_system_list(
    const nb_plugin_system_t *ps,
    nb_plugin_metadata_t (*metadatas)[],
    int max_plugins,
    int *count
);

/* Register event handler */
nb_status_t nb_plugin_system_add_handler(
    nb_plugin_system_t *ps,
    nb_event_handler_t handler
);

/* Fire event to all handlers */
nb_status_t nb_plugin_system_fire_event(
    const nb_plugin_system_t *ps,
    const nb_event_t *event
);

/* Get stats */
nb_status_t nb_plugin_system_stats(
    const nb_plugin_system_t *ps,
    int *total,
    int *enabled,
    int *disabled
);

#endif /* NEURALBLITZ_PLUGIN_H */
