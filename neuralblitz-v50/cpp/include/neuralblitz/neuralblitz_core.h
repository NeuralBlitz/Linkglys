#ifndef NEURALBLITZ_CORE_H
#define NEURALBLITZ_CORE_H

#include <vector>
#include <string>
#include <cstdint>
#include <memory>
#include <functional>
#include <optional>
#include <variant>
#include <map>
#include <set>
#include <unordered_map>
#include <algorithm>
#include <cmath>
#include <random>
#include <sstream>
#include <iomanip>
#include <chrono>

namespace neuralblitz {

// ============================================================================
// Tensor Types
// ============================================================================

template<typename T>
class Tensor {
private:
    std::vector<T> data_;
    std::vector<size_t> shape_;
    std::vector<size_t> strides_;

public:
    Tensor() = default;
    
    explicit Tensor(const std::vector<size_t>& shape) 
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
    
    T& flat_at(size_t index) { return data_[index]; }
    const T& flat_at(size_t index) const { return data_[index]; }
    
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
    
    static Tensor<T> zeros(const std::vector<size_t>& shape) {
        Tensor<T> t(shape);
        std::fill(t.data_.begin(), t.data_.end(), T{});
        return t;
    }
    
    static Tensor<T> ones(const std::vector<size_t>& shape) {
        Tensor<T> t(shape);
        std::fill(t.data_.begin(), t.data_.end(), T{1});
        return t;
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

using FloatTensor = Tensor<float>;
using DoubleTensor = Tensor<double>;
using IntTensor = Tensor<int32_t>;
using UInt8Tensor = Tensor<uint8_t>;

// ============================================================================
// Activation Functions
// ============================================================================

namespace activation {
    FloatTensor relu(const FloatTensor& input);
    FloatTensor leaky_relu(const FloatTensor& input, float alpha = 0.01f);
    FloatTensor sigmoid(const FloatTensor& input);
    FloatTensor tanh(const FloatTensor& input);
    FloatTensor softmax(FloatTensor& input);
    FloatTensor elu(const FloatTensor& input, float alpha = 1.0f);
    FloatTensor swish(const FloatTensor& input);
    FloatTensor mish(const FloatTensor& input);
}

// ============================================================================
// Neural Network Layers
// ============================================================================

class Layer {
public:
    virtual ~Layer() = default;
    
    virtual FloatTensor forward(const FloatTensor& input) = 0;
    virtual FloatTensor backward(const FloatTensor& grad_output) = 0;
    virtual std::vector<std::vector<float>> get_parameters() const = 0;
    virtual void set_parameters(const std::vector<std::vector<float>>& params) = 0;
    virtual std::vector<float> get_gradients() const = 0;
    virtual void zero_gradients() = 0;
};

class Dense : public Layer {
private:
    size_t input_size_;
    size_t output_size_;
    std::vector<float> weights_;
    std::vector<float> bias_;
    std::vector<float> grad_weights_;
    std::vector<float> grad_bias_;
    FloatTensor last_input_;
    FloatTensor last_output_;

public:
    Dense(size_t input_size, size_t output_size);
    
    FloatTensor forward(const FloatTensor& input) override;
    FloatTensor backward(const FloatTensor& grad_output) override;
    
    std::vector<std::vector<float>> get_parameters() const override {
        return {weights_, bias_};
    }
    
    void set_parameters(const std::vector<std::vector<float>>& params) override {
        if (params.size() >= 2) {
            weights_ = params[0];
            bias_ = params[1];
        }
    }
    
    std::vector<float> get_gradients() const override { return grad_weights_; }
    void zero_gradients() override;
    
    void set_learning_rate(float lr) { learning_rate_ = lr; }
    void update_weights();
    
private:
    float learning_rate_ = 0.001f;
};

class Conv2D : public Layer {
private:
    size_t in_channels_;
    size_t out_channels_;
    size_t kernel_size_;
    size_t stride_;
    size_t padding_;
    std::vector<float> weights_;
    std::vector<float> bias_;

public:
    Conv2D(size_t in_channels, size_t out_channels, size_t kernel_size, 
           size_t stride = 1, size_t padding = 0);
    
    FloatTensor forward(const FloatTensor& input) override;
    FloatTensor backward(const FloatTensor& grad_output) override;
    
    std::vector<std::vector<float>> get_parameters() const override {
        return {weights_, bias_};
    }
    
    void set_parameters(const std::vector<std::vector<float>>& params) override {
        if (params.size() >= 2) {
            weights_ = params[0];
            bias_ = params[1];
        }
    }
    
    std::vector<float> get_gradients() const override { return {}; }
    void zero_gradients() override {}
};

class BatchNorm : public Layer {
private:
    size_t num_features_;
    float epsilon_;
    float momentum_;
    std::vector<float> gamma_;
    std::vector<float> beta_;
    std::vector<float> running_mean_;
    std::vector<float> running_var_;
    bool training_;

public:
    BatchNorm(size_t num_features, float epsilon = 1e-5, float momentum = 0.1f);
    
    FloatTensor forward(const FloatTensor& input) override;
    FloatTensor backward(const FloatTensor& grad_output) override;
    
    std::vector<std::vector<float>> get_parameters() const override {
        return {gamma_, beta_};
    }
    
    void set_parameters(const std::vector<std::vector<float>>& params) override {
        if (params.size() >= 2) {
            gamma_ = params[0];
            beta_ = params[1];
        }
    }
    
    std::vector<float> get_gradients() const override { return {}; }
    void zero_gradients() override {}
    
    void train() { training_ = true; }
    void eval() { training_ = false; }
};

class Dropout : public Layer {
private:
    float probability_;
    bool training_;

public:
    Dropout(float probability = 0.5f);
    
    FloatTensor forward(const FloatTensor& input) override;
    FloatTensor backward(const FloatTensor& grad_output) override;
    
    std::vector<std::vector<float>> get_parameters() const override { return {}; }
    void set_parameters(const std::vector<std::vector<float>>&) override {}
    std::vector<float> get_gradients() const override { return {}; }
    void zero_gradients() override {}
    
    void train() { training_ = true; }
    void eval() { training_ = false; }
};

// ============================================================================
// Neural Network Model
// ============================================================================

class Model {
private:
    std::vector<std::unique_ptr<Layer>> layers_;
    
public:
    void add_layer(std::unique_ptr<Layer> layer);
    
    FloatTensor predict(const FloatTensor& input);
    
    void train_mode();
    void eval_mode();
    
    void train(
        const std::vector<FloatTensor>& inputs,
        const std::vector<FloatTensor>& targets,
        float learning_rate,
        int epochs,
        const std::string& loss = "mse"
    );
    
    float evaluate(const std::vector<FloatTensor>& inputs, 
                   const std::vector<FloatTensor>& targets);
    
    void save(const std::string& path) const;
    void load(const std::string& path);
    
    size_t num_layers() const { return layers_.size(); }
};

// ============================================================================
// Loss Functions
// ============================================================================

namespace loss {
    float mse(const FloatTensor& pred, const FloatTensor& target);
    float cross_entropy(const FloatTensor& pred, const FloatTensor& target);
    float binary_cross_entropy(const FloatTensor& pred, const FloatTensor& target);
    FloatTensor mse_grad(const FloatTensor& pred, const FloatTensor& target);
    FloatTensor cross_entropy_grad(const FloatTensor& pred, const FloatTensor& target);
}

// ============================================================================
// Optimizers
// ============================================================================

class Optimizer {
public:
    virtual ~Optimizer() = default;
    virtual void step() = 0;
    virtual void zero_grad() = 0;
};

class SGD : public Optimizer {
private:
    std::vector<std::reference_wrapper<Layer>> layers_;
    float learning_rate_;
    float momentum_;
    float weight_decay_;
    std::map<Layer*, std::vector<float>> velocities_;

public:
    SGD(const std::vector<std::reference_wrapper<Layer>>& layers,
        float learning_rate = 0.001f, float momentum = 0.9f);
    
    void step() override;
    void zero_grad() override;
};

class Adam : public Optimizer {
private:
    std::vector<std::reference_wrapper<Layer>> layers_;
    float learning_rate_;
    float beta1_;
    float beta2_;
    float epsilon_;
    int t_;
    std::map<Layer*, std::vector<float>> m_;
    std::map<Layer*, std::vector<float>> v_;

public:
    Adam(const std::vector<std::reference_wrapper<Layer>>& layers,
         float learning_rate = 0.001f);
    
    void step() override;
    void zero_grad() override;
};

// ============================================================================
// Version Info
// ============================================================================

constexpr const char* VERSION = "50.0.0";
constexpr const char* NAME = "NeuralBlitz";

} // namespace neuralblitz

#endif // NEURALBLITZ_CORE_H
