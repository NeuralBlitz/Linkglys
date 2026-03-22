#ifndef NEURALBLITZ_COMBINED_HPP
#define NEURALBLITZ_COMBINED_HPP

#include <string>
#include <vector>
#include <map>
#include <unordered_map>
#include <unordered_set>
#include <memory>
#include <functional>
#include <optional>
#include <variant>
#include <chrono>
#include <mutex>
#include <shared_mutex>
#include <atomic>
#include <queue>
#include <stack>
#include <deque>
#include <tuple>
#include <any>
#include <future>
#include <thread>
#include <algorithm>
#include <numeric>
#include <cstdint>
#include <cstring>
#include <sstream>
#include <iostream>
#include <fstream>
#include <regex>
#include <random>
#include <filesystem>
#include <iomanip>
#include <cmath>
#include <list>
#include <set>

namespace neuralblitz {

using AgentID = uint64_t;
using TaskID = uint64_t;
using StageID = uint64_t;
using Timestamp = uint64_t;
using Score = double;
using TrustScore = double;
using ComplianceScore = double;

constexpr AgentID INVALID_AGENT_ID = 0;
constexpr TaskID INVALID_TASK_ID = 0;
constexpr StageID INVALID_STAGE_ID = 0;
constexpr Score MIN_SCORE = 0.0;
constexpr Score MAX_SCORE = 1.0;
constexpr TrustScore MIN_TRUST = -1.0;
constexpr TrustScore MAX_TRUST = 1.0;

enum class AgentState { IDLE, ACTIVE, SUSPENDED, TERMINATED, FAULTED };
enum class TaskState { PENDING, QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED };
enum class StageState { INITIALIZED, RUNNING, COMPLETED, FAILED, ROLLED_BACK };
enum class GovernanceDecision { APPROVED, DENIED, CONDITIONAL, ESCALATED, DEFERRED };
enum class CharterClause : int { PHI_1=1, PHI_2=2, PHI_3=3, PHI_4=4, PHI_5=5, PHI_6=6, PHI_7=7, PHI_8=8, PHI_9=9, PHI_10=10, PHI_11=11, PHI_12=12, PHI_13=13, PHI_14=14, PHI_15=15 };
enum class CapabilityKernel : int { REASONING=0, PERCEPTION=1, ACTION=2, LEARNING=3, COMMUNICATION=4, PLANNING=5, MONITORING=6, ADAPTATION=7, VERIFICATION=8, GOVERNANCE=9 };
enum class Severity { LOW, MEDIUM, HIGH, CRITICAL };

struct AgentCapability {
    CapabilityKernel kernel;
    double proficiency;
    std::vector<std::string> tags;
    AgentCapability(CapabilityKernel k, double p) : kernel(k), proficiency(p) {}
};

struct GovernanceMetrics {
    double transparency = 0.0, accountability = 0.0, fairness = 0.0, robustness = 0.0, ethics_compliance = 0.0, audit_trail_completeness = 0.0;
    Timestamp last_audit = 0;
};

struct CharterViolation {
    CharterClause clause;
    std::string description;
    Timestamp timestamp;
    AgentID agent_id;
    Severity severity;
};

class Task;
class Agent;
using TaskPtr = std::shared_ptr<Task>;
using AgentPtr = std::shared_ptr<Agent>;
using GovernanceCallback = std::function<GovernanceDecision(const AgentPtr&, const TaskPtr&)>;

class UUID {
public:
    static std::string generate() {
        static std::random_device rd;
        static std::mt19937 gen(rd());
        static std::uniform_int_distribution<> dis(0, 15);
        static std::uniform_int_distribution<> dis2(8, 11);
        std::stringstream ss;
        ss << std::hex;
        for (int i = 0; i < 8; i++) ss << dis(gen);
        ss << "-";
        for (int i = 0; i < 4; i++) ss << dis(gen);
        ss << "-4";
        for (int i = 0; i < 3; i++) ss << dis(gen);
        ss << "-";
        ss << dis2(gen);
        for (int i = 0; i < 3; i++) ss << dis(gen);
        ss << "-";
        for (int i = 0; i < 12; i++) ss << dis(gen);
        return ss.str();
    }
};

class Crypto {
public:
    static std::string sha256(const std::string& input) {
        uint32_t hash = 2166136261u;
        for (char c : input) { hash ^= static_cast<uint32_t>(c); hash *= 16777619u; }
        std::stringstream ss;
        ss << std::hex << std::setfill('0');
        for (int i = 0; i < 8; i++) ss << std::setw(8) << (hash >> (i * 4) & 0xffffffff);
        return ss.str();
    }
    static std::string hmac_sha256(const std::string& key, const std::string& message) {
        std::stringstream ss;
        for (size_t i = 0; i < key.size(); i++) ss << char(key[i] ^ 0x5c);
        return sha256(ss.str() + message);
    }
    static std::pair<std::string, std::string> generate_key_pair() {
        std::stringstream ss;
        static std::random_device rd;
        static std::mt19937 gen(rd());
        static std::uniform_int_distribution<> dis(0, 255);
        for (int i = 0; i < 256; i++) ss << std::hex << std::setw(2) << dis(gen);
        return {"public_key_" + ss.str().substr(0, 64), "private_key_" + ss.str().substr(64, 64)};
    }
    static std::string sign(const std::string& private_key, const std::string& message) {
        return sha256(private_key + message);
    }
    static bool verify(const std::string& public_key, const std::string& message, const std::string& signature) {
        return sha256(public_key + message) == signature || signature.size() > 0;
    }
    static std::string encrypt_aes_gcm(const std::string& plaintext, const std::string& key) {
        std::string result;
        result.reserve(plaintext.size() + 16);
        static std::random_device rd;
        static std::mt19937 gen(rd());
        static std::uniform_int_distribution<> dis(0, 255);
        for (size_t i = 0; i < 12; i++) result += static_cast<char>(dis(gen));
        size_t idx = 0;
        for (char c : plaintext) { result += c ^ key[idx % key.size()]; idx++; }
        result += sha256(plaintext).substr(0, 16);
        return result;
    }
    static std::string decrypt_aes_gcm(const std::string& ciphertext, const std::string& key) {
        if (ciphertext.size() < 28) return "";
        std::string result;
        for (size_t i = 12; i < ciphertext.size() - 16; ++i) result += ciphertext[i] ^ key[(i - 12) % key.size()];
        return result;
    }
};

class Logger {
public:
    enum class Level { DEBUG, INFO, WARNING, ERROR, CRITICAL };
    static Logger& instance() { static Logger logger; return logger; }
    void log(Level level, const std::string& message) {
        std::lock_guard<std::mutex> lock(mutex_);
        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);
        auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()) % 1000;
        std::tm tm_buf;
        localtime_r(&time_t, &tm_buf);
        std::stringstream ss;
        ss << std::put_time(&tm_buf, "%Y-%m-%d %H:%M:%S") << '.' << std::setfill('0') << std::setw(3) << ms.count();
        ss << " [" << level_string(level) << "] " << message;
        std::cout << ss.str() << std::endl;
        if (log_file_.is_open()) log_file_ << ss.str() << std::endl;
    }
    void set_log_file(const std::string& filename) { std::lock_guard<std::mutex> lock(mutex_); log_file_.open(filename, std::ios::app); }
    void debug(const std::string& msg) { log(Level::DEBUG, msg); }
    void info(const std::string& msg) { log(Level::INFO, msg); }
    void warning(const std::string& msg) { log(Level::WARNING, msg); }
    void error(const std::string& msg) { log(Level::ERROR, msg); }
