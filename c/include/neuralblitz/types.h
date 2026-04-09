#ifndef NEURALBLITZ_TYPES_H
#define NEURALBLITZ_TYPES_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* ──────────────────────────────────────────────────────────────
 * Core Type Definitions for NeuralBlitz C Implementation
 * ────────────────────────────────────────────────────────────── */

#define NB_MAX_NAME_LEN     128
#define NB_MAX_PATH_LEN     512
#define NB_MAX_TOOLS        256
#define NB_MAX_AGENTS       64
#define NB_MAX_POLICIES     128
#define NB_MAX_PLUGINS      64
#define NB_MAX_DIM          1024
#define NB_MAX_HISTORY      10000
#define NB_MAX_MSG_LEN      4096
#define NB_MAX_ARGS         32

/* ──────────────────────────────────────────────────────────────
 * Status Codes
 * ────────────────────────────────────────────────────────────── */

typedef enum {
    NB_OK          =  0,
    NB_ERR         = -1,
    NB_ERR_NULL    = -2,
    NB_ERR_ALLOC   = -3,
    NB_ERR_BOUNDS  = -4,
    NB_ERR_EXISTS  = -5,
    NB_ERR_NOTFOUND= -6,
    NB_ERR_INVALID = -7,
    NB_ERR_TIMEOUT = -8,
} nb_status_t;

/* ──────────────────────────────────────────────────────────────
 * Precision Parameters (Beta Distribution)
 * ────────────────────────────────────────────────────────────── */

typedef struct {
    double alpha;        /* Beta distribution alpha parameter */
    double beta;         /* Beta distribution beta parameter */
    double confidence;   /* Current confidence [0, 1] */
    double precision;    /* Current precision estimate */
    double temperature;  /* Softmax temperature for policy selection */
} nb_precision_t;

/* ──────────────────────────────────────────────────────────────
 * Intent Vector (7-dimensional phi values)
 * ────────────────────────────────────────────────────────────── */

#define NB_INTENT_DIM 7

typedef enum {
    NB_PHI_DOMINANCE      = 0,
    NB_PHI_HARMONY        = 1,
    NB_PHI_CREATION       = 2,
    NB_PHI_PRESERVATION   = 3,
    NB_PHI_TRANSFORMATION = 4,
    NB_PHI_KNOWLEDGE      = 5,
    NB_PHI_CONNECTION     = 6,
} nb_phi_axis_t;

typedef struct {
    double values[NB_INTENT_DIM];
    double magnitude;
    double coherence;    /* How aligned the dimensions are */
} nb_intent_t;

/* ──────────────────────────────────────────────────────────────
 * Consciousness Level
 * ────────────────────────────────────────────────────────────── */

typedef enum {
    NB_CONSCIOUS_DORMANT     = 0,
    NB_CONSCIOUS_AWARE       = 1,
    NB_CONSCIOUS_FOCUSED     = 2,
    NB_CONSCIOUS_TRANSCENDENT= 3,
    NB_CONSCIOUS_SINGULARITY = 4,
} nb_consciousness_t;

/* ──────────────────────────────────────────────────────────────
 * Cognitive State
 * ────────────────────────────────────────────────────────────── */

typedef struct {
    nb_consciousness_t level;
    double coherence;          /* Overall coherence [0, 1] */
    double complexity;         /* Complexity measure */
    double free_energy;        /* Expected free energy */
    double epistemic_value;    /* Information gain */
    double pragmatic_value;    /* Goal achievement */
    double entropy;            /* Uncertainty measure */
    double self_awareness;     /* Self-reflection depth */
    int64_t  update_count;     /* Number of updates */
} nb_cognitive_state_t;

/* ──────────────────────────────────────────────────────────────
 * Execution Result
 * ────────────────────────────────────────────────────────────── */

typedef enum {
    NB_EXEC_SUCCESS = 0,
    NB_EXEC_FAILURE = 1,
    NB_EXEC_TIMEOUT = 2,
    NB_EXEC_CANCELLED = 3,
} nb_exec_status_t;

typedef struct {
    nb_exec_status_t status;
    char    output[NB_MAX_MSG_LEN];
    double  duration_ms;
    double  confidence;
    char    error[NB_MAX_MSG_LEN];
    int     exit_code;
} nb_exec_result_t;

/* ──────────────────────────────────────────────────────────────
 * Tool Lens (Bidirectional Morphism)
 * ────────────────────────────────────────────────────────────── */

typedef struct nb_tool_lens  nb_tool_lens_t;
typedef struct nb_tool_registry nb_tool_registry_t;

/* Tool forward mapping: input -> tool_args */
typedef nb_exec_result_t (*nb_tool_forward_t)(
    const nb_tool_lens_t *lens,
    const void *input,
    size_t input_size
);

/* Tool backward mapping: output -> updated beliefs */
typedef int (*nb_tool_backward_t)(
    const nb_tool_lens_t *lens,
    const void *output,
    size_t output_size,
    void *belief_update
);

/* Tool composition operator */
typedef nb_tool_lens_t* (*nb_tool_compose_t)(
    const nb_tool_lens_t *a,
    const nb_tool_lens_t *b
);

