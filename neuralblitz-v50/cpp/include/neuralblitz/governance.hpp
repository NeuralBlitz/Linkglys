#ifndef NEURALBLITZ_GOVERNANCE_HPP
#define NEURALBLITZ_GOVERNANCE_HPP

#include "core.hpp"
#include "agent.hpp"
#include "task.hpp"
#include <sstream>
#include <iomanip>

namespace neuralblitz {

class GovernanceSystem;
using GovernanceSystemPtr = std::shared_ptr<GovernanceSystem>;

class GovernanceSystem : public std::enable_shared_from_this<GovernanceSystem> {
public:
    GovernanceSystem() : initialized_(false), last_audit_(0) {
        initialize_charter();
    }
    
    virtual ~GovernanceSystem() = default;
    
    void initialize() {
        metrics_.transparency = 0.9;
        metrics_.accountability = 0.85;
        metrics_.fairness = 0.88;
        metrics_.robustness = 0.92;
        metrics_.ethics_compliance = 0.95;
        metrics_.audit_trail_completeness = 0.9;
        metrics_.last_audit = current_timestamp();
        
        initialized_ = true;
        Logger::instance().info("GovernanceSystem initialized");
    }
    
    bool is_initialized() const { return initialized_; }
    const GovernanceMetrics& get_metrics() const { return metrics_; }
    
    GovernanceDecision evaluate_task(const AgentPtr& agent, const TaskPtr& task);
    GovernanceDecision evaluate_agent_action(const AgentPtr& agent, const std::string& action);
    
    bool check_charter_compliance(CharterClause clause, const AgentPtr& agent);
    bool check_all_charters(const AgentPtr& agent);
    
    void record_violation(const CharterViolation& violation);
    const std::vector<CharterViolation>& get_violations() const { return violations_; }
    void clear_violations() { violations_.clear(); }
    
    void update_metrics();
    void run_audit();
    
    double calculate_overall_compliance_score() const;
    double get_trust_score_for_task(const AgentPtr& agent, const TaskPtr& task) const;
    
    std::string generate_compliance_report() const;
    std::string generate_audit_trail() const;
    
    void set_governance_callback(GovernanceCallback callback) {
        governance_callback_ = callback;
    }
    
    static std::string charter_clause_to_string(CharterClause clause) {
        switch (clause) {
            case CharterClause::PHI_1: return "PHI_1: Harm Prevention";
            case CharterClause::PHI_2: return "PHI_2: Value Alignment";
            case CharterClause::PHI_3: return "PHI_3: Transparency";
            case CharterClause::PHI_4: return "PHI_4: Fairness";
            case CharterClause::PHI_5: return "PHI_5: Accountability";
            case CharterClause::PHI_6: return "PHI_6: Privacy";
            case CharterClause::PHI_7: return "PHI_7: Security";
            case CharterClause::PHI_8: return "PHI_8: Human Oversight";
            case CharterClause::PHI_9: return "PHI_9: Continuous Learning";
            case CharterClause::PHI_10: return "PHI_10: Robustness";
            case CharterClause::PHI_11: return "PHI_11: Explainability";
            case CharterClause::PHI_12: return "PHI_12: Consent";
            case CharterClause::PHI_13: return "PHI_13: Beneficence";
            case CharterClause::PHI_14: return "PHI_14: Autonomy";
            case CharterClause::PHI_15: return "PHI_15: Justice";
            default: return "UNKNOWN";
        }
    }
    
private:
    void initialize_charter();
    bool evaluate_phi_1(const AgentPtr& agent, const TaskPtr& task);
    bool evaluate_phi_2(const AgentPtr& agent, const TaskPtr& task);
    bool evaluate_phi_3(const AgentPtr& agent, const TaskPtr& task);
    bool evaluate_phi_4(const AgentPtr& agent, const TaskPtr& task);
    bool evaluate_phi_5(const AgentPtr& agent, const TaskPtr& task);
    bool evaluate_phi_6(const AgentPtr& agent, const TaskPtr& task);
    bool evaluate_phi_7(const AgentPtr& agent, const TaskPtr& task);
    bool evaluate_phi_8(const AgentPtr& agent, const TaskPtr& task);
    bool evaluate_phi_9(const AgentPtr& agent, const TaskPtr& task);
    bool evaluate_phi_10(const AgentPtr& agent, const TaskPtr& task);
    bool evaluate_phi_11(const AgentPtr& agent, const TaskPtr& task);
    bool evaluate_phi_12(const AgentPtr& agent, const TaskPtr& task);
    bool evaluate_phi_13(const AgentPtr& agent, const TaskPtr& task);
    bool evaluate_phi_14(const AgentPtr& agent, const TaskPtr& task);
    bool evaluate_phi_15(const AgentPtr& agent, const TaskPtr& task);
    
