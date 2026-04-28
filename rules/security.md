# Security Guardrails

Multi-layered security for AI agent systems. Prompt engineering alone cannot enforce security — use middleware-driven policy engines.

## Input Layer

- **PII Redaction**: Strip credit cards, SSNs, emails before queries reach the orchestrator
- **Prompt Injection Detection**: Use secondary classifier models to detect malicious instructions
- **Input Validation**: Schema-validate all tool inputs before execution
- **Rate Limiting**: Per-user and per-agent request throttling

## Access Control

- **Principle of Least Privilege**: Agents get minimum permissions for their task
- **RBAC**: Role-based access control for tool invocation
- **Tool Authorization**: Explicit allow-lists per agent, deny-by-default
- **Credential Isolation**: Never share credentials across agents

## Runtime Interception

- **Middleware Hooks**: Intercept all tool calls before execution
- **Schema Validation**: Verify tool call parameters match expected schemas
- **Threshold Enforcement**: Block operations exceeding predefined limits (cost, time, data volume)
- **Circuit Breakers**: Auto-halt agents stuck in loops or exceeding error rates

## Output Auditing

- **Hallucination Scoring**: Verify factual claims before external output
- **Toxicity Screening**: Scan outputs for harmful, biased, or non-compliant content
- **Data Leakage Detection**: Ensure no secrets, keys, or PII in agent outputs
- **Tone Analysis**: Flag aggressive or inappropriate communications

## Execution Sandboxing

- **Filesystem Isolation**: Limit file access to task-specific directories
- **Network Egress Control**: Restrict outbound connections to approved endpoints
- **Process Isolation**: Run tool execution in sandboxed environments
- **Resource Caps**: CPU, memory, and time limits per execution

## Audit Trail

- **Immutable Logging**: Record every system prompt, reasoning step, and tool call
- **Cryptographic Verification**: Hash-chain audit entries for tamper detection
- **Inter-Agent Identity**: Verify agent identity before accepting claims
- **Hallucination Chain Prevention**: Mark unverified claims from other agents

## Anti-Patterns

- ❌ Relying solely on system prompt for security rules
- ❌ Sharing credentials across agent boundaries
- ❌ Allowing unrestricted filesystem or network access
- ❌ Trusting inter-agent claims without verification
- ❌ Logging secrets or PII in audit trails

## Key Takeaways

- Security requires middleware enforcement, not just prompt instructions
- Apply principle of least privilege to all tool access
- Intercept and validate tool calls before execution
- Sandbox all execution environments
- Maintain immutable audit trails
- Never trust inter-agent claims without cryptographic verification
