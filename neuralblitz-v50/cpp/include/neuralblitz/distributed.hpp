#ifndef NEURALBLITZ_DISTRIBUTED_HPP
#define NEURALBLITZ_DISTRIBUTED_HPP

#include "extended.hpp"

namespace neuralblitz {

// ============== Message Queue ==============

class MessageQueue {
public:
    struct Message {
        std::string id;
        std::string type;
        std::string payload;
        AgentID sender;
        AgentID receiver;
        Timestamp timestamp;
        int priority;
        
        Message(const std::string& t, const std::string& p, AgentID s, AgentID r, int pri = 0)
            : id(UUID::generate()), type(t), payload(p), sender(s), receiver(r),
              timestamp(current_timestamp()), priority(pri) {}
    };
    
    void enqueue(const Message& msg) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (msg.priority > 0) {
            priority_queue_.push(msg);
        } else {
            queue_.push(msg);
        }
        cv_.notify_one();
    }
    
    bool dequeue(Message& msg) {
        std::unique_lock<std::mutex> lock(mutex_);
        cv_.wait_for(lock, std::chrono::milliseconds(100), [this] {
            return !queue_.empty() || !priority_queue_.empty();
        });
        
        if (!priority_queue_.empty()) {
            msg = priority_queue_.top();
            priority_queue_.pop();
            return true;
        }
        
        if (!queue_.empty()) {
            msg = queue_.front();
            queue_.pop();
            return true;
        }
        
        return false;
    }
    
    size_t size() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return queue_.size() + priority_queue_.size();
    }
    
    bool empty() const { return size() == 0; }
    
private:
    struct PriorityComparator {
        bool operator()(const Message& a, const Message& b) const {
            return a.priority < b.priority;
        }
    };
    
    std::queue<Message> queue_;
    std::priority_queue<Message, std::vector<Message>, PriorityComparator> priority_queue_;
    mutable std::mutex mutex_;
    std::condition_variable cv_;
    
    static Timestamp current_timestamp() {
        return std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();
    }
};

// ============== Network Protocol ==============

class NetworkProtocol {
public:
    enum class PacketType {
        HEARTBEAT,
        TASK_REQUEST,
        TASK_RESPONSE,
        AGENT_DISCOVERY,
        STATE_SYNC,
        GOVERNANCE_QUERY,
        CONSENSUS_VOTE
    };
    
    struct Packet {
        PacketType type;
        std::string source_id;
        std::string target_id;
        std::string payload;
        Timestamp timestamp;
        uint32_t sequence_number;
        
        Packet(PacketType t, const std::string& src, const std::string& tgt, const std::string& pay)
            : type(t), source_id(src), target_id(tgt), payload(pay),
              timestamp(current_timestamp()), sequence_number(0) {}
    };
    
    static std::string serialize(const Packet& pkt) {
        std::stringstream ss;
        ss << static_cast<int>(pkt.type) << "|"
           << pkt.source_id << "|"
           << pkt.target_id << "|"
           << pkt.payload << "|"
           << pkt.timestamp << "|"
           << pkt.sequence_number;
        return ss.str();
    }
    
    static Packet deserialize(const std::string& data) {
        std::stringstream ss(data);
        std::string token;
        std::vector<std::string> parts;
        
        while (std::getline(ss, token, '|')) {
            parts.push_back(token);
        }
        
        if (parts.size() >= 6) {
            Packet pkt(static_cast<PacketType>(std::stoi(parts[0])), parts[1], parts[2], parts[3]);
            pkt.timestamp = std::stoull(parts[4]);
            pkt.sequence_number = std::stoul(parts[5]);
            return pkt;
        }
        
        return Packet(PacketType::HEARTBEAT, "", "", "");
    }
    
private:
    static Timestamp current_timestamp() {
        return std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();
    }
};

// ============== Distributed Node ==============

class DistributedNode {
public:
    DistributedNode(AgentID id, const std::string& addr, int port)
        : node_id_(id), address_(addr), port_(port), state_(NodeState::FOLLOWER),
          current_term_(0), last_contact_(current_timestamp()) {}
    
    AgentID get_id() const { return node_id_; }
    std::string get_address() const { return address_; }
    int get_port() const { return port_; }
    NodeState get_state() const { return state_; }
    uint64_t get_current_term() const { return current_term_; }
    