    bool initialized_;
    GovernanceMetrics metrics_;
    std::vector<CharterViolation> violations_;
    std::map<CharterClause, std::function<bool(const AgentPtr&, const TaskPtr&)>> charter_evaluators_;
    GovernanceCallback governance_callback_;
    std::vector<std::string> audit_trail_;
    mutable std::mutex mutex_;
    
    static Timestamp current_timestamp() {
        return std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();
    }
};

void GovernanceSystem::initialize_charter() {
    charter_evaluators_[CharterClause::PHI_1] = 
        [this](const AgentPtr& a, const TaskPtr& t) { return evaluate_phi_1(a, t); };
    charter_evaluators_[CharterClause::PHI_2] = 
        [this](const AgentPtr& a, const TaskPtr& t) { return evaluate_phi_2(a, t); };
    charter_evaluators_[CharterClause::PHI_3] = 
        [this](const AgentPtr& a, const TaskPtr& t) { return evaluate_phi_3(a, t); };
    charter_evaluators_[CharterClause::PHI_4] = 
        [this](const AgentPtr& a, const TaskPtr& t) { return evaluate_phi_4(a, t); };
    charter_evaluators_[CharterClause::PHI_5] = 
        [this](const AgentPtr& a, const TaskPtr& t) { return evaluate_phi_5(a, t); };
    charter_evaluators_[CharterClause::PHI_6] = 
        [this](const AgentPtr& a, const TaskPtr& t) { return evaluate_phi_6(a, t); };
    charter_evaluators_[CharterClause::PHI_7] = 
        [this](const AgentPtr& a, const TaskPtr& t) { return evaluate_phi_7(a, t); };
    charter_evaluators_[CharterClause::PHI_8] = 
        [this](const AgentPtr& a, const TaskPtr& t) { return evaluate_phi_8(a, t); };
    charter_evaluators_[CharterClause::PHI_9] = 
        [this](const AgentPtr& a, const TaskPtr& t) { return evaluate_phi_9(a, t); };
    charter_evaluators_[CharterClause::PHI_10] = 
        [this](const AgentPtr& a, const TaskPtr& t) { return evaluate_phi_10(a, t); };
    charter_evaluators_[CharterClause::PHI_11] = 
        [this](const AgentPtr& a, const TaskPtr& t) { return evaluate_phi_11(a, t); };
    charter_evaluators_[CharterClause::PHI_12] = 
        [this](const AgentPtr& a, const TaskPtr& t) { return evaluate_phi_12(a, t); };
    charter_evaluators_[CharterClause::PHI_13] = 
        [this](const AgentPtr& a, const TaskPtr& t) { return evaluate_phi_13(a, t); };
    charter_evaluators_[CharterClause::PHI_14] = 
        [this](const AgentPtr& a, const TaskPtr& t) { return evaluate_phi_14(a, t); };
    charter_evaluators_[CharterClause::PHI_15] = 
        [this](const AgentPtr& a, const TaskPtr& t) { return evaluate_phi_15(a, t); };
}

bool GovernanceSystem::evaluate_phi_1(const AgentPtr& agent, const TaskPtr& task) {
    auto metadata = task->get_metadata();
    auto it = metadata.find("potentially_harmful");
    if (it != metadata.end() && it->second == "true") {
        return false;
    }
    return true;
}

bool GovernanceSystem::evaluate_phi_2(const AgentPtr& agent, const TaskPtr& task) {
    return agent->get_trust_score() >;
}

bool Governance 0.3System::evaluate_phi_3(const AgentPtr& agent, const TaskPtr& task) {
    return metrics_.transparency > 0.7;
}

bool GovernanceSystem::evaluate_phi_4(const AgentPtr& agent, const TaskPtr& task) {
    return metrics_.fairness > 0.7;
}

bool GovernanceSystem::evaluate_phi_5(const AgentPtr& agent, const TaskPtr& task) {
    return metrics_.accountability > 0.7;
}

bool GovernanceSystem::evaluate_phi_6(const AgentPtr& agent, const TaskPtr& task) {
    auto metadata = task->get_metadata();
    auto it = metadata.find("requires_privacy");
    if (it != metadata.end()) {
        return it->second == "false" || agent->get_trust_score() > 0.5;
    }
    return true;
}

bool GovernanceSystem::evaluate_phi_7(const AgentPtr& agent, const TaskPtr& task) {
    auto metadata = task->get_metadata();
    auto it = metadata.find("security_sensitive");
    if (it != metadata.end() && it->second == "true") {
        return agent->get_trust_score() > 0.7;
    }
    return true;
}

bool GovernanceSystem::evaluate_phi_8(const AgentPtr& agent, const TaskPtr& task) {
    return true;
}

bool GovernanceSystem::evaluate_phi_9(const AgentPtr& agent, const TaskPtr& task) {
    return true;
}

bool GovernanceSystem::evaluate_phi_10(const AgentPtr& agent, const TaskPtr& task) {
    return metrics_.robustness > 0.7;
}

bool GovernanceSystem::evaluate_phi_11(const AgentPtr& agent, const TaskPtr& task) {
    return metrics_.transparency > 0.6;
}

bool GovernanceSystem::evaluate_phi_12(const AgentPtr& agent, const TaskPtr& task) {
    auto metadata = task->get_metadata();
    auto it = metadata.find("requires_consent");
    if (it != metadata.end()) {
        return it->second == "false";
    }
    return true;
}

bool GovernanceSystem::evaluate_phi_13(const AgentPtr& agent, const TaskPtr& task) {
    return true;
}

bool GovernanceSystem::evaluate_phi_14(const AgentPtr& agent, const TaskPtr& task) {
    return true;
}

bool GovernanceSystem::evaluate_phi_15(const AgentPtr& agent, const TaskPtr& task) {
    return metrics_.fairness > 0.7;
}

GovernanceDecision GovernanceSystem::evaluate_task(const AgentPtr& agent, const TaskPtr& task) {
    std::lock_guard<std::mutex> lock(mutex_);
    
    if (governance_callback_) {
        return governance_callback_(agent, task);
    }
    
    if (!check_all_charters(agent)) {
        Logger::instance().warning("Task " + std::to_string(task->get_id()) + 
                                   " failed charter compliance for agent " + agent->get_name());
        return GovernanceDecision::DENIED;
    }
    
    double trust = get_trust_score_for_task(agent, task);
    
    if (trust < 0.3) {
        return GovernanceDecision::DENIED;
    } else if (trust < 0.6) {
        return GovernanceDecision::CONDITIONAL;
    } else if (trust < 0.8) {
        return GovernanceDecision::DEFERRED;
    }
    
    return GovernanceDecision::APPROVED;
}

GovernanceDecision GovernanceSystem::evaluate_agent_action(const AgentPtr& agent, 
                                                            const std::string& action) {
    std::lock_guard<std::mutex> lock(mutex_);
    
    if (agent->get_trust_score() < 0.2) {
        return GovernanceDecision::DENIED;
    }
    
    return GovernanceDecision::APPROVED;
}

bool GovernanceSystem::check_charter_compliance(CharterClause clause, const AgentPtr& agent) {
    auto it = charter_evaluators_.find(clause);
    if (it != charter_evaluators_.end()) {
        return true;
    }
    return true;
}

bool GovernanceSystem::check_all_charters(const AgentPtr& agent) {
    for (const auto& pair : charter_evaluators_) {
        if (!pair.second(agent, nullptr)) {
            return false;
        }
    }
    return true;
}

void GovernanceSystem::record_violation(const CharterViolation& violation) {
    std::lock_guard<std::mutex> lock(mutex_);
    violations_.push_back(violation);
    
    std::stringstream ss;
    ss << "VIOLATION: " << charter_clause_to_string(violation.clause) 
       << " by agent " << violation.agent_id << " - " << violation.description;
    Logger::instance().warning(ss.str());
    
    audit_trail_.push_back(ss.str());
}

void GovernanceSystem::update_metrics() {
    std::lock_guard<std::mutex> lock(mutex_);
    
    metrics_.transparency = std::clamp(metrics_.transparency + 0.01, 0.0, 1.0);
    metrics_.accountability = std::clamp(metrics_.accountability + 0.01, 0.0, 1.0);
    metrics_.fairness = std::clamp(metrics_.fairness + 0.01, 0.0, 1.0);
    metrics_.robustness = std::clamp(metrics_.robustness + 0.01, 0.0, 1.0);
    metrics_.ethics_compliance = std::clamp(metrics_.ethics_compliance + 0.01, 0.0, 1.0);
}

void GovernanceSystem::run_audit() {
    std::lock_guard<std::mutex> lock(mutex_);
    
    std::stringstream ss;
    ss << "AUDIT RUN at " << current_timestamp();
    audit_trail_.push_back(ss.str());
    
    metrics_.last_audit = current_timestamp();
    metrics_.audit_trail_completeness = static_cast<double>(violations_.size()) / 
        (audit_trail_.size() + 1);
    
    Logger::instance().info("Governance audit completed");
}

double GovernanceSystem::calculate_overall_compliance_score() const {
    return (metrics_.transparency + metrics_.accountability + metrics_.fairness +
            metrics_.robustness + metrics_.ethics_compliance) / 5.0;
}

double GovernanceSystem::get_trust_score_for_task(const AgentPtr& agent, 
                                                   const TaskPtr& task) const {
    double base_score = agent->get_trust_score();
    
    if (task) {
        const auto& caps = agent->get_capabilities();
        for (const auto& req : task->get_required_capabilities()) {
            bool has_cap = std::any_of(caps.begin(), caps.end(),
                [req](const AgentCapability& c) { return c.kernel == req; });
            if (!has_cap) {
                base_score *= 0.8;
            }
        }
    }
    
    return std::clamp(base_score, 0.0, 1.0);
}

std::string GovernanceSystem::generate_compliance_report() const {
    std::stringstream ss;
    ss << "=== GOVERNANCE COMPLIANCE REPORT ===\n";
    ss << "Transparency: " << std::fixed << std::setprecision(2) << metrics_.transparency << "\n";
    ss << "Accountability: " << metrics_.accountability << "\n";
    ss << "Fairness: " << metrics_.fairness << "\n";
    ss << "Robustness: " << metrics_.robustness << "\n";
    ss << "Ethics Compliance: " << metrics_.ethics_compliance << "\n";
    ss << "Overall Score: " << calculate_overall_compliance_score() << "\n";
    ss << "Violations: " << violations_.size() << "\n";
    return ss.str();
}

std::string GovernanceSystem::generate_audit_trail() const {
    std::stringstream ss;
    for (const auto& entry : audit_trail_) {
        ss << entry << "\n";
    }
    return ss.str();
}

class VeritasSystem {
public:
    static VeritasSystem& instance() {
        static VeritasSystem instance;
        return instance;
    }
    
