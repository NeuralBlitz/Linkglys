#include <stdio.h>
#include <string.h>
#include "neuralblitz/plugin.h"

/* ──────────────────────────────────────────────────────────────
 * Plugin System Implementation
 * ────────────────────────────────────────────────────────────── */

nb_status_t nb_plugin_system_init(nb_plugin_system_t *ps) {
    if (!ps) return NB_ERR_NULL;
    memset(ps, 0, sizeof(*ps));
    return NB_OK;
}

nb_status_t nb_plugin_system_register(
    nb_plugin_system_t *ps,
    const nb_plugin_t *plugin
) {
    if (!ps || !plugin) return NB_ERR_NULL;
    if (ps->count >= NB_MAX_PLUGINS) return NB_ERR_BOUNDS;

    /* Check for duplicate name */
    for (int i = 0; i < ps->count; i++) {
        if (strcmp(ps->plugins[i].metadata.name, plugin->metadata.name) == 0) {
            return NB_ERR_EXISTS;
        }
    }

    memcpy(&ps->plugins[ps->count], plugin, sizeof(*plugin));
    ps->count++;
    return NB_OK;
}

nb_status_t nb_plugin_system_unregister(nb_plugin_system_t *ps, const char *name) {
    if (!ps || !name) return NB_ERR_NULL;

    for (int i = 0; i < ps->count; i++) {
        if (strcmp(ps->plugins[i].metadata.name, name) == 0) {
            /* Shift remaining */
            for (int j = i; j < ps->count - 1; j++) {
                ps->plugins[j] = ps->plugins[j + 1];
            }
            ps->count--;
            return NB_OK;
        }
    }
    return NB_ERR_NOTFOUND;
}

nb_status_t nb_plugin_system_init_all(nb_plugin_system_t *ps, void *ctx) {
    if (!ps) return NB_ERR_NULL;

    for (int i = 0; i < ps->count; i++) {
        if (ps->plugins[i].enabled && ps->plugins[i].init) {
            int ret = ps->plugins[i].init(ctx);
            if (ret != 0) return NB_ERR;
        }
    }
    return NB_OK;
}

nb_status_t nb_plugin_system_shutdown_all(nb_plugin_system_t *ps) {
    if (!ps) return NB_ERR_NULL;

    for (int i = ps->count - 1; i >= 0; i--) {
        if (ps->plugins[i].enabled && ps->plugins[i].shutdown) {
            ps->plugins[i].shutdown(ps->plugins[i].ctx);
        }
    }
    return NB_OK;
}

nb_status_t nb_plugin_system_enable(nb_plugin_system_t *ps, const char *name, bool enabled) {
    if (!ps || !name) return NB_ERR_NULL;

    for (int i = 0; i < ps->count; i++) {
        if (strcmp(ps->plugins[i].metadata.name, name) == 0) {
            ps->plugins[i].enabled = enabled;
            return NB_OK;
        }
    }
    return NB_ERR_NOTFOUND;
}

const nb_plugin_t* nb_plugin_system_find(const nb_plugin_system_t *ps, const char *name) {
    if (!ps || !name) return NULL;

    for (int i = 0; i < ps->count; i++) {
        if (strcmp(ps->plugins[i].metadata.name, name) == 0) {
            return &ps->plugins[i];
        }
    }
    return NULL;
}

nb_status_t nb_plugin_system_list(
    const nb_plugin_system_t *ps,
    nb_plugin_metadata_t (*metadatas)[],
    int max_plugins,
    int *count
) {
    if (!ps || !metadatas || !count) return NB_ERR_NULL;

    *count = NB_MIN(max_plugins, ps->count);
    for (int i = 0; i < *count; i++) {
        (*metadatas)[i] = ps->plugins[i].metadata;
    }
    return NB_OK;
}

nb_status_t nb_plugin_system_add_handler(
    nb_plugin_system_t *ps,
    nb_event_handler_t handler
) {
    if (!ps || !handler) return NB_ERR_NULL;
    if (ps->handler_count >= NB_MAX_PLUGINS) return NB_ERR_BOUNDS;

    ps->handlers[ps->handler_count] = handler;
    ps->handler_count++;
    return NB_OK;
}

nb_status_t nb_plugin_system_fire_event(
    const nb_plugin_system_t *ps,
    const nb_event_t *event
) {
    if (!ps || !event) return NB_ERR_NULL;

    for (int i = 0; i < ps->handler_count; i++) {
        ps->handlers[i](event, NULL);
    }
    return NB_OK;
}

nb_status_t nb_plugin_system_stats(
    const nb_plugin_system_t *ps,
    int *total,
    int *enabled,
    int *disabled
) {
    if (!ps) return NB_ERR_NULL;

    if (total) *total = ps->count;

    if (enabled || disabled) {
        int ec = 0, dc = 0;
        for (int i = 0; i < ps->count; i++) {
            if (ps->plugins[i].enabled) ec++;
            else dc++;
        }
        if (enabled) *enabled = ec;
        if (disabled) *disabled = dc;
    }
    return NB_OK;
}
