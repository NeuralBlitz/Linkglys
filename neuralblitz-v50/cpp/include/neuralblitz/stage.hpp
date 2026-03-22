#ifndef NEURALBLITZ_STAGE_HPP
#define NEURALBLITZ_STAGE_HPP

#include "core.hpp"
#include "task.hpp"

namespace neuralblitz {

class Stage : public std::enable_shared_from_this<Stage> {
public:
    Stage(StageID id, const std::string& name)
        : id_(id), name_(name), state_(StageState::INITIALIZED),
          progress_(0.0), created_at_(current_timestamp()),
          started_at_(0), completed_at_(0), retry_count_(0), max_retries_(3) {
        uuid_ = UUID::generate();
    }
    
    virtual ~Stage() = default;
    
    StageID get_id() const { return id_; }
    std::string get_name() const { return name_; }
    std::string get_uuid() const { return uuid_; }
    StageState get_state() const {
        std::shared_lock<std::shared_mutex> lock(state_mutex_);
        return state_;
    }
    double get_progress() const { return progress_; }
    Timestamp get_created_at() const { return created_at_; }
    Timestamp get_started_at() const { return started_at_; }
    Timestamp get_completed_at() const { return completed_at_; }
    int get_retry_count() const { return retry_count_; }
    int get_max_retries() const { return max_retries_; }
    
    const std::vector<TaskPtr>& get_tasks() const { return tasks_; }
    const std::vector<StageID>& get_dependencies() const { return dependencies_; }
    const std::map<std::string, std::string>& get_metadata() const { return metadata_; }
    
    void set_name(const std::string& name) { name_ = name; }
    void set_max_retries(int max) { max_retries_ = max; }
    void set_state(StageState state) {
        std::lock_guard<std::shared_mutex> lock(state_mutex_);
        state_ = state;
        
        if (state == StageState::RUNNING && started_at_ == 0) {
            started_at_ = current_timestamp();
        } else if (state == StageState::COMPLETED || state == StageState::FAILED) {
            completed_at_ = current_timestamp();
        }
    }
    
    void add_task(const TaskPtr& task) {
        tasks_.push_back(task);
        update_progress();
    }
    
    void add_dependency(StageID stage_id) {
        if (std::find(dependencies_.begin(), dependencies_.end(), stage_id) 
            == dependencies_.end()) {
            dependencies_.push_back(stage_id);
        }
    }
    
    void add_metadata(const std::string& key, const std::string& value) {
        metadata_[key] = value;
    }
    
    void set_progress(double progress) {
        std::lock_guard<std::shared_mutex> lock(state_mutex_);
        progress_ = std::clamp(progress, 0.0, 1.0);
    }
    
    void update_progress() {
        if (tasks_.empty()) {
            set_progress(0.0);
            return;
        }
        
        double total_progress = 0.0;
        for (const auto& task : tasks_) {
            total_progress += task->get_progress();
        }
        
        set_progress(total_progress / tasks_.size());
    }
    
    bool is_completed() const {
        std::shared_lock<std::shared_mutex> lock(state_mutex_);
        return state_ == StageState::COMPLETED;
    }
    
    bool is_failed() const {
        std::shared_lock<std::shared_mutex> lock(state_mutex_);
        return state_ == StageState::FAILED;
    }
    
    bool is_running() const {
        std::shared_lock<std::shared_mutex> lock(state_mutex_);
        return state_ == StageState::RUNNING;
    }
    
    bool can_execute() const {
        for (const auto& task : tasks_) {
            if (!task->is_completed()) {
                return false;
            }
        }
        return true;
    }
    
    virtual void execute();
    virtual bool should_retry() const {
        return retry_count_ < max_retries_ && is_failed();
    }
    
    void increment_retry() { retry_count_++; }
    void reset() {
        retry_count_ = 0;
        set_progress(0.0);
        set_state(StageState::INITIALIZED);
    }
    
