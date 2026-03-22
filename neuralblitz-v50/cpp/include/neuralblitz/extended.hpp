#ifndef NEURALBLITZ_EXTENDED_HPP
#define NEURALBLITZ_EXTENDED_HPP

#include "combined.hpp"
#include <algorithm>
#include <cmath>
#include <complex>
#include <numeric>
#include <future>
#include <shared_mutex>

namespace neuralblitz {

// ============== Distributed Consensus (Raft-like) ==============

class ConsensusModule {
public:
    enum class NodeState { FOLLOWER, CANDIDATE, LEADER };
    enum class LogEntryStatus { PENDING, COMMITTED, APPLIED };

    struct LogEntry {
        uint64_t term;
        uint64_t index;
        std::string command;
        Timestamp timestamp;
        LogEntryStatus status;
        
        LogEntry(uint64_t t, uint64_t i, const std::string& cmd)
            : term(t), index(i), command(cmd), timestamp(current_timestamp()), status(LogEntryStatus::PENDING) {}
    };

    ConsensusModule(AgentID node_id) 
        : node_id_(node_id), current_term_(0), voted_for_(INVALID_AGENT_ID),
          commit_index_(0), last_applied_(0), state_(NodeState::FOLLOWER),
          last_heartbeat_(current_timestamp()) {}

    AgentID get_node_id() const { return node_id_; }
    NodeState get_state() const { return state_; }
    uint64_t get_current_term() const { return current_term_; }

    void become_leader() {
        state_ = NodeState::LEADER;
        leader_id_ = node_id_;
        Logger::instance().info("Node " + std::to_string(node_id_) + " became leader");
    }

    void become_follower(uint64_t term) {
        state_ = NodeState::FOLLOWER;
        current_term_ = term;
    }

    bool is_leader() const { return state_ == NodeState::LEADER; }

    void append_log(const std::string& command) {
        LogEntry entry(current_term_, log_.size() + 1, command);
        log_.push_back(entry);
    }

    uint64_t get_log_size() const { return log_.size(); }

    bool replicate_to(uint64_t node_id) {
        if (!is_leader()) return false;
        replicated_to_.insert(node_id);
        return true;
    }

    bool is_majority(size_t total_nodes) {
        return replicated_to_.size() >= (total_nodes / 2 + 1);
    }

    void commit_entries() {
        for (size_t i = commit_index_; i < log_.size(); ++i) {
            if (log_[i].status == LogEntryStatus::PENDING) {
                log_[i].status = LogEntryStatus::COMMITTED;
                commit_index_ = i + 1;
            }
        }
    }

private:
    AgentID node_id_;
    uint64_t current_term_;
    AgentID voted_for_;
    AgentID leader_id_;
    uint64_t commit_index_;
    uint64_t last_applied_;
    NodeState state_;
    Timestamp last_heartbeat_;
    std::vector<LogEntry> log_;
    std::set<AgentID> replicated_to_;

    static Timestamp current_timestamp() {
        return std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();
    }
};

// ============== ML Training ==============

class MLTrainingEngine {
public:
    struct Model {
        std::string name;
        std::vector<double> weights;
        double bias;
        double learning_rate;
        uint64_t epoch;
        double accuracy;
        
        Model(const std::string& n, size_t input_size) 
            : name(n), bias(0.0), learning_rate(0.01), epoch(0), accuracy(0.0) {
            weights.resize(input_size, 0.0);
        }
    };

    struct TrainingData {
        std::vector<std::vector<double>> inputs;
        std::vector<double> labels;
        std::vector<double> outputs;
    };

    MLTrainingEngine() : training_in_progress_(false) {}

    Model create_model(const std::string& name, size_t input_size) {
        return Model(name, input_size);
    }

