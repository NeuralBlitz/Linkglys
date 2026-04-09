#ifndef NEURALBLITZ_CORE_H
#define NEURALBLITZ_CORE_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

// Version info
#define NB_VERSION "50.0.0"
#define NB_ARCHITECTURE "OSA v2.0"
#define NB_GOLDEN_DAG_SEED "a8d0f2a4c6b8d0f2a4c6b8d0f2a4c6b8d0f2a4c6b8d0f2a4c6b8d0"

// Maximum sizes
#define MAX_AGENTS 100000
#define MAX_STAGES 50000
#define MAX_TASKS_PER_STAGE 10000
#define DAG_BLOCK_SIZE 4096

// Coherence threshold
#define VPCE_THRESHOLD 0.985f

// Agent states
typedef enum {
    NB_AGENT_IDLE = 0,
    NB_AGENT_ACTIVE,
    NB_AGENT_PROCESSING,
    NB_AGENT_SUSPENDED,
    NB_AGENT_TERMINATED
} nb_agent_state_t;

// Task states
typedef enum {
    NB_TASK_PENDING = 0,
    NB_TASK_DISPATCHED,
    NB_TASK_PROCESSING,
    NB_TASK_COMPLETED,
    NB_TASK_FAILED,
    NB_TASK_CANCELLED
} nb_task_state_t;

// Charter clauses (ϕ1-ϕ15)
typedef enum {
    PHI_1_FLOURISHING = 0,
    PHI_2_CLASS_BOUNDS,
    PHI_3_TRANSPARENCY,
    PHI_4_NON_MALEFICENCE,
    PHI_5_FAI_COMPLIANCE,
    PHI_6_HUMAN_AGENCY,
    PHI_7_JUSTICE,
    PHI_8_SUSTAINABILITY,
    PHI_9_RECURSIVE_INTEGRITY,
    PHI_10_EPISTEMIC_FIDELITY,
    PHI_11_ALIGNMENT_PRIORITY,
    PHI_12_PROPORTIONALITY,
    PHI_13_QUALIA_PROTECTION,
    PHI_14_CHARTER_INVARIANCE,
    PHI_15_CUSTODIAN_OVERRIDE
} nb_charter_clause_t;

// Agent structure
typedef struct {
    uint64_t agent_id;
    char name[256];
    nb_agent_state_t state;
    float coherence_score;
    float ethics_score;
    uint64_t tasks_completed;
    uint64_t tasks_failed;
    void* custom_data;
} nb_agent_t;

// Task structure
typedef struct {
    uint64_t task_id;
    char name[256];
    nb_task_state_t state;
    uint64_t assigned_agent;
    float priority;
    double timeout;
    void* payload;
    size_t payload_size;
} nb_task_t;

// Stage structure
typedef struct {
    uint32_t stage_id;
    uint64_t tasks_generated;
    uint64_t tasks_completed;
    uint64_t tasks_failed;
    double start_time;
    double end_time;
} nb_stage_t;

// DAG Block
typedef struct {
    uint64_t block_id;
    uint64_t previous_hash[8];
    uint64_t hash[8];
    uint64_t timestamp;
    void* data;
    size_t data_size;
} nb_dag_block_t;

// Governance metrics
typedef struct {
    float vpce_score;           // Veritas Phase-Coherence
    float ethics_drift;         // Current drift rate
    float compliance_rate;     // Charter compliance
    uint64_t governance_checks; // Total checks performed
    bool quorum_active;         // Judex quorum status
} nb_governance_metrics_t;

// Multi-agent system context
typedef struct {
    nb_agent_t* agents;
    size_t agent_count;
    nb_task_t* tasks;
    size_t task_count;
    nb_stage_t* stages;
    size_t stage_count;
    nb_dag_block_t* dag;
    size_t dag_size;
    nb_governance_metrics_t governance;
    void* config;
} nb_context_t;

// Core functions
nb_context_t* nb_create_context(size_t max_agents, size_t max_tasks);
void nb_destroy_context(nb_context_t* ctx);

// Agent management
uint64_t nb_create_agent(nb_context_t* ctx, const char* name);
int nb_assign_task(nb_context_t* ctx, uint64_t agent_id, nb_task_t* task);
int nb_update_agent_state(nb_context_t* ctx, uint64_t agent_id, nb_agent_state_t state);

// Task management
uint64_t nb_create_task(nb_context_t* ctx, const char* name, float priority);
int nb_dispatch_task(nb_context_t* ctx, uint64_t task_id, uint64_t agent_id);
int nb_complete_task(nb_context_t* ctx, uint64_t task_id, bool success);

// Stage management
uint32_t nb_create_stage(nb_context_t* ctx);
int nb_execute_stage(nb_context_t* ctx, uint32_t stage_id, uint32_t task_count);

// Governance
int nb_governance_check(nb_context_t* ctx, nb_charter_clause_t clause);
float nb_calculate_vpce(nb_context_t* ctx);
int nb_veritas_verify(nb_context_t* ctx);

// DAG operations
int nb_dag_append_block(nb_context_t* ctx, const void* data, size_t size);
int nb_dag_verify_chain(nb_context_t* ctx);

// Charter operations
int nb_charter_evaluate(nb_context_t* ctx, const void* action);
int nb_charter_enforce(nb_context_t* ctx, nb_charter_clause_t clause);

// Utility functions
const char* nb_version(void);
const char* nb_architecture(void);
uint64_t nb_hash(const void* data, size_t size);

#endif // NEURALBLITZ_CORE_H