    std::string to_json() const;
    
private:
    StageID id_;
    std::string name_;
    std::string uuid_;
    mutable std::shared_mutex state_mutex_;
    StageState state_;
    double progress_;
    Timestamp created_at_;
    Timestamp started_at_;
    Timestamp completed_at_;
    int retry_count_;
    int max_retries_;
    
    std::vector<TaskPtr> tasks_;
    std::vector<StageID> dependencies_;
    std::map<std::string, std::string> metadata_;
    
    static Timestamp current_timestamp() {
        return std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();
    }
};

class ParallelStage : public Stage {
public:
    ParallelStage(StageID id, const std::string& name, size_t parallelism = 4)
        : Stage(id, name), parallelism_(parallelism) {}
    
    size_t get_parallelism() const { return parallelism_; }
    void set_parallelism(size_t p) { parallelism_ = p; }
    
    void execute() override;
    
private:
    size_t parallelism_;
};

class SequentialStage : public Stage {
public:
    SequentialStage(StageID id, const std::string& name)
        : Stage(id, name), current_task_index_(0) {}
    
    size_t get_current_task_index() const { return current_task_index_; }
    void set_current_task_index(size_t idx) { current_task_index_ = idx; }
    
    void execute() override;
    
private:
    size_t current_task_index_;
};

class DAG : public std::enable_shared_from_this<DAG> {
public:
    DAG(const std::string& name = "DAG")
        : name_(name), next_stage_id_(1), progress_(0.0), 
          created_at_(current_timestamp()) {
        uuid_ = UUID::generate();
    }
    
    virtual ~DAG() = default;
    
    std::string get_name() const { return name_; }
    std::string get_uuid() const { return uuid_; }
    double get_progress() const { return progress_; }
    Timestamp get_created_at() const { return created_at_; }
    
    const std::map<StageID, StagePtr>& get_stages() const { return stages_; }
    const std::vector<StageID>& get_entry_points() const { return entry_points_; }
    const std::vector<StageID>& get_exit_points() const { return exit_points_; }
    
    StagePtr add_stage(const std::string& name, StageType type = StageType::SEQUENTIAL) {
        auto stage = std::make_shared<Stage>(next_stage_id_++, name);
        
        if (type == StageType::PARALLEL) {
            stage = std::make_shared<ParallelStage>(stage->get_id(), name);
        } else if (type == StageType::SEQUENTIAL) {
            stage = std::make_shared<SequentialStage>(stage->get_id(), name);
        }
        
        stages_[stage->get_id()] = stage;
        
        Logger::instance().debug("Added stage: " + name + " (ID: " + 
                                 std::to_string(stage->get_id()) + ")");
        return stage;
    }
    
    void add_dependency(StageID from, StageID to) {
        auto from_stage = get_stage(from);
        auto to_stage = get_stage(to);
        
        if (from_stage && to_stage) {
            to_stage->add_dependency(from);
            
            if (std::find(exit_points_.begin(), exit_points_.end(), from) 
                == exit_points_.end()) {
            }
        }
    }
    
    void add_task_to_stage(StageID stage_id, const TaskPtr& task) {
        auto stage = get_stage(stage_id);
        if (stage) {
            stage->add_task(task);
        }
    }
    
    StagePtr get_stage(StageID id) const {
        auto it = stages_.find(id);
        return (it != stages_.end()) ? it->second : nullptr;
    }
    
    void set_entry_point(StageID id) {
        if (std::find(entry_points_.begin(), entry_points_.end(), id) 
            == entry_points_.end()) {
            entry_points_.push_back(id);
        }
    }
    
    void set_exit_point(StageID id) {
        if (std::find(exit_points_.begin(), exit_points_.end(), id) 
            == exit_points_.end()) {
            exit_points_.push_back(id);
        }
    }
    
    bool is_valid() const;
    bool has_cycle() const;
    std::vector<StageID> get_execution_order() const;
    
    void execute();
    void update_progress();
    