    void train(Model& model, const TrainingData& data, uint64_t epochs = 10) {
        training_in_progress_ = true;
        Logger::instance().info("Starting training for model: " + model.name);

        for (uint64_t e = 0; e < epochs && training_in_progress_; ++e) {
            model.epoch = e;
            double total_error = 0.0;

            for (size_t i = 0; i < data.inputs.size(); ++i) {
                double prediction = predict(model, data.inputs[i]);
                double error = data.labels[i] - prediction;
                total_error += error * error;

                for (size_t j = 0; j < model.weights.size(); ++j) {
                    model.weights[j] += model.learning_rate * error * data.inputs[i][j];
                }
                model.bias += model.learning_rate * error;
            }

            model.accuracy = 1.0 - (total_error / data.inputs.size());
        }

        training_in_progress_ = false;
        Logger::instance().info("Training completed. Final accuracy: " + std::to_string(model.accuracy));
    }

    double predict(const Model& model, const std::vector<double>& input) {
        double sum = model.bias;
        for (size_t i = 0; i < std::min(input.size(), model.weights.size()); ++i) {
            sum += input[i] * model.weights[i];
        }
        return sigmoid(sum);
    }

    void stop_training() { training_in_progress_ = false; }

private:
    bool training_in_progress_;

    double sigmoid(double x) const {
        return 1.0 / (1.0 + std::exp(-std::clamp(x, -500.0, 500.0)));
    }
};

// ============== Monitoring & Metrics ==============

class MetricsCollector {
public:
    struct Metric {
        std::string name;
        double value;
        Timestamp timestamp;
        std::map<std::string, std::string> tags;
    };

    MetricsCollector() : last_collection_(current_timestamp()) {}

    void record(const std::string& name, double value, const std::map<std::string, std::string>& tags = {}) {
        Metric m{name, value, current_timestamp(), tags};
        metrics_.push_back(m);
    }

    void record_agent_metric(AgentID agent_id, const std::string& metric, double value) {
        record(metric, value, {{"agent_id", std::to_string(agent_id)}});
    }

    void record_task_metric(TaskID task_id, const std::string& metric, double value) {
        record(metric, value, {{"task_id", std::to_string(task_id)}});
    }

    double get_average(const std::string& name) const {
        double sum = 0.0;
        int count = 0;
        for (const auto& m : metrics_) {
            if (m.name == name) {
                sum += m.value;
                count++;
            }
        }
        return count > 0 ? sum / count : 0.0;
    }

    std::vector<Metric> get_recent(const std::string& name, size_t n = 10) const {
        std::vector<Metric> result;
        for (auto it = metrics_.rbegin(); it != metrics_.rend() && result.size() < n; ++it) {
            if (it->name == name) result.push_back(*it);
        }
        return result;
    }

    void clear() { metrics_.clear(); }

    size_t get_size() const { return metrics_.size(); }

private:
    std::vector<Metric> metrics_;
    Timestamp last_collection_;

    static Timestamp current_timestamp() {
        return std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();
    }
};

class MonitoringService {
public:
    MonitoringService() : running_(false), alerts_enabled_(true) {
        metrics_ = std::make_shared<MetricsCollector>();
    }

    std::shared_ptr<MetricsCollector> get_metrics() const { return metrics_; }

    void start() {
        running_ = true;
        Logger::instance().info("MonitoringService started");
    }

    void stop() {
        running_ = false;
        Logger::instance().info("MonitoringService stopped");
    }

    void record_agent_heartbeat(AgentID agent_id) {
        metrics_->record_agent_metric(agent_id, "heartbeat", 1.0);
    }

    void record_task_completion(TaskID task_id, uint64_t duration_ms) {
        metrics_->record_task_metric(task_id, "completion_time", static_cast<double>(duration_ms));
    }

    void record_system_load(double load) {
        metrics_->record("system_load", load);
    }

    void record_memory_usage(uint64_t bytes) {
        metrics_->record("memory_usage", static_cast<double>(bytes));
    }

    void enable_alerts() { alerts_enabled_ = true; }
    void disable_alerts() { alerts_enabled_ = false; }

    void check_and_alert() {
        if (!alerts_enabled_ || !running_) return;

        double avg_load = metrics_->get_average("system_load");
        if (avg_load > 0.9) {
            Logger::instance().warning("High system load detected: " + std::to_string(avg_load));
        }

        size_t task_count = metrics_->get_size();
        if (task_count > 10000) {
            Logger::instance().warning("High metric count: " + std::to_string(task_count));
        }
    }