    void set_state(NodeState state) { state_ = state; }
    void set_term(uint64_t term) { current_term_ = term; }
    void update_contact() { last_contact_ = current_timestamp(); }
    
    bool is_alive() const {
        return (current_timestamp() - last_contact_) < 30000; // 30s timeout
    }
    
    bool send_message(const std::string& type, const std::string& payload) {
        Logger::instance().debug("Node " + std::to_string(node_id_) + " sending " + type);
        return true;
    }
    
private:
    AgentID node_id_;
    std::string address_;
    int port_;
    NodeState state_;
    uint64_t current_term_;
    Timestamp last_contact_;
    
    static Timestamp current_timestamp() {
        return std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();
    }
};

// ============== Service Mesh ==============

class ServiceMesh {
public:
    ServiceMesh() : message_id_(0) {}
    
    void register_service(const std::string& name, AgentID agent_id) {
        services_[name] = agent_id;
        Logger::instance().info("Service registered: " + name + " -> Agent " + std::to_string(agent_id));
    }
    
    void unregister_service(const std::string& name) {
        services_.erase(name);
    }
    
    AgentID resolve_service(const std::string& name) {
        auto it = services_.find(name);
        return (it != services_.end()) ? it->second : INVALID_AGENT_ID;
    }
    
    bool call_service(const std::string& service, const std::string& payload, std::string& response) {
        AgentID target = resolve_service(service);
        if (target == INVALID_AGENT_ID) {
            return false;
        }
        
        response = "response_to_" + payload + "_from_" + std::to_string(target);
        return true;
    }
    
    std::vector<std::string> list_services() const {
        std::vector<std::string> result;
        for (const auto& pair : services_) {
            result.push_back(pair.first);
        }
        return result;
    }
    
private:
    std::map<std::string, AgentID> services_;
    std::atomic<uint64_t> message_id_;
};

// ============== API Server ==============

class APIServer {
public:
    struct Request {
        std::string method;
        std::string path;
        std::map<std::string, std::string> headers;
        std::string body;
    };
    
    struct Response {
        int status_code;
        std::string body;
        std::map<std::string, std::string> headers;
        
        Response(int code = 200, const std::string& b = "") : status_code(code), body(b) {}
    };
    
    using RouteHandler = std::function<Response(const Request&)>;
    
    void register_route(const std::string& method, const std::string& path, RouteHandler handler) {
        std::string key = method + ":" + path;
        routes_[key] = handler;
    }
    
    Response handle_request(const Request& req) {
        std::string key = req.method + ":" + req.path;
        
        auto it = routes_.find(key);
        if (it != routes_.end()) {
            return it->second(req);
        }
        
        return Response(404, "Not Found");
    }
    
    void start(int port) {
        running_ = true;
        port_ = port;
        Logger::instance().info("API Server started on port " + std::to_string(port));
    }
    
    void stop() {
        running_ = false;
        Logger::instance().info("API Server stopped");
    }
    
    bool is_running() const { return running_; }
    int get_port() const { return port_; }
    
private:
    std::map<std::string, RouteHandler> routes_;
    bool running_;
    int port_;
};

// ============== Health Check ==============

class HealthCheck {
public:
    struct HealthStatus {
        bool healthy;
        std::string component;
        Timestamp last_check;
        std::string message;
        
        HealthStatus(bool h, const std::string& c, const std::string& m)
            : healthy(h), component(c), last_check(current_timestamp()), message(m) {}
    };
    
    void register_check(const std::string& name, std::function<HealthStatus()> checker) {
        checkers_[name] = checker;
    }
    
    std::vector<HealthStatus> run_all_checks() {
        std::vector<HealthStatus> results;
        
        for (auto& pair : checkers_) {
            try {
                results.push_back(pair.second());
            } catch (const std::exception& e) {
                results.emplace_back(false, pair.first, std::string("Error: ") + e.what());
            }
        }
        
        return results;
    }
    
    bool is_healthy() const {
        for (const auto& pair : checkers_) {
            try {
                auto status = pair.second();
                if (!status.healthy) return false;
            } catch (...) {
                return false;
            }
        }
        return true;
    }
    
private:
    std::map<std::string, std::function<HealthStatus()>> checkers_;
    
    static Timestamp current_timestamp() {
        return std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();
    }
};

// ============== Rate Limiter ==============

