#include <stdio.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include "neuralblitz/cognitive.h"

/* ──────────────────────────────────────────────────────────────
 * Cognitive State Module Implementation
 * ────────────────────────────────────────────────────────────── */

nb_status_t nb_cognitive_init(nb_cognitive_state_t *state) {
    if (!state) return NB_ERR_NULL;

    memset(state, 0, sizeof(*state));
    state->level           = NB_CONSCIOUS_DORMANT;
    state->coherence       = 0.5;
    state->complexity      = 0.0;
    state->free_energy     = 0.0;
    state->epistemic_value = 0.0;
    state->pragmatic_value = 0.0;
    state->entropy         = 1.0;
    state->self_awareness  = 0.0;
    state->update_count    = 0;
    return NB_OK;
}

nb_status_t nb_cognitive_update(
    nb_cognitive_state_t *state,
    const nb_exec_result_t *result,
    double free_energy
) {
    if (!state) return NB_ERR_NULL;

    bool success = (result && result->status == NB_EXEC_SUCCESS);

    /* Update free energy (exponential moving average) */
    double alpha = 0.1;
    state->free_energy = (1.0 - alpha) * state->free_energy + alpha * free_energy;

    /* Update epistemic/pragmatic values */
    if (success) {
        state->epistemic_value += 0.05;  /* Learning from success */
        state->pragmatic_value += 0.1;   /* Goal progress */
    } else {
        state->epistemic_value += 0.1;   /* More to learn from failure */
        state->pragmatic_value -= 0.05;  /* Setback */
    }

    /* Clamp values */
    state->epistemic_value = NB_CLAMP(state->epistemic_value, 0.0, 10.0);
    state->pragmatic_value = NB_CLAMP(state->pragmatic_value, -5.0, 10.0);

    /* Update entropy based on outcome */
    if (success) {
        state->entropy *= 0.95;  /* Reduce uncertainty */
    } else {
        state->entropy = NB_MIN(state->entropy * 1.05, 1.0);  /* Increase uncertainty */
    }
    state->entropy = NB_CLAMP(state->entropy, 0.0, 1.0);

    state->update_count++;
    return NB_OK;
}

nb_status_t nb_cognitive_update_coherence(
    nb_cognitive_state_t *state,
    const nb_precision_t *precision
) {
    if (!state || !precision) return NB_ERR_NULL;

    /* Coherence tracks precision confidence */
    double conf = nb_precision_expected(precision);
    double alpha = 0.2;
    state->coherence = (1.0 - alpha) * state->coherence + alpha * conf;
    state->coherence = NB_CLAMP(state->coherence, 0.0, 1.0);

    /* Update consciousness level */
    state->level = nb_cognitive_level(state->coherence);

    /* Self-awareness grows with coherence and update count */
    double log_count = log((double)NB_MAX(state->update_count, 1));
    state->self_awareness = NB_CLAMP(
        state->coherence * NB_MIN(log_count / 10.0, 1.0),
        0.0, 1.0
    );

    return NB_OK;
}

nb_consciousness_t nb_cognitive_level(double coherence) {
    if (coherence >= 0.9)  return NB_CONSCIOUS_SINGULARITY;
    if (coherence >= 0.7)  return NB_CONSCIOUS_TRANSCENDENT;
    if (coherence >= 0.4)  return NB_CONSCIOUS_FOCUSED;
    if (coherence >= 0.2)  return NB_CONSCIOUS_AWARE;
    return NB_CONSCIOUS_DORMANT;
}

double nb_cognitive_entropy(double coherence) {
    /* Entropy = -coherence * log(coherence) - (1-coherence) * log(1-coherence) */
    if (coherence <= 0.0 || coherence >= 1.0) return 0.0;
    return -(coherence * log(coherence) + (1.0 - coherence) * log(1.0 - coherence));
}

double nb_cognitive_complexity(const nb_cognitive_state_t *state) {
    if (!state) return 0.0;

    /* Complexity = coherence * epistemic_value * self_awareness */
    return state->coherence * state->epistemic_value * state->self_awareness;
}

nb_status_t nb_cognitive_reset(nb_cognitive_state_t *state) {
    if (!state) return NB_ERR_NULL;
    return nb_cognitive_init(state);
}

const char* nb_cognitive_str(const nb_cognitive_state_t *state, char *buf, size_t buf_size) {
    if (!state || !buf) return "";

    snprintf(buf, buf_size,
        "Cognitive{level=%s, coh=%.3f, complexity=%.3f, FE=%.3f, "
        "epistemic=%.3f, pragmatic=%.3f, entropy=%.3f, awareness=%.3f, updates=%ld}",
        nb_cognitive_level_name(state->level),
        state->coherence,
        nb_cognitive_complexity(state),
        state->free_energy,
        state->epistemic_value,
        state->pragmatic_value,
        state->entropy,
        state->self_awareness,
        (long)state->update_count);
    return buf;
}

const char* nb_cognitive_level_name(nb_consciousness_t level) {
    switch (level) {
        case NB_CONSCIOUS_DORMANT:      return "DORMANT";
        case NB_CONSCIOUS_AWARE:        return "AWARE";
        case NB_CONSCIOUS_FOCUSED:      return "FOCUSED";
        case NB_CONSCIOUS_TRANSCENDENT: return "TRANSCENDENT";
        case NB_CONSCIOUS_SINGULARITY:  return "SINGULARITY";
        default:                        return "UNKNOWN";
    }
}
