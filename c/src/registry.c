#include <stdio.h>
#include <string.h>
#include <math.h>
#include <float.h>
#include "neuralblitz/registry.h"

/* ──────────────────────────────────────────────────────────────
 * Tool Registry Implementation
 * ────────────────────────────────────────────────────────────── */

nb_status_t nb_registry_init(nb_tool_registry_t *reg) {
    if (!reg) return NB_ERR_NULL;

    memset(reg, 0, sizeof(*reg));
    reg->count = 0;
    reg->total_executions = 0;
    reg->total_latency = 0.0;
    return NB_OK;
}

nb_status_t nb_registry_register(
    nb_tool_registry_t *reg,
    const nb_tool_lens_t *lens,
    const nb_tool_schema_t *schema
) {
    if (!reg || !lens) return NB_ERR_NULL;
    if (reg->count >= NB_MAX_TOOLS) return NB_ERR_BOUNDS;

    /* Check for duplicate name */
    for (int i = 0; i < reg->count; i++) {
        if (strcmp(reg->tools[i].name, lens->name) == 0) {
            return NB_ERR_EXISTS;
        }
    }

    int idx = reg->count;
    memcpy(&reg->tools[idx], lens, sizeof(*lens));
    if (schema) {
        memcpy(&reg->schemas[idx], schema, sizeof(*schema));
    } else {
        memset(&reg->schemas[idx], 0, sizeof(*schema));
        strncpy(reg->schemas[idx].name, lens->name, NB_MAX_NAME_LEN - 1);
    }

    reg->fallback_count[idx] = 0;
    reg->count++;
    return NB_OK;
}

const nb_tool_lens_t* nb_registry_find(const nb_tool_registry_t *reg, const char *name) {
    if (!reg || !name) return NULL;

    for (int i = 0; i < reg->count; i++) {
        if (strcmp(reg->tools[i].name, name) == 0) {
            return &reg->tools[i];
        }
    }
    return NULL;
}

const nb_tool_lens_t* nb_registry_get(const nb_tool_registry_t *reg, int index) {
    if (!reg || index < 0 || index >= reg->count) return NULL;
    return &reg->tools[index];
}

/* Score a tool for a given intent and precision */
static double score_tool(const nb_tool_lens_t *tool, const nb_intent_t *intent, const nb_precision_t *precision) {
    if (!tool || !tool->enabled) return -DBL_MAX;

    /* Score = precision * tool_usage_factor * intent_coherence_bonus */
    double precision_score = nb_precision_expected(&tool->precision);
    double usage_score = log((double)NB_MAX(tool->usage_count, 1)) / log(1000.0);
    usage_score = NB_CLAMP(usage_score, 0.0, 1.0);

    /* Prefer tools with lower free energy */
    double fe_score = 1.0 / (1.0 + fabs(tool->free_energy));

    return precision_score * 0.4 + usage_score * 0.3 + fe_score * 0.3;
}

nb_status_t nb_registry_discover(
    const nb_tool_registry_t *reg,
    const nb_intent_t *intent,
    const nb_precision_t *precision,
    int *tool_indices,
    int max_results,
    int *result_count
) {
    if (!reg || !tool_indices || !result_count) return NB_ERR_NULL;
    if (max_results <= 0) return NB_ERR_INVALID;

    /* Score all tools */
    double scores[NB_MAX_TOOLS];
    int indices[NB_MAX_TOOLS];

    for (int i = 0; i < reg->count; i++) {
        scores[i] = score_tool(&reg->tools[i], intent, precision);
        indices[i] = i;
    }

    /* Simple selection sort for top-K */
    for (int i = 0; i < NB_MIN(max_results, reg->count); i++) {
        int best = i;
        for (int j = i + 1; j < reg->count; j++) {
            if (scores[j] > scores[best]) best = j;
        }
        if (best != i) {
            double tmp_s = scores[i]; scores[i] = scores[best]; scores[best] = tmp_s;
            int tmp_idx = indices[i]; indices[i] = indices[best]; indices[best] = tmp_idx;
        }
        tool_indices[i] = indices[i];
    }

    *result_count = NB_MIN(max_results, reg->count);
    return NB_OK;
}

nb_status_t nb_registry_get_fallbacks(
    const nb_tool_registry_t *reg,
    int tool_index,
    const int **fallbacks,
    int *count
) {
    if (!reg || !fallbacks || !count) return NB_ERR_NULL;
    if (tool_index < 0 || tool_index >= reg->count) return NB_ERR_BOUNDS;

    *fallbacks = reg->fallbacks[tool_index];
    *count = reg->fallback_count[tool_index];
    return NB_OK;
}

nb_status_t nb_registry_add_fallback(
    nb_tool_registry_t *reg,
    int tool_index,
    int fallback_index
) {
    if (!reg) return NB_ERR_NULL;
    if (tool_index < 0 || tool_index >= reg->count) return NB_ERR_BOUNDS;
    if (fallback_index < 0 || fallback_index >= reg->count) return NB_ERR_INVALID;

    int fc = reg->fallback_count[tool_index];
    if (fc >= NB_MAX_ARGS) return NB_ERR_BOUNDS;

    /* Check for duplicate */
    for (int i = 0; i < fc; i++) {
        if (reg->fallbacks[tool_index][i] == fallback_index) return NB_ERR_EXISTS;
    }

    reg->fallbacks[tool_index][fc] = fallback_index;
    reg->fallback_count[tool_index]++;
    return NB_OK;
}

nb_status_t nb_registry_update_stats(
    nb_tool_registry_t *reg,
    int tool_index,
    double duration_ms,
    bool success
) {
    if (!reg) return NB_ERR_NULL;
    if (tool_index < 0 || tool_index >= reg->count) return NB_ERR_BOUNDS;

    nb_tool_lens_t *tool = &reg->tools[tool_index];
    tool->avg_latency = (tool->avg_latency * tool->usage_count + duration_ms) / (tool->usage_count + 1);
    tool->usage_count++;

    nb_precision_update(&tool->precision, success);

    reg->total_executions++;
    reg->total_latency += duration_ms;
    return NB_OK;
}

nb_status_t nb_registry_list(
    const nb_tool_registry_t *reg,
    char (*names)[NB_MAX_NAME_LEN],
    int max_names,
    int *count
) {
    if (!reg || !names || !count) return NB_ERR_NULL;

    *count = NB_MIN(max_names, reg->count);
    for (int i = 0; i < *count; i++) {
        strncpy(names[i], reg->tools[i].name, NB_MAX_NAME_LEN - 1);
        names[i][NB_MAX_NAME_LEN - 1] = '\0';
    }
    return NB_OK;
}

nb_status_t nb_registry_stats(
    const nb_tool_registry_t *reg,
    int *tool_count,
    int *enabled_count,
    double *avg_latency
) {
    if (!reg) return NB_ERR_NULL;

    if (tool_count) *tool_count = reg->count;

    if (enabled_count) {
        int ec = 0;
        for (int i = 0; i < reg->count; i++) {
            if (reg->tools[i].enabled) ec++;
        }
        *enabled_count = ec;
    }

    if (avg_latency) {
        *avg_latency = reg->total_executions > 0
            ? reg->total_latency / reg->total_executions
            : 0.0;
    }

    return NB_OK;
}

nb_status_t nb_registry_clear(nb_tool_registry_t *reg) {
    if (!reg) return NB_ERR_NULL;
    memset(reg, 0, sizeof(*reg));
    return NB_OK;
}
