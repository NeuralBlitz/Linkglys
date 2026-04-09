#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include "neuralblitz/lens.h"
#include "neuralblitz/precision.h"

/* ──────────────────────────────────────────────────────────────
 * Tool Lens Module Implementation
 * Bidirectional morphisms for tool execution
 * ────────────────────────────────────────────────────────────── */

nb_status_t nb_lens_init(
    nb_tool_lens_t *lens,
    const char *name,
    const char *version,
    nb_tool_forward_t forward,
    nb_tool_backward_t backward,
    void *context
) {
    if (!lens || !name || !forward) return NB_ERR_NULL;

    memset(lens, 0, sizeof(*lens));
    strncpy(lens->name, name, NB_MAX_NAME_LEN - 1);
    if (version) strncpy(lens->version, version, 31);
    else strncpy(lens->version, "1.0.0", 31);

    lens->forward  = forward;
    lens->backward = backward;
    lens->compose  = NULL;
    lens->context  = context;
    lens->enabled  = true;

    /* Initialize precision with uniform prior */
    nb_precision_init(&lens->precision, 1.0, 1.0, 1.0);

    lens->free_energy   = 0.0;
    lens->usage_count   = 0;
    lens->avg_latency   = 0.0;
    return NB_OK;
}

nb_exec_result_t nb_lens_forward(
    const nb_tool_lens_t *lens,
    const void *input,
    size_t input_size
) {
    nb_exec_result_t result;
    memset(&result, 0, sizeof(result));

    if (!lens) {
        result.status = NB_EXEC_FAILURE;
        strncpy(result.error, "null lens", NB_MAX_MSG_LEN - 1);
        return result;
    }

    if (!lens->enabled) {
        result.status = NB_EXEC_FAILURE;
        strncpy(result.error, "tool disabled", NB_MAX_MSG_LEN - 1);
        return result;
    }

    if (!lens->forward) {
        result.status = NB_EXEC_FAILURE;
        strncpy(result.error, "no forward function", NB_MAX_MSG_LEN - 1);
        return result;
    }

    struct timespec ts_start, ts_end;
    clock_gettime(CLOCK_MONOTONIC, &ts_start);

    result = lens->forward(lens, input, input_size);

    clock_gettime(CLOCK_MONOTONIC, &ts_end);
    double duration_ms = (ts_end.tv_sec - ts_start.tv_sec) * 1000.0
                       + (ts_end.tv_nsec - ts_start.tv_nsec) / 1e6;

    /* Update stats */
    ((nb_tool_lens_t *)lens)->avg_latency =
        (lens->avg_latency * lens->usage_count + duration_ms) / (lens->usage_count + 1);
    ((nb_tool_lens_t *)lens)->usage_count++;

    return result;
}

nb_status_t nb_lens_backward(
    const nb_tool_lens_t *lens,
    const void *output,
    size_t output_size,
    void *belief_update
) {
    if (!lens || !lens->backward) return NB_ERR;
    return lens->backward(lens, output, output_size, belief_update);
}

/* Helper context for composed lenses */
typedef struct {
    nb_tool_lens_t a;
    nb_tool_lens_t b;
} nb_compose_ctx_t;

static nb_exec_result_t composed_forward(
    const nb_tool_lens_t *composed,
    const void *input,
    size_t input_size
) {
    nb_compose_ctx_t *ctx = (nb_compose_ctx_t *)composed->context;
    if (!ctx) {
        nb_exec_result_t r;
        memset(&r, 0, sizeof(r));
        r.status = NB_EXEC_FAILURE;
        strncpy(r.error, "null compose context", NB_MAX_MSG_LEN - 1);
        return r;
    }

    /* Execute a: input -> intermediate */
    char intermediate[NB_MAX_MSG_LEN];
    nb_exec_result_t ra = ctx->a.forward(&ctx->a, input, input_size);
    if (ra.status != NB_EXEC_SUCCESS) return ra;

    /* Copy a's output to intermediate buffer */
    size_t len = strlen(ra.output);
    memcpy(intermediate, ra.output, NB_MIN(len, sizeof(intermediate) - 1));
    intermediate[NB_MIN(len, sizeof(intermediate) - 1)] = '\0';

    /* Execute b: intermediate -> final output */
    return ctx->b.forward(&ctx->b, intermediate, strlen(intermediate));
}

