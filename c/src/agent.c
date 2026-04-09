#include <stdio.h>
#include <string.h>
#include <time.h>
#include "neuralblitz/agent.h"

/* ──────────────────────────────────────────────────────────────
 * Agent Module Implementation
 * ────────────────────────────────────────────────────────────── */

static void fire_event(nb_agent_system_t *sys, nb_event_type_t type,
                       const char *source, const char *data) {
    if (!sys->event_handler) return;

    nb_event_t event;
    memset(&event, 0, sizeof(event));
    event.type = type;
    strncpy(event.source, source, NB_MAX_NAME_LEN - 1);
    strncpy(event.data, data, NB_MAX_MSG_LEN - 1);
    event.timestamp = (double)time(NULL);

    sys->event_handler(&event, sys->event_user_data);
}

nb_status_t nb_system_init(nb_agent_system_t *sys) {
    if (!sys) return NB_ERR_NULL;

    memset(sys, 0, sizeof(*sys));
    sys->agent_count = 0;
    nb_registry_init(&sys->registry);
    return NB_OK;
}

nb_status_t nb_system_set_handler(
    nb_agent_system_t *sys,
    nb_event_handler_t handler,
    void *user_data
) {
    if (!sys) return NB_ERR_NULL;
    sys->event_handler = handler;
    sys->event_user_data = user_data;
    return NB_OK;
}

nb_status_t nb_system_create_agent(
    nb_agent_system_t *sys,
    const char *id,
    const char *name,
    const char *type,
    nb_agent_t **out_agent
) {
    if (!sys || !id) return NB_ERR_NULL;
    if (sys->agent_count >= NB_MAX_AGENTS) return NB_ERR_BOUNDS;

    /* Check for duplicate ID */
    for (int i = 0; i < sys->agent_count; i++) {
        if (strcmp(sys->agents[i].id, id) == 0) return NB_ERR_EXISTS;
    }

    nb_agent_t *agent = &sys->agents[sys->agent_count];
    nb_status_t status = nb_agent_init(agent, id, name, type);
    NB_CHECK(status);

    sys->agent_count++;
    if (out_agent) *out_agent = agent;

    fire_event(sys, NB_EVENT_AGENT_STATE_CHANGE, id, "created");
    return NB_OK;
}

nb_agent_t* nb_system_get_agent(nb_agent_system_t *sys, const char *id) {
    if (!sys || !id) return NULL;

    for (int i = 0; i < sys->agent_count; i++) {
        if (strcmp(sys->agents[i].id, id) == 0) {
            return &sys->agents[i];
        }
    }
    return NULL;
}

nb_status_t nb_system_remove_agent(nb_agent_system_t *sys, const char *id) {
    if (!sys || !id) return NB_ERR_NULL;

    for (int i = 0; i < sys->agent_count; i++) {
        if (strcmp(sys->agents[i].id, id) == 0) {
            /* Shift remaining agents */
            for (int j = i; j < sys->agent_count - 1; j++) {
                sys->agents[j] = sys->agents[j + 1];
            }
            sys->agent_count--;
            fire_event(sys, NB_EVENT_AGENT_STATE_CHANGE, id, "removed");
            return NB_OK;
        }
    }
    return NB_ERR_NOTFOUND;
}

nb_status_t nb_system_list_agents(
    const nb_agent_system_t *sys,
    nb_agent_t **agents,
    int max_agents,
    int *count
) {
    if (!sys || !agents || !count) return NB_ERR_NULL;

    *count = NB_MIN(max_agents, sys->agent_count);
    for (int i = 0; i < *count; i++) {
        agents[i] = &sys->agents[i];
    }
    return NB_OK;
}

/* ──────────────────────────────────────────────────────────────
 * Single Agent Operations
 * ────────────────────────────────────────────────────────────── */

nb_status_t nb_agent_init(
    nb_agent_t *agent,
    const char *id,
    const char *name,
    const char *type
) {
    if (!agent || !id) return NB_ERR_NULL;

    memset(agent, 0, sizeof(*agent));
    strncpy(agent->id, id, NB_MAX_NAME_LEN - 1);
    if (name)  strncpy(agent->name, name, NB_MAX_NAME_LEN - 1);
    if (type)  strncpy(agent->type, type, NB_MAX_NAME_LEN - 1);

    agent->state = NB_AGENT_IDLE;
    agent->total_free_energy = 0.0;
    agent->action_count = 0;
    agent->avg_precision = 0.0;
    agent->created_at = time(NULL);
    agent->updated_at = agent->created_at;

    nb_cognitive_init(&agent->cognitive_state);
    nb_precision_init(&agent->precision, 1.0, 1.0, 1.0);
    nb_intent_uniform(&agent->intent);

    return NB_OK;
}

