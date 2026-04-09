#ifndef NEURALBLITZ_COGNITIVE_H
#define NEURALBLITZ_COGNITIVE_H

#include "neuralblitz/types.h"

/* ──────────────────────────────────────────────────────────────
 * Cognitive State Module
 * Manages agent consciousness levels, coherence, and state updates.
 * ────────────────────────────────────────────────────────────── */

/* Initialize cognitive state */
nb_status_t nb_cognitive_init(nb_cognitive_state_t *state);

/* Update cognitive state based on tool execution result */
nb_status_t nb_cognitive_update(
    nb_cognitive_state_t *state,
    const nb_exec_result_t *result,
    double free_energy
);

/* Update coherence from precision */
nb_status_t nb_cognitive_update_coherence(
    nb_cognitive_state_t *state,
    const nb_precision_t *precision
);

/* Determine consciousness level from coherence */
nb_consciousness_t nb_cognitive_level(double coherence);

/* Compute entropy from coherence */
double nb_cognitive_entropy(double coherence);

/* Compute complexity from state variables */
double nb_cognitive_complexity(const nb_cognitive_state_t *state);

/* Reset cognitive state */
nb_status_t nb_cognitive_reset(nb_cognitive_state_t *state);

/* Convert to string */
const char* nb_cognitive_str(const nb_cognitive_state_t *state, char *buf, size_t buf_size);

/* Get level name */
const char* nb_cognitive_level_name(nb_consciousness_t level);

#endif /* NEURALBLITZ_COGNITIVE_H */
