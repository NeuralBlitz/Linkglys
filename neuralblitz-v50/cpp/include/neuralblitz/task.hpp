#ifndef NEURALBLITZ_TASK_HPP
#define NEURALBLITZ_TASK_HPP

#include "core.hpp"
#include "agent.hpp"

namespace neuralblitz {

class Task : public std::enable_shared_from_this<Task> {
public:
    Task(TaskID id, const std::string& name, const std::string& payload = "")
        : id_(id), name_(name), payload_(payload), state_(TaskState::PENDING),
          priority_(0), progress_(0.0), result_(""), error_(""),
          created_at_(current_timestamp()), started_at_(0), completed_at_(0),
          executor_id_(INVALID_AGENT_ID), estimated_duration_(1000) {
        uuid_ = UUID::generate();
    }
    
    virtual ~Task() = default;
    
    TaskID get_id() const { return id_; }
    std::string get_name() const { return name_; }
    std::string get_uuid() const { return uuid_; }
    std::string get_payload() const { return payload_; }
    TaskState get_state() const {
        std::shared_lock<std::shared_mutex> lock(state_mutex_);
        return state_;
    }
    int get_priority() const { return priority_; }
    double get_progress() const { return progress_; }
    const std::string& get_result() const { return result_; }
    const std::string& get_error() const { return error_; }
    Timestamp get_created_at() const { return created_at_; }
    Timestamp get_started_at() const { return started_at_; }
    Timestamp get_completed_at() const { return completed_at_; }
    AgentID get_executor_id() const { return executor_id_; }
    uint64_t get_estimated_duration() const { return estimated_duration_; }
    
    const std::vector<CapabilityKernel>& get_required_capabilities() const { 
        return required_capabilities_; 
    }
    const std::vector<AgentID>& get_dependencies() const { return dependencies_; }
    const std::map<std::string, std::string>& get_metadata() const { return metadata_; }
    
    void set_name(const std::string& name) { name_ = name; }
    void set_payload(const std::string& payload) { payload_ = payload; }
    void set_priority(int priority) { priority_ = priority; }
    void set_estimated_duration(uint64_t ms) { estimated_duration_ = ms; }
    
    void add_required_capability(CapabilityKernel cap) {
        if (std::find(required_capabilities_.begin(), required_capabilities_.end(), cap) 
            == required_capabilities_.end()) {
            required_capabilities_.push_back(cap);
        }
    }
    
    void add_dependency(TaskID dep_id) {
        if (std::find(dependencies_.begin(), dependencies_.end(), dep_id)
            == dependencies_.end()) {
            dependencies_.push_back(dep_id);
        }
    }
    
    void add_metadata(const std::string& key, const std::string& value) {
        metadata_[key] = value;
    }
    
    void set_state(TaskState state) {
        std::lock_guard<std::shared_mutex> lock(state_mutex_);
        state_ = state;
        
        if (state == TaskState::RUNNING && started_at_ == 0) {
            started_at_ = current_timestamp();
        } else if (state == TaskState::COMPLETED || state == TaskState::FAILED) {
            completed_at_ = current_timestamp();
        }
    }
    
    void set_executor_id(AgentID id) { executor_id_ = id; }
    void set_result(const std::string& result) { result_ = result; }
    void set_error(const std::string& error) { error_ = error; }
    void set_progress(double progress) { 
        std::lock_guard<std::shared_mutex> lock(state_mutex_);
        progress_ = std::clamp(progress, 0.0, 1.0); 
    }
    
    bool is_completed() const {
        std::shared_lock<std::shared_mutex> lock(state_mutex_);
        return state_ == TaskState::COMPLETED;
    }
    
    bool is_failed() const {
        std::shared_lock<std::shared_mutex> lock(state_mutex_);
        return state_ == TaskState::FAILED;
    }
    
    bool is_running() const {
        std::shared_lock<std::shared_mutex> lock(state_mutex_);
        return state_ == TaskState::RUNNING;
    }
    
    bool is_pending() const {
        std::shared_lock<std::shared_mutex> lock(state_mutex_);
        return state_ == TaskState::PENDING;
    }
    
