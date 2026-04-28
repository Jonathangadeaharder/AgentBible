# Python Clean Code

## Naming Conventions

```python
import data_processor          # modules: lowercase_with_underscores
class UserManager: pass        # classes: PascalCase
def calculate_total(): pass    # functions: lowercase_with_underscores
MAX_BUFFER_SIZE = 1024         # constants: UPPER_SNAKE_CASE
self._internal_count = 0       # private: _leading_underscore
```

## Type Hints

- Always annotate public function parameters and return values
- Use `typing` module for advanced types (`Optional`, `Union`, `TypeVar`)
- Use `dataclass` for simple data containers

```python
@dataclass
class Person:
    name: str
    age: int
    email: str
```

## Docstrings

- Follow PEP 257 for all public modules, functions, classes, methods
- Use imperative mood: "Calculate the area" not "Calculates the area"

## Function Design

- Small, focused functions (under 20 lines)
- Max 5 parameters; use `**kwargs` or dataclasses for more
- Use guard clauses (early returns) to avoid deep nesting

## Error Handling

- Catch specific exceptions, never bare `except:`
- Use context managers (`with`) for resource management
- Log exceptions with context; never silently swallow

```python
try:
    with open(filename) as f:
        return json.load(f)
except FileNotFoundError:
    logger.warning(f"{filename} not found, using defaults")
    return {}
except json.JSONDecodeError as e:
    raise ValueError(f"Invalid JSON: {e}")
```

## Anti-Patterns to Avoid

| Anti-Pattern | Fix |
|--------------|-----|
| Mutable default args (`def f(items=[])`) | Use `None` default |
| Deep nesting (>3 levels) | Guard clauses / early returns |
| Broad `except:` | Catch specific exceptions |
| `result += str(item)` in loops | Use `"".join()` |
| `using namespace std` equivalent | N/A (Python-specific) |

## Performance

- Use `set` for membership testing (O(1))
- Use generators for large datasets
- Use f-strings for formatting
- Prefer `list.sort()` / `sorted()` over manual sorting

## Pythonic Idioms

- List comprehensions over `map`/`filter`
- Unpacking: `a, b = b, a`
- Walrus operator: `if (n := len(data)) > 10:`
- `enumerate()` over manual index tracking
