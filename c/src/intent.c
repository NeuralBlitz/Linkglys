#include <stdio.h>
#include <string.h>
#include <math.h>
#include <float.h>
#include "neuralblitz/intent.h"

/* ──────────────────────────────────────────────────────────────
 * Intent Vector Implementation
 * 7-dimensional phi vector for agent intentions
 * ────────────────────────────────────────────────────────────── */

nb_status_t nb_intent_create(nb_intent_t *intent, const double values[NB_INTENT_DIM]) {
    if (!intent || !values) return NB_ERR_NULL;

    for (int i = 0; i < NB_INTENT_DIM; i++) {
        intent->values[i] = values[i];
    }
    intent->magnitude = nb_intent_magnitude(intent);
    intent->coherence = nb_intent_coherence(intent);
    return NB_OK;
}

nb_status_t nb_intent_uniform(nb_intent_t *intent) {
    if (!intent) return NB_ERR_NULL;

    double val = 1.0 / sqrt((double)NB_INTENT_DIM);
    for (int i = 0; i < NB_INTENT_DIM; i++) {
        intent->values[i] = val;
    }
    intent->magnitude = 1.0;
    intent->coherence = 1.0;
    return NB_OK;
}

nb_status_t nb_intent_zero(nb_intent_t *intent) {
    if (!intent) return NB_ERR_NULL;

    memset(intent->values, 0, sizeof(intent->values));
    intent->magnitude = 0.0;
    intent->coherence = 0.0;
    return NB_OK;
}

double nb_intent_magnitude(const nb_intent_t *intent) {
    if (!intent) return 0.0;

    double sum = 0.0;
    for (int i = 0; i < NB_INTENT_DIM; i++) {
        sum += intent->values[i] * intent->values[i];
    }
    return sqrt(sum);
}

double nb_intent_coherence(const nb_intent_t *intent) {
    if (!intent) return 0.0;

    double mag = intent->magnitude;
    if (mag < 1e-10) return 0.0;

    /* Coherence = how aligned the dimensions are
     * Perfect coherence: all dimensions point in same direction
     * Computed as: max(|dot with uniform| / magnitude) normalized to [0,1] */
    double uniform_val = 1.0 / sqrt((double)NB_INTENT_DIM);
    double dot = 0.0;
    for (int i = 0; i < NB_INTENT_DIM; i++) {
        dot += intent->values[i] * uniform_val;
    }

    /* Normalize: perfect alignment gives 1.0 */
    double coherence = dot / mag;
    return NB_CLAMP(coherence, 0.0, 1.0);
}

nb_status_t nb_intent_normalize(nb_intent_t *intent) {
    if (!intent) return NB_ERR_NULL;

    double mag = nb_intent_magnitude(intent);
    if (mag < 1e-10) {
        /* Can't normalize zero vector; set to uniform */
        return nb_intent_uniform(intent);
    }

    for (int i = 0; i < NB_INTENT_DIM; i++) {
        intent->values[i] /= mag;
    }
    intent->magnitude = 1.0;
    intent->coherence = nb_intent_coherence(intent);
    return NB_OK;
}

double nb_intent_dot(const nb_intent_t *a, const nb_intent_t *b) {
    if (!a || !b) return 0.0;

    double sum = 0.0;
    for (int i = 0; i < NB_INTENT_DIM; i++) {
        sum += a->values[i] * b->values[i];
    }
    return sum;
}

double nb_intent_similarity(const nb_intent_t *a, const nb_intent_t *b) {
    if (!a || !b) return 0.0;

    double mag_a = nb_intent_magnitude(a);
    double mag_b = nb_intent_magnitude(b);
    if (mag_a < 1e-10 || mag_b < 1e-10) return 0.0;

    return nb_intent_dot(a, b) / (mag_a * mag_b);
}

nb_status_t nb_intent_scale(nb_intent_t *intent, double scalar) {
    if (!intent) return NB_ERR_NULL;

    for (int i = 0; i < NB_INTENT_DIM; i++) {
        intent->values[i] *= scalar;
    }
    intent->magnitude = nb_intent_magnitude(intent);
    intent->coherence = nb_intent_coherence(intent);
    return NB_OK;
}

nb_status_t nb_intent_add(const nb_intent_t *a, const nb_intent_t *b, nb_intent_t *result) {
    if (!a || !b || !result) return NB_ERR_NULL;

    for (int i = 0; i < NB_INTENT_DIM; i++) {
        result->values[i] = a->values[i] + b->values[i];
    }
    result->magnitude = nb_intent_magnitude(result);
    result->coherence = nb_intent_coherence(result);
    return NB_OK;
}

nb_status_t nb_intent_sub(const nb_intent_t *a, const nb_intent_t *b, nb_intent_t *result) {
    if (!a || !b || !result) return NB_ERR_NULL;

    for (int i = 0; i < NB_INTENT_DIM; i++) {
        result->values[i] = a->values[i] - b->values[i];
    }
    result->magnitude = nb_intent_magnitude(result);
    result->coherence = nb_intent_coherence(result);
    return NB_OK;
}

nb_status_t nb_intent_clamp(nb_intent_t *intent, double lo, double hi) {
    if (!intent) return NB_ERR_NULL;

    for (int i = 0; i < NB_INTENT_DIM; i++) {
        intent->values[i] = NB_CLAMP(intent->values[i], lo, hi);
    }
    intent->magnitude = nb_intent_magnitude(intent);
    intent->coherence = nb_intent_coherence(intent);
    return NB_OK;
}

nb_phi_axis_t nb_intent_dominant(const nb_intent_t *intent) {
    if (!intent) return NB_PHI_DOMINANCE;

    int best = 0;
    double max_val = fabs(intent->values[0]);
    for (int i = 1; i < NB_INTENT_DIM; i++) {
        double v = fabs(intent->values[i]);
        if (v > max_val) {
            max_val = v;
            best = i;
        }
    }
    return (nb_phi_axis_t)best;
}

const char* nb_intent_str(const nb_intent_t *intent, char *buf, size_t buf_size) {
    if (!intent || !buf) return "";

    const char *axis_names[] = {
        "dominance", "harmony", "creation", "preservation",
        "transformation", "knowledge", "connection"
    };

    char vals[256];
    int pos = 0;
    for (int i = 0; i < NB_INTENT_DIM; i++) {
        pos += snprintf(vals + pos, sizeof(vals) - pos,
            "%s%.3f", i > 0 ? ", " : "", intent->values[i]);
    }

    snprintf(buf, buf_size,
        "Intent{[%s], mag=%.3f, coh=%.3f, dom=%s}",
        vals, intent->magnitude, intent->coherence,
        axis_names[nb_intent_dominant(intent)]);
    return buf;
}
