# Python Design Patterns

## Strategy Pattern — Switch algorithms at runtime

```python
from abc import ABC, abstractmethod

class PaymentStrategy(ABC):
    @abstractmethod
    def process_payment(self, amount: float) -> bool: ...

class CreditCardPayment(PaymentStrategy):
    def process_payment(self, amount: float) -> bool:
        return True

class PaymentProcessor:
    def __init__(self, strategy: PaymentStrategy):
        self._strategy = strategy
    def execute_payment(self, amount: float) -> bool:
        return self._strategy.process_payment(amount)
```

## Observer Pattern — Notify on state changes

```python
class Subject:
    def __init__(self):
        self._observers: list[Observer] = []
    def attach(self, observer: Observer):
        self._observers.append(observer)
    def notify(self, message: str):
        for obs in self._observers:
            obs.update(message)
```

## Decorator Pattern — Add functionality dynamically

```python
from functools import wraps
import time

def timing(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.time() - start:.4f}s")
        return result
    return wrapper
```

## Context Manager — Resource cleanup

```python
from contextlib import contextmanager

@contextmanager
def managed_resource():
    resource = acquire_resource()
    try:
        yield resource
    finally:
        release_resource(resource)
```

## Quick Reference

| Pattern | Problem | When to Use |
|---------|---------|-------------|
| Strategy | Switch algorithms | Multiple approaches for same task |
| Observer | Notifications | One-to-many dependencies |
| Decorator | Add functionality | Enhance functions/methods |
| Context Manager | Resource cleanup | File/connection handling |
| Factory | Object creation | Complex instantiation logic |
| Adapter | Interface compatibility | Integrate incompatible systems |

## Python-Specific Features

| Feature | Use Case |
|---------|----------|
| `@property` | Computed attributes |
| `@staticmethod` | Utility functions without instance |
| `@classmethod` | Alternative constructors |
| `@dataclass` | Simple data containers |
| `Protocol` | Structural typing (duck typing with hints) |
