#ifndef NEURALBLITZ_AGENT_HPP
#define NEURALBLITZ_AGENT_HPP

#include "core.hpp"
#include <optional>
#include <algorithm>

namespace neuralblitz {

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
    AgentState get_state() const { 
        std::shared_lock<std::shared_mutex> lock(state_mutex_);
        return state_; 
    }
    TrustScore get_trust_score() const {
        std::shared_lock<std::shared_mutex> lock(state_mutex_);
        return trust_score_;
    }
    double get_performance_score() const {
        std::shared_lock<std::shared_mutex> lock(state_mutex_);
        return performance_score_;
    }
    Timestamp get_created_at() const { return created_at_; }
    Timestamp get_last_active() const { return last_active_; }
    
    const std::vector<AgentCapability>& get_capabilities() const { return capabilities_; }
    const std::map<AgentID, double>& get_relationships() const { return relationships_; }
    const std::vector<std::string>& get_tags() const { return tags_; }
    
    void set_name(const std::string& name) { name_ = name; }
    void set_state(AgentState state) {
        std::lock_guard<std::shared_mutex> lock(state_mutex_);
        state_ = state;
        last_active_ = current_timestamp();
    }
    
    void add_capability(CapabilityKernel kernel, double proficiency) {
        capabilities_.emplace_back(kernel, proficiency);
    }
    
    void add_capability_tag(CapabilityKernel kernel, const std::string& tag) {
        auto it = std::find_if(capabilities_.begin(), capabilities_.end(),
            [kernel](const AgentCapability& cap) { return cap.kernel == kernel; });
        if (it != capabilities_.end()) {
            it->tags.push_back(tag);
        }
    }
    
    void add_tag(const std::string& tag) {
        if (std::find(tags_.begin(), tags_.end(), tag) == tags_.end()) {
            tags_.push_back(tag);
        }
    }
    
    void update_trust_score(TrustScore delta) {
        std::lock_guard<std::shared_mutex> lock(state_mutex_);
        trust_score_ = std::clamp(trust_score_ + delta, MIN_TRUST, MAX_TRUST);
        last_active_ = current_timestamp();
    }
    
    void record_task_completion(bool success) {
        std::lock_guard<std::shared_mutex> lock(state_mutex_);
        task_count_++;
        if (success) success_count_++;
        
        if (task_count_ > 0) {
            performance_score_ = static_cast<double>(success_count_) / task_count_;
        }
        
        last_active_ = current_timestamp();
    }
    
    void update_relationship(AgentID other_id, double trust_delta) {
        std::lock_guard<std::shared_mutex> lock(state_mutex_);
        auto it = relationships_.find(other_id);
        if (it == relationships_.end()) {
            relationships_[other_id] = std::clamp(0.5 + trust_delta, MIN_TRUST, MAX_TRUST);
        } else {
            it->second = std::clamp(it->second + trust_delta, MIN_TRUST, MAX_TRUST);
        }
    }
    
    double get_relationship(AgentID other_id) const {
        std::shared_lock<std::shared_mutex> lock(state_mutex_);
        auto it = relationships_.find(other_id);
        return (it != relationships_.end()) ? it->second : 0.0;
    }
    
    bool can_handle_task(const TaskPtr& task) const;
    bool is_available() const {
        std::shared_lock<std::shared_mutex> lock(state_mutex_);
        return state_ == AgentState::IDLE || state_ == AgentState::ACTIVE;
    }
    
    virtual TaskPtr execute_task(const TaskPtr& task);
    virtual std::string get_agent_type() const { return "BaseAgent"; }
    
    std::string to_json() const;
    static AgentPtr from_json(const std::string& json);
    
protected:
    AgentID id_;
    std::string name_;
    std::string uuid_;
    mutable std::shared_mutex state_mutex_;
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
        return std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();
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
    
    TaskPtr execute_task(const TaskPtr& task) override;
    
private:
    CapabilityKernel primary_kernel_;
};

class AgentCluster {
public:
    AgentCluster(AgentID id, const std::string& name)
        : id_(id), name_(name), leader_id_(INVALID_AGENT_ID) {}
    
    AgentID get_id() const { return id_; }
    std::string get_name() const { return name_; }
    const std::vector<AgentPtr>& get_members() const { return members_; }
    size_t get_size() const { return members_.size(); }
    
    void add_member(const AgentPtr& agent) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (std::find(members_.begin(), members_.end(), agent) == members_.end()) {
            members_.push_back(agent);
            if (leader_id_ == INVALID_AGENT_ID) {
                leader_id_ = agent->get_id();
            }
        }
    }
    
    void remove_member(AgentID agent_id) {
        std::lock_guard<std::mutex> lock(mutex_);
        members_.erase(
            std::remove_if(members_.begin(), members_.end(),
                [agent_id](const AgentPtr& a) { return a->get_id() == agent_id; }),
            members_.end());
        
        if (leader_id_ == agent_id && !members_.empty()) {
            leader_id_ = members_.front()->get_id();
        }
    }
    
    AgentPtr get_leader() const {
        std::lock_guard<std::mutex> lock(mutex_);
        for (const auto& member : members_) {
            if (member->get_id() == leader_id_) {
                return member;
            }
        }
        return nullptr;
    }
    
    std::vector<AgentPtr> get_available_agents() const {
        std::lock_guard<std::mutex> lock(mutex_);
        std::vector<AgentPtr> available;
        for (const auto& member : members_) {
            if (member->is_available()) {
                available.push_back(member);
            }
        }
        return available;
    }
    
    void set_leader(AgentID agent_id) {
        std::lock_guard<std::mutex> lock(mutex_);
        for (const auto& member : members_) {
            if (member->get_id() == agent_id) {
                leader_id_ = agent_id;
                return;
            }
        }
    }
    
    double get_average_trust() const {
        std::lock_guard<std::mutex> lock(mutex_);
        if (members_.empty()) return 0.0;
        
        double sum = 0.0;
        for (const auto& m : members_) {
            sum += m->get_trust_score();
        }
        return sum / members_.size();
    }
    
