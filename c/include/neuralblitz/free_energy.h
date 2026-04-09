#ifndef NEURALBLITZ_FREE_ENERGY_H
#define NEURALBLITZ_FREE_ENERGY_H

#include "neuralblitz/types.h"

/* ──────────────────────────────────────────────────────────────
 * Free Energy Module
 * Expected Free Energy: G(π) = Epistemic Value - Pragmatic Value
 * Used for policy evaluation and tool selection in active inference.
 * ────────────────────────────────────────────────────────────── */

/* Compute expected free energy for a policy */
double nb_free_energy_expected(
    const nb_policy_t *policy,
    const nb_precision_t *precision,
    const nb_intent_t *intent
);

/* Compute epistemic value (information gain / curiosity) */
double nb_free_energy_epistemic(
    const nb_policy_t *policy,
    const nb_precision_t *precision
);

/* Compute pragmatic value (goal achievement / utility) */
double nb_free_energy_pragmatic(
    const nb_policy_t *policy,
    const nb_intent_t *intent
);

/* Evaluate and rank policies by expected free energy */
nb_status_t nb_free_energy_evaluate_policies(
    nb_policy_t *policies,
    int policy_count,
    const nb_precision_t *precision,
    const nb_intent_t *intent
);

/* Select best policy (lowest expected free energy) */
const nb_policy_t* nb_free_energy_select_best(
    const nb_policy_t *policies,
    int policy_count
);

/* Compute precision-weighted free energy */
double nb_free_energy_precision_weighted(
    double free_energy,
    const nb_precision_t *precision
);

/* Update policy probabilities via softmax over free energy */
nb_status_t nb_free_energy_softmax(
    nb_policy_t *policies,
    int policy_count,
    double temperature
);

/* Convert to string */
const char* nb_free_energy_str(double g, char *buf, size_t buf_size);

#endif /* NEURALBLITZ_FREE_ENERGY_H */