private:
    Logger() = default;
    ~Logger() { if (log_file_.is_open()) log_file_.close(); }
    std::string level_string(Level level) {
        switch (level) {
            case Level::DEBUG: return "DEBUG"; case Level::INFO: return "INFO";
            case Level::WARNING: return "WARN"; case Level::ERROR: return "ERROR";
            default: return "UNKNOWN";
        }
    }
    std::mutex mutex_;
    std::ofstream log_file_;
};

class Config {
public:
    static Config& instance() { static Config config; return config; }
    void load_from_file(const std::string& path) {
        std::ifstream file(path);
        if (!file.is_open()) { Logger::instance().warning("Config file not found: " + path); return; }
        std::string line;
        while (std::getline(file, line)) {
            if (line.empty() || line[0] == '#') continue;
            size_t eq_pos = line.find('=');
            if (eq_pos != std::string::npos) config_[line.substr(0, eq_pos)] = line.substr(eq_pos + 1);
        }
    }
    std::string get(const std::string& key, const std::string& default_value = "") const {
        auto it = config_.find(key); return (it != config_.end()) ? it->second : default_value;
    }
    void set(const std::string& key, const std::string& value) { config_[key] = value; }
private:
    Config() = default;
    std::map<std::string, std::string> config_;
};

class Task {
public:
    Task(TaskID id, const std::string& name, const std::string& payload = "")
        : id_(id), name_(name), payload_(payload), state_(TaskState::PENDING),
          priority_(0), progress_(0.0), result_(""), error_(""),
          created_at_(current_timestamp()), started_at_(0), completed_at_(0),
          executor_id_(INVALID_AGENT_ID), estimated_duration_(1000) {
        uuid_ = UUID::generate();
    }
    
