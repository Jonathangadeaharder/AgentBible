# Architecture Decision Principles

Document all significant architecture decisions for transparency, traceability, and knowledge sharing.

## ADR Format

Every ADR has 6 fields:

1. **Title** — Brief, descriptive
2. **Status** — Proposed, Accepted, Deprecated, Superseded, Rejected
3. **Context** — Problem statement and driving forces
4. **Decision** — Chosen approach and rationale
5. **Consequences** — Positive and negative outcomes
6. **Alternatives** — Considered options and why rejected

## When to Create an ADR

- Affects system structure or behavior
- Significant cost or risk implications
- Difficult to change later
- Impacts multiple teams/components
- Technology selection
- Cross-cutting concerns (security, performance, scalability)

## ADR Lifecycle

**Statuses**: Proposed → Accepted → Deprecated → Superseded (or Rejected from Proposed)

### When to Create New vs Update

**Create New**: Fundamental direction change, original context no longer applies, multiple teams affected differently, previous decision superseded.

**Update Existing**: Implementation details change, minor consequences discovered, clarifications, typo fixes.

## Numbering

- Sequential: ADR-001, ADR-002, etc.
- Never reuse numbers
- Filename: `ADR-042-postgresql-analytics.md`
- Reference in code/docs/commits

## Design Principles

### 1. Separation of Concerns
- Divide into distinct features, minimal overlap
- Single responsibility per module
- Clear boundaries

### 2. Modularity
- Independent development, testing, deployment
- Minimize dependencies
- Well-defined interfaces

### 3. Scalability
- Horizontal scaling when possible
- Consider performance implications
- Plan for growth

### 4. Maintainability
- Simplicity over cleverness
- Easy to understand and modify
- Document complex decisions
- No legacy fallbacks — replace old implementations entirely

### 5. Security
- Security by design
- Principle of least privilege
- Threat modeling for critical components

## ADR Anti-Patterns

### Decision Without Alternatives
```
// Bad
# ADR: Use React
Decision: We will use React.

// Good
# ADR: Use React for Frontend
## Alternatives
- React: Large ecosystem, team has 3 years experience
- Vue: Simpler, but team has LOW familiarity
- Angular: Full framework, but team has NONE familiarity
## Decision
Choose React: team expertise + tight timeline.
```

### Vague Consequences
```
// Bad
Consequences: This will be good.

// Good
## Consequences
Positive: Reduces API response time 40%, simplifies caching
Negative: Increases DB CPU 15%, 2 weeks migration downtime
Risks: Small community, vendor lock-in to PostgreSQL
```

### ADR for Trivial Decisions
```
// Bad: This is a coding standard, not architecture
# ADR: Use PascalCase for Class Names
```

## ADR Checklist

- [ ] Context complete (problem, constraints)
- [ ] Alternatives documented (2-3 options)
- [ ] Decision rationale clear
- [ ] Consequences analyzed (positive + negative)
- [ ] Stakeholders consulted
- [ ] Reversibility assessed

## Key Takeaways

- ADRs prevent repeated "why did we do it this way?" discussions
- Always document 2-3 alternatives with rejection rationale
- Be specific about consequences — vague consequences are useless
- Mark deprecated/superseded ADRs; never reuse numbering
- Reference ADRs in commits and PRs
- Not for trivial decisions — use coding standards for style
