# C++ Parallel Programming

## Threading

```cpp
#include <thread>

void worker(int id) { /* ... */ }

std::thread t1(worker, 1);
std::thread t2(worker, 2);
t1.join();
t2.join();
```

### RAII Thread Guard

```cpp
class ThreadGuard {
    std::thread& t;
public:
    explicit ThreadGuard(std::thread& t_) : t(t_) {}
    ~ThreadGuard() { if (t.joinable()) t.join(); }
};
```

## std::async and Futures

```cpp
#include <future>

auto future = std::async(std::launch::async, computeExpensiveResult);
auto result = future.get();
```

## Parallel Algorithms (C++17)

```cpp
#include <algorithm>
#include <execution>

std::sort(std::execution::par, vec.begin(), vec.end());
auto sum = std::reduce(std::execution::par, vec.begin(), vec.end(), 0);
```

## Atomic Operations

```cpp
#include <atomic>

std::atomic<int> counter{0};
counter.fetch_add(1);
counter.load();
counter.store(newValue);
```

## Mutexes and Locks

```cpp
#include <mutex>

std::mutex mtx;

void safe_increment() {
    std::lock_guard<std::mutex> lock(mtx);
    ++shared_data;
}

// Read-write lock
std::shared_mutex rw_mutex;
int read_val() const { std::shared_lock lock(rw_mutex); return data[i]; }
void write_val(int v) { std::unique_lock lock(rw_mutex); data[i] = v; }
```

## Thread-Safe Queue

```cpp
template<typename T>
class ThreadSafeQueue {
    std::mutex mtx;
    std::queue<T> queue;
    std::condition_variable cv;
public:
    void push(T item) {
        std::lock_guard lock(mtx);
        queue.push(item);
        cv.notify_one();
    }
    T pop() {
        std::unique_lock lock(mtx);
        cv.wait(lock, [this]{ return !queue.empty(); });
        T item = queue.front(); queue.pop();
        return item;
    }
};
```

## Best Practices

- Minimize lock contention (fine-grained locking)
- Use lock-free data structures when possible
- RAII for thread-local resources
- Test with ThreadSanitizer
- Profile before optimizing