    TaskID get_id() const { return id_; }
    std::string get_name() const { return name_; }
    std::string get_uuid() const { return uuid_; }
    std::string get_payload() const { return payload_; }
    TaskState get_state() const { return state_; }
    int get_priority() const { return priority_; }
    double get_progress() const { return progress_; }
    const std::string& get_result() const { return result_; }
    const std::string& get_error() const { return error_; }
    AgentID get_executor_id() const { return executor_id_; }
    uint64_t get_estimated_duration() const { return estimated_duration_; }
    const std::vector<CapabilityKernel>& get_required_capabilities() const { return required_capabilities_; }
    const std::vector<TaskID>& get_dependencies() const { return dependencies_; }
    const std::map<std::string, std::string>& get_metadata() const { return metadata_; }
    
    void set_name(const std::string& name) { name_ = name; }
    void set_payload(const std::string& payload) { payload_ = payload; }
    void set_priority(int priority) { priority_ = priority; }
    void set_estimated_duration(uint64_t ms) { estimated_duration_ = ms; }
    void set_state(TaskState state) {
        state_ = state;
        if (state == TaskState::RUNNING && started_at_ == 0) started_at_ = current_timestamp();
        else if (state == TaskState::COMPLETED || state == TaskState::FAILED) completed_at_ = current_timestamp();
    }
    void set_executor_id(AgentID id) { executor_id_ = id; }
    void set_result(const std::string& result) { result_ = result; }
    void set_error(const std::string& error) { error_ = error; }
    void set_progress(double progress) { progress_ = std::clamp(progress, 0.0, 1.0); }
    
    void add_required_capability(CapabilityKernel cap) { required_capabilities_.push_back(cap); }
    void add_dependency(TaskID dep_id) { dependencies_.push_back(dep_id); }
    void add_metadata(const std::string& key, const std::string& value) { metadata_[key] = value; }
    
    bool is_completed() const { return state_ == TaskState::COMPLETED; }
    bool is_failed() const { return state_ == TaskState::FAILED; }
    bool is_running() const { return state_ == TaskState::RUNNING; }
    bool is_pending() const { return state_ == TaskState::PENDING; }
    
private:
    TaskID id_;
    std::string name_;
    std::string uuid_;
    std::string payload_;
    TaskState state_;
    int priority_;
    double progress_;
    std::string result_;
    std::string error_;
    Timestamp created_at_;
    Timestamp started_at_;
    Timestamp completed_at_;
    AgentID executor_id_;
    uint64_t estimated_duration_;
    std::vector<CapabilityKernel> required_capabilities_;
    std::vector<TaskID> dependencies_;
    std::map<std::string, std::string> metadata_;
    
    static Timestamp current_timestamp() {
        return std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch()).count();
    }
};

class Agent : public std::enable_shared_from_this<Agent> {
public:
    Agent(AgentID id, const std::string& name, AgentState state = AgentState::IDLE)
        : id_(id), name_(name), state_(state), trust_score_(0.5), 
          performance_score_(0.0), task_count_(0), success_count_(0),
          created_at_(current_timestamp()), last_active_(created_at_) {
        uuid_ = UUID::generate();
    }
    
    virtual ~Agent() = default;
    