    uint64_t get_actual_duration() const {
        if (started_at_ == 0 || completed_at_ == 0) return 0;
        return completed_at_ - started_at_;
    }
    
    virtual std::string execute() {
        set_state(TaskState::RUNNING);
        
        Logger::instance().debug("Executing task: " + name_);
        
        std::this_thread::sleep_for(std::chrono::milliseconds(estimated_duration_));
        
        set_result("Task completed successfully");
        set_state(TaskState::COMPLETED);
        
        return get_result();
    }
    
    std::string to_json() const;
    
private:
    TaskID id_;
    std::string name_;
    std::string uuid_;
    std::string payload_;
    mutable std::shared_mutex state_mutex_;
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
    std::vector<AgentID> dependencies_;
    std::map<std::string, std::string> metadata_;
    
    static Timestamp current_timestamp() {
        return std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();
    }
};

class TaskWithCheckpoint : public Task {
public:
    TaskWithCheckpoint(TaskID id, const std::string& name, const std::string& payload = "")
        : Task(id, name, payload), checkpoint_interval_(5000), last_checkpoint_(0) {}
    
    void set_checkpoint_interval(uint64_t ms) { checkpoint_interval_ = ms; }
    uint64_t get_checkpoint_interval() const { return checkpoint_interval_; }
    
    void save_checkpoint() {
        last_checkpoint_ = current_timestamp();
        checkpoints_.push_back({
            last_checkpoint_,
            get_progress(),
            get_result()
        });
        Logger::instance().debug("Checkpoint saved for task " + std::to_string(get_id()));
    }
    
    bool should_checkpoint() const {
        return current_timestamp() - last_checkpoint_ >= checkpoint_interval_;
    }
    
    const std::vector<CheckpointData>& get_checkpoints() const { return checkpoints_; }
    
    bool restore_to_checkpoint(size_t index) {
        if (index >= checkpoints_.size()) return false;
        
        const auto& cp = checkpoints_[index];
        set_progress(cp.progress);
        set_result(cp.result);
        Logger::instance().info("Restored task " + std::to_string(get_id()) + 
                                " to checkpoint " + std::to_string(index));
        return true;
    }
    
private:
    struct CheckpointData {
        Timestamp time;
        double progress;
        std::string result;
    };
    
    uint64_t checkpoint_interval_;
    Timestamp last_checkpoint_;
    std::vector<CheckpointData> checkpoints_;
    
    static Timestamp current_timestamp() {
        return std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();
    }
};

class TaskQueue {
public:
    TaskQueue() : next_task_id_(1) {}
    
    TaskPtr enqueue(const std::string& name, const std::string& payload = "", int priority = 0) {
        auto task = std::make_shared<Task>(next_task_id_++, name, payload);
        task->set_priority(priority);
        
        std::lock_guard<std::mutex> lock(mutex_);
        
        if (priority > 0) {
            priority_queue_.push(task);
        } else {
            regular_queue_.push(task);
        }
        
        Logger::instance().debug("Task enqueued: " + name);
        return task;
    }
    
    TaskPtr dequeue() {
        std::lock_guard<std::mutex> lock(mutex_);
        
        if (!priority_queue_.empty()) {
            auto task = priority_queue_.top();
            priority_queue_.pop();
            return task;
        }
        
        if (!regular_queue_.empty()) {
            auto task = regular_queue_.front();
            regular_queue_.pop();
            return task;
        }
        
        return nullptr;
    }
    
    TaskPtr get_task(TaskID id) const {
        std::lock_guard<std::mutex> lock(mutex_);
        
        for (const auto& t : pending_tasks_) {
            if (t->get_id() == id) return t;
        }
        
        return nullptr;
    }
    
    void mark_pending(const TaskPtr& task) {
        std::lock_guard<std::mutex> lock(mutex_);
        pending_tasks_.push_back(task);
    }
    
    void remove_pending(TaskID id) {
        std::lock_guard<std::mutex> lock(mutex_);
        pending_tasks_.erase(
            std::remove_if(pending_tasks_.begin(), pending_tasks_.end(),
                [id](const TaskPtr& t) { return t->get_id() == id; }),
            pending_tasks_.end());
    }
    
