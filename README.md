# AgentBible

Comprehensive development guidelines for AI coding agents. Works with Claude Code, GitHub Copilot, Windsurf, Cursor, and any tool supporting the [AGENTS.md](https://agents.md) standard.

## What's Inside

```
AgentBible/
├── AGENTS.md           # Universal agent instructions (always loaded)
├── TEMPLATE.md         # Templates for new rules, skills, and workflows
├── rules/              # Always-on coding standards
├── skills/             # Language-specific knowledge (loaded on demand)
│   ├── python/
│   ├── csharp/
│   ├── cpp/
│   └── react/
├── workflows/          # Manual procedures (/command)
├── scripts/            # Deployment and validation tools
├── docs/               # Architecture decisions, specs, due diligence
│   ├── architecture/   # ADRs (ADR-001 through ADR-005)
│   └── specs/          # Design specifications
└── openspec/           # OpenSpec change management
```

### Rules (Always On)

Cross-language principles loaded every session:

| Rule | What it covers |
|------|---------------|
| `clean-code.md` | Naming, functions, comments, error handling, boundaries |
| `patterns.md` | Design patterns decision framework (when to use, when not to) |
| `testing.md` | Test pyramid, coverage, naming, mocking, anti-patterns |
| `commit.md` | Conventional commits, atomic changes, WHY not WHAT |
| `architecture.md` | ADR process, design principles, documentation standards |
| `ipc.md` | IPC mechanism selection (REST, gRPC, queues, shared memory) |
| `mcp.md` | Model Context Protocol integration, tool design, A2A communication |
| `orchestration.md` | Workflow patterns (Sequential, Concurrent, Handoff, Magentic) |
| `security.md` | Security guardrails, RBAC, sandboxing, audit trails, PII redaction |
| `memory.md` | Tiered memory architecture, decay, extraction, bi-temporal tracking |
| `behaviour.md` | Agent behavior, planning, Reflexion self-correction, circuit breakers |

### Skills (On Demand)

Language-specific knowledge that loads when you work with matching files:

| Skill | Triggers on | Covers |
|-------|------------|--------|
| `python/` | `**/*.py` | PEP 8, pytest, Ruff, async, patterns, IPC |
| `csharp/` | `**/*.cs` | Naming, xUnit, EF Core, ASP.NET, patterns |
| `cpp/` | `**/*.cpp`, `**/*.hpp` | Naming, Google Test, CMake, RAII, patterns |
| `react/` | `**/*.jsx`, `**/*.tsx`, `**/*.ts`, `**/*.js` | Hooks, Vitest, React Query, patterns |

### Workflows (Manual)

Multi-step procedures invoked with `/command`:

| Command | What it does |
|---------|-------------|
| `/research` | Structured research with plan confirmation and citations |
| `/comment-guard` | Verify comment truthfulness (WHY not WHAT) |
| `/doc-drift-guard` | Check docs match actual code and architecture |
| `/adr-validator` | Validate architecture decision records |
| `/tech-debt-triage` | Assess and prioritize technical debt |
| `/static-analysis` | Run language-appropriate static analysis tools |
| `/evaluate` | Analyze execution trajectories, detect failure patterns, self-correct |

## Quick Start

### Option 1: Copy AGENTS.md

Copy `AGENTS.md` to your project root. Works with any agent that reads AGENTS.md files.

### Option 2: Deploy to Specific Tools

```bash
# Deploy to GitHub Copilot (all languages)
python scripts/deploy_to_copilot.py

# Deploy to GitHub Copilot (specific languages)
python scripts/deploy_to_copilot.py python react

# Deploy to Windsurf (requires language argument)
python scripts/deploy_to_windsurf.py python react

# Deploy to Claude Code (requires target: user or project)
python scripts/deploy_to_claude.py user
python scripts/deploy_to_claude.py project python react
```

### Option 3: Use as Skills (Claude Code)

```bash
# Symlink into your project
ln -s /path/to/AgentBible/skills .claude/skills/agentbible

# Or copy specific skills
cp -r AgentBible/skills/python .claude/skills/python
```

## How It Works

| Category | When loaded | Purpose |
|----------|-------------|---------|
| **AGENTS.md** | Always | Universal instructions for any agent |
| **rules/** | Always (every session) | Cross-language coding standards |
| **skills/** | On demand (file match or manual) | Language-specific knowledge |
| **workflows/** | Manual only (`/command`) | Multi-step procedures with side effects |

## Supported Tools

| Tool | How it uses AgentBible |
|------|----------------------|
| **Claude Code** | AGENTS.md + rules/ as CLAUDE.md, skills/ as .claude/skills/, workflows/ as custom commands |
| **GitHub Copilot** | AGENTS.md as copilot-instructions.md, rules/ as .instructions.md |
| **Windsurf** | AGENTS.md + rules/ as .windsurf/rules/, skills/ as memories |
| **Cursor** | AGENTS.md as .cursor/rules, rules/ as .cursor/rules/*.md |
| **Any agent** | AGENTS.md in project root |

## Adding Content

### New Language

1. Create `skills/{language}/SKILL.md` with frontmatter
2. Add topic files: clean-code.md, patterns.md, testing.md, static-analysis.md, parallel.md, ipc.md
3. Add the language to `lang_config` in all three deploy scripts
4. Update README and AGENTS.md skill tables

### New Rule

1. Create `rules/{name}.md` (under 200 lines)
2. Reference it in AGENTS.md

### New Workflow

1. Create `workflows/{name}.md` with `disable-model-invocation: true` frontmatter
2. Reference it in AGENTS.md

See `TEMPLATE.md` for templates.

## License

Internal use — Development guidelines for AI agents.