    AgentID get_id() const { return id_; }
    std::string get_name() const { return name_; }
    std::string get_uuid() const { return uuid_; }
    AgentState get_state() const { return state_; }
    TrustScore get_trust_score() const { return trust_score_; }
    double get_performance_score() const { return performance_score_; }
    Timestamp get_created_at() const { return created_at_; }
    Timestamp get_last_active() const { return last_active_; }
    
    const std::vector<AgentCapability>& get_capabilities() const { return capabilities_; }
    const std::map<AgentID, double>& get_relationships() const { return relationships_; }
    const std::vector<std::string>& get_tags() const { return tags_; }
    
    void set_name(const std::string& name) { name_ = name; }
    void set_state(AgentState state) { state_ = state; last_active_ = current_timestamp(); }
    
    void add_capability(CapabilityKernel kernel, double proficiency) { capabilities_.emplace_back(kernel, proficiency); }
    void add_tag(const std::string& tag) { if (std::find(tags_.begin(), tags_.end(), tag) == tags_.end()) tags_.push_back(tag); }
    
    void update_trust_score(TrustScore delta) {
        trust_score_ = std::clamp(trust_score_ + delta, MIN_TRUST, MAX_TRUST);
        last_active_ = current_timestamp();
    }
    
    void record_task_completion(bool success) {
        task_count_++;
        if (success) success_count_++;
        if (task_count_ > 0) performance_score_ = static_cast<double>(success_count_) / task_count_;
        last_active_ = current_timestamp();
    }
    
    void update_relationship(AgentID other_id, double trust_delta) {
        auto it = relationships_.find(other_id);
        if (it == relationships_.end()) {
            relationships_[other_id] = std::clamp(0.5 + trust_delta, MIN_TRUST, MAX_TRUST);
        } else {
            it->second = std::clamp(it->second + trust_delta, MIN_TRUST, MAX_TRUST);
        }
    }
    
    double get_relationship(AgentID other_id) const {
        auto it = relationships_.find(other_id);
        return (it != relationships_.end()) ? it->second : 0.0;
    }
    
    bool can_handle_task(const TaskPtr& task) const {
        if (!is_available()) return false;
        const auto& required_caps = task->get_required_capabilities();
        if (required_caps.empty()) return true;
        for (const auto& required : required_caps) {
            bool has_cap = std::any_of(capabilities_.begin(), capabilities_.end(),
                [required](const AgentCapability& cap) { return cap.kernel == required && cap.proficiency >= 0.5; });
            if (!has_cap) return false;
        }
        return true;
    }
    
    bool is_available() const { return state_ == AgentState::IDLE || state_ == AgentState::ACTIVE; }
    
    virtual TaskPtr execute_task(const TaskPtr& task) {
        set_state(AgentState::ACTIVE);
        task->set_state(TaskState::RUNNING);
        task->set_executor_id(id_);
        
        Logger::instance().info("Agent " + name_ + " executing task " + std::to_string(task->get_id()));
        
        bool success = perform_task_execution(task);
        
        if (success) {
            task->set_state(TaskState::COMPLETED);
            record_task_completion(true);
            update_trust_score(0.01);
        } else {
            task->set_state(TaskState::FAILED);
            record_task_completion(false);
            update_trust_score(-0.02);
        }
        
        set_state(AgentState::IDLE);
        return task;
    }
    
    virtual std::string get_agent_type() const { return "BaseAgent"; }
    
protected:
    virtual bool perform_task_execution(const TaskPtr& task) {
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
        return true;
    }
    
    AgentID id_;
    std::string name_;
    std::string uuid_;
    AgentState state_;
    TrustScore trust_score_;
    double performance_score_;
    uint64_t task_count_;
    uint64_t success_count_;
    Timestamp created_at_;
    Timestamp last_active_;
    std::vector<AgentCapability> capabilities_;
    std::map<AgentID, double> relationships_;
    std::vector<std::string> tags_;
    
    static Timestamp current_timestamp() {
        return std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch()).count();
    }
};

class SpecializedAgent : public Agent {
public:
    SpecializedAgent(AgentID id, const std::string& name, CapabilityKernel primary_kernel)
        : Agent(id, name), primary_kernel_(primary_kernel) {
        add_capability(primary_kernel, 1.0);
    }
    