    std::string generate_report() const {
        std::stringstream ss;
        ss << "=== MONITORING REPORT ===\n";
        ss << "System Load: " << metrics_->get_average("system_load") << "\n";
        ss << "Memory Usage: " << metrics_->get_average("memory_usage") << " bytes\n";
        ss << "Total Metrics: " << metrics_->get_size() << "\n";
        ss << "Running: " << (running_ ? "Yes" : "No") << "\n";
        return ss.str();
    }

private:
    bool running_;
    bool alerts_enabled_;
    std::shared_ptr<MetricsCollector> metrics_;
};

// ============== Enhanced Governance ==============

class EnhancedGovernanceSystem {
public:
    struct Policy {
        std::string id;
        std::string name;
        std::string description;
        bool enabled;
        double threshold;
        
        Policy(const std::string& i, const std::string& n, const std::string& d, double t)
            : id(i), name(n), description(d), enabled(true), threshold(t) {}
    };

    EnhancedGovernanceSystem() : base_governance_(std::make_shared<GovernanceSystem>()) {
        initialize_policies();
    }

    void initialize_policies() {
        policies_["POLICY_001"] = Policy("POLICY_001", "MaxTrustThreshold", "Maximum trust score threshold", 0.95);
        policies_["POLICY_002"] = Policy("POLICY_002", "MinPerformance", "Minimum performance score", 0.5);
        policies_["POLICY_003"] = Policy("POLICY_003", "MaxTaskRate", "Maximum task rate per agent", 100.0);
        policies_["POLICY_004"] = Policy("POLICY_004", "RequireAttestation", "Require valid attestation", 0.8);
        policies_["POLICY_005"] = Policy("POLICY_005", "AuditFrequency", "Audit trail frequency check", 0.9);
    }

    GovernanceDecision evaluate_agent(AgentPtr agent, TaskPtr task) {
        GovernanceDecision base_decision = base_governance_->evaluate_task(agent, task);

        if (!check_policies(agent)) {
            return GovernanceDecision::DENIED;
        }

        return base_decision;
    }

    bool check_policies(AgentPtr agent) {
        for (auto& pair : policies_) {
            if (!pair.second.enabled) continue;

            if (pair.first == "POLICY_001" && agent->get_trust_score() > pair.second.threshold) {
                Logger::instance().warning("Policy violation: " + pair.first);
                return false;
            }

            if (pair.first == "POLICY_002" && agent->get_performance_score() < pair.second.threshold) {
                Logger::instance().warning("Policy violation: " + pair.first);
                return false;
            }
        }
        return true;
    }

    void enable_policy(const std::string& policy_id) {
        if (policies_.count(policy_id)) {
            policies_[policy_id].enabled = true;
            Logger::instance().info("Policy enabled: " + policy_id);
        }
    }

    void disable_policy(const std::string& policy_id) {
        if (policies_.count(policy_id)) {
            policies_[policy_id].enabled = false;
            Logger::instance().info("Policy disabled: " + policy_id);
        }
    }

    std::vector<std::string> get_violating_agents(const std::vector<AgentPtr>& agents) {
        std::vector<std::string> violations;
        for (const auto& agent : agents) {
            if (!check_policies(agent)) {
                violations.push_back(agent->get_name() + " (ID: " + std::to_string(agent->get_id()) + ")");
            }
        }
        return violations;
    }

    std::string generate_policy_report() const {
        std::stringstream ss;
        ss << "=== POLICY REPORT ===\n";
        for (const auto& pair : policies_) {
            ss << pair.first << ": " << pair.second.name 
               << " [enabled: " << (pair.second.enabled ? "YES" : "NO") << "]\n";
        }
        return ss.str();
    }

private:
    std::shared_ptr<GovernanceSystem> base_governance_;
    std::map<std::string, Policy> policies_;
};

// ============== Event System ==============

class EventSystem {
public:
    enum class EventType {
        AGENT_REGISTERED,
        AGENT_UNREGISTERED,
        TASK_SUBMITTED,
        TASK_COMPLETED,
        TASK_FAILED,
        GOVERNANCE_DECISION,
        VIOLATION_DETECTED,
        SYSTEM_ALERT
    };

