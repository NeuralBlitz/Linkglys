#include <stdio.h>
#include <string.h>
#include <math.h>
#include <float.h>
#include "neuralblitz/free_energy.h"
#include "neuralblitz/precision.h"

/* ──────────────────────────────────────────────────────────────
 * Free Energy Module Implementation
 * Expected Free Energy: G(π) = Epistemic Value - Pragmatic Value
 * ────────────────────────────────────────────────────────────── */

double nb_free_energy_epistemic(
    const nb_policy_t *policy,
    const nb_precision_t *precision
) {
    if (!policy || !precision) return 0.0;

    /* Epistemic value = information gain = uncertainty reduction
     * Proportional to policy length (more tools = more learning)
     * Inversely proportional to precision (high precision = less to learn) */
    double length_factor = (double)NB_MIN(policy->length, 10) / 10.0;
    double uncertainty = 1.0 - nb_precision_expected(precision);

    return length_factor * uncertainty * 10.0;
}

double nb_free_energy_pragmatic(
    const nb_policy_t *policy,
    const nb_intent_t *intent
) {
    if (!policy || !intent) return 0.0;

    /* Pragmatic value = goal alignment
     * How well the policy's free energy matches the agent's intent */
    double goal_match = 1.0 - NB_MIN(fabs(policy->expected_free_energy), 1.0);
    double intent_weight = intent->coherence;

    return goal_match * intent_weight * 10.0;
}

double nb_free_energy_expected(
    const nb_policy_t *policy,
    const nb_precision_t *precision,
    const nb_intent_t *intent
) {
    if (!policy) return 0.0;

    double epistemic = nb_free_energy_epistemic(policy, precision);
    double pragmatic = nb_free_energy_pragmatic(policy, intent);

    /* G(π) = Epistemic Value - Pragmatic Value
     * Lower is better (less surprise expected) */
    return epistemic - pragmatic;
}

nb_status_t nb_free_energy_evaluate_policies(
    nb_policy_t *policies,
    int policy_count,
    const nb_precision_t *precision,
    const nb_intent_t *intent
) {
    if (!policies || policy_count <= 0) return NB_ERR_NULL;

    for (int i = 0; i < policy_count; i++) {
        policies[i].expected_free_energy = nb_free_energy_expected(
            &policies[i], precision, intent);
        policies[i].epistemic_value = nb_free_energy_epistemic(&policies[i], precision);
        policies[i].pragmatic_value = nb_free_energy_pragmatic(&policies[i], intent);
    }
    return NB_OK;
}

const nb_policy_t* nb_free_energy_select_best(
    const nb_policy_t *policies,
    int policy_count
) {
    if (!policies || policy_count <= 0) return NULL;

    const nb_policy_t *best = &policies[0];
    for (int i = 1; i < policy_count; i++) {
        if (policies[i].expected_free_energy < best->expected_free_energy) {
            best = &policies[i];
        }
    }
    return best;
}

double nb_free_energy_precision_weighted(
    double free_energy,
    const nb_precision_t *precision
) {
    if (!precision) return free_energy;

    /* Weight free energy by precision confidence */
    double confidence = nb_precision_expected(precision);
    return free_energy * (1.0 - confidence) + free_energy * confidence * 0.1;
}

nb_status_t nb_free_energy_softmax(
    nb_policy_t *policies,
    int policy_count,
    double temperature
) {
    if (!policies || policy_count <= 0) return NB_ERR_NULL;
    if (temperature <= 0) return NB_ERR_INVALID;

    /* Compute softmax probabilities over negative free energy */
    double max_fe = -DBL_MAX;
    for (int i = 0; i < policy_count; i++) {
        double neg_fe = -policies[i].expected_free_energy / temperature;
        if (neg_fe > max_fe) max_fe = neg_fe;
    }

    double sum_exp = 0.0;
    for (int i = 0; i < policy_count; i++) {
        double neg_fe = -policies[i].expected_free_energy / temperature;
        policies[i].probability = exp(neg_fe - max_fe); /* Numerically stable */
        sum_exp += policies[i].probability;
    }

    /* Normalize */
    for (int i = 0; i < policy_count; i++) {
        policies[i].probability /= sum_exp;
    }

    return NB_OK;
}

const char* nb_free_energy_str(double g, char *buf, size_t buf_size) {
    if (!buf) return "";

    const char *interpretation;
    if (g < -5.0)       interpretation = "highly preferred";
    else if (g < -2.0)  interpretation = "preferred";
    else if (g < 0.0)   interpretation = "slightly preferred";
    else if (g < 2.0)   interpretation = "neutral";
    else if (g < 5.0)   interpretation = "slightly surprising";
    else                interpretation = "highly surprising";

    snprintf(buf, buf_size, "FreeEnergy{G=%.3f: %s}", g, interpretation);
    return buf;
}