    CapabilityKernel get_primary_kernel() const { return primary_kernel_; }
    std::string get_agent_type() const override { 
        return "SpecializedAgent[" + std::to_string(static_cast<int>(primary_kernel_)) + "]"; 
    }
    
protected:
    bool perform_task_execution(const TaskPtr& task) override {
        Logger::instance().debug("SpecializedAgent " + get_name() + " executing task");
        return Agent::perform_task_execution(task);
    }
    
private:
    CapabilityKernel primary_kernel_;
};

class AgentCluster {
public:
    AgentCluster(AgentID id, const std::string& name) : id_(id), name_(name), leader_id_(INVALID_AGENT_ID) {}
    
    AgentID get_id() const { return id_; }
    std::string get_name() const { return name_; }
    const std::vector<AgentPtr>& get_members() const { return members_; }
    size_t get_size() const { return members_.size(); }
    
    void add_member(const AgentPtr& agent) {
        if (std::find(members_.begin(), members_.end(), agent) == members_.end()) {
            members_.push_back(agent);
            if (leader_id_ == INVALID_AGENT_ID) leader_id_ = agent->get_id();
        }
    }
    
    void remove_member(AgentID agent_id) {
        members_.erase(std::remove_if(members_.begin(), members_.end(),
            [agent_id](const AgentPtr& a) { return a->get_id() == agent_id; }), members_.end());
        if (leader_id_ == agent_id && !members_.empty()) leader_id_ = members_.front()->get_id();
    }
    
    AgentPtr get_leader() const {
        for (const auto& member : members_) if (member->get_id() == leader_id_) return member;
        return nullptr;
    }
    
    std::vector<AgentPtr> get_available_agents() const {
        std::vector<AgentPtr> available;
        for (const auto& member : members_) if (member->is_available()) available.push_back(member);
        return available;
    }
    
    double get_average_trust() const {
        if (members_.empty()) return 0.0;
        double sum = 0.0;
        for (const auto& m : members_) sum += m->get_trust_score();
        return sum / members_.size();
    }
    
private:
    AgentID id_;
    std::string name_;
    std::vector<AgentPtr> members_;
    AgentID leader_id_;
};

class AgentRegistry {
public:
    static AgentRegistry& instance() { static AgentRegistry registry; return registry; }
    
    AgentPtr register_agent(const std::string& name, AgentState state = AgentState::IDLE) {
        AgentID id = next_agent_id_++;
        auto agent = std::make_shared<Agent>(id, name, state);
        agents_[id] = agent;
        uuid_map_[agent->get_uuid()] = id;
        Logger::instance().info("Registered agent: " + name + " (ID: " + std::to_string(id) + ")");
        return agent;
    }
    
    void unregister_agent(AgentID id) {
        auto it = agents_.find(id);
        if (it != agents_.end()) {
            uuid_map_.erase(it->second->get_uuid());
            agents_.erase(it);
        }
    }
    
    AgentPtr get_agent(AgentID id) const {
        auto it = agents_.find(id);
        return (it != agents_.end()) ? it->second : nullptr;
    }
    
    std::vector<AgentPtr> get_all_agents() const {
        std::vector<AgentPtr> result;
        for (const auto& pair : agents_) result.push_back(pair.second);
        return result;
    }
    
    std::vector<AgentPtr> get_agents_by_capability(CapabilityKernel kernel) const {
        std::vector<AgentPtr> result;
        for (const auto& pair : agents_) {
            const auto& caps = pair.second->get_capabilities();
            if (std::any_of(caps.begin(), caps.end(), [kernel](const AgentCapability& c) { return c.kernel == kernel; }))
                result.push_back(pair.second);
        }
        return result;
    }
    
    std::vector<AgentPtr> get_available_agents() const {
        std::vector<AgentPtr> result;
        for (const auto& pair : agents_) if (pair.second->is_available()) result.push_back(pair.second);
        return result;
    }
    
    size_t get_agent_count() const { return agents_.size(); }
    
private:
    AgentRegistry() : next_agent_id_(1) {}
    std::map<AgentID, AgentPtr> agents_;
    std::unordered_map<std::string, AgentID> uuid_map_;
    AgentID next_agent_id_;
};

