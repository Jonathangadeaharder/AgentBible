---
id: SPEC-AGENT-BIBLE
kind: spec
title: AgentBible — Universal Agent Development Guidelines
status: draft
authors: []
reviewers: []
tags: []
supersedes: []
superseded_by: []
depends_on: []
blocks: []
implements: []
related: []
external: []
project: AgentBible
checksum: 6c7d13f113a031ff284e3480528b82c18578ab752b4fde0449dc3bab5fba0985
---

## Overview

AgentBible provides comprehensive, cross-platform development guidelines for AI coding agents. It is a markdown knowledge base organized into three tiers: rules (always-on standards), skills (language-specific knowledge), and workflows (manual multi-step procedures).

## Key Decisions

| Decision | Choice |
|----------|--------|
| Content format | Plain markdown, no build step |
| Organization | rules/ (always) + skills/ (on-demand) + workflows/ (manual) |
| Entry point | AGENTS.md in project root |
| Deployment | Platform-specific scripts under scripts/ |

## Directory Structure

```
AgentBible/
├── AGENTS.md           # Universal entry point (always loaded)
├── rules/              # Always-on coding standards
│   ├── architecture.md # ADR process and principles
│   ├── behaviour.md    # Agent behavior, planning, self-correction
│   ├── clean-code.md   # Naming, functions, comments, error handling
│   ├── commit.md       # Conventional commits, atomic changes
│   ├── ipc.md          # IPC mechanism selection
│   ├── mcp.md          # Model Context Protocol integration
│   ├── memory.md       # Tiered memory architecture
│   ├── orchestration.md # Workflow orchestration patterns
│   ├── patterns.md     # Design patterns decision framework
│   ├── security.md     # Security guardrails and RBAC
│   └── testing.md      # Testing pyramid, coverage, mocking
├── skills/             # Language-specific knowledge (on-demand)
│   ├── python/
│   ├── csharp/
│   ├── cpp/
│   └── react/
├── workflows/          # Manual procedures (/command)
│   ├── adr-validator.md
│   ├── comment-guard.md
│   ├── doc-drift-guard.md
│   ├── evaluate.md
│   ├── research.md
│   ├── static-analysis.md
│   └── tech-debt-triage.md
└── scripts/            # Platform deployment tools
    ├── deploy_to_claude.py
    ├── deploy_to_copilot.py
    ├── deploy_to_windsurf.py
    ├── install-commit-hook.ps1
    └── validate-commits.ps1
```

## Content Tiers

| Tier | When Loaded | Purpose | Examples |
|------|-------------|---------|----------|
| AGENTS.md | Always | Universal instructions | Quick start, project structure |
| rules/ | Every session | Cross-language standards | Testing, security, clean code |
| skills/ | On file match | Language-specific | Python async, C# EF Core |
| workflows/ | Manual /command | Multi-step procedures | Static analysis, research |

## Platform Support

| Platform | AGENTS.md → | rules/ → | skills/ → |
|----------|-------------|----------|-----------|
| Claude Code | AGENTS.md | CLAUDE.md | .claude/skills/ |
| GitHub Copilot | AGENTS.md | global.instructions.md | {lang}.instructions.md |
| Windsurf | AGENTS.md | global_rules.md | {lang}_rules.md |
| Cursor | AGENTS.md | .cursor/rules/*.md | N/A |
