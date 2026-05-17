# ADR-002: Rule System for Agent Instructions

**Status:** Accepted

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
