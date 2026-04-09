#ifndef NEURALBLITZ_PRECISION_H
#define NEURALBLITZ_PRECISION_H

#include "neuralblitz/types.h"

/* ──────────────────────────────────────────────────────────────
 * Precision Module
 * Implements Beta Distribution-based precision/confidence tracking
 * for active inference agents.
 * ────────────────────────────────────────────────────────────── */

/* Initialize precision parameters with prior beliefs */
nb_status_t nb_precision_init(nb_precision_t *p, double alpha, double beta, double temperature);

/* Update precision based on outcome */
nb_status_t nb_precision_update(nb_precision_t *p, bool success);

/* Get expected precision (mean of Beta distribution) */
double nb_precision_expected(const nb_precision_t *p);

/* Get variance of precision estimate */
double nb_precision_variance(const nb_precision_t *p);

/* Bayesian update with new evidence */
nb_status_t nb_precision_bayesian_update(nb_precision_t *p, int successes, int failures);

/* Compute confidence interval (95%) */
nb_status_t nb_precision_confidence_interval(const nb_precision_t *p, double *lower, double *upper);

/* Precision-weighted combination of two precision estimates */
nb_status_t nb_precision_combine(
    const nb_precision_t *a,
    const nb_precision_t *b,
    nb_precision_t *result
);

/* Decay precision over time (forgetting factor) */
nb_status_t nb_precision_decay(nb_precision_t *p, double decay_factor);

/* Reset to uniform prior */
nb_status_t nb_precision_reset(nb_precision_t *p);

/* Convert to string for debugging */
const char* nb_precision_str(const nb_precision_t *p, char *buf, size_t buf_size);

#endif /* NEURALBLITZ_PRECISION_H */