    std::vector<StagePtr> get_ready_stages() const {
        std::vector<StagePtr> ready;
        
        for (const auto& pair : stages_) {
            if (pair.second->get_state() == StageState::INITIALIZED) {
                bool all_deps_completed = true;
                
                for (auto dep_id : pair.second->get_dependencies()) {
                    auto dep_stage = get_stage(dep_id);
                    if (!dep_stage || !dep_stage->is_completed()) {
                        all_deps_completed = false;
                        break;
                    }
                }
                
                if (all_deps_completed) {
                    ready.push_back(pair.second);
                }
            }
        }
        
        return ready;
    }
    
    size_t get_stage_count() const { return stages_.size(); }
    size_t get_completed_stage_count() const {
        size_t count = 0;
        for (const auto& pair : stages_) {
            if (pair.second->is_completed()) count++;
        }
        return count;
    }
    
private:
    enum class StageType { SEQUENTIAL, PARALLEL };
    
    std::string name_;
    std::string uuid_;
    std::map<StageID, StagePtr> stages_;
    std::vector<StageID> entry_points_;
    std::vector<StageID> exit_points_;
    StageID next_stage_id_;
    double progress_;
    Timestamp created_at_;
    
    static Timestamp current_timestamp() {
        return std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();
    }
};

bool DAG::is_valid() const {
    if (stages_.empty()) return false;
    if (entry_points_.empty()) return false;
    
    for (const auto& pair : stages_) {
        for (auto dep_id : pair.second->get_dependencies()) {
            if (stages_.find(dep_id) == stages_.end()) {
                return false;
            }
        }
    }
    
    return !has_cycle();
}

bool DAG::has_cycle() const {
    std::set<StageID> visited;
    std::set<StageID> recursion_stack;
    
    std::function<bool(StageID)> dfs = [&](StageID id) -> bool {
        visited.insert(id);
        recursion_stack.insert(id);
        
        auto stage = get_stage(id);
        if (stage) {
            for (auto dep_id : stage->get_dependencies()) {
                if (visited.find(dep_id) == visited.end()) {
                    if (dfs(dep_id)) return true;
                } else if (recursion_stack.find(dep_id) != recursion_stack.end()) {
                    return true;
                }
            }
        }
        
        recursion_stack.erase(id);
        return false;
    };
    
    for (const auto& pair : stages_) {
        if (visited.find(pair.first) == visited.end()) {
            if (dfs(pair.first)) return true;
        }
    }
    
    return false;
}

std::vector<StageID> DAG::get_execution_order() const {
    std::vector<StageID> result;
    std::set<StageID> visited;
    
    std::function<void(StageID)> dfs = [&](StageID id) {
        if (visited.find(id) != visited.end()) return;
        visited.insert(id);
        
        auto stage = get_stage(id);
        if (stage) {
            for (auto dep_id : stage->get_dependencies()) {
                dfs(dep_id);
            }
        }
        
        result.push_back(id);
    };
    
    for (auto entry_id : entry_points_) {
        dfs(entry_id);
    }
    
    return result;
}

void DAG::execute() {
    Logger::instance().info("Executing DAG: " + name_);
    
    while (true) {
        auto ready = get_ready_stages();
        
        if (ready.empty()) {
            break;
        }
        
        for (auto& stage : ready) {
            if (stage->get_state() == StageState::INITIALIZED) {
                stage->set_state(StageState::RUNNING);
                stage->execute();
                
                if (stage->is_completed()) {
                    stage->set_state(StageState::COMPLETED);
                } else if (stage->is_failed()) {
                    if (stage->should_retry()) {
                        stage->increment_retry();
                        stage->set_state(StageState::INITIALIZED);
                    }
                }
            }
        }
        
        update_progress();
    }
    
    Logger::instance().info("DAG execution completed: " + name_);
}

void DAG::update_progress() {
    if (stages_.empty()) {
        progress_ = 0.0;
        return;
    }
    
    double total = 0.0;
    for (const auto& pair : stages_) {
        total += pair.second->get_progress();
    }
    progress_ = total / stages_.size();
}

void Stage::execute() {
    set_state(StageState::RUNNING);
    
    Logger::instance().info("Executing stage: " + name_);
    
    for (auto& task : tasks_) {
        if (task->is_pending()) {
            auto agent = AgentRegistry::instance().get_available_agents().empty() ? 
                nullptr : AgentRegistry::instance().get_available_agents()[0];
            
            if (agent) {
                agent->execute_task(task);
            }
        }
        
        update_progress();
    }
    
    bool all_completed = std::all_of(tasks_.begin(), tasks_.end(),
        [](const TaskPtr& t) { return t->is_completed(); });
    
    if (all_completed) {
        set_state(StageState::COMPLETED);
        set_progress(1.0);
    } else {
        set_state(StageState::FAILED);
    }
    
    Logger::instance().info("Stage " + name_ + " " + 
                            (is_completed() ? "completed" : "failed"));
}

execute() {
   void ParallelStage:: set_state(StageState::RUNNING);
    
    Logger::instance().info("Executing parallel stage: " + get_name() + 
                            " (parallelism: " + std::to_string(parallelism_) + ")");
    
    std::vector<std::future<void>> futures;
    
    for (auto& task : tasks_) {
        if (task->is_pending()) {
            futures.push_back(std::async(std::launch::async, [&]() {
                auto agent = AgentRegistry::instance().get_available_agents().empty() ?
                    nullptr : AgentRegistry::instance().get_available_agents()[0];
                if (agent) {
                    agent->execute_task(task);
                }
            }));
        }
        
        if (futures.size() >= parallelism_) {
            futures[0].get();
            futures.erase(futures.begin());
        }
    }
    
    for (auto& f : futures) {
        f.get();
    }
    
    update_progress();
    
    bool all_completed = std::all_of(tasks_.begin(), tasks_.end(),
        [](const TaskPtr& t) { return t->is_completed(); });
    
    set_state(all_completed ? StageState::COMPLETED : StageState::FAILED);
}

void SequentialStage::execute() {
    set_state(StageState::RUNNING);
    
    Logger::instance().info("Executing sequential stage: " + get_name());
    
    for (size_t i = current_task_index_; i < tasks_.size(); ++i) {
        auto& task = tasks_[i];
        
        if (task->is_pending()) {
            auto agent = AgentRegistry::instance().get_available_agents().empty() ?
                nullptr : AgentRegistry::instance().get_available_agents()[0];
            
            if (agent) {
                agent->execute_task(task);
            }
        }
        
        current_task_index_ = i + 1;
        update_progress();
        
        if (task->is_failed()) {
            set_state(StageState::FAILED);
            return;
        }
    }
    
    set_state(StageState::COMPLETED);
    set_progress(1.0);
}

std::string Stage::to_json() const {
    std::stringstream ss;
    ss << "{";
    ss << "\"id\":" << id_ << ",";
    ss << "\"name\":\"" << name_ << "\",";
    ss << "\"state\":" << static_cast<int>(state_) << ",";
    ss << "\"progress\":" << progress_ << ",";
    ss << "\"task_count\":" << tasks_.size();
    ss << "}";
    return ss.str();
}

class Pipeline {
public:
    Pipeline(const std::string& name) : name_(name), current_stage_index_(0) {
        uuid_ = UUID::generate();
    }
    
    std::string get_name() const { return name_; }
    std::string get_uuid() const { return uuid_; }
    size_t get_stage_count() const { return stages_.size(); }
    
    void add_stage(const StagePtr& stage) {
        stages_.push_back(stage);
    }
    
    void execute() {
        Logger::instance().info("Executing pipeline: " + name_);
        
        for (size_t i = 0; i < stages_.size(); ++i) {
            current_stage_index_ = i;
            
            auto& stage = stages_[i];
            stage->execute();
            
            if (stage->is_failed()) {
                Logger::instance().error("Pipeline failed at stage: " + stage->get_name());
                return;
            }
        }
        
        Logger::instance().info("Pipeline completed: " + name_);
    }
    
    StagePtr get_current_stage() const {
        if (current_stage_index_ < stages_.size()) {
            return stages_[current_stage_index_];
        }
        return nullptr;
    }
    
private:
    std::string name_;
    std::string uuid_;
    std::vector<StagePtr> stages_;
    size_t current_stage_index_;
};

}

#endif
