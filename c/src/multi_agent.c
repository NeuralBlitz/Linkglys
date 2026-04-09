#include <stdio.h>
#include <string.h>
#include <time.h>
#include "neuralblitz/multi_agent.h"

/* ──────────────────────────────────────────────────────────────
 * Multi-Agent Coordination Implementation
 * ────────────────────────────────────────────────────────────── */

nb_status_t nb_multi_agent_init(nb_multi_agent_t *ma) {
    if (!ma) return NB_ERR_NULL;

    memset(ma, 0, sizeof(*ma));
    nb_system_init(&ma->system);
    nb_shared_state_t *ss = &ma->shared_state;
    memset(ss, 0, sizeof(*ss));
    ss->global_coherence = 0.5;

    return NB_OK;
}

nb_status_t nb_multi_agent_add(nb_multi_agent_t *ma, const nb_agent_t *agent) {
    if (!ma || !agent) return NB_ERR_NULL;

    nb_agent_t *new_agent;
    nb_status_t s = nb_system_create_agent(&ma->system, agent->id, agent->name, agent->type, &new_agent);
    NB_CHECK(s);

    /* Initialize social precision entry */
    if (ma->social_count < NB_MAX_AGENTS) {
        strncpy(ma->social[ma->social_count].agent_id, agent->id, NB_MAX_NAME_LEN - 1);
        nb_precision_init(&ma->social[ma->social_count].precision, 1.0, 1.0, 1.0);
        ma->social[ma->social_count].reliability = 0.5;
        ma->social[ma->social_count].interaction_count = 0;
        ma->social[ma->social_count].last_interaction = 0;
        ma->social_count++;
    }

    return NB_OK;
}

nb_status_t nb_multi_agent_remove(nb_multi_agent_t *ma, const char *agent_id) {
    if (!ma || !agent_id) return NB_ERR_NULL;

    nb_status_t s = nb_system_remove_agent(&ma->system, agent_id);
    NB_CHECK(s);

    /* Remove social precision entry */
    for (int i = 0; i < ma->social_count; i++) {
        if (strcmp(ma->social[i].agent_id, agent_id) == 0) {
            for (int j = i; j < ma->social_count - 1; j++) {
                ma->social[j] = ma->social[j + 1];
            }
            ma->social_count--;
            break;
        }
    }

    return NB_OK;
}

/* ── Communication ── */

nb_status_t nb_multi_agent_send(
    nb_multi_agent_t *ma,
    const char *from,
    const char *to,
    nb_msg_type_t type,
    const void *payload,
    size_t payload_size
) {
    if (!ma || !from || !to) return NB_ERR_NULL;
    if (ma->message_count >= NB_MAX_MESSAGES) return NB_ERR_BOUNDS;

    nb_message_t *msg = &ma->messages[ma->message_count];
    memset(msg, 0, sizeof(*msg));

    strncpy(msg->from, from, NB_MAX_NAME_LEN - 1);
    strncpy(msg->to, to, NB_MAX_NAME_LEN - 1);
    msg->type = type;
    msg->timestamp = (double)time(NULL);
    msg->payload_size = NB_MIN(payload_size, NB_MAX_MSG_LEN - 1);
    if (payload && payload_size > 0) {
        memcpy(msg->payload, payload, msg->payload_size);
        msg->payload[msg->payload_size] = '\0';
    }

    /* Generate correlation ID */
    snprintf(msg->correlation_id, sizeof(msg->correlation_id), "%ld", (long)ma->message_count);

    ma->message_count++;
    return NB_OK;
}

nb_status_t nb_multi_agent_broadcast(
    nb_multi_agent_t *ma,
    const char *from,
    const char *channel,
    const void *payload,
    size_t payload_size
) {
    if (!ma || !from) return NB_ERR_NULL;

    /* Send to all agents in the channel */
    for (int i = 0; i < ma->system.agent_count; i++) {
        nb_multi_agent_send(ma, from, ma->system.agents[i].id,
            NB_MSG_BROADCAST, payload, payload_size);
    }
    return NB_OK;
}

nb_status_t nb_multi_agent_receive(
    nb_multi_agent_t *ma,
    const char *to,
    nb_message_t *msg
) {
    if (!ma || !to || !msg) return NB_ERR_NULL;

    for (int i = 0; i < ma->message_count; i++) {
        if (strcmp(ma->messages[i].to, to) == 0) {
            memcpy(msg, &ma->messages[i], sizeof(*msg));
            /* Remove message (shift remaining) */
            for (int j = i; j < ma->message_count - 1; j++) {
                ma->messages[j] = ma->messages[j + 1];
            }
            ma->message_count--;
            return NB_OK;
        }
    }
    return NB_ERR_NOTFOUND;
}

nb_status_t nb_multi_agent_create_channel(nb_multi_agent_t *ma, const char *name) {
    if (!ma || !name) return NB_ERR_NULL;
    if (ma->channel_count >= NB_MAX_CHANNELS) return NB_ERR_BOUNDS;

    strncpy(ma->channels[ma->channel_count], name, NB_MAX_NAME_LEN - 1);
    ma->channel_count++;
    return NB_OK;
}

/* ── Shared State ── */