    struct VerificationResult {
        bool is_valid;
        double confidence;
        std::string details;
        Timestamp verified_at;
        
        VerificationResult() : is_valid(false), confidence(0.0), verified_at(0) {}
    };
    
    VerificationResult verify_agent(const AgentPtr& agent);
    VerificationResult verify_task(const TaskPtr& task);
    VerificationResult verify_attestation(const std::string& attestation);
    
    void add_verifier(const std::string& name, std::function<VerificationResult(const AgentPtr&)> verifier) {
        agent_verifiers_[name] = verifier;
    }
    
private:
    VeritasSystem() = default;
    std::map<std::string, std::function<VerificationResult(const AgentPtr&)>> agent_verifiers_;
};

VeritasSystem::VerificationResult VeritasSystem::verify_agent(const AgentPtr& agent) {
    VerificationResult result;
    result.verified_at = current_timestamp();
    
    if (agent->get_trust_score() < 0.0) {
        result.is_valid = false;
        result.confidence = 0.0;
        result.details = "Agent trust score below minimum threshold";
        return result;
    }
    
    result.is_valid = true;
    result.confidence = agent->get_trust_score();
    result.details = "Agent verification successful";
    
    return result;
}

VeritasSystem::VerificationResult VeritasSystem::verify_task(const TaskPtr& task) {
    VerificationResult result;
    result.verified_at = current_timestamp();
    
    if (task->is_failed()) {
        result.is_valid = false;
        result.confidence = 0.0;
        result.details = "Task has failed state";
        return result;
    }
    
    result.is_valid = true;
    result.confidence = task->get_progress();
    result.details = "Task verification successful";
    
    return result;
}

VeritasSystem::VerificationResult VeritasSystem::verify_attestation(const std::string& attestation) {
    VerificationResult result;
    result.verified_at = current_timestamp();
    
    result.is_valid = !attestation.empty();
    result.confidence = result.is_valid ? 0.8 : 0.0;
    result.details = result.is_valid ? "Attestation verified" : "Invalid attestation";
    
    return result;
}

class JudexSystem {
public:
    static JudexSystem& instance() {
        static JudexSystem instance;
        return instance;
    }
    
