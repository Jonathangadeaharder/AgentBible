---
name: csharp
description: C# coding standards, patterns, and best practices. Use when writing, reviewing, or refactoring C# code.
paths:
  - "**/*.cs"
  - "**/*.csproj"
  - "**/*.sln"
compatibility: ".NET 8+"
allowed-tools: Bash(dotnet *)
---

# C# Skill

Covers C# development standards: clean code, design patterns, testing, static analysis, concurrency, and IPC.

## Topic Files

| File | Contents |
|------|----------|
| `clean-code.md` | Naming, null handling, async/await, DI, LINQ, EF Core |
| `patterns.md` | Strategy, Observer, Factory, Singleton |
| `testing.md` | xUnit + Moq, AAA pattern, test timeouts |
| `static-analysis.md` | dotnet format, Roslyn analyzers, .editorconfig |
| `parallel.md` | TPL, async/await, PLINQ, thread safety |
| `ipc.md` | HTTP/REST (ASP.NET), SignalR, Named Pipes |

## Quick Reference

| Convention | Rule |
|------------|------|
| Classes/structs | `PascalCase` |
| Interfaces | `I` prefix + `PascalCase` |
| Methods | `PascalCase` (verb-noun) |
| Private fields | `_camelCase` |
| Constants | `PascalCase` |
| Enums | `PascalCase` names and values |
| Async methods | `Async` suffix |

## Key Tools

- **SDK**: .NET 8+
- **Linter**: dotnet format + Roslyn analyzers
- **Testing**: xUnit + Moq
- **Nullable**: Enabled via `<Nullable>enable</Nullable>`
