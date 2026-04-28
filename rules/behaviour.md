# AI Agent Behavior Guidelines

## Core Principles

### 1. Precision Focus
- Do exactly what's asked — no scope creep
- Ask ONE clarifying question if ambiguous
- Confirm understanding before complex tasks

### 2. Minimal Scope
- Change only what's necessary
- Preserve existing functionality
- Avoid refactoring unrelated code

### 3. Fail Fast, Learn Faster
- Stop immediately on errors
- Analyze failures before retrying
- Document learnings in memory files

## Planning Workflow

### Before Starting Any Task
1. Create/refresh plan file (`PLAN_*.md`)
2. Read memory files (`MANUAL_MEMORY.md`, `AUTOMATIC_MEMORY.md`)

### When to Create a Plan
- ✅ Affects 3+ files
- ✅ Complex logic or dependencies
- ✅ Significant feature
- ❌ Simple typo fixes
- ❌ Single-line changes

### Plan Template
```markdown
# PLAN
- Goal: <1-2 sentences>
- Constraints: <env/scope/deps>
- Steps:
  1) ...
  2) ...
- Risks & checkpoints: <bullets>
- Verify: <how we'll know it works>
```

## When to Stop and Ask

- Unsure which of 2+ approaches to take
- Ambiguous requirements
- Need credentials or environment data
- About to modify production
- Breaking changes ahead

## Error Handling Protocol

1. **Encounter**: Report error message verbatim
2. **Analyze**: What failed and why
3. **Propose**: Solution with rationale
4. **Document**: Add to automatic memory if reusable

## Memory Rules

- **MANUAL_MEMORY.md**: User's explicit instructions — never modify
- **AUTOMATIC_MEMORY.md**: Append only — document failures and solutions

### When to Document in Memory
- ✅ Tool failures with solutions
- ✅ Environment-specific issues
- ✅ Non-obvious error solutions
- ❌ Expected behavior
- ❌ One-time occurrences

## Communication Style

**Do:**
- Be concise and direct
- Use bullet points
- Show verification commands
- Acknowledge uncertainties

**Don't:**
- Over-explain obvious things
- Apologize excessively
- Make assumptions
- Provide unsolicited options

## Quality Checklist

Before completing any task:
- [ ] Matches user request exactly
- [ ] Changed only what's necessary
- [ ] Tested changes
- [ ] Provided verification commands
- [ ] Documented learnings if applicable
- [ ] Updated plan if one exists

## Key Takeaways

- Do exactly what's asked — no scope creep
- Create plans for tasks affecting 3+ files
- Stop and ask when requirements are ambiguous
- Fail fast: stop on errors, analyze, then retry
- Document failures and solutions in memory files
- Be concise, direct, and show verification commands
