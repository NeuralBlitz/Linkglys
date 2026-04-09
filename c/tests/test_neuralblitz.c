#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <assert.h>
#include <time.h>

#include "neuralblitz/api.h"

/* ──────────────────────────────────────────────────────────────
 * NeuralBlitz C Test Suite
 * Comprehensive tests for all modules
 * ────────────────────────────────────────────────────────────── */

static int tests_run = 0;
static int tests_passed = 0;
static int tests_failed = 0;

#define TEST(name) \
    tests_run++; \
    printf("  [TEST] %s ... ", #name);

#define ASSERT(cond) \
    do { \
        if (!(cond)) { \
            printf("FAILED at line %d\n", __LINE__); \
            tests_failed++; \
            return; \
        } \
    } while(0)

#define ASSERT_EQ(a, b) \
    do { \
        if ((a) != (b)) { \
            printf("FAILED: %d != %d at line %d\n", (int)(a), (int)(b), __LINE__); \
            tests_failed++; \
            return; \
        } \
    } while(0)

#define ASSERT_NEAR(a, b, eps) \
    do { \
        if (fabs((a) - (b)) > (eps)) { \
            printf("FAILED: %.6f != %.6f (eps=%.6f) at line %d\n", \
                   (double)(a), (double)(b), (double)(eps), __LINE__); \
            tests_failed++; \
            return; \
        } \
    } while(0)

#define PASS() \
    do { printf("PASSED\n"); tests_passed++; } while(0)

/* ──────────────────────────────────────────────────────────────
 * Precision Tests
 * ────────────────────────────────────────────────────────────── */

static void test_precision_init(void) {
    TEST(precision_init);
    nb_precision_t p;
    nb_status_t s = nb_precision_init(&p, 5.0, 3.0, 1.0);
    ASSERT_EQ(s, NB_OK);
    ASSERT_NEAR(p.alpha, 5.0, 0.001);
    ASSERT_NEAR(p.beta, 3.0, 0.001);
    ASSERT_NEAR(p.confidence, 0.625, 0.001); /* 5/(5+3) */
    ASSERT_NEAR(p.precision, 8.0, 0.001);    /* 5+3 */
    PASS();
}

static void test_precision_update_success(void) {
    TEST(precision_update_success);
    nb_precision_t p;
    nb_precision_init(&p, 1.0, 1.0, 1.0);

    for (int i = 0; i < 10; i++) {
        nb_precision_update(&p, true);
    }
    ASSERT_NEAR(p.alpha, 11.0, 0.001);
    ASSERT_NEAR(p.beta, 1.0, 0.001);
    ASSERT_NEAR(p.confidence, 11.0/12.0, 0.001);
    PASS();
}

static void test_precision_update_failure(void) {
    TEST(precision_update_failure);
    nb_precision_t p;
    nb_precision_init(&p, 5.0, 1.0, 1.0);

    for (int i = 0; i < 5; i++) {
        nb_precision_update(&p, false);
    }
    ASSERT_NEAR(p.alpha, 5.0, 0.001);
    ASSERT_NEAR(p.beta, 6.0, 0.001);
    ASSERT_NEAR(p.confidence, 5.0/11.0, 0.001);
    PASS();
}

static void test_precision_bayesian_update(void) {
    TEST(precision_bayesian_update);
    nb_precision_t p;
    nb_precision_init(&p, 1.0, 1.0, 1.0);

    nb_precision_bayesian_update(&p, 20, 5);
    ASSERT_NEAR(p.alpha, 21.0, 0.001);
    ASSERT_NEAR(p.beta, 6.0, 0.001);
    PASS();
}

static void test_precision_confidence_interval(void) {
    TEST(precision_confidence_interval);
    nb_precision_t p;
    nb_precision_init(&p, 50.0, 50.0, 1.0);

    double lower, upper;
    nb_status_t s = nb_precision_confidence_interval(&p, &lower, &upper);
    ASSERT_EQ(s, NB_OK);
    ASSERT(lower < 0.5);
    ASSERT(upper > 0.5);
    ASSERT(lower >= 0.0 && lower <= 1.0);
    ASSERT(upper >= 0.0 && upper <= 1.0);
    PASS();
}

static void test_precision_combine(void) {
    TEST(precision_combine);
    nb_precision_t a, b, result;
    nb_precision_init(&a, 10.0, 5.0, 1.0);
    nb_precision_init(&b, 5.0, 10.0, 1.0);

    nb_status_t s = nb_precision_combine(&a, &b, &result);
    ASSERT_EQ(s, NB_OK);
    ASSERT_NEAR(result.confidence, 0.5, 0.01); /* Equal weights */
    PASS();
}

static void test_precision_decay(void) {
    TEST(precision_decay);
    nb_precision_t p;
    nb_precision_init(&p, 20.0, 5.0, 1.0);
    double before = p.confidence;

    nb_precision_decay(&p, 0.5);
    /* Should move toward (1,1) prior */
    ASSERT(p.alpha < 20.0);
    ASSERT(p.beta < 5.0);
    PASS();
}

static void test_precision_reset(void) {
    TEST(precision_reset);
    nb_precision_t p;
    nb_precision_init(&p, 50.0, 10.0, 2.0);
    nb_precision_reset(&p);
    ASSERT_NEAR(p.alpha, 1.0, 0.001);
    ASSERT_NEAR(p.beta, 1.0, 0.001);
    ASSERT_NEAR(p.confidence, 0.5, 0.001);
    PASS();
}

/* ──────────────────────────────────────────────────────────────
 * Intent Tests
 * ────────────────────────────────────────────────────────────── */

static void test_intent_create(void) {
    TEST(intent_create);
    nb_intent_t intent;
    double values[] = {0.5, 0.3, 0.7, 0.2, 0.6, 0.4, 0.8};
    nb_status_t s = nb_intent_create(&intent, values);
    ASSERT_EQ(s, NB_OK);
    ASSERT(intent.magnitude > 0);
    ASSERT(intent.coherence > 0 && intent.coherence <= 1.0);
    PASS();
}

static void test_intent_uniform(void) {
    TEST(intent_uniform);
    nb_intent_t intent;
    nb_status_t s = nb_intent_uniform(&intent);
    ASSERT_EQ(s, NB_OK);
    ASSERT_NEAR(intent.magnitude, 1.0, 0.001);
    ASSERT_NEAR(intent.coherence, 1.0, 0.001);
    PASS();
}

static void test_intent_zero(void) {
    TEST(intent_zero);
    nb_intent_t intent;
    nb_status_t s = nb_intent_zero(&intent);
    ASSERT_EQ(s, NB_OK);
    ASSERT_NEAR(intent.magnitude, 0.0, 0.001);
    ASSERT_NEAR(intent.coherence, 0.0, 0.001);
    PASS();
}

static void test_intent_normalize(void) {
    TEST(intent_normalize);
    nb_intent_t intent;
    double values[] = {3.0, 4.0, 0.0, 0.0, 0.0, 0.0, 0.0};
    nb_intent_create(&intent, values);
    nb_intent_normalize(&intent);
    ASSERT_NEAR(intent.magnitude, 1.0, 0.001);
    PASS();
}

static void test_intent_dot(void) {
    TEST(intent_dot);
    nb_intent_t a, b;
    double va[] = {1, 0, 0, 0, 0, 0, 0};
    double vb[] = {0, 1, 0, 0, 0, 0, 0};
    nb_intent_create(&a, va);
    nb_intent_create(&b, vb);
    ASSERT_NEAR(nb_intent_dot(&a, &b), 0.0, 0.001);

    double vc[] = {1, 0, 0, 0, 0, 0, 0};
    nb_intent_create(&b, vc);
    ASSERT_NEAR(nb_intent_dot(&a, &b), 1.0, 0.001);
    PASS();
}

static void test_intent_similarity(void) {
    TEST(intent_similarity);
    nb_intent_t a, b;
    double va[] = {1, 0, 0, 0, 0, 0, 0};
    double vb[] = {1, 0, 0, 0, 0, 0, 0};
    nb_intent_create(&a, va);
    nb_intent_create(&b, vb);
    ASSERT_NEAR(nb_intent_similarity(&a, &b), 1.0, 0.001);
    PASS();
}

static void test_intent_scale(void) {
    TEST(intent_scale);
    nb_intent_t intent;
    nb_intent_uniform(&intent);
    nb_intent_scale(&intent, 2.0);
    ASSERT_NEAR(intent.magnitude, 2.0, 0.001);
    PASS();
}

static void test_intent_add(void) {
    TEST(intent_add);
    nb_intent_t a, b, result;
    double va[] = {1, 0, 0, 0, 0, 0, 0};
    double vb[] = {0, 1, 0, 0, 0, 0, 0};
    nb_intent_create(&a, va);
    nb_intent_create(&b, vb);
    nb_intent_add(&a, &b, &result);
    ASSERT_NEAR(result.values[0], 1.0, 0.001);
    ASSERT_NEAR(result.values[1], 1.0, 0.001);
    PASS();
}

static void test_intent_clamp(void) {
    TEST(intent_clamp);
    nb_intent_t intent;
    double values[] = {5.0, -3.0, 10.0, 0.0, 0.0, 0.0, 0.0};
    nb_intent_create(&intent, values);
    nb_intent_clamp(&intent, -2.0, 2.0);
    for (int i = 0; i < NB_INTENT_DIM; i++) {
        ASSERT(intent.values[i] >= -2.0 && intent.values[i] <= 2.0);
    }
    PASS();
}

static void test_intent_dominant(void) {
    TEST(intent_dominant);
    nb_intent_t intent;
    double values[] = {0.1, 0.1, 5.0, 0.1, 0.1, 0.1, 0.1};
    nb_intent_create(&intent, values);
    ASSERT_EQ(nb_intent_dominant(&intent), NB_PHI_CREATION);
    PASS();
}

/* ──────────────────────────────────────────────────────────────
 * Free Energy Tests
 * ────────────────────────────────────────────────────────────── */

static void test_free_energy_epistemic(void) {
    TEST(free_energy_epistemic);
    nb_policy_t policy;
    memset(&policy, 0, sizeof(policy));
    policy.length = 5;

    nb_precision_t precision;
    nb_precision_init(&precision, 1.0, 1.0, 1.0);

    double ev = nb_free_energy_epistemic(&policy, &precision);
    ASSERT(ev > 0);
    PASS();
}

static void test_free_energy_pragmatic(void) {
    TEST(free_energy_pragmatic);
    nb_policy_t policy;
    memset(&policy, 0, sizeof(policy));
    policy.expected_free_energy = 0.5;

    nb_intent_t intent;
    nb_intent_uniform(&intent);

    double pv = nb_free_energy_pragmatic(&policy, &intent);
    ASSERT(pv >= 0);
    PASS();
}

static void test_free_energy_evaluate_policies(void) {
    TEST(free_energy_evaluate_policies);
    nb_policy_t policies[3];
    memset(policies, 0, sizeof(policies));
    policies[0].length = 3;
    policies[1].length = 5;
    policies[2].length = 1;

    nb_precision_t precision;
    nb_precision_init(&precision, 10.0, 5.0, 1.0);

    nb_intent_t intent;
    nb_intent_uniform(&intent);

    nb_status_t s = nb_free_energy_evaluate_policies(policies, 3, &precision, &intent);
    ASSERT_EQ(s, NB_OK);
    PASS();
}

static void test_free_energy_select_best(void) {
    TEST(free_energy_select_best);
    nb_policy_t policies[3];
    memset(policies, 0, sizeof(policies));
    policies[0].expected_free_energy = 5.0;
    policies[1].expected_free_energy = -2.0;
    policies[2].expected_free_energy = 3.0;

    const nb_policy_t *best = nb_free_energy_select_best(policies, 3);
    ASSERT(best != NULL);
    ASSERT_NEAR(best->expected_free_energy, -2.0, 0.001);
    PASS();
}

static void test_free_energy_softmax(void) {
    TEST(free_energy_softmax);
    nb_policy_t policies[3];
    memset(policies, 0, sizeof(policies));
    policies[0].expected_free_energy = -5.0;
    policies[1].expected_free_energy = 0.0;
    policies[2].expected_free_energy = 5.0;

    nb_status_t s = nb_free_energy_softmax(policies, 3, 1.0);
    ASSERT_EQ(s, NB_OK);

    double sum = 0;
    for (int i = 0; i < 3; i++) {
        ASSERT(policies[i].probability >= 0);
        sum += policies[i].probability;
    }
    ASSERT_NEAR(sum, 1.0, 0.001);
    PASS();
}

/* ──────────────────────────────────────────────────────────────
 * Cognitive Tests
 * ────────────────────────────────────────────────────────────── */

static void test_cognitive_init(void) {
    TEST(cognitive_init);
    nb_cognitive_state_t state;
    nb_status_t s = nb_cognitive_init(&state);
    ASSERT_EQ(s, NB_OK);
    ASSERT_EQ(state.level, NB_CONSCIOUS_DORMANT);
    ASSERT_NEAR(state.coherence, 0.5, 0.001);
    PASS();
}

static void test_cognitive_level(void) {
    TEST(cognitive_level);
    ASSERT_EQ(nb_cognitive_level(0.0), NB_CONSCIOUS_DORMANT);
    ASSERT_EQ(nb_cognitive_level(0.3), NB_CONSCIOUS_AWARE);
    ASSERT_EQ(nb_cognitive_level(0.5), NB_CONSCIOUS_FOCUSED);
    ASSERT_EQ(nb_cognitive_level(0.8), NB_CONSCIOUS_TRANSCENDENT);
    ASSERT_EQ(nb_cognitive_level(0.95), NB_CONSCIOUS_SINGULARITY);
    PASS();
}

static void test_cognitive_entropy(void) {
    TEST(cognitive_entropy);
    ASSERT_NEAR(nb_cognitive_entropy(0.5), 0.693, 0.01); /* Maximum entropy */
    ASSERT_NEAR(nb_cognitive_entropy(0.0), 0.0, 0.001);
    ASSERT_NEAR(nb_cognitive_entropy(1.0), 0.0, 0.001);
    PASS();
}

static void test_cognitive_update(void) {
    TEST(cognitive_update);
    nb_cognitive_state_t state;
    nb_cognitive_init(&state);

    nb_exec_result_t result;
    memset(&result, 0, sizeof(result));
    result.status = NB_EXEC_SUCCESS;

    nb_status_t s = nb_cognitive_update(&state, &result, 2.0);
    ASSERT_EQ(s, NB_OK);
    ASSERT(state.epistemic_value > 0);
    ASSERT(state.update_count > 0);
    PASS();
}

static void test_cognitive_update_coherence(void) {
    TEST(cognitive_update_coherence);
    nb_cognitive_state_t state;
    nb_cognitive_init(&state);

    nb_precision_t precision;
    nb_precision_init(&precision, 20.0, 5.0, 1.0);

    nb_status_t s = nb_cognitive_update_coherence(&state, &precision);
    ASSERT_EQ(s, NB_OK);
    ASSERT(state.coherence > 0.5); /* High precision should increase coherence */
    PASS();
}

/* ──────────────────────────────────────────────────────────────
 * Registry Tests
 * ────────────────────────────────────────────────────────────── */

/* Sample tool forward function */
static nb_exec_result_t sample_forward(const nb_tool_lens_t *lens, const void *input, size_t input_size) {
    NB_UNUSED(lens);
    nb_exec_result_t result;
    memset(&result, 0, sizeof(result));
    result.status = NB_EXEC_SUCCESS;
    snprintf(result.output, NB_MAX_MSG_LEN, "processed: %.*s", (int)NB_MIN(input_size, 100), (const char *)input);
    result.duration_ms = 5.0;
    result.confidence = 0.9;
    return result;
}

static int sample_backward(const nb_tool_lens_t *lens, const void *output, size_t output_size, void *belief_update) {
    NB_UNUSED(lens); NB_UNUSED(output); NB_UNUSED(output_size); NB_UNUSED(belief_update);
    return 0;
}

static void test_registry_init(void) {
    TEST(registry_init);
    nb_tool_registry_t reg;
    nb_status_t s = nb_registry_init(&reg);
    ASSERT_EQ(s, NB_OK);
    ASSERT_EQ(reg.count, 0);
    PASS();
}

static void test_registry_register(void) {
    TEST(registry_register);
    nb_tool_registry_t reg;
    nb_registry_init(&reg);

    nb_tool_lens_t lens;
    nb_lens_init(&lens, "test_tool", "1.0.0", sample_forward, sample_backward, NULL);

    nb_status_t s = nb_registry_register(&reg, &lens, NULL);
    ASSERT_EQ(s, NB_OK);
    ASSERT_EQ(reg.count, 1);

    /* Duplicate should fail */
    s = nb_registry_register(&reg, &lens, NULL);
    ASSERT_EQ(s, NB_ERR_EXISTS);
    PASS();
}

static void test_registry_find(void) {
    TEST(registry_find);
    nb_tool_registry_t reg;
    nb_registry_init(&reg);

    nb_tool_lens_t lens;
    nb_lens_init(&lens, "find_me", "1.0.0", sample_forward, sample_backward, NULL);
    nb_registry_register(&reg, &lens, NULL);

    const nb_tool_lens_t *found = nb_registry_find(&reg, "find_me");
    ASSERT(found != NULL);
    ASSERT(strcmp(found->name, "find_me") == 0);

    ASSERT(nb_registry_find(&reg, "nonexistent") == NULL);
    PASS();
}

static void test_registry_discover(void) {
    TEST(registry_discover);
    nb_tool_registry_t reg;
    nb_registry_init(&reg);

    /* Register multiple tools */
    for (int i = 0; i < 5; i++) {
        nb_tool_lens_t lens;
        char name[32];
        snprintf(name, sizeof(name), "tool_%d", i);
        nb_lens_init(&lens, name, "1.0.0", sample_forward, sample_backward, NULL);
        nb_registry_register(&reg, &lens, NULL);
    }

    nb_intent_t intent;
    nb_intent_uniform(&intent);

    nb_precision_t precision;
    nb_precision_init(&precision, 10.0, 5.0, 1.0);

    int indices[10], count;
    nb_status_t s = nb_registry_discover(&reg, &intent, &precision, indices, 3, &count);
    ASSERT_EQ(s, NB_OK);
    ASSERT(count == 3);
    PASS();
}

static void test_registry_fallbacks(void) {
    TEST(registry_fallbacks);
    nb_tool_registry_t reg;
    nb_registry_init(&reg);

    nb_tool_lens_t a, b;
    nb_lens_init(&a, "primary", "1.0.0", sample_forward, sample_backward, NULL);
    nb_lens_init(&b, "fallback", "1.0.0", sample_forward, sample_backward, NULL);
    nb_registry_register(&reg, &a, NULL);
    nb_registry_register(&reg, &b, NULL);

    nb_status_t s = nb_registry_add_fallback(&reg, 0, 1);
    ASSERT_EQ(s, NB_OK);

    const int *fallbacks;
    int count;
    s = nb_registry_get_fallbacks(&reg, 0, &fallbacks, &count);
    ASSERT_EQ(s, NB_OK);
    ASSERT_EQ(count, 1);
    ASSERT_EQ(fallbacks[0], 1);
    PASS();
}

static void test_registry_stats(void) {
    TEST(registry_stats);
    nb_tool_registry_t reg;
    nb_registry_init(&reg);

    nb_tool_lens_t lens;
    nb_lens_init(&lens, "stat_tool", "1.0.0", sample_forward, sample_backward, NULL);
    nb_registry_register(&reg, &lens, NULL);

    int tool_count, enabled_count;
    double avg_latency;
    nb_status_t s = nb_registry_stats(&reg, &tool_count, &enabled_count, &avg_latency);
    ASSERT_EQ(s, NB_OK);
    ASSERT_EQ(tool_count, 1);
    ASSERT_EQ(enabled_count, 1);
    PASS();
}

/* ──────────────────────────────────────────────────────────────
 * Lens Tests
 * ────────────────────────────────────────────────────────────── */

static void test_lens_init(void) {
    TEST(lens_init);
    nb_tool_lens_t lens;
    nb_status_t s = nb_lens_init(&lens, "my_tool", "2.0.0", sample_forward, sample_backward, NULL);
    ASSERT_EQ(s, NB_OK);
    ASSERT(strcmp(lens.name, "my_tool") == 0);
    ASSERT(lens.enabled);
    PASS();
}

static void test_lens_forward(void) {
    TEST(lens_forward);
    nb_tool_lens_t lens;
    nb_lens_init(&lens, "forward_test", "1.0.0", sample_forward, sample_backward, NULL);

    nb_exec_result_t result = nb_lens_forward(&lens, "hello", 5);
    ASSERT_EQ(result.status, NB_EXEC_SUCCESS);
    ASSERT(strstr(result.output, "processed:") != NULL);
    PASS();
}

static void test_lens_record(void) {
    TEST(lens_record);
    nb_tool_lens_t lens;
    nb_lens_init(&lens, "record_test", "1.0.0", sample_forward, sample_backward, NULL);

    nb_lens_record(&lens, 10.0, true);
    ASSERT_EQ(lens.usage_count, 1);
    ASSERT_NEAR(lens.avg_latency, 10.0, 0.001);

    nb_lens_record(&lens, 20.0, true);
    ASSERT_EQ(lens.usage_count, 2);
    ASSERT_NEAR(lens.avg_latency, 15.0, 0.001);
    PASS();
}

static void test_lens_enable(void) {
    TEST(lens_enable);
    nb_tool_lens_t lens;
    nb_lens_init(&lens, "enable_test", "1.0.0", sample_forward, sample_backward, NULL);

    nb_lens_enable(&lens, false);
    ASSERT(!lens.enabled);

    nb_exec_result_t result = nb_lens_forward(&lens, "test", 4);
    ASSERT_EQ(result.status, NB_EXEC_FAILURE);
    PASS();
}

static void test_lens_reset_stats(void) {
    TEST(lens_reset_stats);
    nb_tool_lens_t lens;
    nb_lens_init(&lens, "reset_test", "1.0.0", sample_forward, sample_backward, NULL);
    nb_lens_record(&lens, 5.0, true);
    nb_lens_record(&lens, 10.0, true);

    nb_lens_reset_stats(&lens);
    ASSERT_EQ(lens.usage_count, 0);
    ASSERT_NEAR(lens.avg_latency, 0.0, 0.001);
    PASS();
}

/* ──────────────────────────────────────────────────────────────
 * Agent Tests
 * ────────────────────────────────────────────────────────────── */

static void test_agent_init(void) {
    TEST(agent_init);
    nb_agent_t agent;
    nb_status_t s = nb_agent_init(&agent, "agent_1", "Test Agent", "inference");
    ASSERT_EQ(s, NB_OK);
    ASSERT(strcmp(agent.id, "agent_1") == 0);
    ASSERT_EQ(agent.state, NB_AGENT_IDLE);
    PASS();
}

static void test_agent_system(void) {
    TEST(agent_system);
    nb_agent_system_t sys;
    nb_system_init(&sys);

    nb_agent_t *agent;
    nb_status_t s = nb_system_create_agent(&sys, "sys_1", "System Agent", "reasoning", &agent);
    ASSERT_EQ(s, NB_OK);
    ASSERT(sys.agent_count == 1);

    nb_agent_t *found = nb_system_get_agent(&sys, "sys_1");
    ASSERT(found != NULL);
    ASSERT(strcmp(found->id, "sys_1") == 0);

    s = nb_system_remove_agent(&sys, "sys_1");
    ASSERT_EQ(s, NB_OK);
    ASSERT(sys.agent_count == 0);
    PASS();
}

static void test_agent_evaluate_policies(void) {
    TEST(agent_evaluate_policies);
    nb_agent_t agent;
    nb_agent_init(&agent, "eval_1", "Eval Agent", "inference");

    nb_policy_t policies[2];
    memset(policies, 0, sizeof(policies));
    policies[0].length = 3;
    policies[0].expected_free_energy = 2.0;
    policies[1].length = 5;
    policies[1].expected_free_energy = -1.0;

    nb_status_t s = nb_agent_evaluate_policies(&agent, policies, 2);
    ASSERT_EQ(s, NB_OK);
    ASSERT_NEAR(agent.current_policy.expected_free_energy, -1.0, 0.001);
    PASS();
}

/* ──────────────────────────────────────────────────────────────
 * Multi-Agent Tests
 * ────────────────────────────────────────────────────────────── */

static void test_multi_agent_init(void) {
    TEST(multi_agent_init);
    nb_multi_agent_t ma;
    nb_status_t s = nb_multi_agent_init(&ma);
    ASSERT_EQ(s, NB_OK);
    ASSERT_EQ(ma.system.agent_count, 0);
    ASSERT_EQ(ma.message_count, 0);
    PASS();
}

static void test_multi_agent_add_remove(void) {
    TEST(multi_agent_add_remove);
    nb_multi_agent_t ma;
    nb_multi_agent_init(&ma);

    nb_agent_t agent;
    nb_agent_init(&agent, "ma_1", "MA Agent 1", "inference");

    nb_status_t s = nb_multi_agent_add(&ma, &agent);
    ASSERT_EQ(s, NB_OK);
    ASSERT(ma.system.agent_count == 1);

    s = nb_multi_agent_remove(&ma, "ma_1");
    ASSERT_EQ(s, NB_OK);
    ASSERT(ma.system.agent_count == 0);
    PASS();
}

static void test_multi_agent_send_receive(void) {
    TEST(multi_agent_send_receive);
    nb_multi_agent_t ma;
    nb_multi_agent_init(&ma);

    nb_status_t s = nb_multi_agent_send(&ma, "alice", "bob", NB_MSG_QUERY, "hello?", 7);
    ASSERT_EQ(s, NB_OK);
    ASSERT_EQ(ma.message_count, 1);

    nb_message_t msg;
    s = nb_multi_agent_receive(&ma, "bob", &msg);
    ASSERT_EQ(s, NB_OK);
    ASSERT(strcmp(msg.from, "alice") == 0);
    ASSERT(strcmp(msg.to, "bob") == 0);
    ASSERT_EQ(msg.type, NB_MSG_QUERY);
    PASS();
}

static void test_multi_agent_broadcast(void) {
    TEST(multi_agent_broadcast);
    nb_multi_agent_t ma;
    nb_multi_agent_init(&ma);

    /* Add agents */
    nb_agent_t a1, a2;
    nb_agent_init(&a1, "a1", "Agent 1", "inference");
    nb_agent_init(&a2, "a2", "Agent 2", "reasoning");
    nb_multi_agent_add(&ma, &a1);
    nb_multi_agent_add(&ma, &a2);

    nb_status_t s = nb_multi_agent_broadcast(&ma, "server", "general", "broadcast msg", 14);
    ASSERT_EQ(s, NB_OK);
    /* Should have 2 messages (one per agent) */
    ASSERT(ma.message_count >= 2);
    PASS();
}

static void test_multi_agent_channels(void) {
    TEST(multi_agent_channels);
    nb_multi_agent_t ma;
    nb_multi_agent_init(&ma);

    nb_status_t s = nb_multi_agent_create_channel(&ma, "channel_1");
    ASSERT_EQ(s, NB_OK);
    s = nb_multi_agent_create_channel(&ma, "channel_2");
    ASSERT_EQ(s, NB_OK);
    ASSERT_EQ(ma.channel_count, 2);
    PASS();
}

/* ──────────────────────────────────────────────────────────────
 * Shared State Tests
 * ────────────────────────────────────────────────────────────── */

static void test_shared_state(void) {
    TEST(shared_state);
    nb_shared_state_t state;
    memset(&state, 0, sizeof(state));

    nb_status_t s = nb_shared_set(&state, "temperature", 22.5, 10.0, "sensor_1");
    ASSERT_EQ(s, NB_OK);
    ASSERT_EQ(state.count, 1);

    double value, precision;
    s = nb_shared_get(&state, "temperature", &value, &precision);
    ASSERT_EQ(s, NB_OK);
    ASSERT_NEAR(value, 22.5, 0.001);
    ASSERT_NEAR(precision, 10.0, 0.001);

    /* Update same key */
    s = nb_shared_set(&state, "temperature", 23.0, 5.0, "sensor_2");
    ASSERT_EQ(s, NB_OK);
    /* Weighted average: (22.5*10 + 23.0*5) / (10+5) = 22.666... */
    ASSERT_NEAR(state.beliefs[0].value, 22.666, 0.01);
    ASSERT_NEAR(state.beliefs[0].precision, 15.0, 0.001);
    PASS();
}

static void test_shared_coherence(void) {
    TEST(shared_coherence);
    nb_shared_state_t state;
    memset(&state, 0, sizeof(state));

    nb_shared_set(&state, "belief_1", 0.8, 10.0, "a");
    nb_shared_set(&state, "belief_2", 0.7, 5.0, "b");

    nb_status_t s = nb_shared_update_coherence(&state);
    ASSERT_EQ(s, NB_OK);
    ASSERT(state.global_coherence > 0);
    PASS();
}

/* ──────────────────────────────────────────────────────────────
 * Social Precision Tests
 * ────────────────────────────────────────────────────────────── */

static void test_social_update(void) {
    TEST(social_update);
    nb_multi_agent_t ma;
    nb_multi_agent_init(&ma);

    nb_status_t s = nb_social_update(&ma, "observer", "target", true);
    ASSERT_EQ(s, NB_OK);

    nb_precision_t precision;
    s = nb_social_get(&ma, "observer", "target", &precision);
    ASSERT_EQ(s, NB_OK);
    ASSERT_NEAR(precision.alpha, 2.0, 0.001); /* 1 + 1 success */
    PASS();
}

/* ──────────────────────────────────────────────────────────────
 * Plugin Tests
 * ────────────────────────────────────────────────────────────── */

static int test_plugin_init_fn(void *ctx) { (void)ctx; return 0; }
static int test_plugin_shutdown_fn(void *ctx) { (void)ctx; return 0; }

static void test_plugin_system(void) {
    TEST(plugin_system);
    nb_plugin_system_t ps;
    nb_plugin_system_init(&ps);

    nb_plugin_t plugin;
    memset(&plugin, 0, sizeof(plugin));
    strcpy(plugin.metadata.name, "test_plugin");
    strcpy(plugin.metadata.version, "1.0.0");
    plugin.metadata.type = NB_PLUGIN_TOOL;
    plugin.init = test_plugin_init_fn;
    plugin.shutdown = test_plugin_shutdown_fn;
    plugin.enabled = true;

    nb_status_t s = nb_plugin_system_register(&ps, &plugin);
    ASSERT_EQ(s, NB_OK);
    ASSERT_EQ(ps.count, 1);

    const nb_plugin_t *found = nb_plugin_system_find(&ps, "test_plugin");
    ASSERT(found != NULL);

    s = nb_plugin_system_unregister(&ps, "test_plugin");
    ASSERT_EQ(s, NB_OK);
    ASSERT_EQ(ps.count, 0);
    PASS();
}

static void test_plugin_init_all(void) {
    TEST(plugin_init_all);
    nb_plugin_system_t ps;
    nb_plugin_system_init(&ps);

    nb_plugin_t p1, p2;
    memset(&p1, 0, sizeof(p1));
    strcpy(p1.metadata.name, "p1");
    p1.init = test_plugin_init_fn;
    p1.enabled = true;

    memset(&p2, 0, sizeof(p2));
    strcpy(p2.metadata.name, "p2");
    p2.init = test_plugin_init_fn;
    p2.enabled = false; /* Disabled */

    nb_plugin_system_register(&ps, &p1);
    nb_plugin_system_register(&ps, &p2);

    nb_status_t s = nb_plugin_system_init_all(&ps, NULL);
    ASSERT_EQ(s, NB_OK); /* Only p1 should be initialized */

    int total, enabled, disabled;
    s = nb_plugin_system_stats(&ps, &total, &enabled, &disabled);
    ASSERT_EQ(s, NB_OK);
    ASSERT_EQ(total, 2);
    ASSERT_EQ(enabled, 1);
    ASSERT_EQ(disabled, 1);
    PASS();
}

/* ──────────────────────────────────────────────────────────────
 * Integration Tests
 * ────────────────────────────────────────────────────────────── */

static void test_engine_init_shutdown(void) {
    TEST(engine_init_shutdown);
    nb_engine_t engine;
    nb_status_t s = nb_engine_init(&engine);
    ASSERT_EQ(s, NB_OK);
    ASSERT(engine.initialized);

    s = nb_engine_shutdown(&engine);
    ASSERT_EQ(s, NB_OK);
    ASSERT(!engine.initialized);
    PASS();
}

static void test_engine_register_tool(void) {
    TEST(engine_register_tool);
    nb_engine_t engine;
    nb_engine_init(&engine);

    nb_status_t s = nb_engine_register_tool(&engine,
        "engine_tool", "1.0.0", sample_forward, sample_backward, NULL, NULL);
    ASSERT_EQ(s, NB_OK);
    ASSERT(engine.registry.count == 1);

    nb_engine_shutdown(&engine);
    PASS();
}

static void test_engine_create_agent(void) {
    TEST(engine_create_agent);
    nb_engine_t engine;
    nb_engine_init(&engine);

    nb_status_t s = nb_engine_create_agent(&engine, "eng_1", "Engine Agent", "inference");
    ASSERT_EQ(s, NB_OK);
    ASSERT(engine.agent_system.agent_count == 1);

    nb_engine_shutdown(&engine);
    PASS();
}

static void test_full_inference_cycle(void) {
    TEST(full_inference_cycle);
    nb_engine_t engine;
    nb_engine_init(&engine);

    /* Register a tool */
    nb_engine_register_tool(&engine, "echo_tool", "1.0.0", sample_forward, sample_backward, NULL, NULL);

    /* Create an agent */
    nb_engine_create_agent(&engine, "infer_1", "Inference Agent", "inference");

    /* Execute inference */
    nb_exec_result_t result;
    nb_status_t s = nb_engine_infer(&engine, "infer_1", "test input", 10, &result);
    /* May fail if no policy is selected, but engine should not crash */
    (void)s;

    nb_engine_shutdown(&engine);
    PASS();
}

/* ──────────────────────────────────────────────────────────────
 * Version Test
 * ────────────────────────────────────────────────────────────── */

static void test_version(void) {
    TEST(version);
    nb_version_t v = nb_version();
    ASSERT(v.version != NULL);
    ASSERT(v.build_date != NULL);
    ASSERT(v.compiler != NULL);
    ASSERT(strcmp(v.version, "1.0.0") == 0);
    PASS();
}

/* ──────────────────────────────────────────────────────────────
 * Null/Error Tests
 * ────────────────────────────────────────────────────────────── */

static void test_null_checks(void) {
    TEST(null_checks);
    ASSERT_EQ(nb_precision_init(NULL, 1, 1, 1), NB_ERR_NULL);
    ASSERT_EQ(nb_intent_create(NULL, NULL), NB_ERR_NULL);
    ASSERT_EQ(nb_cognitive_init(NULL), NB_ERR_NULL);
    ASSERT_EQ(nb_lens_init(NULL, "x", "1.0", sample_forward, sample_backward, NULL), NB_ERR_NULL);
    ASSERT_EQ(nb_registry_init(NULL), NB_ERR_NULL);
    ASSERT_EQ(nb_agent_init(NULL, "x", "x", "x"), NB_ERR_NULL);
    ASSERT_EQ(nb_system_init(NULL), NB_ERR_NULL);
    ASSERT_EQ(nb_multi_agent_init(NULL), NB_ERR_NULL);
    ASSERT_EQ(nb_plugin_system_init(NULL), NB_ERR_NULL);
    ASSERT_EQ(nb_engine_init(NULL), NB_ERR_NULL);
    PASS();
}

/* ──────────────────────────────────────────────────────────────
 * String Output Tests
 * ────────────────────────────────────────────────────────────── */

static void test_string_outputs(void) {
    TEST(string_outputs);
    char buf[512];

    nb_precision_t p;
    nb_precision_init(&p, 10.0, 5.0, 1.5);
    const char *s = nb_precision_str(&p, buf, sizeof(buf));
    ASSERT(strlen(s) > 0);
    ASSERT(strstr(buf, "Precision") != NULL);

    nb_intent_t intent;
    nb_intent_uniform(&intent);
    s = nb_intent_str(&intent, buf, sizeof(buf));
    ASSERT(strlen(s) > 0);
    ASSERT(strstr(buf, "Intent") != NULL);

    nb_cognitive_state_t cs;
    nb_cognitive_init(&cs);
    s = nb_cognitive_str(&cs, buf, sizeof(buf));
    ASSERT(strlen(s) > 0);
    ASSERT(strstr(buf, "Cognitive") != NULL);

    nb_tool_lens_t lens;
    nb_lens_init(&lens, "str_test", "1.0", sample_forward, sample_backward, NULL);
    s = nb_lens_str(&lens, buf, sizeof(buf));
    ASSERT(strlen(s) > 0);
    ASSERT(strstr(buf, "Lens") != NULL);
    PASS();
}

/* ──────────────────────────────────────────────────────────────
 * Main
 * ────────────────────────────────────────────────────────────── */

typedef void (*test_fn_t)(void);

int main(void) {
    printf("╔══════════════════════════════════════════════════════════════╗\n");
    printf("║       NeuralBlitz C Implementation — Test Suite             ║\n");
    printf("╚══════════════════════════════════════════════════════════════╝\n\n");

    printf("Version: %s (%s, %s)\n\n",
        nb_version().version, nb_version().build_date, nb_version().compiler);

    test_fn_t tests[] = {
        /* Precision */
        test_precision_init,
        test_precision_update_success,
        test_precision_update_failure,
        test_precision_bayesian_update,
        test_precision_confidence_interval,
        test_precision_combine,
        test_precision_decay,
        test_precision_reset,

        /* Intent */
        test_intent_create,
        test_intent_uniform,
        test_intent_zero,
        test_intent_normalize,
        test_intent_dot,
        test_intent_similarity,
        test_intent_scale,
        test_intent_add,
        test_intent_clamp,
        test_intent_dominant,

        /* Free Energy */
        test_free_energy_epistemic,
        test_free_energy_pragmatic,
        test_free_energy_evaluate_policies,
        test_free_energy_select_best,
        test_free_energy_softmax,

        /* Cognitive */
        test_cognitive_init,
        test_cognitive_level,
        test_cognitive_entropy,
        test_cognitive_update,
        test_cognitive_update_coherence,

        /* Registry */
        test_registry_init,
        test_registry_register,
        test_registry_find,
        test_registry_discover,
        test_registry_fallbacks,
        test_registry_stats,

        /* Lens */
        test_lens_init,
        test_lens_forward,
        test_lens_record,
        test_lens_enable,
        test_lens_reset_stats,

        /* Agent */
        test_agent_init,
        test_agent_system,
        test_agent_evaluate_policies,

        /* Multi-Agent */
        test_multi_agent_init,
        test_multi_agent_add_remove,
        test_multi_agent_send_receive,
        test_multi_agent_broadcast,
        test_multi_agent_channels,

        /* Shared State */
        test_shared_state,
        test_shared_coherence,

        /* Social Precision */
        test_social_update,

        /* Plugin */
        test_plugin_system,
        test_plugin_init_all,

        /* Integration */
        test_version,
        test_engine_init_shutdown,
        test_engine_register_tool,
        test_engine_create_agent,
        test_full_inference_cycle,

        /* Edge Cases */
        test_null_checks,
        test_string_outputs,
    };

    int num_tests = sizeof(tests) / sizeof(tests[0]);

    for (int i = 0; i < num_tests; i++) {
        tests[i]();
    }

    printf("\n");
    printf("══════════════════════════════════════════════════════════════\n");
    printf("Results: %d/%d passed", tests_passed, tests_run);
    if (tests_failed > 0) {
        printf(", %d FAILED", tests_failed);
    }
    printf("\n");
    printf("══════════════════════════════════════════════════════════════\n");

    return tests_failed > 0 ? 1 : 0;
}
