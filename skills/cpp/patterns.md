# C++ Design Patterns

## RAII — Automatic Resource Management

```cpp
class FileHandler {
    std::ifstream file;
public:
    FileHandler(const std::string& filename) : file(filename) {
        if (!file.is_open()) throw std::runtime_error("Could not open file");
    }
    ~FileHandler() { if (file.is_open()) file.close(); }
    FileHandler(const FileHandler&) = delete;
    FileHandler& operator=(const FileHandler&) = delete;
};
```

## Smart Pointers

```cpp
std::unique_ptr<MyClass> ptr = std::make_unique<MyClass>();  // exclusive
std::shared_ptr<MyClass> shared = std::make_shared<MyClass>(); // shared
std::weak_ptr<MyClass> weak = shared;                         // non-owning
```

## Strategy Pattern

```cpp
class PaymentStrategy {
public:
    virtual ~PaymentStrategy() = default;
    virtual bool processPayment(double amount) = 0;
};

class CreditCardPayment : public PaymentStrategy {
public:
    bool processPayment(double amount) override { return true; }
};

class PaymentProcessor {
    std::unique_ptr<PaymentStrategy> strategy_;
public:
    explicit PaymentProcessor(std::unique_ptr<PaymentStrategy> s)
        : strategy_(std::move(s)) {}
    bool executePayment(double amount) { return strategy_->processPayment(amount); }
};
```

## Quick Reference

| Pattern | Problem | When to Use |
|---------|---------|-------------|
| RAII | Resource management | All resource handling |
| Smart Pointers | Memory management | Dynamic allocation |
| Strategy | Algorithm switching | Multiple approaches |
| Observer | Event notification | Loose coupling |

## Modern C++ Guidelines

1. Stack allocation over heap
2. Smart pointers over raw pointers
3. Move semantics for performance
4. Const correctness consistently
5. Rule of Five for resource-managing classes
