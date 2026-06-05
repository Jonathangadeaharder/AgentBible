---
id: ADR-005
kind: adr
title: Multi-Platform Deployment Strategy
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
checksum: a57d579b40e0fd4297341afd98ca06140130fee656f57e934c2d8ceaa7cda5d2
---

**Context:** AgentBible targets multiple AI coding platforms (Claude Code, GitHub Copilot, Windsurf, Cursor). Each platform has different configuration files, symlink conventions, and instruction loading mechanisms.

**Decision:** Provide platform-specific deploy scripts under `scripts/` that copy content to each platform's expected locations. The AGENTS.md file works universally when placed in the project root. Rules map to platform equivalents: rules/ → CLAUDE.md for Claude Code, copilot-instructions.md for Copilot, .cursor/rules/ for Cursor.

**Consequences:**
- Positive: Single source, multiple deployment targets
- Positive: Deploy scripts are auditable and idempotent
- Negative: Platform-specific formatting differences require script maintenance
- Negative: Not all platforms support the full feature set (frontmatter, file-watch triggers)

**Alternatives:**
- One AGENTS.md per platform: Fragments the knowledge base
- Single universal format: Loses platform-specific optimizations
