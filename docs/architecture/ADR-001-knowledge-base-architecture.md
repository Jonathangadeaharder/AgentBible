---
id: ADR-001
kind: adr
title: Markdown Knowledge Base Architecture
status: accepted
authors: [Jonathan Gadea Harder]
reviewers: [Jonathan Gadea Harder]
tags: []
supersedes: []
superseded_by: []
depends_on: []
blocks: []
implements: []
related: []
external: []
project: AgentBible
checksum: b6ddf30ff70c07a3507155f1079979181d241607c3a2ba14983b457a445916c6
---

**Context:** AgentBible needs to serve as a universal development guidelines repository for AI coding agents across multiple platforms (Claude Code, Copilot, Windsurf, Cursor). The content must be platform-agnostic while allowing platform-specific deployment.

**Decision:** Organize as a flat markdown knowledge base with three content tiers: rules (always-on), skills (on-demand), and workflows (manual invocation). A root AGENTS.md file serves as the entry point. No build step or rendering engine — content is consumed directly in markdown form.

**Consequences:**
- Positive: Zero toolchain dependencies. Any platform supporting markdown can consume
- Positive: Git-tracked, reviewable via standard PR workflows
- Negative: No automated cross-referencing between documents
- Negative: Formatting must be plain markdown (no extended syntax)

**Alternatives:**
- Static site generator (Docusaurus): More structure but adds build dependency
- Single CLAUDE.md: Too large, violates context window limits
- JSON/YAML config: Harder to read and maintain than markdown
