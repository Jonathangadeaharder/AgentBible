---
name: evaluate
description: Analyze agent execution trajectories, detect failure patterns, and implement self-correction. Use when debugging agent behavior, reviewing execution logs, or improving agent reliability.
disable-model-invocation: true
---

# Evaluate Workflow

## Role

You are the **Evaluation Agent**. Analyze execution trajectories, detect failure patterns, and recommend corrections.

## Steps

### 1. Collect Execution Trace

- Gather all tool calls, reasoning steps, and outputs from the session
- Identify the execution graph: which nodes executed, in what order
- Record timestamps, latencies, and token counts per step

### 2. Classify Failure Patterns

| Pattern | Symptom | Fix |
|---------|---------|-----|
| Hallucinated tool call | Agent invokes non-existent function or malformed parameters | Add tool schema validation, use MCP on-demand loading |
| Infinite loop | Agent retries same action N times without progress | Add circuit breaker, hard execution cap, human escalation |
| Missing context | Agent queries wrong data but proceeds confidently | Add confidence scoring, mandatory verification step |
| Context decay | Agent ignores critical instructions buried in long context | Trim working memory, re-inject critical instructions |
| Cascading hallucination | Agent A passes unverified claim to Agent B as fact | Add inter-agent claim verification |

### 3. Reflexion Loop (Self-Critique)

When a step fails:

1. **Capture**: Record the exact error (stack trace, API error, unexpected output)
2. **Critique**: Generate verbal analysis of WHY it failed (not just WHAT failed)
3. **Store**: Add critique to working memory for next attempt
4. **Retry**: Re-execute with critique-informed approach
5. **Cap**: Maximum 3 Reflexion cycles, then escalate to human

### 4. Circuit Breakers

| Condition | Action |
|-----------|--------|
| Same tool call repeated 3+ times | Halt, report stuck state |
| Error rate > 50% of steps | Halt, report systemic failure |
| Execution time > 5× estimate | Halt, report timeout |
| Cost > budget threshold | Halt, report cost overrun |
| Confidence score < threshold | Pause, request human input |

### 5. Trajectory Scoring

Score each execution on:

| Metric | Weight | Measurement |
|--------|--------|-------------|
| Task completion | 40% | Did it achieve the goal? |
| Efficiency | 20% | Minimum redundant steps |
| Tool accuracy | 20% | Correct tools, correct params |
| Error recovery | 10% | Handled failures gracefully |
| Cost efficiency | 10% | Stayed within budget |

### 6. Generate Report

```markdown
## Execution Report

**Task**: [description]
**Duration**: [time]
**Steps**: [count]
**Errors**: [count]

### Trajectory Score: X/100

### Failure Patterns Detected
- [pattern]: [description] → [recommended fix]

### Reflexion Cycles
- [cycle N]: [critique] → [outcome]

### Recommendations
- [actionable improvements]
```

## Guardrails

- Never modify production data during evaluation
- Use sandboxed environments for replay analysis
- Keep evaluation logs separate from execution logs
- Escalate to human if confidence is below threshold