nb_status_t nb_shared_set(
    nb_shared_state_t *state,
    const char *key,
    double value,
    double precision,
    const char *source
) {
    if (!state || !key) return NB_ERR_NULL;

    /* Find existing or create new */
    for (int i = 0; i < state->count; i++) {
        if (strcmp(state->beliefs[i].key, key) == 0) {
            /* Weighted update with precision */
            double total_prec = state->beliefs[i].precision + precision;
            state->beliefs[i].value =
                (state->beliefs[i].value * state->beliefs[i].precision + value * precision) / total_prec;
            state->beliefs[i].precision = total_prec;
            state->beliefs[i].timestamp = (double)time(NULL);
            if (source) strncpy(state->beliefs[i].source, source, NB_MAX_NAME_LEN - 1);
            state->version++;
            return NB_OK;
        }
    }

    /* New belief */
    if (state->count >= NB_MAX_TOOLS) return NB_ERR_BOUNDS;

    nb_shared_belief_t *b = &state->beliefs[state->count];
    strncpy(b->key, key, NB_MAX_NAME_LEN - 1);
    b->value = value;
    b->precision = precision;
    b->timestamp = (double)time(NULL);
    if (source) strncpy(b->source, source, NB_MAX_NAME_LEN - 1);
    state->count++;
    state->version++;
    return NB_OK;
}

nb_status_t nb_shared_get(
    const nb_shared_state_t *state,
    const char *key,
    double *value,
    double *precision
) {
    if (!state || !key || !value) return NB_ERR_NULL;

    for (int i = 0; i < state->count; i++) {
        if (strcmp(state->beliefs[i].key, key) == 0) {
            *value = state->beliefs[i].value;
            if (precision) *precision = state->beliefs[i].precision;
            return NB_OK;
        }
    }
    return NB_ERR_NOTFOUND;
}

nb_status_t nb_shared_update_coherence(nb_shared_state_t *state) {
    if (!state) return NB_ERR_NULL;
    if (state->count == 0) {
        state->global_coherence = 0.0;
        return NB_OK;
    }

    /* Global coherence = average precision-weighted agreement */
    double total_prec = 0.0;
    double weighted_sum = 0.0;
    for (int i = 0; i < state->count; i++) {
        total_prec += state->beliefs[i].precision;
        weighted_sum += state->beliefs[i].value * state->beliefs[i].precision;
    }

    state->global_coherence = total_prec > 0 ? fabs(weighted_sum / total_prec) : 0.0;
    state->global_coherence = NB_CLAMP(state->global_coherence, 0.0, 1.0);
    return NB_OK;
}

/* ── Social Precision ── */

nb_status_t nb_social_update(
    nb_multi_agent_t *ma,
    const char *observer,
    const char *observed,
    bool success
) {
    if (!ma || !observer || !observed) return NB_ERR_NULL;

    /* Find or create social precision entry */
    for (int i = 0; i < ma->social_count; i++) {
        if (strcmp(ma->social[i].agent_id, observed) == 0) {
            nb_precision_update(&ma->social[i].precision, success);
            ma->social[i].interaction_count++;
            ma->social[i].last_interaction = (double)time(NULL);

            /* Update reliability (exponential moving average) */
            double alpha = 0.1;
            ma->social[i].reliability =
                (1.0 - alpha) * ma->social[i].reliability + alpha * (success ? 1.0 : 0.0);
            return NB_OK;
        }
    }

    /* New entry */
    if (ma->social_count >= NB_MAX_AGENTS) return NB_ERR_BOUNDS;

    nb_social_precision_t *sp = &ma->social[ma->social_count];
    strncpy(sp->agent_id, observed, NB_MAX_NAME_LEN - 1);
    nb_precision_init(&sp->precision, 1.0, 1.0, 1.0);
    sp->reliability = success ? 1.0 : 0.0;
    sp->interaction_count = 1;
    sp->last_interaction = (double)time(NULL);
    ma->social_count++;
    return NB_OK;
}

nb_status_t nb_social_get(
    const nb_multi_agent_t *ma,
    const char *observer,
    const char *observed,
    nb_precision_t *precision
) {
    NB_UNUSED(observer); /* In a full implementation, observer-specific beliefs would be tracked */

    if (!ma || !observed || !precision) return NB_ERR_NULL;

    for (int i = 0; i < ma->social_count; i++) {
        if (strcmp(ma->social[i].agent_id, observed) == 0) {
            memcpy(precision, &ma->social[i].precision, sizeof(*precision));
            return NB_OK;
        }
    }
    return NB_ERR_NOTFOUND;
}

/* ── Coordination ── */

nb_status_t nb_multi_agent_coordinate(
    nb_multi_agent_t *ma,
    nb_policy_t *policies,
    int policy_count
) {
    if (!ma || !policies) return NB_ERR_NULL;

    /* Update shared state coherence */
    nb_shared_update_coherence(&ma->shared_state);

    /* Evaluate policies considering all agents' precision */
    for (int i = 0; i < ma->system.agent_count; i++) {
        nb_agent_t *agent = &ma->system.agents[i];
        nb_agent_evaluate_policies(agent, policies, policy_count);
    }

    return NB_OK;
}

const char* nb_multi_agent_status(const nb_multi_agent_t *ma, char *buf, size_t buf_size) {
    if (!ma || !buf) return "";

    snprintf(buf, buf_size,
        "MultiAgent{agents=%d, messages=%d, beliefs=%d, social=%d, "
        "channels=%d, coherence=%.3f}",
        ma->system.agent_count,
        ma->message_count,
        ma->shared_state.count,
        ma->social_count,
        ma->channel_count,
        ma->shared_state.global_coherence);
    return buf;
}
