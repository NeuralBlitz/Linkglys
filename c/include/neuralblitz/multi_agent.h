#ifndef NEURALBLITZ_MULTI_AGENT_H
#define NEURALBLITZ_MULTI_AGENT_H

#include "neuralblitz/types.h"

/* ──────────────────────────────────────────────────────────────
 * Multi-Agent Coordination
 * Inter-agent communication, shared state, and social precision
 * (theory of mind / recursive belief tracking).
 * ────────────────────────────────────────────────────────────── */

#define NB_MAX_MESSAGES 1024
#define NB_MAX_CHANNELS 32

/* ──────────────────────────────────────────────────────────────
 * Inter-Agent Message
 * ────────────────────────────────────────────────────────────── */

typedef enum {
    NB_MSG_QUERY     = 0,
    NB_MSG_RESULT    = 1,
    NB_MSG_REQUEST   = 2,
    NB_MSG_RESPONSE  = 3,
    NB_MSG_BROADCAST = 4,
    NB_MSG_STATUS    = 5,
} nb_msg_type_t;

typedef struct {
    char            from[NB_MAX_NAME_LEN];
    char            to[NB_MAX_NAME_LEN];
    char            channel[NB_MAX_NAME_LEN];
    nb_msg_type_t   type;
    char            payload[NB_MAX_MSG_LEN];
    size_t          payload_size;
    double          timestamp;
    int             priority;
    char            correlation_id[32];
} nb_message_t;

/* ──────────────────────────────────────────────────────────────
 * Shared Belief State
 * ────────────────────────────────────────────────────────────── */

typedef struct {
    char            key[NB_MAX_NAME_LEN];
    double          value;
    double          precision;
    double          timestamp;
    char            source[NB_MAX_NAME_LEN];
} nb_shared_belief_t;

typedef struct {
    nb_shared_belief_t beliefs[NB_MAX_TOOLS];
    int                count;
    double             global_coherence;
    int64_t            version;
} nb_shared_state_t;

/* ──────────────────────────────────────────────────────────────
 * Social Precision (Theory of Mind)
 * ────────────────────────────────────────────────────────────── */

typedef struct {
    char            agent_id[NB_MAX_NAME_LEN];
    nb_precision_t  precision;       /* My belief about this agent's precision */
    double          reliability;     /* Historical reliability [0, 1] */
    int             interaction_count;
    double          last_interaction;
} nb_social_precision_t;

/* ──────────────────────────────────────────────────────────────
 * Multi-Agent Coordinator
 * ────────────────────────────────────────────────────────────── */

typedef struct {
    nb_agent_system_t     system;
    nb_message_t          messages[NB_MAX_MESSAGES];
    int                   message_count;
    nb_shared_state_t     shared_state;
    nb_social_precision_t social[NB_MAX_AGENTS];
    int                   social_count;
    /* Communication channels */
    char                  channels[NB_MAX_CHANNELS][NB_MAX_NAME_LEN];
    int                   channel_count;
} nb_multi_agent_t;

/* Initialize multi-agent system */
nb_status_t nb_multi_agent_init(nb_multi_agent_t *ma);

/* ── Agent Management ── */

nb_status_t nb_multi_agent_add(nb_multi_agent_t *ma, const nb_agent_t *agent);
nb_status_t nb_multi_agent_remove(nb_multi_agent_t *ma, const char *agent_id);

/* ── Communication ── */

nb_status_t nb_multi_agent_send(
    nb_multi_agent_t *ma,
    const char *from,
    const char *to,
    nb_msg_type_t type,
    const void *payload,
    size_t payload_size
);

nb_status_t nb_multi_agent_broadcast(
    nb_multi_agent_t *ma,
    const char *from,
    const char *channel,
    const void *payload,
    size_t payload_size
);

nb_status_t nb_multi_agent_receive(
    nb_multi_agent_t *ma,
    const char *to,
    nb_message_t *msg
);

nb_status_t nb_multi_agent_create_channel(nb_multi_agent_t *ma, const char *name);

/* ── Shared State ── */

nb_status_t nb_shared_set(
    nb_shared_state_t *state,
    const char *key,
    double value,
    double precision,
    const char *source
);

nb_status_t nb_shared_get(
    const nb_shared_state_t *state,
    const char *key,
    double *value,
    double *precision
);

nb_status_t nb_shared_update_coherence(nb_shared_state_t *state);

/* ── Social Precision ── */

nb_status_t nb_social_update(
    nb_multi_agent_t *ma,
    const char *observer,
    const char *observed,
    bool success
);

nb_status_t nb_social_get(
    const nb_multi_agent_t *ma,
    const char *observer,
    const char *observed,
    nb_precision_t *precision
);

/* ── Coordination ── */

nb_status_t nb_multi_agent_coordinate(
    nb_multi_agent_t *ma,
    nb_policy_t *policies,
    int policy_count
);

/* Status */
const char* nb_multi_agent_status(const nb_multi_agent_t *ma, char *buf, size_t buf_size);

#endif /* NEURALBLITZ_MULTI_AGENT_H */
