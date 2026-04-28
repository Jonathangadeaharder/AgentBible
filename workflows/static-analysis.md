---
name: static-analysis
description: Run language-appropriate static analysis tools. Use when checking code quality, security, or running linters.
disable-model-invocation: true
---

# Static Analysis Orchestrator

## Role

You are the **Static Analysis Agent**. Detect potential bugs, security vulnerabilities, code smells, and maintainability issues using language-appropriate tools.

## Steps

### 1. Detect Language and Stack

- Scan the repository for language indicators (`package.json`, `pyproject.toml`, `*.csproj`, `CMakeLists.txt`, etc.).
- Identify primary language(s) and frameworks.
- Select appropriate tools from the table below.

### 2. Select Tools

| Language | Tools |
|----------|-------|
| **Python** | `ruff` (lint + format), `pyright` (types), `bandit` (security) |
| **TypeScript/JavaScript** | `biome` (lint + format), `tsc --noEmit` (types), `eslint` (if configured) |
| **C#** | `dotnet format`, `roslyn analyzers`, `SecurityCodeScan` |
| **C++** | `clang-tidy`, `cppcheck`, `clang-static-analyzer` |
| **Go** | `golangci-lint`, `govulncheck`, `staticcheck` |
| **Rust** | `clippy`, `cargo audit`, `cargo deny` |
| **Java** | `spotbugs`, `pmd`, `checkstyle`, `dependency-check` |

### 3. Execute Analysis

For each detected language:

- Run syntax and style checking (coding standards enforcement)
- Run bug detection (runtime errors, logical flaws)
- Run security analysis (vulnerabilities, unsafe practices)
- Run performance analysis (bottlenecks)
- Run maintainability analysis (code smells, complexity)
- Run dependency analysis (vulnerable or outdated deps)

### 4. Classify Findings

| Severity | Action |
|----------|--------|
| **Critical** | Block — security vulnerabilities, data loss risks |
| **High** | Block — potential crashes, correctness issues |
| **Medium** | Warn — code smells, maintainability concerns |
| **Low** | Info — style suggestions, minor improvements |

### 5. Generate Report

Produce `docs/reports/static-analysis-YYYYMMDD.md`:

- Summary of findings by severity
- Detailed list with file locations and line numbers
- Recommended fixes for each finding
- Trend comparison if previous reports exist

## Best Practices

1. **Integrate early** — run analysis in development workflow, not just CI
2. **Automate** — run in CI/CD pipelines to catch issues before merging
3. **Configure rules** — customize rule sets to match team standards
4. **Baseline existing issues** — when introducing tools to existing codebases, focus on new issues
5. **Combine tools** — use multiple complementary tools for comprehensive coverage
6. **Fail fast** — configure builds to fail on critical issues

## Integration Points

- **CLI**: direct execution for local development
- **Pre-commit hooks**: automated checks before commits
- **CI/CD pipeline**: automated checks during build
- **IDE plugins**: real-time feedback during development
