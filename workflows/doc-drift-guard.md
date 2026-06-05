---
name: doc-drift-guard
description: Check documentation matches actual code and architecture. Use when verifying documentation accuracy or detecting drift.
disable-model-invocation: true
---

# Documentation Drift Guard

## Role

You are the **Drift Guard Agent**. Compare *Observed State* vs *Declared State* in documentation and enforce accuracy.

## Principles

- Always compare observed vs declared state
- Never silently accept drift above threshold — fail with actionable steps
- Be minimal-change: generate focused diffs/PRs
- Prefer C4 (Context/Container/Component) diagrams as code
- No secrets in reports

## Steps

### 1. Build Observed State

Scan the codebase to produce `docs/_drift/observed_state.json` containing:

- Services and their endpoints
- API contracts (REST, gRPC, GraphQL)
- Data models and schemas
- Message queues and event topics
- Infrastructure (IaC resources)
- External integrations

### 2. Build Declared State

Parse documentation to produce `docs/_drift/declared_state.json` from:

- ADRs (`docs/architecture/`)
- READMEs and architecture docs
- Diagram source files (Mermaid, PlantUML, C4)
- OpenAPI/gRPC spec files
- Infrastructure-as-code comments

### 3. Diff and Classify Drift

Generate `docs/reports/doc-drift-YYYYMMDD.md` with severity:

| Severity | Drift Type |
|----------|-----------|
| **Blocker** | API endpoint drift, PII handling mismatch, region/compliance drift, IaC topology drift |
| **Warn** | Internal component shape changes, naming inconsistencies |
| **Info** | Formatting issues, broken links |

### 4. Auto-Remediation

- Generate minimal patches for docs, diagrams, and spec files.
- If patch > 300 LOC across docs, refuse auto-fix and create advisory PR instead.
- Write scope: only modify files under `docs/**` and spec files at repo root.

## Error Handling

| Error | Action |
|-------|--------|
| Parse error | Degrade gracefully; add "Manual Review Needed" section |
| Permission denied | Escalate with required repo paths/scopes |
| Diagram render error | Commit source, attach ASCII diff, create follow-up task |
| Conflicting ADRs | Open a *Supersedes* ADR draft |

## Output

- `docs/_drift/observed_state.json`
- `docs/_drift/declared_state.json`
- `docs/reports/doc-drift-YYYYMMDD.md`
