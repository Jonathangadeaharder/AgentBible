---
name: cpp
description: C++ coding standards, patterns, and best practices. Use when writing, reviewing, or refactoring C++ code.
paths:
  - "**/*.cpp"
  - "**/*.hpp"
  - "**/*.h"
  - "**/*.cc"
  - "**/*.cxx"
  - "**/CMakeLists.txt"
---

# C++ Skill

Covers C++ development standards: clean code, design patterns, testing, static analysis, concurrency, and IPC.

## Topic Files

| File | Contents |
|------|----------|
| `clean-code.md` | RAII, const correctness, smart pointers, naming |
| `patterns.md` | RAII, Smart Pointers, Strategy, Observer |
| `testing.md` | Google Test + Google Mock, CTest timeouts |
| `static-analysis.md` | Cppcheck config and inline suppression |
| `parallel.md` | std::thread, std::async, parallel algorithms, atomics |
| `ipc.md` | TCP sockets, shared memory, message queues |

## Quick Reference

| Convention | Rule |
|------------|------|
| Classes/structs | `PascalCase` |
| Functions/variables | `camelCase` |
| Constants | `kCamelCase` or `UPPER_SNAKE_CASE` |
| Private members | `trailing_underscore_` |
| Header guards | `#pragma once` |

## Key Principles

- **RAII**: All resource management through constructors/destructors
- **Const correctness**: Use `const` liberally
- **Smart pointers**: `unique_ptr` > `shared_ptr` > raw pointer
- **Move semantics**: Use `std::move` for ownership transfer
- **Rule of Five**: destructor, copy/move ctor, copy/move assignment
