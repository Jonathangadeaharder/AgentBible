---
id: TDD-AGNT
kind: tdd
title: AgentBible
description: >-
  Universal development guidelines for AI coding agents — rules, skills,
  workflows
status: draft
date: 2026-05-17T00:00:00.000Z
authors: []
reviewers: []
risk_level: low
scope_type: project
tags:
  - documentation
  - agent-instructions
  - ai-coding
related: []
checksum: 7b1a17ae9785bcec9af132bdc3b9eb712926b870041d31670c8ddbf2bff46f9e
---

## Executive Summary

AgentBible is a documentation-only project providing universal development guidelines for AI coding agents. Healthy but minimal: 11 rules, 4 language skills, 7 workflows in pure markdown. No code, no dependencies, no tests, no CI/CD. Low risk — the main concern is lack of validation that rules are correct and up to date.

## Scope

Assessed: the full markdown knowledge base, cross-platform deploy scripts for Claude Code / Copilot / Windsurf. Excluded: external agent platforms' own configuration (opencode.json, AGENTS.md) — those are consumer-side setups, not part of AgentBible itself.

## Architecture

Flat file hierarchy organized into `rules/`, `skills/`, `workflows/`, `scripts/`. No build step or runtime. Content is self-referential — rules reference each other via convention. Deploy scripts copy content per-platform.

## Tech Stack

Pure markdown. No languages, runtimes, or frameworks. Shell scripts for deploy (bash).

## Code Quality

No automated testing. No linting. Documentation structure is well-organized with clear cross-references. No validation exists that the guidance is internally consistent or technically correct.

## Security

No auth, secrets, or data handling. Threat surface is limited to deploy scripts that write to agent configuration directories.

## Scalability & Performance

Not applicable — static content with no runtime. Scales by adding more markdown files.

## Operations & DevOps

No CI/CD. Manual deploy via local shell scripts. No observability, monitoring, or runbooks.

## Dependencies & Third-Party Risk

Zero runtime dependencies. Deploy scripts depend on standard Unix utilities (cp, mkdir).

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Rule correctness unvalidated | Medium | Medium | Add automated consistency checks or cross-reference validation |
| Guidance drift as platforms evolve | Medium | Low | Schedule quarterly review cycle |
| No test coverage on deploy scripts | Low | Low | Add shellcheck to CI if repo gains CI |

## Recommendations

1. Add automated consistency validation for cross-references between rules — owner TBD, before Q3 2026.
2. Establish a review cadence (quarterly) to verify guidance is current with agent platform releases.
3. Consider adding minimal CI (markdown lint, shellcheck on deploy scripts) to catch formatting and shell errors.
