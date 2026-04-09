#include <stdio.h>
#include <string.h>
#include <time.h>
#include "neuralblitz/api.h"

/* ──────────────────────────────────────────────────────────────
 * NeuralBlitz C API Implementation
 * ────────────────────────────────────────────────────────────── */

nb_version_t nb_version(void) {
    nb_version_t v;
    static char ver[32];
    static char date[32];
    static char compiler[64];

    snprintf(ver, sizeof(ver), "%d.%d.%d",
        NEURALBLITZ_VERSION_MAJOR, NEURALBLITZ_VERSION_MINOR, NEURALBLITZ_VERSION_PATCH);
    v.version = ver;
    v.build_date = __DATE__;
    v.compiler = compiler;
#ifdef __GNUC__
    snprintf(compiler, sizeof(compiler), "GCC %d.%d.%d", __GNUC__, __GNUC_MINOR__, __GNUC_PATCHLEVEL__);
#elif defined(__clang__)
    snprintf(compiler, sizeof(compiler), "Clang %d.%d.%d", __clang_major__, __clang_minor__, __clang_patchlevel__);
#else
    snprintf(compiler, sizeof(compiler), "unknown");
#endif
    return v;
}

nb_status_t nb_engine_init(nb_engine_t *engine) {
    if (!engine) return NB_ERR_NULL;
    memset(engine, 0, sizeof(*engine));

    nb_status_t s;
    s = nb_system_init(&engine->agent_system);
    NB_CHECK(s);
    s = nb_multi_agent_init(&engine->multi_agent);
    NB_CHECK(s);
    s = nb_plugin_system_init(&engine->plugin_system);
    NB_CHECK(s);
    s = nb_registry_init(&engine->registry);
    NB_CHECK(s);

    engine->initialized = true;
    return NB_OK;
}

nb_status_t nb_engine_shutdown(nb_engine_t *engine) {
    if (!engine) return NB_ERR_NULL;

    /* Shutdown plugins */
    nb_plugin_system_shutdown_all(&engine->plugin_system);

    /* Clear registries */
    nb_registry_clear(&engine->registry);
    nb_system_init(&engine->agent_system); /* Reset agent system */

    engine->initialized = false;
    return NB_OK;
}

nb_status_t nb_engine_register_tool(
    nb_engine_t *engine,
    const char *name,
    const char *version,
    nb_tool_forward_t forward,
    nb_tool_backward_t backward,
    void *context,
    const nb_tool_schema_t *schema
) {
    if (!engine || !name || !forward) return NB_ERR_NULL;
    if (!engine->initialized) return NB_ERR;

    nb_tool_lens_t lens;
    nb_status_t s = nb_lens_init(&lens, name, version, forward, backward, context);
    NB_CHECK(s);

    return nb_registry_register(&engine->registry, &lens, schema);
}

nb_status_t nb_engine_create_agent(
    nb_engine_t *engine,
    const char *id,
    const char *name,
    const char *type
) {
    if (!engine || !id) return NB_ERR_NULL;
    if (!engine->initialized) return NB_ERR;

    nb_status_t s = nb_system_create_agent(&engine->agent_system, id, name, type, NULL);
    NB_CHECK(s);

    /* Also add to multi-agent system */
    nb_agent_t *agent = nb_system_get_agent(&engine->agent_system, id);
    if (agent) {
        return nb_multi_agent_add(&engine->multi_agent, agent);
    }
    return NB_ERR_NOTFOUND;
}

nb_status_t nb_engine_infer(
    nb_engine_t *engine,
    const char *agent_id,
    const void *input,
    size_t input_size,
    nb_exec_result_t *result
) {
    if (!engine || !agent_id || !result) return NB_ERR_NULL;
    if (!engine->initialized) return NB_ERR;

    nb_agent_t *agent = nb_system_get_agent(&engine->agent_system, agent_id);
    if (!agent) return NB_ERR_NOTFOUND;

    /* Set agent to running */
    nb_agent_set_state(agent, NB_AGENT_RUNNING);

    /* Execute */
    nb_status_t s = nb_agent_execute(agent, &engine->registry, input, input_size, result);
    NB_CHECK(s);

    /* Update multi-agent social precision */
    nb_multi_agent_update_social_precision(&engine->multi_agent, "engine", agent_id,
        result->status == NB_EXEC_SUCCESS);

    return NB_OK;
}

nb_status_t nb_engine_status(const nb_engine_t *engine, char *buf, size_t buf_size) {
    if (!engine || !buf) return NB_ERR_NULL;

    char ma_buf[256];
    nb_multi_agent_status(&engine->multi_agent, ma_buf, sizeof(ma_buf));

    snprintf(buf, buf_size,
        "Engine{version=%d.%d.%d, initialized=%s, agents=%d, tools=%d, %s}",
        NEURALBLITZ_VERSION_MAJOR, NEURALBLITZ_VERSION_MINOR, NEURALBLITZ_VERSION_PATCH,
        engine->initialized ? "true" : "false",
        engine->agent_system.agent_count,
        engine->registry.count,
        ma_buf);
    return NB_OK;
}
