# Python Static Analysis

## Tools

- **Ruff** — Linter + formatter (replaces Flake8, Black, isort)
- **MyPy** — Static type checker

## Commands

```bash
# After editing
ruff check $FILE && ruff format --check $FILE && mypy $FILE

# Before committing
ruff check --fix . && ruff format . && mypy .

# First time
pip install ruff mypy
```

## pyproject.toml — Ruff

```toml
[tool.ruff]
line-length = 88
target-version = "py39"
extend-exclude = [".git", "__pycache__", ".venv", "migrations", "build", "dist"]

[tool.ruff.lint]
select = [
    "E", "W", "F", "I", "N", "UP", "B", "C4", "S", "T20",
    "PT", "RET", "SIM", "ARG", "ERA", "PL", "PERF", "RUF",
]
ignore = ["E203", "E501"]
fixable = ["ALL"]
mccabe.max-complexity = 10

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101", "ARG", "PLR2004"]
"__init__.py" = ["F401"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

## pyproject.toml — MyPy

```toml
[tool.mypy]
python_version = "3.9"
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_return_any = true
warn_unreachable = true
strict_equality = true
incremental = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

## Inline Suppression

```python
x = 1  # noqa: E501
result = func()  # type: ignore[no-untyped-call]
```