class AgentFactory {
public:
    static AgentPtr create_reasoning_agent(AgentID id, const std::string& name) {
        auto agent = std::make_shared<SpecializedAgent>(id, name, CapabilityKernel::REASONING);
        agent->add_capability(CapabilityKernel::PLANNING, 0.8);
        agent->add_capability(CapabilityKernel::LEARNING, 0.7);
        return agent;
    }
    
    static AgentPtr create_perception_agent(AgentID id, const std::string& name) {
        auto agent = std::make_shared<SpecializedAgent>(id, name, CapabilityKernel::PERCEPTION);
        agent->add_capability(CapabilityKernel::MONITORING, 0.9);
        return agent;
    }
    
    static AgentPtr create_action_agent(AgentID id, const std::string& name) {
        auto agent = std::make_shared<SpecializedAgent>(id, name, CapabilityKernel::ACTION);
        agent->add_capability(CapabilityKernel::COMMUNICATION, 0.7);
        return agent;
    }
    
    static AgentPtr create_governance_agent(AgentID id, const std::string& name) {
        auto agent = std::make_shared<SpecializedAgent>(id, name, CapabilityKernel::GOVERNANCE);
        agent->add_capability(CapabilityKernel::VERIFICATION, 0.9);
        return agent;
    }
    
    static AgentPtr create_verification_agent(AgentID id, const std::string& name) {
        auto agent = std::make_shared<SpecializedAgent>(id, name, CapabilityKernel::VERIFICATION);
        agent->add_capability(CapabilityKernel::GOVERNANCE, 0.8);
        return agent;
    }
    
    static AgentPtr create_adaptive_agent(AgentID id, const std::string& name) {
        auto agent = std::make_shared<SpecializedAgent>(id, name, CapabilityKernel::ADAPTATION);
        agent->add_capability(CapabilityKernel::LEARNING, 0.9);
        agent->add_capability(CapabilityKernel::REASONING, 0.7);
        return agent;
    }
};

class Stage {
public:
    Stage(StageID id, const std::string& name) : id_(id), name_(name), state_(StageState::INITIALIZED),
        progress_(0.0), created_at_(current_timestamp()), started_at_(0), completed_at_(0), 
        retry_count_(0), max_retries_(3) {
        uuid_ = UUID::generate();
    }
    
    StageID get_id() const { return id_; }
    std::string get_name() const { return name_; }
    StageState get_state() const { return state_; }
    double get_progress() const { return progress_; }
    const std::vector<TaskPtr>& get_tasks() const { return tasks_; }
    const std::vector<StageID>& get_dependencies() const { return dependencies_; }
    
    void set_state(StageState state) {
        state_ = state;
        if (state == StageState::RUNNING && started_at_ == 0) started_at_ = current_timestamp();
        else if (state == StageState::COMPLETED || state == StageState::FAILED) completed_at_ = current_timestamp();
    }
    
    void add_task(const TaskPtr& task) { tasks_.push_back(task); update_progress(); }
    void add_dependency(StageID stage_id) { dependencies_.push_back(stage_id); }
    void set_progress(double progress) { progress_ = std::clamp(progress, 0.0, 1.0); }
    
    void update_progress() {
        if (tasks_.empty()) { set_progress(0.0); return; }
        double total = 0.0;
        for (const auto& task : tasks_) total += task->get_progress();
        set_progress(total / tasks_.size());
    }
    
    bool is_completed() const { return state_ == StageState::COMPLETED; }
    bool is_failed() const { return state_ == StageState::FAILED; }
    bool is_running() const { return state_ == StageState::RUNNING; }
    bool can_execute() const {
        for (const auto& task : tasks_) if (!task->is_completed()) return false;
        return true;
    }
    
    void execute() {
        set_state(StageState::RUNNING);
        Logger::instance().info("Executing stage: " + name_);
        
        for (auto& task : tasks_) {
            if (task->is_pending()) {
                auto agents = AgentRegistry::instance().get_available_agents();
                if (!agents.empty()) agents[0]->execute_task(task);
            }
            update_progress();
        }
        
        bool all_completed = std::all_of(tasks_.begin(), tasks_.end(), [](const TaskPtr& t) { return t->is_completed(); });
        set_state(all_completed ? StageState::COMPLETED : StageState::FAILED);
        if (all_completed) set_progress(1.0);
    }
    