class RateLimiter {
public:
    RateLimiter(int max_requests, int window_ms)
        : max_requests_(max_requests), window_ms_(window_ms) {}
    
    bool allow_request(AgentID agent_id) {
        auto now = current_timestamp();
        auto& record = limits_[agent_id];
        
        auto& requests = record.requests;
        
        while (!requests.empty() && (now - requests.front()) > window_ms_) {
            requests.pop();
        }
        
        if (static_cast<int>(requests.size()) < max_requests_) {
            requests.push(now);
            return true;
        }
        
        return false;
    }
    
    void reset(AgentID agent_id) {
        limits_.erase(agent_id);
    }
    
    void set_limits(int max_requests, int window_ms) {
        max_requests_ = max_requests;
        window_ms_ = window_ms;
    }
    
private:
    struct LimitRecord {
        std::queue<Timestamp> requests;
    };
    
    int max_requests_;
    int window_ms_;
    std::map<AgentID, LimitRecord> limits_;
    
    static Timestamp current_timestamp() {
        return std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();
    }
};

// ============== Circuit Breaker ==============

class CircuitBreaker {
public:
    enum class State { CLOSED, OPEN, HALF_OPEN };
    
    CircuitBreaker(int failure_threshold = 5, int timeout_ms = 30000)
        : state_(State::CLOSED), failure_count_(0), success_count_(0),
          failure_threshold_(failure_threshold), timeout_ms_(timeout_ms),
          last_failure_time_(0) {}
    
    bool allow_request() {
        auto now = current_timestamp();
        
        if (state_ == State::OPEN) {
            if ((now - last_failure_time_) > static_cast<uint64_t>(timeout_ms_)) {
                state_ = State::HALF_OPEN;
                success_count_ = 0;
                Logger::instance().info("Circuit breaker moving to HALF_OPEN");
                return true;
            }
            return false;
        }
        
        return true;
    }
    
    void record_success() {
        success_count_++;
        
        if (state_ == State::HALF_OPEN) {
            if (success_count_ >= 2) {
                state_ = State::CLOSED;
                failure_count_ = 0;
                Logger::instance().info("Circuit breaker CLOSED");
            }
        } else {
            failure_count_ = 0;
        }
    }
    
    void record_failure() {
        failure_count_++;
        last_failure_time_ = current_timestamp();
        
        if (failure_count_ >= failure_threshold_) {
            state_ = State::OPEN;
            Logger::instance().warning("Circuit breaker OPENED");
        }
    }
    
    State get_state() const { return state_; }
    
private:
    State state_;
    int failure_count_;
    int success_count_;
    int failure_threshold_;
    int timeout_ms_;
    Timestamp last_failure_time_;
    
    static Timestamp current_timestamp() {
        return std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();
    }
};

// ============== Cache ==============

template<typename K, typename V>
class Cache {
public:
    Cache(size_t max_size = 1000, int ttl_ms = 60000)
        : max_size_(max_size), ttl_ms_(ttl_ms) {}
    
    void put(const K& key, const V& value) {
        auto now = current_timestamp();
        
        if (cache_.size() >= max_size_) {
            evict_oldest();
        }
        
        cache_[key] = {value, now};
    }
    
    bool get(const K& key, V& value) {
        auto it = cache_.find(key);
        
        if (it == cache_.end()) {
            return false;
        }
        
        if ((current_timestamp() - it->second.timestamp) > static_cast<uint64_t>(ttl_ms_)) {
            cache_.erase(it);
            return false;
        }
        
        value = it->second.value;
        return true;
    }
    
    bool contains(const K& key) {
        V temp;
        return get(key, temp);
    }
    
    void clear() { cache_.clear(); }
    
    size_t size() const { return cache_.size(); }
    
private:
    struct CacheEntry {
        V value;
        Timestamp timestamp;
    };
    
    void evict_oldest() {
        Timestamp oldest = UINT64_MAX;
        K oldest_key;
        
        for (const auto& pair : cache_) {
            if (pair.second.timestamp < oldest) {
                oldest = pair.second.timestamp;
                oldest_key = pair.first;
            }
        }
        
        cache_.erase(oldest_key);
    }
    
    size_t max_size_;
    int ttl_ms_;
    std::map<K, CacheEntry> cache_;
    
    static Timestamp current_timestamp() {
        return std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();
    }
};

}

#endif
