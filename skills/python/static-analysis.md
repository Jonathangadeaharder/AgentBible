# Python Static Analysis

## Tools

- **Ruff** — Linter + formatter (replaces Flake8, Black, isort)
- **Pyright** — Static type checker (fast, strict, VS Code compatible)

## Commands

```bash
# After editing
ruff check $FILE && ruff format --check $FILE && pyright $FILE

# Before committing
ruff check --fix . && ruff format . && pyright .

# First time
uv tool install ruff
uv tool install pyright
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

## pyrightconfig.json

```json
{
  "pythonVersion": "3.9",
  "typeCheckingMode": "strict",
  "reportMissingImports": true,
  "reportMissingTypeStubs": false,
  "exclude": ["**/node_modules", "**/__pycache__", ".venv", "migrations"]
}
```

## Inline Suppression

```python
x = 1  # noqa: E501
result = func()  # type: ignore[no-untyped-call]
```
