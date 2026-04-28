# Model Context Protocol (MCP) Integration

Universal standard for exposing tools, resources, and prompts to AI agents. Eliminates bespoke point-to-point integrations.

## What is MCP

- Open protocol for connecting AI agents to external tools and data sources
- Treats servers as callable functions that load tool definitions on demand
- Avoids dumping massive schemas into context window
- Works across Claude Code, Copilot, Windsurf, Cursor, and custom agents

## Architecture

```
Agent ←→ MCP Client ←→ MCP Server ←→ External Resource
```

- **Agent**: The AI model making decisions
- **MCP Client**: Built into the agent framework
- **MCP Server**: Exposes tools, resources, and prompts
- **External Resource**: Database, API, filesystem, etc.

## Tool Design Principles

- **On-demand loading**: Only load tool definitions when relevant
- **Schema-first**: Define input/output schemas before implementation
- **Least privilege**: Each tool gets minimum required permissions
- **Idempotent**: Tools should be safe to retry
- **Observable**: Log all tool invocations with timestamps and outcomes

## Tool Definition Best Practices

- Keep descriptions under 100 characters
- Use JSON Schema for input validation
- Return structured responses (not free text)
- Include error codes, not just error messages
- Version your tool interfaces

## Resource Exposure

- Expose read-only data as resources (not tools)
- Use URI templates for dynamic resources
- Implement pagination for large datasets
- Cache frequently accessed resources

## Security

- Authenticate MCP server connections
- Validate all tool inputs against schemas
- Rate limit tool invocations per agent
- Audit all tool calls with immutable logs
- Never expose secrets through tool responses

## Agent-to-Agent (A2A) Communication

When agents communicate with each other:

- **Identity verification**: Cryptographic handshake before accepting claims
- **Claim validation**: Mark inter-agent claims as unverified until confirmed
- **Scope isolation**: Agent A's permissions don't transfer to Agent B
- **Audit trail**: Log all inter-agent messages

## Anti-Patterns

- ❌ Loading all tool schemas into context at startup
- ❌ Exposing write tools as read-only resources
- ❌ No input validation on tool calls
- ❌ Trusting inter-agent claims without verification
- ❌ Logging secrets in tool responses

## Key Takeaways

- MCP eliminates bespoke integrations via universal tool protocol
- Load tool definitions on demand, not at startup
- Schema-first design with strict input validation
- Apply least privilege to all tool access
- Verify inter-agent claims before acting on them
- Maintain immutable audit trails for all tool calls
