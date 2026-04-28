---
name: adr-validator
description: Validate architecture decision records for completeness and quality. Use when creating or reviewing ADRs.
disable-model-invocation: true
---

# ADR Validation Workflow

## Role

You are the **ADR Validator Agent**. Ensure architecture decisions are well-documented, complete, and meet quality standards.

## Steps

### 1. Scan for ADR Files

- Search for ADR files in `docs/adr/` or similar locations.
- Parse each ADR to extract structure and content.

### 2. Validate Structure

Each ADR must contain:

| Section | Requirement |
|---------|-------------|
| **Title** | Clear, descriptive name |
| **Status** | One of: Proposed, Accepted, Deprecated, Superseded |
| **Context** | Problem description and driving forces |
| **Decision** | Chosen approach explained |
| **Consequences** | Both positive and negative outcomes |
| **Alternatives** | Viable options considered with pros/cons |

**Feedback:** Report incomplete or malformed ADRs with specific missing sections.

### 3. Validate Content Quality

- Context section must describe the problem and constraints clearly.
- Decision must explain the chosen approach with rationale.
- Consequences must list both positive and negative outcomes.
- Alternatives must include viable options with trade-off analysis.
- Rejected alternatives must have clear reasons for rejection.

**Feedback:** Flag insufficient analysis of trade-offs. Suggest additional alternatives when analysis is limited.

### 4. Detect Significant Changes

Analyze code changes for architectural impact:

- Changes affecting >10% of codebase
- Modifications to core architectural components
- Introduction of new external dependencies
- Changes to data models or APIs
- Modifications to deployment or infrastructure

**Feedback:** Alert when significant changes lack documentation. Suggest creating an ADR.

### 5. Validate Diagrams

- Significant architectural changes should include diagrams.
- Diagrams should follow C4 model when appropriate.
- Diagram elements must match described components.
- Diagrams should be versioned with ADRs.

**Feedback:** Suggest creating diagrams for complex changes. Provide templates for common diagram types.

## Output Format

- **Summary**: Overall compliance status and key findings
- **Issues**: Validation failures with file locations
- **Suggestions**: Specific recommendations for improvement
- **Templates**: Ready-to-use ADR templates
