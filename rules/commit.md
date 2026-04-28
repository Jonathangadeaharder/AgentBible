# Commit Message Standards

Clear, informative commit messages enhance project history and collaboration.

## Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

| Type | Use For |
|------|---------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Formatting (no code meaning change) |
| `refactor` | Code change (not fix or feature) |
| `perf` | Performance improvement |
| `test` | Adding/correcting tests |
| `build` | Build system/dependencies |
| `ci` | CI configuration |
| `chore` | Other changes |

### Subject Rules

- Imperative present tense ("change" not "changed")
- No capital first letter
- No period at end
- < 50 characters

### Body Rules

- Imperative present tense
- Motivation for change
- Contrast with previous behavior
- Wrap at 72 characters

### Footer

- Reference issues: `Fixes #123`, `Closes #456`
- Breaking changes: `BREAKING CHANGE: ...`

## The Golden Rule

**Explain WHY, not WHAT. The diff shows WHAT changed.**

```
// Bad (describes WHAT)
fix(api): change timeout from 30s to 60s

// Good (explains WHY)
fix(api): increase timeout to prevent mobile network failures

Users on mobile networks experienced frequent timeouts during
peak hours. Extended to 60s based on 99th percentile response
time from production logs.

Fixes #1234
```

## Pre-Commit Checklist

### Code Quality
- [ ] All tests pass locally
- [ ] No debug code or console.log
- [ ] No commented-out code
- [ ] Code formatted per project standards

### Atomicity
- [ ] ONE logical unit (feature, fix, or refactor)
- [ ] Change understandable independently
- [ ] If reverted, won't break unrelated functionality
- [ ] All modified files relate to stated change

### Message Quality
- [ ] Follows `<type>(<scope>): <subject>` format
- [ ] Subject under 50 characters
- [ ] Body explains WHY (rationale, context, alternatives)
- [ ] References issue/ticket number

## Atomic Commits

One complete, logical change that stands alone.

```
// Bad: Mixed concerns — 5 changes in one commit
fix: various bug fixes and add new feature

// Good: Split into 5 commits
fix(auth): resolve session timeout on login
build(deps): upgrade React 17.0.2 to 18.2.0
feat(profile): add user profile editing page
docs(readme): fix typos in installation section
refactor(db): extract connection pooling to module
```

## Commit Anti-Patterns

| Bad | Good |
|-----|------|
| "Fixed stuff" | `fix(api): handle null response from payment gateway` |
| "WIP" | Split into atomic commits |
| "asdfasdf" | Meaningful message |
| "Updates" | Specific description |
| "Addressed PR comments" | `refactor(auth): simplify token validation logic` |
| "Final commit" | `test(orders): add edge case for expired coupons` |

## Branch Naming

Match commit conventions:
```
feat/user-profile-page
fix/payment-timeout-issue
refactor/extract-validation
docs/update-api-docs
```

## Key Takeaways

- **WHY over WHAT** — explain rationale, not changes
- **Atomic commits** — one logical change per commit
- **Clear format** — follow conventional commits
- **Reference issues** — always link to tickets
- **Think of future** — write for someone in 6 months
- **Test first** — all tests pass before committing