    struct Event {
        EventType type;
        Timestamp timestamp;
        std::string source;
        std::string data;
        std::map<std::string, std::string> metadata;
        
        Event(EventType t, const std::string& s, const std::string& d)
            : type(t), timestamp(current_timestamp()), source(s), data(d) {}
    };

    using EventHandler = std::function<void(const Event&)>;

    void subscribe(EventType type, EventHandler handler) {
        handlers_[type].push_back(handler);
    }

    void publish(EventType type, const std::string& source, const std::string& data,
                 const std::map<std::string, std::string>& metadata = {}) {
        Event event(type, source, data);
        event.metadata = metadata;
        
        auto it = handlers_.find(type);
        if (it != handlers_.end()) {
            for (const auto& handler : it->second) {
                handler(event);
            }
        }
        
        events_.push_back(event);
    }

    std::vector<Event> get_events(EventType type) const {
        std::vector<Event> result;
        for (const auto& e : events_) {
            if (e.type == type) result.push_back(e);
        }
        return result;
    }

    std::vector<Event> get_recent_events(size_t n = 100) const {
        std::vector<Event> result;
        for (auto it = events_.rbegin(); it != events_.rend() && result.size() < n; ++it) {
            result.push_back(*it);
        }
        return result;
    }

    void clear() { events_.clear(); }

private:
    std::map<EventType, std::vector<EventHandler>> handlers_;
    std::vector<Event> events_;

    static Timestamp current_timestamp() {
        return std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();
    }
};

// ============== Load Balancer ==============

class LoadBalancer {
public:
    enum class Strategy { ROUND_ROBIN, LEAST_CONNECTIONS, WEIGHTED, RANDOM };

    LoadBalancer(Strategy strategy = Strategy::ROUND_ROBIN) 
        : strategy_(strategy), current_index_(0) {}

    AgentPtr select_agent(const std::vector<AgentPtr>& agents) {
        if (agents.empty()) return nullptr;

        switch (strategy_) {
            case Strategy::ROUND_ROBIN:
                return round_robin(agents);
            case Strategy::LEAST_CONNECTIONS:
               (agents);
            case Strategy::WEIGHTED:
                return weighted(agents);
            case Strategy return least_connections::RANDOM:
            default:
                return random_selection(agents);
        }
    }

    void set_strategy(Strategy s) { strategy_ = s; }

private:
    Strategy strategy_;
    size_t current_index_;

    AgentPtr round_robin(const std::vector<AgentPtr>& agents) {
        auto agent = agents[current_index_ % agents.size()];
        current_index_++;
        return agent;
    }

    AgentPtr least_connections(const std::vector<AgentPtr>& agents) {
        AgentPtr best = nullptr;
        double lowest_load = 1e9;
        
        for (const auto& agent : agents) {
            double load = 1.0 - agent->get_performance_score();
            if (load < lowest_load && agent->is_available()) {
                lowest_load = load;
                best = agent;
            }
        }
        
        return best ? best : agents[0];
    }

    AgentPtr weighted(const std::vector<AgentPtr>& agents) {
        double total_weight = 0.0;
        for (const auto& agent : agents) {
            total_weight += agent->get_trust_score();
        }
        
        static std::random_device rd;
        static std::mt19937 gen(rd());
        std::uniform_real_distribution<> dis(0.0, total_weight);
        
        double target = dis(gen);
        double cumulative = 0.0;
        
        for (const auto& agent : agents) {
            cumulative += agent->get_trust_score();
            if (cumulative >= target) return agent;
        }
        
        return agents.back();
    }

    AgentPtr random_selection(const std::vector<AgentPtr>& agents) {
        static std::random_device rd;
        static std::mt19937 gen(rd());
        std::uniform_int_distribution<> dis(0, agents.size() - 1);
        return agents[dis(gen)];
    }
};

}

#endif
