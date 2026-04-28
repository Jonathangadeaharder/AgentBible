# C++ Clean Code

## Naming Conventions

```cpp
class UserManager { };              // classes: PascalCase
void calculateTotalPrice();         // functions: camelCase
const int kMaxBufferSize = 1024;    // constants: kCamelCase
const double PI = 3.14159;          // or UPPER_SNAKE_CASE

class Example {
    int count_;                     // private: trailing_underscore
    std::string name_;
};
```

## RAII — Resource Management

- Never use raw `new`/`delete`
- Use containers and smart pointers
- Exception safety through proper resource management

```cpp
class FileHandler {
    std::ifstream file_;
public:
    explicit FileHandler(const std::string& filename) : file_(filename) {
        if (!file_.is_open()) throw std::runtime_error("Failed to open");
    }
    ~FileHandler() { if (file_.is_open()) file_.close(); }
    FileHandler(const FileHandler&) = delete;
    FileHandler& operator=(const FileHandler&) = delete;
};
```

## Const Correctness

- `const` for parameters, return values, member functions
- `constexpr` for compile-time constants
- `const&` for large parameters

## Smart Pointers

```cpp
auto ptr = std::make_unique<int>(42);       // exclusive ownership
auto shared = std::make_shared<MyClass>();   // shared ownership
```

## Function Design

- Small, focused functions
- Pass large objects by `const&`
- Use `auto` for type deduction

## Anti-Patterns

| Anti-Pattern | Fix |
|--------------|-----|
| Raw `new`/`delete` | Smart pointers |
| `using namespace std;` | Explicit `std::` |
| Complex macros | `inline` functions / templates |
| Unnecessary copies | `const&` parameters |

## Performance

- Return by value (move semantics kick in)
- `reserve()` vectors when size is known
- Use move semantics for ownership transfer

## Error Handling

- Exceptions for error conditions
- RAII for resource cleanup
- `std::optional` for optional values
