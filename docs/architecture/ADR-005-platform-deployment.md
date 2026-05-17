# ADR-005: Multi-Platform Deployment Strategy

**Status:** Accepted

**Context:** AgentBible targets multiple AI coding platforms (Claude Code, GitHub Copilot, Windsurf, Cursor). Each platform has different configuration files, symlink conventions, and instruction loading mechanisms.

**Decision:** Provide platform-specific deploy scripts under `scripts/` that copy or symlink content to each platform's expected locations. The AGENTS.md file works universally when placed in the project root. Rules map to platform equivalents: rules/ → .claude/ for Claude Code, copilot-instructions.md for Copilot, .cursor/rules/ for Cursor.

**Consequences:**
- Positive: Single source, multiple deployment targets
- Positive: Deploy scripts are auditable and idempotent
- Negative: Platform-specific formatting differences require script maintenance
- Negative: Not all platforms support the full feature set (frontmatter, file-watch triggers)

**Alternatives:**
- One AGENTS.md per platform: Fragments the knowledge base
- Single universal format: Loses platform-specific optimizations
