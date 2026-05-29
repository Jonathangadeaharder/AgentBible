---
id: ADR-004
kind: adr
title: Workflow Orchestration System
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
checksum: 37a3f70789d8189afd9e79788c025c8d6785cc29fd2691aa3d8dc83596b564ab
---

**Context:** Some procedures are multi-step, side-effect-bearing, and should not run automatically. Agents need manual commands for research, validation, triage, and evaluation workflows.

**Decision:** Workflows are markdown files under `workflows/` with `disable-model-invocation: true` frontmatter. Users invoke them with `/command` syntax (e.g., `/research`, `/adr-validator`). Each workflow is a self-contained script with step-by-step instructions, tool calls, and expected outputs.

**Consequences:**
- Positive: Explicit user control over complex operations
- Positive: Workflows can include bash commands, API calls, and analysis steps
- Negative: Requires user discipline to invoke workflows
- Negative: Frontmatter parsing depends on agent platform support

**Alternatives:**
- Always-on automation: Would run expensive analyses without user intent
- Shell scripts: Lose natural language reasoning and agent context