    size_t size() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return priority_queue_.size() + regular_queue_.size();
    }
    
    bool empty() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return priority_queue_.empty() && regular_queue_.empty();
    }
    
    size_t get_pending_count() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return pending_tasks_.size();
    }
    
    void clear() {
        std::lock_guard<std::mutex> lock(mutex_);
        while (!priority_queue_.empty()) priority_queue_.pop();
        while (!regular_queue_.empty()) regular_queue_.pop();
        pending_tasks_.clear();
    }
    
private:
    struct TaskComparator {
        bool operator()(const TaskPtr& a, const TaskPtr& b) const {
            return a->get_priority() < b->get_priority();
        }
    };
    
    mutable std::mutex mutex_;
    std::priority_queue<TaskPtr, std::vector<TaskPtr>, TaskComparator> priority_queue_;
    std::queue<TaskPtr> regular_queue_;
    std::vector<TaskPtr> pending_tasks_;
    TaskID next_task_id_;
};

class TaskScheduler {
public:
    TaskScheduler(size_t num_workers = 4) 
        : num_workers_(num_workers), running_(false), tasks_completed_(0),
          tasks_failed_(0) {}
    
    ~TaskScheduler() {
        stop();
    }
    
    void start() {
        if (running_) return;
        running_ = true;
        
        for (size_t i = 0; i < num_workers_; ++i) {
            workers_.emplace_back([this]() { worker_loop(); });
        }
        
        Logger::instance().info("TaskScheduler started with " + std::to_string(num_workers_) + " workers");
    }
    
    void stop() {
        running_ = false;
        
        for (auto& worker : workers_) {
            if (worker.joinable()) {
                worker.join();
            }
        }
        workers_.clear();
        
        Logger::instance().info("TaskScheduler stopped");
    }
    
    TaskPtr submit_task(const std::string& name, const std::string& payload = "",
                        int priority = 0, CapabilityKernel required_cap = CapabilityKernel::REASONING) {
        auto task = queue_.enqueue(name, payload, priority);
        task->add_required_capability(required_cap);
        queue_.mark_pending(task);
        
        {
            std::lock_guard<std::mutex> lock(mutex_);
            pending_tasks_.insert(task->get_id());
        }
        
        cv_.notify_one();
        return task;
    }
    
    TaskPtr submit_task_with_dependencies(
        const std::string& name,
        const std::string& payload,
        const std::vector<TaskID>& dependencies,
        int priority = 0) {
        
        auto task = queue_.enqueue(name, payload, priority);
        for (auto dep_id : dependencies) {
            task->add_dependency(dep_id);
        }
        
        queue_.mark_pending(task);
        
        {
            std::lock_guard<std::mutex> lock(mutex_);
            pending_tasks_.insert(task->get_id());
            task_dependencies_[task->get_id()] = dependencies;
        }
        
        cv_.notify_one();
        return task;
    }
    
    bool cancel_task(TaskID task_id) {
        std::lock_guard<std::mutex> lock(mutex_);
        
        if (running_tasks_.find(task_id) != running_tasks_.end()) {
            return false;
        }
        
        if (pending_tasks_.find(task_id) != pending_tasks_.end()) {
            pending_tasks_.erase(task_id);
            queue_.remove_pending(task_id);
            return true;
        }
        
        return false;
    }
    
    TaskPtr get_task(TaskID id) const {
        return queue_.get_task(id);
    }
    
    std::vector<TaskPtr> get_pending_tasks() const {
        std::vector<TaskPtr> result;
        
        std::lock_guard<std::mutex> lock(mutex_);
        for (auto task_id : pending_tasks_) {
            auto task = queue_.get_task(task_id);
            if (task) result.push_back(task);
        }
        
        return result;
    }
    
    std::vector<TaskPtr> get_running_tasks() const {
        std::lock_guard<std::mutex> lock(mutex_);
        std::vector<TaskPtr> result;
        
        for (auto task_id : running_tasks_) {
            auto task = queue_.get_task(task_id);
            if (task) result.push_back(task);
        }
        
        return result;
    }
    
