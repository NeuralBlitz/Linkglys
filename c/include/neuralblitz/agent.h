#ifndef NEURALBLITZ_AGENT_H
#define NEURALBLITZ_AGENT_H

#include "neuralblitz/types.h"
#include "neuralblitz/precision.h"
#include "neuralblitz/intent.h"
#include "neuralblitz/free_energy.h"
#include "neuralblitz/cognitive.h"
#include "neuralblitz/lens.h"

/* Forward declare for use in function signatures */
typedef struct nb_tool_registry nb_tool_registry_t;

/* ──────────────────────────────────────────────────────────────
 * Agent Module
 * Active inference agent with precision tracking, policy
 * evaluation, and tool execution.
 * ────────────────────────────────────────────────────────────── */

typedef struct nb_agent_system nb_agent_system_t;

/* ──────────────────────────────────────────────────────────────
 * Agent System (manages multiple agents)
 * ────────────────────────────────────────────────────────────── */

typedef struct nb_tool_registry nb_tool_registry_t;

struct nb_agent_system {
    nb_agent_t          agents[NB_MAX_AGENTS];
    int                 agent_count;
    nb_tool_registry_t *registry;
    nb_event_handler_t  event_handler;
    void               *event_user_data;
};

/* Initialize agent system */
nb_status_t nb_system_init(nb_agent_system_t *sys);

/* Set event handler */
nb_status_t nb_system_set_handler(
    nb_agent_system_t *sys,
    nb_event_handler_t handler,
    void *user_data
);

/* Create a new agent */
nb_status_t nb_system_create_agent(
    nb_agent_system_t *sys,
    const char *id,
    const char *name,
    const char *type,
    nb_agent_t **out_agent
);

/* Get agent by ID */
nb_agent_t* nb_system_get_agent(nb_agent_system_t *sys, const char *id);

/* Remove agent */
nb_status_t nb_system_remove_agent(nb_agent_system_t *sys, const char *id);

/* List all agents */
nb_status_t nb_system_list_agents(
    nb_agent_system_t *sys,
    nb_agent_t **agents,
    int max_agents,
    int *count
);

/* ──────────────────────────────────────────────────────────────
 * Single Agent Operations
 * ────────────────────────────────────────────────────────────── */

/* Initialize agent */
nb_status_t nb_agent_init(
    nb_agent_t *agent,
    const char *id,
    const char *name,
    const char *type
);

/* Evaluate policies and select best one */
nb_status_t nb_agent_evaluate_policies(
    nb_agent_t *agent,
    const nb_policy_t *policies,
    int policy_count
);

/* Execute selected policy */
nb_status_t nb_agent_execute(
    nb_agent_t *agent,
    nb_tool_registry_t *registry,
    const void *input,
    size_t input_size,
    nb_exec_result_t *result
);

/* Update agent state */
nb_status_t nb_agent_set_state(nb_agent_t *agent, nb_agent_state_t state);

/* Update agent precision */
nb_status_t nb_agent_update_precision(nb_agent_t *agent, bool success);

/* Get agent status as string */
const char* nb_agent_status_str(const nb_agent_t *agent, char *buf, size_t buf_size);

#endif /* NEURALBLITZ_AGENT_H */
