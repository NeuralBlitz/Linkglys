#ifndef NEURALBLITZ_CORE_H
#define NEURALBLITZ_CORE_H

#include <vector>
#include <string>
#include <cstdint>
#include <memory>
#include <functional>

namespace neuralblitz {

// Forward declarations
template<typename T>
class Tensor;

using FloatTensor = Tensor<float>;
using IntTensor = Tensor<int32_t>;

// Tensor class for multi-dimensional arrays
template<typename T>
class Tensor {
private:
    std::vector<T> data_;
    std::vector<size_t> shape_;
    std::vector<size_t> strides_;

public:
    Tensor() = default;
    
    Tensor(const std::vector<size_t>& shape) 
        : shape_(shape) {
        size_t total = 1;
        for (auto s : shape) total *= s;
        data_.resize(total);
        compute_strides();
    }
    
    Tensor(const std::vector<size_t>& shape, const std::vector<T>& data)
        : shape_(shape), data_(data) {
        compute_strides();
    }
    
    const std::vector<size_t>& shape() const { return shape_; }
    const std::vector<T>& data() const { return data_; }
    std::vector<T>& data() { return data_; }
    
    size_t size() const {
        size_t s = 1;
        for (auto dim : shape_) s *= dim;
        return s;
    }
    
    size_t num_dims() const { return shape_.size(); }
    
    T& at(const std::vector<size_t>& indices) {
        return data_[compute_offset(indices)];
    }
    
    const T& at(const std::vector<size_t>& indices) const {
        return data_[compute_offset(indices)];
    }
    
    void reshape(const std::vector<size_t>& new_shape) {
        size_t total = 1;
        for (auto s : new_shape) total *= s;
        if (total != size()) {
            throw std::runtime_error("Cannot reshape: size mismatch");
        }
        shape_ = new_shape;
        compute_strides();
    }
    
    Tensor<T> slice(size_t dim, size_t index) const {
        if (dim >= shape_.size()) {
            throw std::out_of_range("Dimension out of range");
        }
        
        std::vector<size_t> new_shape = shape_;
        new_shape.erase(new_shape.begin() + dim);
        
        Tensor<T> result(new_shape);
        // Implementation for slicing
        return result;
    }

private:
    size_t compute_offset(const std::vector<size_t>& indices) const {
        if (indices.size() != shape_.size()) {
            throw std::runtime_error("Index dimension mismatch");
        }
        size_t offset = 0;
        for (size_t i = 0; i < indices.size(); ++i) {
            offset += indices[i] * strides_[i];
        }
        return offset;
    }
    
    void compute_strides() {
        strides_.resize(shape_.size());
        if (shape_.empty()) return;
        
        strides_[shape_.size() - 1] = 1;
        for (int i = shape_.size() - 2; i >= 0; --i) {
            strides_[i] = strides_[i + 1] * shape_[i + 1];
        }
    }
};

// Neural network layer base class
class Layer {
public:
    virtual ~Layer() = default;
    
    virtual FloatTensor forward(const FloatTensor& input) = 0;
    virtual std::vector<std::vector<float>> get_parameters() const = 0;
    virtual void set_parameters(const std::vector<std::vector<float>>& params) = 0;
};

// Dense (fully connected) layer
class Dense : public Layer {
private:
    size_t input_size_;
    size_t output_size_;
    std::vector<float> weights_;
    std::vector<float> bias_;
    
public:
    Dense(size_t input_size, size_t output_size);
    
    FloatTensor forward(const FloatTensor& input) override;
    
    std::vector<std::vector<float>> get_parameters() const override {
        return {weights_, bias_};
    }
    
    void set_parameters(const std::vector<std::vector<float>>& params) override {
        if (params.size() >= 2) {
            weights_ = params[0];
            bias_ = params[1];
        }
    }
};

// Activation functions
namespace activation {
    FloatTensor relu(const FloatTensor& input);
    FloatTensor sigmoid(const FloatTensor& input);
    FloatTensor tanh(const FloatTensor& input);
    FloatTensor softmax(FloatTensor& input);
}

// Model class
class Model {
private:
    std::vector<std::unique_ptr<Layer>> layers_;
    
public:
    void add_layer(std::unique_ptr<Layer> layer);
    
    FloatTensor predict(const FloatTensor& input);
    
    void train(
        const std::vector<FloatTensor>& inputs,
        const std::vector<FloatTensor>& targets,
        float learning_rate,
        int epochs
    );
    
    void save(const std::string& path) const;
    void load(const std::string& path);
};

// GoldenDAG for NBHS-512 hashing
class GoldenDAG {
private:
    static constexpr size_t HASH_SIZE = 512 / 8; // 512 bits = 64 bytes
    std::vector<uint8_t> hash_;
    
public:
    GoldenDAG();
    
    static std::vector<uint8_t> generate(
        const std::string& seed = "",
        size_t iterations = 1
    );
    
    std::vector<uint8_t> hash() const { return hash_; }
    
    std::string to_hex() const;
    
    bool verify() const;
};

// Attestation protocol
class Attestation {
public:
    struct AttestationResult {
        bool valid;
        std::string seal;
        float coherence;
        float self_grounding;
        float irreducibility;
    };
    
    static AttestationResult verify(
        const std::vector<uint8_t>& attestation_data,
        const GoldenDAG& goldendag
    );
};

} // namespace neuralblitz

#endif // NEURALBLITZ_CORE_H