nb_status_t nb_agent_evaluate_policies(
    nb_agent_t *agent,
    const nb_policy_t *policies,
    int policy_count
) {
    if (!agent || !policies) return NB_ERR_NULL;
    if (policy_count <= 0) return NB_ERR_INVALID;

    /* Evaluate all policies */
    nb_free_energy_evaluate_policies(
        (nb_policy_t *)policies, /* cast to update fields */
        policy_count,
        &agent->precision,
        &agent->intent
    );

    /* Select best policy */
    const nb_policy_t *best = nb_free_energy_select_best(policies, policy_count);
    if (best) {
        memcpy(&agent->current_policy, best, sizeof(*best));
    }

    /* Apply softmax probabilities */
    nb_policy_t *copy = malloc(sizeof(nb_policy_t) * policy_count);
    if (copy) {
        memcpy(copy, policies, sizeof(nb_policy_t) * policy_count);
        nb_free_energy_softmax(copy, policy_count, agent->precision.temperature);
        /* Store probabilities back */
        for (int i = 0; i < policy_count; i++) {
            ((nb_policy_t *)policies)[i].probability = copy[i].probability;
        }
        free(copy);
    }

    return NB_OK;
}

nb_status_t nb_agent_execute(
    nb_agent_t *agent,
    nb_tool_registry_t *registry,
    const void *input,
    size_t input_size,
    nb_exec_result_t *result
) {
    if (!agent || !registry || !result) return NB_ERR_NULL;

    agent->state = NB_AGENT_RUNNING;
    agent->updated_at = time(NULL);

    /* Execute tools in the selected policy */
    memset(result, 0, sizeof(*result));

    if (agent->current_policy.length <= 0) {
        result->status = NB_EXEC_FAILURE;
        strncpy(result->error, "no policy selected", NB_MAX_MSG_LEN - 1);
        agent->state = NB_AGENT_ERROR;
        return NB_OK;
    }

    /* Execute each tool in the policy sequence */
    const void *current_input = input;
    size_t current_size = input_size;
    char buffer[NB_MAX_MSG_LEN];

    for (int i = 0; i < agent->current_policy.length; i++) {
        int tool_idx = agent->current_policy.tool_indices[i];
        const nb_tool_lens_t *tool = nb_registry_get(registry, tool_idx);
        if (!tool) continue;

        nb_exec_result_t tool_result = nb_lens_forward(tool, current_input, current_size);

        if (tool_result.status != NB_EXEC_SUCCESS) {
            /* Try fallback chain */
            const int *fallbacks;
            int fb_count;
            nb_registry_get_fallbacks(registry, tool_idx, &fallbacks, &fb_count);

            bool recovered = false;
            for (int fb = 0; fb < fb_count && !recovered; fb++) {
                const nb_tool_lens_t *fb_tool = nb_registry_get(registry, fallbacks[fb]);
                if (fb_tool && fb_tool->enabled) {
                    tool_result = nb_lens_forward(fb_tool, current_input, current_size);
                    if (tool_result.status == NB_EXEC_SUCCESS) {
                        recovered = true;
                        tool = fb_tool;
                    }
                }
            }

            if (!recovered) {
                *result = tool_result;
                agent->state = NB_AGENT_ERROR;
                nb_precision_update(&agent->precision, false);
                return NB_OK;
            }
        }

        /* Update tool stats */
        nb_registry_update_stats(registry, tool_idx, tool_result.duration_ms,
            tool_result.status == NB_EXEC_SUCCESS);

        /* Update agent precision */
        nb_precision_update(&agent->precision, tool_result.status == NB_EXEC_SUCCESS);

        /* Prepare input for next tool */
        strncpy(buffer, tool_result.output, NB_MAX_MSG_LEN - 1);
        buffer[NB_MAX_MSG_LEN - 1] = '\0';
        current_input = buffer;
        current_size = strlen(buffer);
    }

    /* Final result */
    result->status = NB_EXEC_SUCCESS;
    if (current_input && current_size > 0) {
        strncpy(result->output, (const char *)current_input, NB_MAX_MSG_LEN - 1);
    }
    result->confidence = nb_precision_expected(&agent->precision);

    agent->action_count++;
    agent->state = NB_AGENT_DONE;
    agent->updated_at = time(NULL);

    nb_cognitive_update(&agent->cognitive_state, result, agent->current_policy.expected_free_energy);
    nb_cognitive_update_coherence(&agent->cognitive_state, &agent->precision);

    return NB_OK;
}

nb_status_t nb_agent_set_state(nb_agent_t *agent, nb_agent_state_t state) {
    if (!agent) return NB_ERR_NULL;
    agent->state = state;
    agent->updated_at = time(NULL);
    return NB_OK;
}

nb_status_t nb_agent_update_precision(nb_agent_t *agent, bool success) {
    if (!agent) return NB_ERR_NULL;
    nb_precision_update(&agent->precision, success);

    /* Update running average */
    agent->avg_precision =
        (agent->avg_precision * agent->action_count + nb_precision_expected(&agent->precision))
        / (agent->action_count + 1);
    return NB_OK;
}

const char* nb_agent_status_str(const nb_agent_t *agent, char *buf, size_t buf_size) {
    if (!agent || !buf) return "";

    const char *state_names[] = {"IDLE", "RUNNING", "PAUSED", "ERROR", "DONE"};

    snprintf(buf, buf_size,
        "Agent{id='%s', name='%s', type='%s', state=%s, "
        "actions=%d, precision=%.3f, FE=%.3f}",
        agent->id, agent->name, agent->type,
        state_names[agent->state],
        agent->action_count,
        nb_precision_expected(&agent->precision),
        agent->total_free_energy);
    return buf;
}
