# Memory Architecture

Tiered memory system for AI agents. Context windows are finite — treat them as managed resources, not infinite append logs.

## Memory Tiers

| Tier | Analogy | Scope | Storage | Loaded When |
|------|---------|-------|---------|-------------|
| Working Memory | RAM | Current task | In-context | Always (current session) |
| Episodic Memory | Disk | Session history | Files/database | On demand |
| Long-Term Memory | Archive | Cross-session | Vector DB + graph | Semantic match |

## Working Memory (Current Context)

- Current task instructions and plan
- Active conversation turns (last N messages)
- Relevant skill content (loaded on demand)
- **Constraint**: Treat as scarce resource — evict stale data aggressively

## Episodic Memory (Session History)

- Previous conversation summaries
- Task outcomes and decisions made
- Error logs and debugging insights
- **Storage**: Files (MEMORY.md) or session-scoped database
- **Access**: Read on session start, append during session

## Long-Term Memory (Cross-Session)

- User preferences and patterns
- Project conventions and decisions
- Accumulated domain knowledge
- **Storage**: Vector embeddings (semantic search) + knowledge graphs (relational)
- **Access**: Retrieve by semantic similarity or graph traversal

## Extraction Protocol (Predict-Calibrate)

Before storing any fact, evaluate:

1. **Utility**: Will this be useful in future sessions?
2. **Specificity**: Is this specific enough to be actionable?
3. **Durability**: Will this still be valid in 30 days?
4. **Uniqueness**: Does this duplicate existing memory?

Only store facts that pass all 4 checks. Skip:
- Transient conversational filler
- One-time observations
- Information that expires quickly
- Duplicates of existing memory

## Intelligent Decay

Score each memory: `relevance = recency × frequency × utility`

- **High relevance**: Always include in context
- **Medium relevance**: Include on semantic match
- **Low relevance**: Archive, exclude from active retrieval
- **Zero relevance**: Delete or compress

## Bi-Temporal Tracking

Track two timelines for each fact:
- **Valid time**: When the fact was true in the real-world
- **Transaction time**: When the agent learned/recalled the fact

Example: "Server migrated to AWS" — valid since Jan 2025, recorded Feb 2025.

## Hybrid Retrieval

1. Embed query → vector similarity search → candidate set
2. Graph traversal → find related entities → expand context
3. Rank by relevance score → inject top-K into working memory
4. This minimizes tokens while maximizing factual grounding

## Anti-Patterns

- ❌ Appending entire conversation history to context
- ❌ Storing every fact without utility evaluation
- ❌ No decay mechanism (memory grows forever)
- ❌ Using only vector search (misses relational context)
- ❌ Treating context window as infinite

## Key Takeaways

- Working memory is scarce — evict stale data aggressively
- Predict-calibrate before storing: utility × specificity × durability × uniqueness
- Implement intelligent decay: recency × frequency × utility scoring
- Use hybrid vector + graph retrieval for long-term memory
- Track bi-temporal data (valid time + transaction time)
- Never dump full conversation history into context
