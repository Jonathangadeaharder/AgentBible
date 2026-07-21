# Actor-Checker LLM Automation Pattern

## Problem

Complex Angular/React SPAs (Ryanair, Iberia) have unknown interaction models.
Writing a blind automation script wastes hours debugging selectors, event handlers,
and overlays. The interactive REPL helps but requires manual step-by-step driving.

## Solution: Actor-Checker Loop

Use a local LLM (LM Studio, `gemma-4-31b-it-qat`) to drive the browser:

1. **Actor** LLM: sees goal + page state + screenshot → proposes ONE REPL command
2. **Execute** the command in the same Camoufox browser
3. **Checker** LLM: sees goal + action + before/after state + screenshot → SUCCESS/FAIL
4. Loop until goal reached or max steps exhausted

## Implementation

File: `scripts/actor_checker.py`

```python
# Key config
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
MODEL = "gemma-4-31b-it-qat"  # 31B works. 26B returns empty content (reasoning model).

# Actor: system prompt includes verified site-specific selector patterns
# Checker: vision analysis of before/after screenshots

# Screenshot resizing: sips -z 600 800 before base64 encoding
# Reasoning model handling: check both content and reasoning_content fields
# Command extraction: find last line matching known command prefixes
```

## What Works

- Actor correctly proposes `clean` → `clicktext Nur Hinflug` → `click [data-ref=...] !force` → `clicktext Spanien` → `eval ...find(Valencia).click()` → `eval ...dates-from...dispatchEvent(click)` → `click [data-ref="flight-search-widget__cta"] !force`
- Checker correctly identifies when one-way radio is checked, when airport picker opens, when Valencia is selected
- Actor adapts: when `clicktext` fails, tries `click` with CSS selector

## What Doesn't Work Yet

- **Overlay persistence**: Ryanair's airport picker dropdown stays open over the calendar. Actor doesn't know to press Escape or click outside. Needs a `close` command.
- **26B model**: Returns empty `content` — output goes to `reasoning_content`. The reasoning text contains chain-of-thought, not just commands. Need to extract the actual command from reasoning.
- **Angular reactive form validation**: `fill()` sets values but Angular marks form as invalid (button stays disabled). Actor needs to know to use `press` (press_sequentially) or dispatch Angular's `markAsDirty()`.

## System Prompt Strategy

Include ALL verified selector patterns in the actor's system prompt as numbered steps.
The LLM follows these patterns reliably:

```
CRITICAL PATTERNS for Ryanair (Angular SPA):
1. Cookie popup: `clean` first...
2. One-way: `clicktext Nur Hinflug`
3. Origin field: `click [data-ref="input-button__display-value"] !force`
4. Select country: `clicktext Spanien`
5. Select airport: `eval Array.from(...).find(e => e.textContent.trim() === 'Valencia').click()`
...
```

## Verified Results (2026-06-28)

With `gemma-4-31b-it-qat`:
- Step 1: `clean` → FAIL (no visible change, but popup removed)
- Step 2: `clicktext Nur Hinflug` → SUCCESS (one-way selected)
- Step 3: `click [data-ref="input-button__display-value"] !force` → SUCCESS (picker opens)
- Step 4: `clicktext Spanien` → SUCCESS
- Step 5: `eval ...find(Valencia).click()` → SUCCESS (Valencia selected!)
- Step 6-8: Destination (Deutschland, Berlin Brandenburg) → SUCCESS
- Step 9-14: Calendar open + day selection → FAIL (overlay blocking)
- Steps got stuck in loop trying to close dropdown

Total: 8/14 steps successful. The actor correctly follows the system prompt patterns.
The remaining blocker is overlay management (closing dropdowns before clicking calendar).
