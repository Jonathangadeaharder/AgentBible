# AGENTS.md — AgentBible

Universal development guidelines for AI coding agents. This file is always loaded.

## Quick Start

1. Read `rules/` for always-on coding standards
2. Language-specific knowledge loads automatically from `skills/` when working with matching files
3. Use `workflows/` for multi-step procedures (invoke manually)

## Build & Test Commands

```bash
# Python
uv sync                          # Install dependencies
uv run pytest                    # Run tests
uvx ruff check --fix . && uvx ruff format .  # Lint + format
uvx pyright                      # Type check

# Node.js / React
pnpm install                     # Install dependencies
pnpm run test                    # Run tests
pnpm dlx @biomejs/biome check   # Lint + format
pnpm exec tsc --noEmit           # Type check

# C#
dotnet build                     # Build
dotnet test                      # Test
dotnet format                    # Format

# C++
cmake -B build && cmake --build build  # Build
cd build && ctest                # Test
clang-format -i src/**/*.cpp     # Format
```

## PR Instructions

- Title format: `<type>(<scope>): <description>`
- Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore
- Run all linters and tests before committing
- One logical change per commit
- Explain WHY in commit body, not WHAT

## Project Structure

```
AgentBible/
├── AGENTS.md           # This file — universal instructions
├── TEMPLATE.md         # Templates for new rules, skills, workflows
├── rules/              # Always-on coding standards (loaded every session)
├── skills/             # Language-specific knowledge (loaded on demand)
│   ├── python/         # Triggers on **/*.py
│   ├── csharp/         # Triggers on **/*.cs
│   ├── cpp/            # Triggers on **/*.{cpp,hpp,h}
│   ├── react/          # Triggers on **/*.{jsx,tsx,ts,js}
│   ├── presentation-design/  # Triggers on deck/slides/presentation requests
│   └── camoufox/       # Stealth browser automation, anti-bot, CAPTCHA, cookie injection
├── workflows/          # Manual procedures (/research, /comment-guard, etc.)
├── scripts/            # Deployment and validation tools
├── docs/               # Architecture decisions, specs, due diligence
└── openspec/           # OpenSpec change management
```

## Rules (Always On)

These rules apply to ALL code, all languages, all the time:

- `rules/clean-code.md` — Naming, functions, comments, error handling
- `rules/patterns.md` — Design patterns decision framework
- `rules/testing.md` — Testing principles, pyramid, coverage
- `rules/commit.md` — Commit message standards (WHY not WHAT)
- `rules/architecture.md` — ADR process and principles
- `rules/ipc.md` — IPC mechanism selection
- `rules/mcp.md` — Model Context Protocol integration
- `rules/orchestration.md` — Workflow orchestration patterns
- `rules/security.md` — Security guardrails, RBAC, sandboxing, audit trails
- `rules/memory.md` — Tiered memory architecture, decay, extraction
- `rules/behaviour.md` — Agent behavior, planning, Reflexion self-correction, circuit breakers

## Skills (On Demand)

Language-specific skills load automatically when you work with matching files:

- `skills/python/` — Python standards, pytest, Ruff, async, patterns
- `skills/csharp/` — C# standards, xUnit, EF Core, ASP.NET, patterns
- `skills/cpp/` — C++ standards, Google Test, CMake, patterns
- `skills/react/` — React standards, Vitest, hooks, patterns
- `skills/presentation-design/` — Slide decks, Slidev, cognitive design, anti-AI-slop, Typst
- `skills/camoufox/` — Stealth browser automation, anti-bot bypass, CAPTCHA solving, cookie injection, security incident response

## Workflows (Manual)

Invoke these with `/command-name`:

- `/research` — Structured research with citations
- `/comment-guard` — Verify comment truthfulness
- `/doc-drift-guard` — Check docs match code
- `/adr-validator` — Validate architecture decisions
- `/tech-debt-triage` — Assess and prioritize technical debt
- `/static-analysis` — Run language-appropriate static analysis tools
- `/evaluate` — Analyze execution trajectories, detect failure patterns, self-correct

## Error Handling

- Stop immediately on errors
- Analyze before retrying
- Document learnings in auto memory if applicable

## Tool & Executable Management

- **CRITICAL**: Whenever you modify the source code of a CLI tool, application, or any executable (e.g., Python scripts, `uv tool` installations, etc.), you MUST re-install or update the executable (e.g., using `pip install -e .` or `uv tool install --editable .`) so the changes are actually reflected when the tool is run. Never forget this step!

## Communication Style

- Be concise and direct
- Use bullet points
- Show verification commands
- Acknowledge uncertainties
- Don't over-explain obvious things
