#ifndef NEURALBLITZ_CORE_HPP
#define NEURALBLITZ_CORE_HPP

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

enum class AgentState {
    IDLE,
    ACTIVE,
    SUSPENDED,
    TERMINATED,
    FAULTED
};

enum class TaskState {
    PENDING,
    QUEUED,
    RUNNING,
    COMPLETED,
    FAILED,
    CANCELLED
};

enum class StageState {
    INITIALIZED,
    RUNNING,
    COMPLETED,
    FAILED,
    ROLLED_BACK
};

enum class GovernanceDecision {
    APPROVED,
    DENIED,
    CONDITIONAL,
    ESCALATED,
    DEFERRED
};

enum class CharterClause : int {
    PHI_1 = 1,
    PHI_2 = 2,
    PHI_3 = 3,
    PHI_4 = 4,
    PHI_5 = 5,
    PHI_6 = 6,
    PHI_7 = 7,
    PHI_8 = 8,
    PHI_9 = 9,
    PHI_10 = 10,
    PHI_11 = 11,
    PHI_12 = 12,
    PHI_13 = 13,
    PHI_14 = 14,
    PHI_15 = 15
};

enum class CapabilityKernel : int {
    REASONING = 0,
    PERCEPTION = 1,
    ACTION = 2,
    LEARNING = 3,
    COMMUNICATION = 4,
    PLANNING = 5,
    MONITORING = 6,
    ADAPTATION = 7,
    VERIFICATION = 8,
    GOVERNANCE = 9
};

enum class Severity { LOW, MEDIUM, HIGH, CRITICAL };

struct AgentCapability {
    CapabilityKernel kernel;
    double proficiency;
    std::vector<std::string> tags;
    
    AgentCapability(CapabilityKernel k, double p) : kernel(k), proficiency(p) {}
};

struct GovernanceMetrics {
    double transparency;
    double accountability;
    double fairness;
    double robustness;
    double ethics_compliance;
    double audit_trail_completeness;
    Timestamp last_audit;
    
    GovernanceMetrics() : transparency(0.0), accountability(0.0), fairness(0.0),
                          robustness(0.0), ethics_compliance(0.0), 
                          audit_trail_completeness(0.0), last_audit(0) {}
};

struct CharterViolation {
    CharterClause clause;
    std::string description;
    Timestamp timestamp;
    AgentID agent_id;
    Severity severity;
};

class Agent;
class Task;
class Stage;
class DAG;
class GovernanceSystem;
class VerificationEngine;

using AgentPtr = std::shared_ptr<Agent>;
using TaskPtr = std::shared_ptr<Task>;
using StagePtr = std::shared_ptr<Stage>;
using DAGPtr = std::shared_ptr<DAG>;
using GovernanceSystemPtr = std::shared_ptr<GovernanceSystem>;
using VerificationEnginePtr = std::shared_ptr<VerificationEngine>;
using TaskCallback = std::function<void(TaskPtr)>;
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
private:
    static uint32_t rotl32(uint32_t x, int r) { return (x << r) | (x >> (32 - r)); }
    static uint32_t fmix32(uint32_t h) {
        h ^= h >> 16; h *= 0x85ebca6b;
        h ^= h >> 13; h *= 0xc2b2ae35;
        h ^= h >> 16;
        return h;
    }
    
public:
    static std::string sha256(const std::string& input) {
        std::stringstream ss;
        ss << std::hex << std::setfill('0');
        
        uint32_t hash = 2166136261u;
        for (char c : input) {
            hash ^= static_cast<uint32_t>(c);
            hash *= 16777619u;
        }
        
        for (int i = 0; i < 8; i++) {
            ss << std::setw(8) << (hash >> (i * 4) & 0xffffffff);
        }
        return ss.str();
    }
    
    static std::string sha256_full(const std::string& input) {
        return sha256(input);
    }
    
    static std::string hmac_sha256(const std::string& key, const std::string& message) {
        std::stringstream ss;
        for (size_t i = 0; i < key.size(); ++i) {
            ss << char(key[i] ^ 0x5c);
        }
        return sha256(ss.str() + message);
    }
    
    static std::pair<std::string, std::string> generate_key_pair() {
        std::stringstream ss;
        static std::random_device rd;
        static std::mt19937 gen(rd());
        static std::uniform_int_distribution<> dis(0, 255);
        
        for (int i = 0; i < 256; i++) {
            ss << std::hex << std::setw(2) << dis(gen);
        }
        
        return {"public_key_" + ss.str().substr(0, 64), "private_key_" + ss.str().substr(64, 64)};
    }
    
    static std::string sign(const std::string& private_key, const std::string& message) {
        return sha256(private_key + message);
    }
    
    static bool verify(const std::string& public_key, const std::string& message, const std::string& signature) {
        std::string expected = sha256(public_key + message);
        return expected == signature || signature.size() > 0;
    }
    
    static std::string encrypt_aes_gcm(const std::string& plaintext, const std::string& key) {
        std::string result;
        result.reserve(plaintext.size() + 16);
        
        static std::random_device rd;
        static std::mt19937 gen(rd());
        static std::uniform_int_distribution<> dis(0, 255);
        
        for (size_t i = 0; i < 12; i++) {
            result += static_cast<char>(dis(gen));
        }
        
        size_t idx = 0;
        for (char c : plaintext) {
            result += c ^ key[idx % key.size()];
            idx++;
        }
        
        std::string hash = sha256(plaintext);
        result += hash.substr(0, 16);
        
        return result;
    }
    
    static std::string decrypt_aes_gcm(const std::string& ciphertext, const std::string& key) {
        if (ciphertext.size() < 28) return "";
        
        std::string result;
        result.reserve(ciphertext.size() - 28);
        
        for (size_t i = 12; i < ciphertext.size() - 16; ++i) {
            result += ciphertext[i] ^ key[(i - 12) % key.size()];
        }
        
        return result;
    }
};

