# Workflow Orchestration Patterns

How to structure multi-agent and multi-step workflows. Choose the right pattern for your use case.

## Core Patterns

| Pattern | Execution | Best For | Risk |
|---------|-----------|----------|------|
| Sequential | Linear, A→B→C | Data pipelines, compliance | Early error corrupts all downstream |
| Concurrent | Parallel fan-out | Document analysis, scraping | Uncontrolled cost/rate limits |
| Handoff | Conditional routing | Triage, domain routing | Context loss during transfer |
| Group Chat | Multi-party debate | Brainstorming, design review | Unstructured, hard to audit |
| Magentic | Supervisor routes dynamically | Open-ended exploration | Non-deterministic, high latency |

## Sequential Flow

- Execute agents in rigid order: A→B→C
- Output of each agent becomes input to next
- **Use when**: Standardized pipelines, linear transformations
- **Avoid when**: Steps are independent (use Concurrent instead)
- **Mitigation**: Validate outputs between steps

## Concurrent (Scatter-Gather)

- Fan out to N parallel workers
- Synchronize with deterministic merge/reducer
- **Use when**: Independent tasks (multi-doc analysis, parallel research)
- **Avoid when**: Tasks have dependencies or shared state
- **Mitigation**: Hard concurrency limits, per-task timeouts, idempotency keys

## Handoff (Router)

- Agent transfers control to specialized peer based on intent/confidence
- **Use when**: Domain-specific routing (support triage, language detection)
- **Avoid when**: Context must be preserved across handoffs
- **Mitigation**: Strict data contracts, shared memory for context continuity

## Orchestrator-Worker

- Central planner decomposes task → farms to workers → synthesizer merges
- **Use when**: Complex tasks decomposable into independent subtasks
- **Avoid when**: Subtasks have tight interdependencies
- **Mitigation**: Concurrency caps, timeout enforcement, idempotency keys

## Human-in-the-Loop

- Pause execution at decision points for human review
- **Use when**: High-stakes decisions, ambiguous routing, confidence below threshold
- **Implement**: Checkpoint state, present options, resume on approval
- **Key**: Make pausing deterministic — don't rely on LLM to decide when to ask

## Error Propagation

| Strategy | When to Use | Behavior |
|----------|-------------|----------|
| Fail-fast | Critical pipelines | Stop entire workflow on first error |
| Continue | Best-effort analysis | Log error, skip step, continue |
| Retry with backoff | Transient failures | Retry N times with exponential delay |
| Fallback | Degraded mode | Switch to alternative agent/approach |

## Concurrency Controls

- **Max parallel agents**: Hard cap (e.g., 10 concurrent workers)
- **Per-tool timeout**: Kill tool calls exceeding threshold
- **Idempotency keys**: Prevent duplicate state mutations on retry
- **Rate limiting**: Respect external API limits
- **Cost caps**: Halt if estimated cost exceeds budget

## Anti-Patterns

- ❌ Unstructured free-form agent conversations (hard to audit, non-deterministic)
- ❌ No concurrency limits (cost explosion, rate limiting)
- ❌ Ignoring error propagation (silent failures compound)
- ❌ Using Magentic pattern for deterministic tasks (unnecessary latency)
- ❌ No human checkpoint for high-stakes decisions

## Key Takeaways

- Sequential for linear pipelines, Concurrent for independent tasks
- Handoff for domain routing, Orchestrator-Worker for decomposable tasks
- Always enforce concurrency limits, timeouts, and idempotency keys
- Use human-in-the-loop for high-stakes or low-confidence decisions
- Choose fail-fast vs continue based on criticality
- Prefer deterministic patterns over free-form agent conversations