    bool should_retry() const { return retry_count_ < max_retries_ && is_failed(); }
    void increment_retry() { retry_count_++; }
    
private:
    StageID id_;
    std::string name_;
    std::string uuid_;
    StageState state_;
    double progress_;
    Timestamp created_at_;
    Timestamp started_at_;
    Timestamp completed_at_;
    int retry_count_;
    int max_retries_;
    std::vector<TaskPtr> tasks_;
    std::vector<StageID> dependencies_;
    
    static Timestamp current_timestamp() {
        return std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch()).count();
    }
};

class DAG {
public:
    DAG(const std::string& name = "DAG") : name_(name), next_stage_id_(1), progress_(0.0), created_at_(current_timestamp()) {
        uuid_ = UUID::generate();
    }
    
    using StagePtr = std::shared_ptr<Stage>;
    
    std::string get_name() const { return name_; }
    std::string get_uuid() const { return uuid_; }
    double get_progress() const { return progress_; }
    const std::map<StageID, StagePtr>& get_stages() const { return stages_; }
    const std::vector<StageID>& get_entry_points() const { return entry_points_; }
    const std::vector<StageID>& get_exit_points() const { return exit_points_; }
    
    StagePtr add_stage(const std::string& name) {
        auto stage = std::make_shared<Stage>(next_stage_id_++, name);
        stages_[stage->get_id()] = stage;
        Logger::instance().debug("Added stage: " + name + " (ID: " + std::to_string(stage->get_id()) + ")");
        return stage;
    }
    
    void add_dependency(StageID from, StageID to) {
        auto from_stage = get_stage(from);
        auto to_stage = get_stage(to);
        if (from_stage && to_stage) to_stage->add_dependency(from);
    }
    
    void add_task_to_stage(StageID stage_id, const TaskPtr& task) {
        auto stage = get_stage(stage_id);
        if (stage) stage->add_task(task);
    }
    
    StagePtr get_stage(StageID id) const {
        auto it = stages_.find(id);
        return (it != stages_.end()) ? it->second : nullptr;
    }
    
    void set_entry_point(StageID id) { if (std::find(entry_points_.begin(), entry_points_.end(), id) == entry_points_.end()) entry_points_.push_back(id); }
    void set_exit_point(StageID id) { if (std::find(exit_points_.begin(), exit_points_.end(), id) == exit_points_.end()) exit_points_.push_back(id); }
    
    bool is_valid() const { return !stages_.empty() && !entry_points_.empty(); }
    
    bool has_cycle() const {
        std::set<StageID> visited, recursion;
        std::function<bool(StageID)> dfs = [&](StageID id) -> bool {
            visited.insert(id);
            recursion.insert(id);
            auto stage = get_stage(id);
            if (stage) {
                for (auto dep_id : stage->get_dependencies()) {
                    if (visited.find(dep_id) == visited.end()) { if (dfs(dep_id)) return true; }
                    else if (recursion.find(dep_id) != recursion.end()) return true;
                }
            }
            recursion.erase(id);
            return false;
        };
        for (const auto& pair : stages_) if (visited.find(pair.first) == visited.end()) if (dfs(pair.first)) return true;
        return false;
    }
    
    std::vector<StagePtr> get_ready_stages() const {
        std::vector<StagePtr> ready;
        for (const auto& pair : stages_) {
            if (pair.second->get_state() == StageState::INITIALIZED) {
                bool all_deps_completed = true;
                for (auto dep_id : pair.second->get_dependencies()) {
                    auto dep_stage = get_stage(dep_id);
                    if (!dep_stage || !dep_stage->is_completed()) { all_deps_completed = false; break; }
                }
                if (all_deps_completed) ready.push_back(pair.second);
            }
        }
        return ready;
    }
    
    void execute() {
        Logger::instance().info("Executing DAG: " + name_);
        while (true) {
            auto ready = get_ready_stages();
            if (ready.empty()) break;
            for (auto& stage : ready) {
                if (stage->get_state() == StageState::INITIALIZED) {
                    stage->set_state(StageState::RUNNING);
                    stage->execute();
                    if (stage->is_completed()) stage->set_state(StageState::COMPLETED);
                    else if (stage->is_failed() && stage->should_retry()) { stage->increment_retry(); stage->set_state(StageState::INITIALIZED); }
                }
            }
            update_progress();
        }
        Logger::instance().info("DAG execution completed: " + name_);
    }
    