private:
    AgentID id_;
    std::string name_;
    mutable std::mutex mutex_;
    std::vector<AgentPtr> members_;
    AgentID leader_id_;
};

class AgentRegistry {
public:
    static AgentRegistry& instance() {
        static AgentRegistry registry;
        return registry;
    }
    
    AgentPtr register_agent(const std::string& name, AgentState state = AgentState::IDLE) {
        AgentID id = next_agent_id_++;
        auto agent = std::make_shared<Agent>(id, name, state);
        
        std::lock_guard<std::mutex> lock(mutex_);
        agents_[id] = agent;
        uuid_map_[agent->get_uuid()] = id;
        
        Logger::instance().info("Registered agent: " + name + " (ID: " + std::to_string(id) + ")");
        return agent;
    }
    
    void unregister_agent(AgentID id) {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = agents_.find(id);
        if (it != agents_.end()) {
            uuid_map_.erase(it->second->get_uuid());
            agents_.erase(it);
            Logger::instance().info("Unregistered agent ID: " + std::to_string(id));
        }
    }
    
    AgentPtr get_agent(AgentID id) const {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = agents_.find(id);
        return (it != agents_.end()) ? it->second : nullptr;
    }
    
    AgentPtr get_agent_by_uuid(const std::string& uuid) const {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = uuid_map_.find(uuid);
        if (it != uuid_map_.end()) {
            return get_agent(it->second);
        }
        return nullptr;
    }
    
    std::vector<AgentPtr> get_all_agents() const {
        std::lock_guard<std::mutex> lock(mutex_);
        std::vector<AgentPtr> result;
        for (const auto& pair : agents_) {
            result.push_back(pair.second);
        }
        return result;
    }
    
    std::vector<AgentPtr> get_agents_by_state(AgentState state) const {
        std::lock_guard<std::mutex> lock(mutex_);
        std::vector<AgentPtr> result;
        for (const auto& pair : agents_) {
            if (pair.second->get_state() == state) {
                result.push_back(pair.second);
            }
        }
        return result;
    }
    
    std::vector<AgentPtr> get_agents_by_capability(CapabilityKernel kernel) const {
        std::lock_guard<std::mutex> lock(mutex_);
        std::vector<AgentPtr> result;
        for (const auto& pair : agents_) {
            const auto& caps = pair.second->get_capabilities();
            if (std::any_of(caps.begin(), caps.end(),
                    [kernel](const AgentCapability& c) { return c.kernel == kernel; })) {
                result.push_back(pair.second);
            }
        }
        return result;
    }
    
    std::vector<AgentPtr> get_available_agents() const {
        std::lock_guard<std::mutex> lock(mutex_);
        std::vector<AgentPtr> result;
        for (const auto& pair : agents_) {
            if (pair.second->is_available()) {
                result.push_back(pair.second);
            }
        }
        return result;
    }
    
    size_t get_agent_count() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return agents_.size();
    }
    
private:
    AgentRegistry() : next_agent_id_(1) {}
    
    mutable std::mutex mutex_;
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

bool Agent::can_handle_task(const TaskPtr& task) const {
    if (!is_available()) return false;
    
    const auto& required_caps = task->get_required_capabilities();
    if (required_caps.empty()) return true;
    
    for (const auto& required : required_caps) {
        bool has_cap = std::any_of(capabilities_.begin(), capabilities_.end(),
            [required](const AgentCapability& cap) {
                return cap.kernel == required && cap.proficiency >= 0.5;
            });
        if (!has_cap) return false;
    }
    
    return true;
}

TaskPtr Agent::execute_task(const TaskPtr& task) {
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

TaskPtr SpecializedAgent::execute_task(const TaskPtr& task) {
    Logger::instance().debug("SpecializedAgent " + get_name() + " executing task with primary kernel " + 
                              std::to_string(static_cast<int>(primary_kernel_)));
    return Agent::execute_task(task);
}

bool Agent::perform_task_execution(const TaskPtr& task) {
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
    return true;
}

std::string Agent::to_json() const {
    std::stringstream ss;
    ss << "{";
    ss << "\"id\":" << id_ << ",";
    ss << "\"uuid\":\"" << uuid_ << "\",";
    ss << "\"name\":\"" << name_ << "\",";
    ss << "\"state\":" << static_cast<int>(state_) << ",";
    ss << "\"trust_score\":" << trust_score_ << ",";
    ss << "\"performance_score\":" << performance_score_ << ",";
    ss << "\"task_count\":" << task_count_ << ",";
    ss << "\"success_count\":" << success_count_;
    ss << "}";
    return ss.str();
}

AgentPtr Agent::from_json(const std::string& json) {
    return nullptr;
}

}

#endif