    size_t get_pending_count() const { return pending_tasks_.size(); }
    size_t get_running_count() const { return running_tasks_.size(); }
    uint64_t get_completed_count() const { return tasks_completed_.load(); }
    uint64_t get_failed_count() const { return tasks_failed_.load(); }
    
    double get_throughput() const {
        auto now = std::chrono::steady_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::seconds>(
            now - start_time_).count();
        if (elapsed == 0) return 0.0;
        return static_cast<double>(tasks_completed_.load()) / elapsed;
    }
    
private:
    void worker_loop() {
        while (running_) {
            TaskPtr task = nullptr;
            
            {
                std::unique_lock<std::mutex> lock(mutex_);
                cv_.wait_for(lock, std::chrono::milliseconds(100),
                    [this] { return !pending_tasks_.empty() || !running_; });
                
                if (!running_) break;
                
                for (auto it = pending_tasks_.begin(); it != pending_tasks_.end(); ++it) {
                    auto t = queue_.get_task(*it);
                    if (t && can_execute(t)) {
                        task = t;
                        pending_tasks_.erase(it);
                        running_tasks_.insert(task->get_id());
                        break;
                    }
                }
            }
            
            if (task) {
                execute_task(task);
            }
        }
    }
    
    bool can_execute(const TaskPtr& task) const {
        const auto& deps = task->get_dependencies();
        
        for (auto dep_id : deps) {
            auto dep_task = queue_.get_task(dep_id);
            if (!dep_task || !dep_task->is_completed()) {
                return false;
            }
        }
        
        return true;
    }
    
    void execute_task(const TaskPtr& task) {
        auto agent = find_available_agent(task);
        
        if (!agent) {
            std::lock_guard<std::mutex> lock(mutex_);
            pending_tasks_.insert(task->get_id());
            running_tasks_.erase(task->get_id());
            return;
        }
        
        try {
            agent->execute_task(task);
            
            std::lock_guard<std::mutex> lock(mutex_);
            running_tasks_.erase(task->get_id());
            queue_.remove_pending(task->get_id());
            
            if (task->is_completed()) {
                tasks_completed_++;
            } else {
                tasks_failed_++;
            }
            
            task_dependencies_.erase(task->get_id());
            
        } catch (const std::exception& e) {
            Logger::instance().error("Task execution failed: " + std::string(e.what()));
            task->set_state(TaskState::FAILED);
            task->set_error(e.what());
            
            std::lock_guard<std::mutex> lock(mutex_);
            running_tasks_.erase(task->get_id());
            tasks_failed_++;
        }
    }
    
    AgentPtr find_available_agent(const TaskPtr& task) {
        auto agents = AgentRegistry::instance().get_available_agents();
        
        for (auto& agent : agents) {
            if (agent->can_handle_task(task)) {
                return agent;
            }
        }
        
        return nullptr;
    }
    
    size_t num_workers_;
    bool running_;
    std::vector<std::thread> workers_;
    std::condition_variable cv_;
    mutable std::mutex mutex_;
    
    TaskQueue queue_;
    std::unordered_set<TaskID> pending_tasks_;
    std::unordered_set<TaskID> running_tasks_;
    std::map<TaskID, std::vector<TaskID>> task_dependencies_;
    
    std::atomic<uint64_t> tasks_completed_;
    std::atomic<uint64_t> tasks_failed_;
    std::chrono::steady_clock::time_point start_time_;
};

std::string Task::to_json() const {
    std::stringstream ss;
    ss << "{";
    ss << "\"id\":" << id_ << ",";
    ss << "\"uuid\":\"" << uuid_ << "\",";
    ss << "\"name\":\"" << name_ << "\",";
    ss << "\"state\":" << static_cast<int>(state_) << ",";
    ss << "\"priority\":" << priority_ << ",";
    ss << "\"progress\":" << progress_ << ",";
    ss << "\"result\":\"" << result_ << "\",";
    ss << "\"error\":\"" << error_ << "\"";
    ss << "}";
    return ss.str();
}

}

#endif
