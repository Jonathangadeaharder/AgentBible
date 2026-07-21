# Direct REST API Usage with Custom userId

When cookies are pre-injected for a specific userId (e.g., `rotator`, `cli_user`,
or any non-Hermes identity), Hermes browser tools (`browser_navigate`,
`browser_click`, etc.) CANNOT be used — they generate their own `hermes_<hash>`
userId and would create a separate session without the injected cookies.

Instead, drive the Camoufox REST server directly via curl. This is the same
server at `http://localhost:9377` that Hermes browser tools and the CLI both use.

## Creating a Tab with a Custom userId

```bash
# sessionKey is REQUIRED — not just userId!
curl -s -X POST "http://localhost:9377/tabs" \
  -H "Content-Type: application/json" \
  -d '{"userId": "rotator", "sessionKey": "rotator", "url": "https://example.com/"}'
# Returns: {"tabId":"2f00d1f5-...", "url":"https://example.com/"}
```

**Pitfall**: `POST /tabs` returns `{"error":"userId and sessionKey required"}` if
`sessionKey` is omitted. Always include both.

## Core REST Operations (all require userId in body or query)

```bash
TAB_ID="2f00d1f5-..."
USER_ID="rotator"

# Navigate
curl -s -X POST "http://localhost:9377/tabs/$TAB_ID/navigate" \
  -H "Content-Type: application/json" \
  -d "{\"userId\": \"$USER_ID\", \"url\": \"https://example.com/page\"}"

# Get snapshot (aria tree with refs e1, e2, ...)
curl -s "http://localhost:9377/tabs/$TAB_ID/snapshot?userId=$USER_ID"

# Click element by ref
curl -s -X POST "http://localhost:9377/tabs/$TAB_ID/click" \
  -H "Content-Type: application/json" \
  -d "{\"userId\": \"$USER_ID\", \"ref\": \"e5\"}"

# Type into element by ref
curl -s -X POST "http://localhost:9377/tabs/$TAB_ID/type" \
  -H "Content-Type: application/json" \
  -d "{\"userId\": \"$USER_ID\", \"ref\": \"e2\", \"text\": \"Default\"}"

# Evaluate JavaScript (read-only)
curl -s -X POST "http://localhost:9377/tabs/$TAB_ID/evaluate" \
  -H "Content-Type: application/json" \
  -d "{\"userId\": \"$USER_ID\", \"expression\": \"document.body.innerText\"}"

# Scroll
curl -s -X POST "http://localhost:9377/tabs/$TAB_ID/scroll" \
  -H "Content-Type: application/json" \
  -d "{\"userId\": \"$USER_ID\", \"direction\": \"down\"}"

# Close tab
curl -s -X DELETE "http://localhost:9377/tabs/$TAB_ID?userId=$USER_ID"
```

## Clicking by CSS Selector (when refs don't cover the element)

```bash
curl -s -X POST "http://localhost:9377/tabs/$TAB_ID/click" \
  -H "Content-Type: application/json" \
  -d "{\"userId\": \"$USER_ID\", \"selector\": \"button.submit\"}"
```

## Extracting Hidden/Truncated Values from Aria Snapshots

The accessibility snapshot masks sensitive values (API keys, tokens) — e.g.,
`xai-...39Hl` instead of the full key. To extract the real value, use the
`/evaluate` endpoint with a regex on `document.body.innerText`:

```bash
# Extract API key from page text
curl -s -X POST "http://localhost:9377/tabs/$TAB_ID/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"userId": "rotator", "expression": "document.body.innerText.match(/xai-[a-zA-Z0-9]+/)?.[0] || \"not found\""}'
```

For more complex extraction (all inputs, all text):

```bash
curl -s -X POST "http://localhost:9377/tabs/$TAB_ID/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"userId": "rotator", "expression": "JSON.stringify({innerText: document.body.innerText, inputs: Array.from(document.querySelectorAll(\"input,textarea\")).map(e=>({type:e.type,value:e.value}))})"}'
```

## Select Option from Dropdown (native Playwright selectOption)

For `<select>` elements that require native `change` events (SPAs that ignore
JS-dispatched events), use the `/select` endpoint:

```bash
curl -s -X POST "http://localhost:9377/tabs/$TAB_ID/select" \
  -H "Content-Type: application/json" \
  -d "{\"userId\": \"$USER_ID\", \"selector\": \"select#myDropdown\", \"value\": \"option_value\"}"
```

Also works with refs: `{"userId":"...", "ref":"e5", "value":"opt1"}`.

**When to use**: Amazon's `a-declarative` framework, Angular Material selects,
React-controlled selects. These ignore `element.value = x; dispatchEvent(new
Event('change'))` because the SPA framework listens for native browser events
that only Playwright's `selectOption` can trigger.

**Limitation**: Does NOT work for Amazon's `a-dropdown-select` custom dropdowns
(see `references/amazon-cookie-injection.md` → "Amazon a-declarative Dropdown
Limitation" for workaround).

## When to Use Direct REST vs Hermes Browser Tools

| Situation | Use |
|-----------|-----|
| Cookies injected for custom userId | **Direct REST API** (this guide) |
| Hermes-managed session (no pre-injected cookies) | Hermes browser tools (`browser_navigate` etc.) |
| CSS selector needed, Hermes-managed session | `camoufox click_element` / `fill_element` CLI |
| CSS selector needed, custom userId session | Direct REST `/click` with `selector` field |
