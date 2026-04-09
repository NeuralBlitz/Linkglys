#include <stdio.h>
#include <string.h>
#include <math.h>
#include <float.h>
#include "neuralblitz/precision.h"

/* ──────────────────────────────────────────────────────────────
 * Precision Module Implementation
 * Beta Distribution-based precision/confidence tracking
 * ────────────────────────────────────────────────────────────── */

nb_status_t nb_precision_init(nb_precision_t *p, double alpha, double beta, double temperature) {
    if (!p) return NB_ERR_NULL;
    if (alpha <= 0 || beta <= 0) return NB_ERR_INVALID;

    p->alpha = alpha;
    p->beta  = beta;
    p->confidence = alpha / (alpha + beta);
    p->precision  = alpha + beta;
    p->temperature = temperature > 0 ? temperature : 1.0;
    return NB_OK;
}

nb_status_t nb_precision_update(nb_precision_t *p, bool success) {
    if (!p) return NB_ERR_NULL;

    if (success) {
        p->alpha += 1.0;
    } else {
        p->beta += 1.0;
    }

    double total = p->alpha + p->beta;
    p->confidence = p->alpha / total;
    p->precision  = total;
    return NB_OK;
}

double nb_precision_expected(const nb_precision_t *p) {
    if (!p) return 0.0;
    return p->alpha / (p->alpha + p->beta);
}

double nb_precision_variance(const nb_precision_t *p) {
    if (!p) return 0.0;
    double total = p->alpha + p->beta;
    return (p->alpha * p->beta) / (total * total * (total + 1.0));
}

nb_status_t nb_precision_bayesian_update(nb_precision_t *p, int successes, int failures) {
    if (!p) return NB_ERR_NULL;
    if (successes < 0 || failures < 0) return NB_ERR_INVALID;

    p->alpha += (double)successes;
    p->beta  += (double)failures;

    double total = p->alpha + p->beta;
    p->confidence = p->alpha / total;
    p->precision  = total;
    return NB_OK;
}

/* Approximate Beta CDF using normal approximation for 95% CI */
nb_status_t nb_precision_confidence_interval(const nb_precision_t *p, double *lower, double *upper) {
    if (!p || !lower || !upper) return NB_ERR_NULL;

    double mean = nb_precision_expected(p);
    double var  = nb_precision_variance(p);
    double std  = sqrt(var);

    /* 95% CI ≈ mean ± 1.96 * std (normal approx, valid for alpha+beta > 30) */
    double margin = 1.96 * std;
    *lower = NB_CLAMP(mean - margin, 0.0, 1.0);
    *upper = NB_CLAMP(mean + margin, 0.0, 1.0);
    return NB_OK;
}

nb_status_t nb_precision_combine(
    const nb_precision_t *a,
    const nb_precision_t *b,
    nb_precision_t *result
) {
    if (!a || !b || !result) return NB_ERR_NULL;

    /* Combine via precision-weighted average */
    double prec_a = a->alpha + a->beta;
    double prec_b = b->alpha + b->beta;
    double total  = prec_a + prec_b;

    result->alpha = (a->alpha * prec_a + b->alpha * prec_b) / total;
    result->beta  = (a->beta  * prec_a + b->beta  * prec_b) / total;

    /* Ensure minimum values */
    if (result->alpha < 1.0) result->alpha = 1.0;
    if (result->beta < 1.0)  result->beta = 1.0;

    double sum = result->alpha + result->beta;
    result->confidence = result->alpha / sum;
    result->precision  = sum;
    result->temperature = (a->temperature + b->temperature) / 2.0;
    return NB_OK;
}

nb_status_t nb_precision_decay(nb_precision_t *p, double decay_factor) {
    if (!p) return NB_ERR_NULL;
    if (decay_factor < 0.0 || decay_factor > 1.0) return NB_ERR_INVALID;

    /* Move alpha and beta toward prior (1, 1) by decay_factor */
    p->alpha = 1.0 + decay_factor * (p->alpha - 1.0);
    p->beta  = 1.0 + decay_factor * (p->beta  - 1.0);

    double total = p->alpha + p->beta;
    p->confidence = p->alpha / total;
    p->precision  = total;
    return NB_OK;
}

nb_status_t nb_precision_reset(nb_precision_t *p) {
    if (!p) return NB_ERR_NULL;
    return nb_precision_init(p, 1.0, 1.0, 1.0);
}

const char* nb_precision_str(const nb_precision_t *p, char *buf, size_t buf_size) {
    if (!p || !buf) return "";
    snprintf(buf, buf_size,
        "Precision{α=%.2f, β=%.2f, conf=%.3f, prec=%.1f, temp=%.2f}",
        p->alpha, p->beta, p->confidence, p->precision, p->temperature);
    return buf;
}
