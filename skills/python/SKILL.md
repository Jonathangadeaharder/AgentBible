---
name: python
description: Python coding standards, patterns, and best practices. Use when writing, reviewing, or refactoring Python code.
paths:
  - "**/*.py"
  - "**/pyproject.toml"
  - "**/requirements*.txt"
compatibility: "Python 3.9+"
allowed-tools: Bash(python *) Bash(uv *) Bash(uvx ruff *) Bash(uvx pyright *) Bash(uvx pytest *)
---

# Python Skill

Covers Python development standards: clean code, design patterns, testing, static analysis, concurrency, and IPC.

## Topic Files

| File | Contents |
|------|----------|
| `clean-code.md` | PEP 8, naming, type hints, docstrings, anti-patterns |
| `patterns.md` | Strategy, Observer, Decorator, Context Manager, dataclasses |
| `testing.md` | Pytest, fixtures, parametrize, mocking, coverage config |
| `static-analysis.md` | Ruff + MyPy config, pyproject.toml examples |
| `parallel.md` | Threading, multiprocessing, asyncio, race conditions |
| `ipc.md` | HTTP/REST, WebSockets, multiprocessing queues, Redis |

## Quick Reference

| Convention | Rule |
|------------|------|
| Modules/packages | `lowercase_with_underscores` |
| Classes | `PascalCase` |
| Functions/variables | `lowercase_with_underscores` |
| Constants | `UPPER_SNAKE_CASE` |
| Private members | `_leading_underscore` |
| Type hints | Required on all public functions |
| Line length | 88 chars (Ruff default) |

## Key Tools

- **Package manager**: uv (not pip)
- **Linter/formatter**: Ruff
- **Type checker**: MyPy
- **Testing**: pytest + pytest-cov
- **Mutation testing**: mutmut
