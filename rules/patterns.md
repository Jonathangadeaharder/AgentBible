# Design Patterns Usage Policy

Detect design smells, recommend the simplest viable pattern, refuse patterns when they add needless complexity.

## Guardrails

- **Must** cite the triggering smell(s) and the benefit (testability, decoupling, reuse)
- **Must not** add >3 new types or >150 LOC without explicit justification
- **YAGNI**: If no immediate client or test uses the new seam, do not introduce a pattern
- **Bench budget**: If pattern adds a dispatch/hop, estimate latency/alloc impact; abort if it breaks budgets
- **Tests first**: Add/adjust tests that prove the need and lock in behavior

## Decision Workflow

1. **Identify Smell(s)**: rigidity, shotgun changes, long conditionals, duplicated algorithms, chatty coupling, unstable dependency, global state
2. **Map Smell → Candidate Pattern(s)** (see quick mapping)
3. **Try lowest-cost alternative first** (function parameter, small interface) before a full pattern
4. **Propose Minimal Plan**: files to touch, interfaces, quick sketch
5. **Add/Update Tests**
6. **Refactor in small steps**; measure impact (perf + readability)
7. **Stop** when the smell is resolved. Do not "collect them all."

## Smell → Pattern Quick Mapping

| Smell | Pattern |
|-------|---------|
| Long `if/else` by type/flag | **Strategy** or **State** |
| Many optional processing steps | **Chain of Responsibility** |
| Need undo/queue/audit | **Command** |
| Cross-module chatter | **Mediator** or **Observer** |
| Stable hierarchy, many operations | **Visitor** |
| Complex construction with validation | **Builder** |
| Incompatible third-party API | **Adapter** |
| Exploding subclass matrix | **Bridge** |
| Part–whole tree | **Composite** |
| Per-instance cross-cutting behavior | **Decorator** |
| Simplify complex subsystem | **Facade** |

## When NOT to Use Patterns

- No measurable smell or requirement; adding abstraction **just in case**
- Pattern introduces **more types than it removes conditionals**
- You can solve it with **a pure function + parameter** (e.g., pass comparator instead of Strategy class)
- Pattern obscures control flow critical for correctness (security/transactions)
- Perf/latency budgets are tight and added indirection is non-trivial
- Team proficiency is low; pattern would hinder maintainability

## Overengineering Signals

- "We might need X later" without a ticket/user
- Factories that return only one concrete type
- Visitors over tiny, volatile hierarchies
- Chain of Responsibility for two `if` branches
- Abstract Factory + Builder + Prototype stack for simple DTOs
- Singleton for logging/config where DI is available
- Decorator stacks where a **single proxy** or **policy flag** would do

## Minimal Implementation Checklist

- **Pre-commit**: list smell(s), selected pattern, and rejected simpler alternatives
- **Introduce**: 1 interface, the smallest set of concretes
- **Wire**: via DI or factory; avoid globals
- **Tests**: unit tests for seams + one integration proving the benefit
- **Docs**: short rationale: *Why this pattern, why now, consequences*
- **Review Gate**: If diff >150 LOC or >3 types, add a note justifying scope

## Key Takeaways

- Patterns solve **existing smells**, not hypothetical future needs
- Try the cheapest fix first (function param, small interface)
- >3 new types or >150 LOC requires explicit justification
- If no test or client uses the seam, don't create it
- Stop when the smell is resolved — don't collect patterns