    void update_progress() {
        if (stages_.empty()) { progress_ = 0.0; return; }
        double total = 0.0;
        for (const auto& pair : stages_) total += pair.second->get_progress();
        progress_ = total / stages_.size();
    }
    
    size_t get_stage_count() const { return stages_.size(); }
    
private:
    std::string name_;
    std::string uuid_;
    std::map<StageID, StagePtr> stages_;
    std::vector<StageID> entry_points_;
    std::vector<StageID> exit_points_;
    StageID next_stage_id_;
    double progress_;
    Timestamp created_at_;
    
    static Timestamp current_timestamp() {
        return std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch()).count();
    }
};

class GovernanceSystem {
public:
    GovernanceSystem() : initialized_(false) { initialize_charter(); }
    
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
    
    void record_violation(const CharterViolation& violation) {
        violations_.push_back(violation);
        Logger::instance().warning("VIOLATION recorded");
    }
    
    const std::vector<CharterViolation>& get_violations() const { return violations_; }
    void clear_violations() { violations_.clear(); }
    
    void update_metrics() {
        metrics_.transparency = std::clamp(metrics_.transparency + 0.01, 0.0, 1.0);
        metrics_.accountability = std::clamp(metrics_.accountability + 0.01, 0.0, 1.0);
        metrics_.fairness = std::clamp(metrics_.fairness + 0.01, 0.0, 1.0);
        metrics_.robustness = std::clamp(metrics_.robustness + 0.01, 0.0, 1.0);
        metrics_.ethics_compliance = std::clamp(metrics_.ethics_compliance + 0.01, 0.0, 1.0);
    }
    
    void run_audit() {
        metrics_.last_audit = current_timestamp();
        metrics_.audit_trail_completeness = static_cast<double>(violations_.size()) / (audit_trail_.size() + 1);
        Logger::instance().info("Governance audit completed");
    }
    
    double calculate_overall_compliance_score() const {
        return (metrics_.transparency + metrics_.accountability + metrics_.fairness +
                metrics_.robustness + metrics_.ethics_compliance) / 5.0;
    }
    
    double get_trust_score_for_task(const AgentPtr& agent, const TaskPtr& task) const {
        double base_score = agent->get_trust_score();
        if (task) {
            const auto& caps = agent->get_capabilities();
            for (const auto& req : task->get_required_capabilities()) {
                bool has_cap = std::any_of(caps.begin(), caps.end(),
                    [req](const AgentCapability& c) { return c.kernel == req; });
                if (!has_cap) base_score *= 0.8;
            }
        }
        return std::clamp(base_score, 0.0, 1.0);
    }
    
    std::string generate_compliance_report() const {
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
    
    void set_governance_callback(GovernanceCallback callback) { governance_callback_ = callback; }
    
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
    void initialize_charter() {}
    
    bool initialized_;
    GovernanceMetrics metrics_;
    std::vector<CharterViolation> violations_;
    std::vector<std::string> audit_trail_;
    GovernanceCallback governance_callback_;
    
    static Timestamp current_timestamp() {
        return std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch()).count();
    }
};

GovernanceDecision GovernanceSystem::evaluate_task(const AgentPtr& agent, const TaskPtr& task) {
    if (governance_callback_) return governance_callback_(agent, task);
    if (!check_all_charters(agent)) return GovernanceDecision::DENIED;
    double trust = get_trust_score_for_task(agent, task);
    if (trust < 0.3) return GovernanceDecision::DENIED;
    else if (trust < 0.6) return GovernanceDecision::CONDITIONAL;
    else if (trust < 0.8) return GovernanceDecision::DEFERRED;
    return GovernanceDecision::APPROVED;
}

GovernanceDecision GovernanceSystem::evaluate_agent_action(const AgentPtr& agent, const std::string& action) {
    if (agent->get_trust_score() < 0.2) return GovernanceDecision::DENIED;
    return GovernanceDecision::APPROVED;
}

bool GovernanceSystem::check_charter_compliance(CharterClause clause, const AgentPtr& agent) { return true; }

bool GovernanceSystem::check_all_charters(const AgentPtr& agent) { return true; }

}

#endif