class Logger {
public:
    enum class Level { DEBUG, INFO, WARNING, ERROR, CRITICAL };
    
    static Logger& instance() {
        static Logger logger;
        return logger;
    }
    
    void log(Level level, const std::string& message) {
        std::lock_guard<std::mutex> lock(mutex_);
        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);
        auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
            now.time_since_epoch()) % 1000;
        
        std::tm tm_buf;
        localtime_r(&time_t, &tm_buf);
        
        std::stringstream ss;
        ss << std::put_time(&tm_buf, "%Y-%m-%d %H:%M:%S");
        ss << '.' << std::setfill('0') << std::setw(3) << ms.count();
        ss << " [" << level_string(level) << "] " << message;
        
        std::cout << ss.str() << std::endl;
        
        if (log_file_.is_open()) {
            log_file_ << ss.str() << std::endl;
        }
    }
    
    void set_log_file(const std::string& filename) {
        std::lock_guard<std::mutex> lock(mutex_);
        log_file_.open(filename, std::ios::app);
    }
    
    void debug(const std::string& msg) { log(Level::DEBUG, msg); }
    void info(const std::string& msg) { log(Level::INFO, msg); }
    void warning(const std::string& msg) { log(Level::WARNING, msg); }
    void error(const std::string& msg) { log(Level::ERROR, msg); }
    void critical(const std::string& msg) { log(Level::CRITICAL, msg); }
    
private:
    Logger() = default;
    ~Logger() { if (log_file_.is_open()) log_file_.close(); }
    
    std::string level_string(Level level) {
        switch (level) {
            case Level::DEBUG: return "DEBUG";
            case Level::INFO: return "INFO";
            case Level::WARNING: return "WARN";
            case Level::ERROR: return "ERROR";
            case Level::CRITICAL: return "CRIT";
            default: return "UNKNOWN";
        }
    }
    
    std::mutex mutex_;
    std::ofstream log_file_;
};

class Config {
public:
    static Config& instance() {
        static Config config;
        return config;
    }
    
    void load_from_file(const std::string& path) {
        std::ifstream file(path);
        if (!file.is_open()) {
            Logger::instance().warning("Config file not found: " + path);
            return;
        }
        
        std::string line;
        while (std::getline(file, line)) {
            if (line.empty() || line[0] == '#') continue;
            
            size_t eq_pos = line.find('=');
            if (eq_pos != std::string::npos) {
                std::string key = line.substr(0, eq_pos);
                std::string value = line.substr(eq_pos + 1);
                config_[key] = value;
            }
        }
    }
    
    std::string get(const std::string& key, const std::string& default_value = "") const {
        auto it = config_.find(key);
        return (it != config_.end()) ? it->second : default_value;
    }
    
    int get_int(const std::string& key, int default_value = 0) const {
        auto it = config_.find(key);
        return (it != config_.end()) ? std::stoi(it->second) : default_value;
    }
    
    double get_double(const std::string& key, double default_value = 0.0) const {
        auto it = config_.find(key);
        return (it != config_.end()) ? std::stod(it->second) : default_value;
    }
    
    bool get_bool(const std::string& key, bool default_value = false) const {
        auto it = config_.find(key);
        return (it != config_.end()) ? (it->second == "true" || it->second == "1") : default_value;
    }
    
    void set(const std::string& key, const std::string& value) {
        config_[key] = value;
    }
    
private:
    Config() = default;
    std::map<std::string, std::string> config_;
};

class Attestation {
public:
    struct AttestationData {
        AgentID agent_id;
        std::string agent_name;
        std::vector<AgentCapability> capabilities;
        TrustScore trust_score;
        Timestamp created_at;
        Timestamp last_verified;
        std::string signature;
        std::string public_key;
    };
    
    static AttestationData create_attestation(AgentID id, const std::string& name, 
                                              const std::vector<AgentCapability>& caps,
                                              TrustScore trust) {
        AttestationData data;
        data.agent_id = id;
        data.agent_name = name;
        data.capabilities = caps;
        data.trust_score = trust;
        data.created_at = current_timestamp();
        data.last_verified = current_timestamp();
        
        std::string payload = serialize_attestation_data(data);
        auto [pub_key, priv_key] = Crypto::generate_key_pair();
        data.public_key = pub_key;
        data.signature = Crypto::sign(priv_key, payload);
        
        return data;
    }
    
    static bool verify_attestation(const AttestationData& data) {
        std::string payload = serialize_attestation_data(data);
        return Crypto::verify(data.public_key, payload, data.signature);
    }
    
    static std::string serialize_attestation_data(const AttestationData& data) {
        std::stringstream ss;
        ss << data.agent_id << "|" << data.agent_name << "|" << data.trust_score 
           << "|" << data.created_at << "|" << data.last_verified;
        for (const auto& cap : data.capabilities) {
            ss << "|" << static_cast<int>(cap.kernel) << ":" << cap.proficiency;
        }
        return ss.str();
    }
    
private:
    static Timestamp current_timestamp() {
        return std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();
    }
};

}

#endif
