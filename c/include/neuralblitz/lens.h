#ifndef NEURALBLITZ_LENS_H
#define NEURALBLITZ_LENS_H

#include "neuralblitz/types.h"

/* ──────────────────────────────────────────────────────────────
 * Tool Lens Module
 * Bidirectional morphisms for tool execution with composition.
 * Forward: input -> tool output
 * Backward: output -> belief updates
 * Composition: (a >> b)(x) = b(a(x))
 * ────────────────────────────────────────────────────────────── */

/* Initialize a tool lens */
nb_status_t nb_lens_init(
    nb_tool_lens_t *lens,
    const char *name,
    const char *version,
    nb_tool_forward_t forward,
    nb_tool_backward_t backward,
    void *context
);

/* Execute tool forward pass */
nb_exec_result_t nb_lens_forward(
    const nb_tool_lens_t *lens,
    const void *input,
    size_t input_size
);

/* Execute backward pass (belief update from output) */
nb_status_t nb_lens_backward(
    const nb_tool_lens_t *lens,
    const void *output,
    size_t output_size,
    void *belief_update
);

/* Compose two lenses: result = b ∘ a (a then b) */
nb_status_t nb_lens_compose(
    const nb_tool_lens_t *a,
    const nb_tool_lens_t *b,
    nb_tool_lens_t *result
);

/* Update lens statistics after execution */
nb_status_t nb_lens_record(nb_tool_lens_t *lens, double duration_ms, bool success);

/* Enable/disable lens */
nb_status_t nb_lens_enable(nb_tool_lens_t *lens, bool enabled);

/* Reset lens statistics */
nb_status_t nb_lens_reset_stats(nb_tool_lens_t *lens);

/* Copy lens */
nb_status_t nb_lens_copy(const nb_tool_lens_t *src, nb_tool_lens_t *dst);

/* Convert to string */
const char* nb_lens_str(const nb_tool_lens_t *lens, char *buf, size_t buf_size);

/* ──────────────────────────────────────────────────────────────
 * Lens Composition Operator (>>)
 * ────────────────────────────────────────────────────────────── */

#define nb_lens_compose_op(a, b, out) nb_lens_compose((a), (b), (out))

#endif /* NEURALBLITZ_LENS_H */
