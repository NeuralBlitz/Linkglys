#include <iostream>
#include <memory>
#include <thread>
#include <chrono>
#include <vector>
#include <string>
#include <cstdlib>
#include <ctime>

#include "neuralblitz/combined.hpp"

using namespace neuralblitz;

void print_header(const std::string& title) {
    std::cout << "\n" << std::string(60, '=') << "\n";
    std::cout << "  " << title << "\n";
    std::cout << std::string(60, '=') << "\n";
}

void demo_basic_agent() {
    print_header("Basic Agent Demo");
    
    auto agent = AgentRegistry::instance().register_agent("TestAgent");
    std::cout << "Created agent: " << agent->get_name() 
              << " (ID: " << agent->get_id() << ")\n";
    
    agent->add_capability(CapabilityKernel::REASONING, 0.9);
    agent->add_capability(CapabilityKernel::PLANNING, 0.8);
    
    std::cout << "Trust Score: " << agent->get_trust_score() << "\n";
    
    auto task = std::make_shared<Task>(1, "Test Task", "payload");
    task->add_required_capability(CapabilityKernel::REASONING);
    
    bool can_handle = agent->can_handle_task(task);
    std::cout << "Can handle task: " << (can_handle ? "Yes" : "No") << "\n";
    
    agent->record_task_completion(true);
    std::cout << "After task - Trust: " << agent->get_trust_score() 
              << ", Performance: " << agent->get_performance_score() << "\n";
}

void demo_agent_factory() {
    print_header("Agent Factory Demo");
    
    auto reasoner = AgentFactory::create_reasoning_agent(100, "ReasonerAlpha");
    auto perceiver = AgentFactory::create_perception_agent(101, "PerceiverBeta");
    auto actor = AgentFactory::create_action_agent(102, "ActorGamma");
    auto governor = AgentFactory::create_governance_agent(103, "GovernorDelta");
    auto verifier = AgentFactory::create_verification_agent(104, "VerifierEpsilon");
    
    std::cout << "Created specialized agents:\n";
    std::cout << "  - " << reasoner->get_name() << " [" << reasoner->get_agent_type() << "]\n";
    std::cout << "  - " << perceiver->get_name() << " [" << perceiver->get_agent_type() << "]\n";
    std::cout << "  - " << actor->get_name() << " [" << actor->get_agent_type() << "]\n";
    std::cout << "  - " << governor->get_name() << " [" << governor->get_agent_type() << "]\n";
    std::cout << "  - " << verifier->get_name() << " [" << verifier->get_agent_type() << "]\n";
}

void demo_cluster() {
    print_header("Agent Cluster Demo");
    
    auto cluster = std::make_shared<AgentCluster>(1, "AlphaCluster");
    
    for (int i = 0; i < 5; ++i) {
        auto agent = AgentRegistry::instance().register_agent("ClusterMember" + std::to_string(i));
        cluster->add_member(agent);
    }
    
    std::cout << "Cluster: " << cluster->get_name() 
              << " (Size: " << cluster->get_size() << ")\n";
    std::cout << "Average Trust: " << cluster->get_average_trust() << "\n";
    
    auto available = cluster->get_available_agents();
    std::cout << "Available Agents: " << available.size() << "\n";
}

void demo_dag() {
    print_header("DAG Pipeline Demo");
    
    auto dag = std::make_shared<DAG>("ProcessingPipeline");
    
    auto stage1 = dag->add_stage("DataIngestion");
    auto stage2 = dag->add_stage("Processing");
    auto stage3 = dag->add_stage("Aggregation");
    
    dag->set_entry_point(stage1->get_id());
    dag->set_exit_point(stage3->get_id());
    
    dag->add_dependency(stage1->get_id(), stage2->get_id());
    dag->add_dependency(stage2->get_id(), stage3->get_id());
    
    for (int i = 0; i < 3; ++i) {
        auto task = std::make_shared<Task>(i + 1, "Task" + std::to_string(i));
        dag->add_task_to_stage(stage1->get_id(), task);
    }
    
    std::cout << "DAG Stages: " << dag->get_stage_count() << "\n";
    std::cout << "Valid: " << (dag->is_valid() ? "Yes" : "No") << "\n";
    std::cout << "Has Cycle: " << (dag->has_cycle() ? "Yes" : "No") << "\n";
}

void demo_governance() {
    print_header("Governance System Demo");
    
    auto governance = std::make_shared<GovernanceSystem>();
    governance->initialize();
    
    auto agent = AgentRegistry::instance().register_agent("GovernedAgent");
    agent->add_capability(CapabilityKernel::GOVERNANCE, 0.9);
    agent->update_trust_score(0.7);
    
    auto task = std::make_shared<Task>(1, "GovernedTask");
    task->add_metadata("requires_privacy", "false");
    task->add_metadata("potentially_harmful", "false");
    
    auto decision = governance->evaluate_task(agent, task);
    
    std::cout << "Governance Decision: ";
    switch (decision) {
        case GovernanceDecision::APPROVED: std::cout << "APPROVED\n"; break;
        case GovernanceDecision::DENIED: std::cout << "DENIED\n"; break;
        case GovernanceDecision::CONDITIONAL: std::cout << "CONDITIONAL\n"; break;
        case GovernanceDecision::ESCALATED: std::cout << "ESCALATED\n"; break;
        case GovernanceDecision::DEFERRED: std::cout << "DEFERRED\n"; break;
    }
    
    std::cout << "\n" << governance->generate_compliance_report();
}