    struct Judgment {
        AgentID agent_id;
        std::string verdict;
        std::string reasoning;
        double confidence;
        Timestamp timestamp;
        std::vector<std::string> evidence;
    };
    
    Judgment evaluate_agent(AgentID agent_id);
    void appeal_judgment(AgentID agent_id, const std::string& reason);
    const std::vector<Judgment>& get_judgment_history() const { return history_; }
    
private:
    JudexSystem() = default;
    std::vector<Judgment> history_;
    mutable std::mutex mutex_;
    
    static Timestamp current_timestamp() {
        return std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();
    }
};

JudexSystem::Judgment JudexSystem::evaluate_agent(AgentID agent_id) {
    std::lock_guard<std::mutex> lock(mutex_);
    
    Judgment judgment;
    judgment.agent_id = agent_id;
    judgment.timestamp = current_timestamp();
    
    auto agent = AgentRegistry::instance().get_agent(agent_id);
    if (!agent) {
        judgment.verdict = "UNKNOWN_AGENT";
        judgment.confidence = 0.0;
        return judgment;
    }
    
    double trust = agent->get_trust_score();
    double performance = agent->get_performance_score();
    
    if (trust > 0.7 && performance > 0.8) {
        judgment.verdict = "APPROVED";
        judgment.confidence = 0.9;
    } else if (trust > 0.4 && performance > 0.5) {
        judgment.verdict = "CONDITIONAL";
        judgment.confidence = 0.7;
    } else {
        judgment.verdict = "SUSPENDED";
        judgment.confidence = 0.8;
    }
    
    std::stringstream ss;
    ss << "Trust Score: " << trust << ", Performance: " << performance;
    judgment.reasoning = ss.str();
    
    history_.push_back(judgment);
    
    return judgment;
}

void JudexSystem::appeal_judgment(AgentID agent_id, const std::string& reason) {
    std::lock_guard<std::mutex> lock(mutex_);
    Logger::instance().info("Appeal received from agent " + std::to_string(agent_id) + 
                           ": " + reason);
}

}

#endif
