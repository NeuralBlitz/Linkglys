#ifndef NEURALBLITZ_COGNITIVE_H
#define NEURALBLITZ_COGNITIVE_H

#include <vector>
#include <string>
#include <cstdint>
#include <memory>
#include <functional>
#include <map>
#include <set>
#include <optional>
#include <variant>
#include <queue>

namespace neuralblitz {
namespace cognitive {

// ============================================================================
// Consciousness Levels
// ============================================================================

enum class ConsciousnessLevel {
    REACTIVE = 0,      // Simple stimulus-response
    ADAPTIVE = 1,     // Learning from experience  
    PREDICTIVE = 2,   // Anticipating future states
    METACOGNITIVE = 3,// Thinking about thinking
    TRANSCENDENT = 4  // Self-aware and beyond
};

std::string consciousness_level_to_string(ConsciousnessLevel level);
ConsciousnessLevel string_to_consciousness_level(const std::string& str);

// ============================================================================
// Intent Vector (7-dimensional)
// ============================================================================

class IntentVector {
public:
    static constexpr size_t DIMENSIONS = 7;

private:
    std::vector<float> phi_values_;
    std::map<std::string, float> custom_dimensions_;
    float coherence_;
    float intensity_;

public:
    IntentVector();
    IntentVector(
        float phi1, float phi2, float phi3, float phi4,
        float phi5, float phi6, float phi7
    );
    
    // Phi dimension getters/setters
    float get_phi1() const { return phi_values_[0]; } // Control/influence
    float get_phi2() const { return phi_values_[1]; } // Balance/integration
    float get_phi3() const { return phi_values_[2]; } // Novelty/innovation
    float get_phi4() const { return phi_values_[3]; } // Stability/security
    float get_phi5() const { return phi_values_[4]; } // Change/evolution
    float get_phi6() const { return phi_values_[5]; } // Understanding/wisdom
    float get_phi7() const { return phi_values_[6]; } // Unity/empathy
    
    void set_phi1(float v) { phi_values_[0] = v; }
    void set_phi2(float v) { phi_values_[1] = v; }
    void set_phi3(float v) { phi_values_[2] = v; }
    void set_phi4(float v) { phi_values_[3] = v; }
    void set_phi5(float v) { phi_values_[4] = v; }
    void set_phi6(float v) { phi_values_[5] = v; }
    void set_phi7(float v) { phi_values_[6] = v; }
    
    // Vector operations
    float dot(const IntentVector& other) const;
    float magnitude() const;
    IntentVector normalize() const;
    IntentVector operator+(const IntentVector& other) const;
    IntentVector operator-(const IntentVector& other) const;
    IntentVector operator*(float scalar) const;
    
    // Coherence
    float get_coherence() const { return coherence_; }
    void set_coherence(float c) { coherence_ = c; }
    float compute_coherence() const;
    
    // Custom dimensions
    void add_dimension(const std::string& name, float value);
    std::optional<float> get_dimension(const std::string& name) const;
    
    std::vector<float> to_vector() const { return phi_values_; }
    std::string to_string() const;
    
    static IntentVector from_map(const std::map<std::string, float>& values);
};

// ============================================================================
// Cognitive State
// ============================================================================

enum class CognitiveState {
    IDLE,
    PERCEIVING,
    ATTENDING,
    LEARNING,
    REASONING,
    DECIDING,
    ACTING,
    REFLECTING,
    DREAMING
};

std::string cognitive_state_to_string(CognitiveState state);

// ============================================================================
// Emotional State
// ============================================================================

class EmotionalState {
public:
    struct Emotion {
        std::string name;
        float intensity;  // 0-1
        float valence;    // -1 (negative) to 1 (positive)
        float arousal;    // 0 (calm) to 1 (excited)
    };

private:
    std::vector<Emotion> emotions_;
    float overall_mood_;
    float stress_level_;
    float engagement_;

public:
    EmotionalState();
    
    void add_emotion(const std::string& name, float intensity);
    void update_emotion(const std::string& name, float intensity);
    std::optional<Emotion> get_emotion(const std::string& name) const;
    
    void set_mood(float mood) { overall_mood_ = mood; }
    float get_mood() const { return overall_mood_; }
    
    void set_stress(float stress) { stress_level_ = stress; }
    float get_stress() const { return stress_level_; }
    
    void set_engagement(float engagement) { engagement_ = engagement; }
    float get_engagement() const { return engagement_; }
    
    std::vector<Emotion> get_emotions() const { return emotions_; }
    std::string to_string() const;
};

// ============================================================================
// Spiking Neural Network
// ============================================================================

class Neuron {
public:
    struct Spike {
        size_t neuron_id;
        float timestamp;
        float amplitude;
    };

private:
    size_t id_;
    float membrane_potential_;
    float threshold_;
    float refractoriness_;
    std::vector<Spike> recent_spikes_;
    
public:
    Neuron(size_t id, float threshold = 1.0f);
    