void demo_crypto() {
    print_header("Cryptography Demo");
    
    std::string message = "NeuralBlitz v50.0 Secure Message";
    
    auto [pub_key, priv_key] = Crypto::generate_key_pair();
    std::cout << "Generated RSA key pair (simulated)\n";
    
    std::string signature = Crypto::sign(priv_key, message);
    std::cout << "Signed message\n";
    
    bool verified = Crypto::verify(pub_key, message, signature);
    std::cout << "Signature verification: " << (verified ? "SUCCESS" : "FAILED") << "\n";
    
    std::string sha = Crypto::sha256(message);
    std::cout << "SHA-256: " << sha.substr(0, 32) << "...\n";
    
    std::string hmac = Crypto::hmac_sha256("secretkey", message);
    std::cout << "HMAC-SHA256: " << hmac.substr(0, 32) << "...\n";
    
    std::string aes_key = "0123456789abcdef0123456789abcdef";
    std::string encrypted = Crypto::encrypt_aes_gcm(message, aes_key);
    std::cout << "AES-GCM encrypted: " << encrypted.size() << " bytes\n";
    
    std::string decrypted = Crypto::decrypt_aes_gcm(encrypted, aes_key);
    std::cout << "Decrypted: " << decrypted << "\n";
}

void demo_massive_scale() {
    print_header("Massive Scale Demo (50,000+ Stages)");
    
    const size_t NUM_AGENTS = 100000;
    const size_t NUM_STAGES = 50000;
    
    std::cout << "Creating massive agent pool...\n";
    auto start = std::chrono::high_resolution_clock::now();
    
    for (size_t i = 0; i < NUM_AGENTS; ++i) {
        auto agent = AgentRegistry::instance().register_agent("Agent" + std::to_string(i));
        
        int cap_count = rand() % 5 + 1;
        for (int j = 0; j < cap_count; ++j) {
            CapabilityKernel cap = static_cast<CapabilityKernel>(rand() % 10);
            agent->add_capability(cap, 0.5 + (rand() % 50) / 100.0);
        }
    }
    
    auto agent_end = std::chrono::high_resolution_clock::now();
    auto agent_duration = std::chrono::duration_cast<std::chrono::milliseconds>(agent_end - start);
    
    std::cout << "Created " << AgentRegistry::instance().get_agent_count() << " agents in "
              << agent_duration.count() << "ms\n";
    
    std::cout << "\nCreating task pipeline with " << NUM_STAGES << " stages...\n";
    
    auto dag = std::make_shared<DAG>("MassivePipeline");
    std::vector<StageID> stage_ids;
    stage_ids.reserve(NUM_STAGES);
    
    for (size_t i = 0; i < NUM_STAGES; ++i) {
        auto stage = dag->add_stage("Stage" + std::to_string(i));
        stage_ids.push_back(stage->get_id());
        
        auto task = std::make_shared<Task>(i + 1, "Task" + std::to_string(i));
        task->set_estimated_duration(1);
        dag->add_task_to_stage(stage->get_id(), task);
        
        if (i > 0) {
            dag->add_dependency(stage_ids[i-1], stage_ids[i]);
        }
        
        if (i % 10000 == 0 && i > 0) {
            std::cout << "  Created " << i << " stages...\n";
        }
    }
    
    dag->set_entry_point(stage_ids.front());
    dag->set_exit_point(stage_ids.back());
    
    auto dag_end = std::chrono::high_resolution_clock::now();
    auto dag_duration = std::chrono::duration_cast<std::chrono::milliseconds>(dag_end - agent_end);
    
    std::cout << "Created DAG with " << dag->get_stage_count() << " stages in "
              << dag_duration.count() << "ms\n";
    std::cout << "DAG Valid: " << (dag->is_valid() ? "Yes" : "No") << "\n";
    std::cout << "Has Cycle: " << (dag->has_cycle() ? "Yes" : "No") << "\n";
    
    auto total_end = std::chrono::high_resolution_clock::now();
    auto total_duration = std::chrono::duration_cast<std::chrono::milliseconds>(total_end - start);
    
    std::cout << "\n=== MASSIVE SCALE SUMMARY ===\n";
    std::cout << "Total Agents: " << AgentRegistry::instance().get_agent_count() << "\n";
    std::cout << "Total Stages: " << NUM_STAGES << "\n";
    std::cout << "Total Time: " << total_duration.count() << "ms\n";
    std::cout << "Memory efficient STL-based implementation\n";
}

int main(int argc, char* argv[]) {
    std::srand(std::time(nullptr));
    
    std::cout << R"(
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║     NeuralBlitz v50.0 Omega Singularity Architecture        ║
    ║              C++ Implementation (OSA v2.0)                   ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    )";
    
    std::vector<std::string> args;
    for (int i = 1; i < argc; ++i) {
        args.push_back(argv[i]);
    }
    
    if (args.empty() || args[0] == "all") {
        demo_basic_agent();
        demo_agent_factory();
        demo_cluster();
        demo_dag();
        demo_governance();
        demo_crypto();
        demo_massive_scale();
    } else if (args[0] == "agent") {
        demo_basic_agent();
        demo_agent_factory();
        demo_cluster();
    } else if (args[0] == "task") {
        demo_dag();
    } else if (args[0] == "governance") {
        demo_governance();
    } else if (args[0] == "crypto") {
        demo_crypto();
    } else if (args[0] == "scale") {
        demo_massive_scale();
    } else {
        std::cout << "Usage: " << argv[0] << " [all|agent|task|governance|crypto|scale]\n";
    }
    
    std::cout << "\n" << std::string(60, '=') << "\n";
    std::cout << "  NeuralBlitz v50.0 C++ Demo Complete\n";
    std::cout << std::string(60, '=') << "\n\n";
    
    return 0;
}
