# ADR-003: Skill Framework for Language-Specific Knowledge

**Status:** Accepted

**Context:** Different programming languages have different conventions, testing frameworks, and toolchains. A single set of rules cannot cover language-specific detail. Skills must load on demand to avoid polluting the context for unrelated files.

**Decision:** Language-specific knowledge lives in `skills/{language}/` directories. Each skill directory has a SKILL.md entry point and topic files (clean-code.md, patterns.md, testing.md, etc.). Skills activate when the agent detects matching file extensions (e.g., `*.py` triggers `skills/python/`).

**Consequences:**
- Positive: Language detail only loads when relevant
- Positive: Skills are discoverable and independently maintainable
- Negative: Some knowledge is cross-language (testing patterns) — may duplicate across skills
- Negative: Skill activation depends on agent platform support for file-watch triggers

**Alternatives:**
- Single language-agnostic ruleset: Loss of language-specific detail
- Per-project copy: No reuse across projects