    void receive_spike(const Spike& spike, float weight);
    bool fire();
    void reset();
    
    size_t get_id() const { return id_; }
    float get_potential() const { return membrane_potential_; }
    std::vector<Spike> get_recent_spikes(size_t n) const;
};

// ============================================================================
// Consciousness Model
// ============================================================================

class ConsciousnessModel {
private:
    ConsciousnessLevel level_;
    float coherence_;
    float complexity_;
    float awareness_;
    float self_reflection_;
    IntentVector current_intent_;
    EmotionalState emotional_state_;
    CognitiveState cognitive_state_;
    std::map<std::string, float> metrics_;

public:
    ConsciousnessModel();
    ConsciousnessModel(
        ConsciousnessLevel level,
        float coherence,
        float complexity
    );
    
    // State management
    void set_level(ConsciousnessLevel level);
    ConsciousnessLevel get_level() const { return level_; }
    
    void update_coherence(float coherence);
    float get_coherence() const { return coherence_; }
    
    void update_complexity(float complexity);
    float get_complexity() const { return complexity_; }
    
    void update_awareness(float awareness);
    float get_awareness() const { return awareness_; }
    
    void set_intent(const IntentVector& intent);
    IntentVector get_intent() const { return current_intent_; }
    
    void set_emotional_state(const EmotionalState& state);
    EmotionalState get_emotional_state() const { return emotional_state_; }
    
    void set_cognitive_state(CognitiveState state);
    CognitiveState get_cognitive_state() const { return cognitive_state_; }
    
    // Metrics
    void set_metric(const std::string& name, float value);
    std::optional<float> get_metric(const std::string& name) const;
    std::map<std::string, float> get_all_metrics() const;
    
    // Consciousness computation
    float compute_consciousness_score() const;
    bool is_self_aware() const;
    
    std::string to_string() const;
};

// ============================================================================
// Working Memory
// ============================================================================

struct WorkingMemoryItem {
    std::string content;
    float salience;
    float recency;
    std::chrono::system_clock::time_point timestamp;
    std::map<std::string, std::string> metadata;
};

class WorkingMemory {
private:
    std::vector<WorkingMemoryItem> items_;
    size_t capacity_;
    float decay_rate_;

public:
    WorkingMemory(size_t capacity = 7);
    
    void add(const WorkingMemoryItem& item);
    void remove(size_t index);
    void clear();
    
    std::vector<WorkingMemoryItem> retrieve_top(size_t n) const;
    std::vector<WorkingMemoryItem> retrieve_by_salience(float threshold) const;
    
    void decay();
    size_t size() const { return items_.size(); }
    size_t capacity() const { return capacity_; }
};

// ============================================================================
// Attention Focus
// ============================================================================

class AttentionFocus {
private:
    std::vector<size_t> focus_indices_;
    float attention_width_;
    float attention_strength_;
    std::map<size_t, float> attention_weights_;

public:
    AttentionFocus(float width = 5.0f, float strength = 1.0f);
    
    void focus_on(const std::vector<size_t>& indices);
    void broaden();
    void narrow();
    
    float get_attention(size_t index) const;
    std::vector<size_t> get_focused_indices() const { return focus_indices_; }
    
    void update_weights(const std::map<size_t, float>& weights);
};

// ============================================================================
// Cognitive Engine
// ============================================================================

class CognitiveEngine {
private:
    std::unique_ptr<ConsciousnessModel> consciousness_;
    std::unique_ptr<WorkingMemory> memory_;
    std::unique_ptr<AttentionFocus> attention_;
    std::vector<std::unique_ptr<Neuron>> network_;
    size_t network_size_;

public:
    CognitiveEngine(size_t network_size = 1000);
    ~CognitiveEngine();
    
    // Processing
    void process_perception(const std::vector<float>& input);
    void process_thought(const IntentVector& intent);
    void make_decision();
    void execute_action();
    
    // State updates
    void update_consciousness(float coherence, float complexity);
    void update_attention(const std::vector<size_t>& focus);
    
    // Getters
    ConsciousnessModel* get_consciousness() const { return consciousness_.get(); }
    WorkingMemory* get_memory() const { return memory_.get(); }
    AttentionFocus* get_attention() const { return attention_.get(); }
    
    // Status
    std::string get_status() const;
    bool is_operational() const;
};

// ============================================================================
// Version
// ============================================================================

constexpr const char* COGNITIVE_VERSION = "50.0.0";

} // namespace cognitive
} // namespace neuralblitz

#endif // NEURALBLITZ_COGNITIVE_H