struct nb_tool_lens {
    char              name[NB_MAX_NAME_LEN];
    char              version[32];
    nb_tool_forward_t forward;
    nb_tool_backward_t backward;
    nb_tool_compose_t compose;
    void             *context;       /* Opaque tool-specific data */
    nb_precision_t    precision;
    double            free_energy;   /* Expected free energy for this tool */
    int               usage_count;
    double            avg_latency;
    bool              enabled;
};

/* ──────────────────────────────────────────────────────────────
 * Tool Schema Entry
 * ────────────────────────────────────────────────────────────── */

typedef enum {
    NB_TYPE_INT,
    NB_TYPE_FLOAT,
    NB_TYPE_STRING,
    NB_TYPE_BOOL,
    NB_TYPE_ARRAY,
    NB_TYPE_OBJECT,
} nb_type_t;

typedef struct {
    char       name[NB_MAX_NAME_LEN];
    nb_type_t  type;
    bool       required;
    char       description[NB_MAX_MSG_LEN];
} nb_param_t;

typedef struct {
    char        name[NB_MAX_NAME_LEN];
    nb_param_t  inputs[NB_MAX_ARGS];
    int         input_count;
    nb_param_t  outputs[NB_MAX_ARGS];
    int         output_count;
    char        tags[NB_MAX_ARGS][NB_MAX_NAME_LEN];
    int         tag_count;
} nb_tool_schema_t;

/* ──────────────────────────────────────────────────────────────
 * Policy
 * ────────────────────────────────────────────────────────────── */

typedef struct {
    char    id[NB_MAX_NAME_LEN];
    int     tool_indices[NB_MAX_ARGS];  /* Sequence of tool indices */
    int     length;
    double  expected_free_energy;
    double  epistemic_value;
    double  pragmatic_value;
    double  probability;
    int     priority;
} nb_policy_t;

/* ──────────────────────────────────────────────────────────────
 * Agent
 * ────────────────────────────────────────────────────────────── */

typedef enum {
    NB_AGENT_IDLE     = 0,
    NB_AGENT_RUNNING  = 1,
    NB_AGENT_PAUSED   = 2,
    NB_AGENT_ERROR    = 3,
    NB_AGENT_DONE     = 4,
} nb_agent_state_t;

typedef struct {
    char                id[NB_MAX_NAME_LEN];
    char                name[NB_MAX_NAME_LEN];
    char                type[NB_MAX_NAME_LEN];
    nb_agent_state_t    state;
    nb_cognitive_state_t cognitive_state;
    nb_precision_t      precision;
    nb_intent_t         intent;
    nb_tool_lens_t     *active_tool;
    nb_policy_t         current_policy;
    double              total_free_energy;
    int                 action_count;
    double              avg_precision;
    int64_t             created_at;
    int64_t             updated_at;
} nb_agent_t;

/* ──────────────────────────────────────────────────────────────
 * Plugin Interface
 * ────────────────────────────────────────────────────────────── */

typedef enum {
    NB_PLUGIN_TOOL   = 0,
    NB_PLUGIN_LRS    = 1,
    NB_PLUGIN_HOOK   = 2,
} nb_plugin_type_t;

typedef struct {
    char    name[NB_MAX_NAME_LEN];
    char    version[32];
    char    author[NB_MAX_NAME_LEN];
    char    description[NB_MAX_MSG_LEN];
    nb_plugin_type_t type;
    int     priority;
} nb_plugin_metadata_t;

typedef struct nb_plugin {
    nb_plugin_metadata_t metadata;
    int  (*init)(void *ctx);
    int  (*shutdown)(void *ctx);
    void *ctx;
    bool enabled;
} nb_plugin_t;

/* ──────────────────────────────────────────────────────────────
 * Event
 * ────────────────────────────────────────────────────────────── */

typedef enum {
    NB_EVENT_TOOL_SELECTED    = 0,
    NB_EVENT_TOOL_EXECUTED    = 1,
    NB_EVENT_PRECISION_UPDATE= 2,
    NB_EVENT_POLICY_EVALUATED = 3,
    NB_EVENT_AGENT_STATE_CHANGE=4,
    NB_EVENT_PLUGIN_LOADED   = 5,
    NB_EVENT_ERROR           = 6,
} nb_event_type_t;

typedef struct {
    nb_event_type_t type;
    char    source[NB_MAX_NAME_LEN];
    char    data[NB_MAX_MSG_LEN];
    double  timestamp;
    int     priority;
} nb_event_t;

/* Callback type for event handling */
typedef void (*nb_event_handler_t)(const nb_event_t *event, void *user_data);

/* ──────────────────────────────────────────────────────────────
 * Utility Macros
 * ────────────────────────────────────────────────────────────── */

#define NB_MIN(a, b)   ((a) < (b) ? (a) : (b))
#define NB_MAX(a, b)   ((a) > (b) ? (a) : (b))
#define NB_CLAMP(x, lo, hi) NB_MIN(NB_MAX(x, lo), hi)
#define NB_ARRAY_SIZE(arr) (sizeof(arr) / sizeof((arr)[0]))
#define NB_UNUSED(x)    (void)(x)

/* Status checking */
#define NB_CHECK(status)  do { \
    if ((status) != NB_OK) return (status); \
} while (0)

#define NB_CHECK_GOTO(status, label)  do { \
    if ((status) != NB_OK) goto label; \
} while (0)

#endif /* NEURALBLITZ_TYPES_H */
