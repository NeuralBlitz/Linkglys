#ifndef NEURALBLITZ_GOLDEN_DAG_H
#define NEURALBLITZ_GOLDEN_DAG_H

#include <vector>
#include <string>
#include <cstdint>
#include <memory>
#include <map>
#include <set>
#include <optional>
#include <chrono>

namespace neuralblitz {

// ============================================================================
// NBHS-512 Cryptographic Hash
// ============================================================================

class NBHSCryptographicHash {
public:
    static constexpr size_t HASH_SIZE = 64; // 512 bits = 64 bytes
    static constexpr size_t SEED_SIZE = 32;

private:
    std::vector<uint8_t> hash_;
    std::vector<uint8_t> seed_;
    uint64_t iteration_;

public:
    NBHSCryptographicHash();
    
    static std::vector<uint8_t> hash(
        const std::string& data,
        const std::vector<uint8_t>& seed = {},
        uint64_t iteration = 1
    );
    
    static std::string hash_hex(
        const std::string& data,
        const std::vector<uint8_t>& seed = {},
        uint64_t iteration = 1
    );
    
    void compute(
        const std::string& data,
        const std::vector<uint8_t>& seed = {},
        uint64_t iteration = 1
    );
    
    std::vector<uint8_t> get_hash() const { return hash_; }
    std::string to_hex() const;
    std::string to_base64() const;
    
    bool verify(const std::string& data) const;
};

// ============================================================================
// TraceID System
// ============================================================================

class TraceID {
public:
    static constexpr size_t TRACE_ID_SIZE = 16;

private:
    std::string trace_id_;
    std::chrono::system_clock::time_point timestamp_;
    std::string parent_span_id_;
    std::map<std::string, std::string> attributes_;

public:
    TraceID();
    explicit TraceID(const std::string& trace_id);
    
    static TraceID generate(
        const std::string& prefix = "T",
        const std::string& component = "CORE"
    );
    
    std::string to_string() const { return trace_id_; }
    std::string get_timestamp() const;
    
    void set_parent(const TraceID& parent);
    void add_attribute(const std::string& key, const std::string& value);
    std::optional<std::string> get_attribute(const std::string& key) const;
    
    bool is_valid() const;
};

// ============================================================================
// CodexID System
// ============================================================================

class CodexID {
public:
    static constexpr size_t CODEX_ID_SIZE = 24;

private:
    std::string codex_id_;
    std::string version_;
    std::string content_hash_;
    std::chrono::system_clock::time_point created_at_;
    std::map<std::string, std::string> metadata_;

public:
    CodexID();
    explicit CodexID(const std::string& codex_id);
    
    static CodexID generate(
        const std::string& content,
        const std::string& version = "1.0.0"
    );
    
    std::string to_string() const { return codex_id_; }
    std::string get_version() const { return version_; }
    std::string get_content_hash() const { return content_hash_; }
    std::string get_timestamp() const;
    
    void add_metadata(const std::string& key, const std::string& value);
    
    bool is_valid() const;
    bool verify_content(const std::string& content) const;
};

// ============================================================================
// GoldenDAG Core
// ============================================================================

class GoldenDAG {
public:
    static constexpr size_t SIGNATURE_SIZE = 64;
    static constexpr size_t CHAIN_LENGTH = 1024;

private:
    std::vector<uint8_t> current_hash_;
    std::vector<uint8_t> previous_hash_;
    std::vector<uint8_t> seed_;
    uint64_t iteration_;
    uint64_t block_index_;
    std::chrono::system_clock::time_point timestamp_;
    std::vector<std::string> chain_;
    std::map<std::string, std::string> metadata_;

public:
    GoldenDAG();
    GoldenDAG(const std::vector<uint8_t>& seed, uint64_t iteration = 1);
    
    static GoldenDAG create(
        const std::string& seed = "",
        uint64_t iteration = 1
    );
    
    // Core hashing
    std::vector<uint8_t> generate(
        const std::string& data,
        const std::vector<uint8_t>& context = {}
    );
    
    std::vector<uint8_t> generate_with_previous(
        const std::string& data,
        const std::vector<uint8_t>& previous
    );
    
    // Chain operations
    void append_block(const std::string& data);
    bool verify_chain() const;
    bool verify_block(size_t index) const;
    
    // Getters
    std::vector<uint8_t> hash() const { return current_hash_; }
    std::string to_hex() const;
    std::string to_base64() const;
    uint64_t get_block_index() const { return block_index_; }
    std::string get_timestamp() const;
    
    // Metadata
    void add_metadata(const std::string& key, const std::string& value);
    std::optional<std::string> get_metadata(const std::string& key) const;
    
    // Serialization
    std::string serialize() const;
    void deserialize(const std::string& data);
};

// ============================================================================
// Attestation
// ============================================================================

class Attestation {
public:
    struct AttestationResult {
        bool valid;
        std::string seal;
        float coherence;
        float self_grounding;
        float irreducibility;
        std::string timestamp;
        std::map<std::string, std::string> details;
    };
    
    struct AttestationData {
        std::string subject;
        std::string claim;
        std::vector<uint8_t> signature;
        std::chrono::system_clock::time_point issued_at;
        std::chrono::system_clock::time_point expires_at;
        std::map<std::string, std::string> extensions;
    };

private:
    GoldenDAG goldendag_;
    AttestationData data_;

public:
    Attestation();
    Attestation(const GoldenDAG& dag);
    
    AttestationResult attest(
        const std::string& subject,
        const std::string& claim
    );
    
    bool verify(
        const std::vector<uint8_t>& attestation_data,
        const GoldenDAG& goldendag
    );
    
    std::vector<uint8_t> sign(
        const std::string& data,
        const std::vector<uint8_t>& private_key
    );
    
    bool verify_signature(
        const std::vector<uint8_t>& data,
        const std::vector<uint8_t>& signature,
        const std::vector<uint8_t>& public_key
    );
    
    // Factory methods
    static Attestation create_omega_attestation();
    static Attestation create_coherence_attestation(float coherence);
    static Attestation create_irreducibility_attestation();
};

// ============================================================================
// Version
// ============================================================================

constexpr const char* GOLDEN_DAG_VERSION = "50.0.0";

} // namespace neuralblitz

#endif // NEURALBLITZ_GOLDEN_DAG_H