static int composed_backward(
    const nb_tool_lens_t *composed,
    const void *output,
    size_t output_size,
    void *belief_update
) {
    nb_compose_ctx_t *ctx = (nb_compose_ctx_t *)composed->context;
    if (!ctx) return -1;

    /* Backward through b first, then a */
    char intermediate[NB_MAX_MSG_LEN];
    int ret_b = ctx->b.backward(&ctx->b, output, output_size, intermediate);
    if (ret_b != 0) return ret_b;

    return ctx->a.backward(&ctx->a, intermediate, strlen(intermediate), belief_update);
}

nb_status_t nb_lens_compose(
    const nb_tool_lens_t *a,
    const nb_tool_lens_t *b,
    nb_tool_lens_t *result
) {
    if (!a || !b || !result) return NB_ERR_NULL;

    /* Allocate compose context */
    nb_compose_ctx_t *ctx = malloc(sizeof(nb_compose_ctx_t));
    if (!ctx) return NB_ERR_ALLOC;

    memcpy(&ctx->a, a, sizeof(*a));
    memcpy(&ctx->b, b, sizeof(*b));

    /* Create composed lens name */
    snprintf(result->name, NB_MAX_NAME_LEN, "%s>>%s", a->name, b->name);
    snprintf(result->version, 31, "%s+%s", a->version, b->version);

    result->forward  = composed_forward;
    result->backward = composed_backward;
    result->compose  = NULL;
    result->context  = ctx;
    result->enabled  = a->enabled && b->enabled;

    /* Composed precision = combination of both */
    nb_precision_combine(&a->precision, &b->precision, &result->precision);

    /* Composed free energy = sum */
    result->free_energy = a->free_energy + b->free_energy;
    result->usage_count = 0;
    result->avg_latency = 0.0;

    return NB_OK;
}

nb_status_t nb_lens_record(nb_tool_lens_t *lens, double duration_ms, bool success) {
    if (!lens) return NB_ERR_NULL;

    lens->avg_latency = (lens->avg_latency * lens->usage_count + duration_ms) / (lens->usage_count + 1);
    lens->usage_count++;

    nb_precision_update(&lens->precision, success);
    return NB_OK;
}

nb_status_t nb_lens_enable(nb_tool_lens_t *lens, bool enabled) {
    if (!lens) return NB_ERR_NULL;
    lens->enabled = enabled;
    return NB_OK;
}

nb_status_t nb_lens_reset_stats(nb_tool_lens_t *lens) {
    if (!lens) return NB_ERR_NULL;
    lens->usage_count = 0;
    lens->avg_latency = 0.0;
    lens->free_energy = 0.0;
    nb_precision_init(&lens->precision, 1.0, 1.0, 1.0);
    return NB_OK;
}

nb_status_t nb_lens_copy(const nb_tool_lens_t *src, nb_tool_lens_t *dst) {
    if (!src || !dst) return NB_ERR_NULL;
    memcpy(dst, src, sizeof(*dst));
    return NB_OK;
}

const char* nb_lens_str(const nb_tool_lens_t *lens, char *buf, size_t buf_size) {
    if (!lens || !buf) return "";

    char prec_buf[128];
    nb_precision_str(&lens->precision, prec_buf, sizeof(prec_buf));

    snprintf(buf, buf_size,
        "Lens{name='%s', ver='%s', %s, fe=%.3f, uses=%d, lat=%.2fms}",
        lens->name, lens->version, prec_buf,
        lens->free_energy, lens->usage_count, lens->avg_latency);
    return buf;
}
