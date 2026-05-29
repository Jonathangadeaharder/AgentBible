---
id: ADR-002
kind: adr
title: Rule System for Agent Instructions
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
checksum: fbb683c31aa6d9c401914a30626e5f19fa5ac092efb37dd909933a58b17b36c6
---

**Context:** Agents need always-on coding standards that load every session. Rules must be cross-language, enforce consistent practices, and remain concise (under 200 lines each).

**Decision:** Each rule is a standalone markdown file under `rules/`. The AGENTS.md references all rules by filename and purpose. Rules are loaded by the agent runtime automatically when the project root is opened. Each rule covers one concern: naming, testing, security, IPC, etc.

**Consequences:**
- Positive: Single source of truth for each concern
- Positive: Easy to add/remove rules without restructuring
- Negative: Rules may overlap (e.g., clean-code and patterns both discuss function design)
- Negative: No dependency ordering between rules

**Alternatives:**
- Monolithic rules document: Too long, hard to maintain
- YAML frontmatter: Over-engineered for plain text rules
