#ifndef NEURALBLITZ_INTENT_H
#define NEURALBLITZ_INTENT_H

#include "neuralblitz/types.h"

/* ──────────────────────────────────────────────────────────────
 * Intent Vector Module
 * 7-dimensional phi vector representing agent intentions
 * ────────────────────────────────────────────────────────────── */

/* Create intent vector from raw values */
nb_status_t nb_intent_create(nb_intent_t *intent, const double values[NB_INTENT_DIM]);

/* Create uniform intent (all dimensions equal) */
nb_status_t nb_intent_uniform(nb_intent_t *intent);

/* Create zero intent */
nb_status_t nb_intent_zero(nb_intent_t *intent);

/* Compute magnitude (L2 norm) */
double nb_intent_magnitude(const nb_intent_t *intent);

/* Compute coherence (how aligned dimensions are, 0-1) */
double nb_intent_coherence(const nb_intent_t *intent);

/* Normalize intent to unit magnitude */
nb_status_t nb_intent_normalize(nb_intent_t *intent);

/* Compute dot product between two intents */
double nb_intent_dot(const nb_intent_t *a, const nb_intent_t *b);

/* Compute cosine similarity */
double nb_intent_similarity(const nb_intent_t *a, const nb_intent_t *b);

/* Scale intent by scalar */
nb_status_t nb_intent_scale(nb_intent_t *intent, double scalar);

/* Add two intents */
nb_status_t nb_intent_add(const nb_intent_t *a, const nb_intent_t *b, nb_intent_t *result);

/* Subtract two intents */
nb_status_t nb_intent_sub(const nb_intent_t *a, const nb_intent_t *b, nb_intent_t *result);

/* Clamp all values to [lo, hi] */
nb_status_t nb_intent_clamp(nb_intent_t *intent, double lo, double hi);

/* Get dominant axis */
nb_phi_axis_t nb_intent_dominant(const nb_intent_t *intent);

/* Convert to string */
const char* nb_intent_str(const nb_intent_t *intent, char *buf, size_t buf_size);

#endif /* NEURALBLITZ_INTENT_H */
