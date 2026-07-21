# Domino's Pizza Ordering with Camoufox

## Overview
Domino's Lieferando menu uses custom `pie-*` elements and has "Free item" promotions that change the modal flow.

## Key Elements
- `pie-radio` — size/option selectors (Classic/Medium/Large, Crust, Sauce)
- `pie-button` — Add to basket button (check `aria-disabled` attribute)
- `pie-icon-button` / `[data-qa=item-action]` — plus button to open item modal
- `pie-chip` — category navigation tabs

## Modal Flow
1. Click plus button to open modal
2. Select required options (size, crust, sauce) via `pie-radio`
3. Scroll to Add button: `scroll_to_element '.ReactModal__Content--after-open pie-button'`
4. Click Add: `click_element '.ReactModal__Content--after-open pie-button:has-text("Add")'`
5. Handle promo popup if it appears (press Escape)

## "Free item" Promotions
Domino's often has "Buy two, get cheapest free" or "Free item with selected orders". These show as "Free item [Product]: 1 Required" in the modal. The Required field is the size selection — it's NOT a separate confirmation. Just select the size and click Add normally.

## Required Fields Detection
```bash
# Check what's required
camoufox eval '(function(){ var m=document.querySelector(".ReactModal__Content--after-open"); if(!m) return "no modal"; var t=m.textContent; var parts=t.split("Required"); return JSON.stringify({reqCount:parts.length-1, context:parts[parts.length-1]?.slice(0,60)}); })()'
```

## Custom Element Clicking
`click_element` with `has-text()` works for `pie-radio` and `pie-button`:
```bash
camoufox click_element '.ReactModal__Content--after-open pie-radio:has-text("Medium (28cm)")' 10000 true
camoufox click_element '.ReactModal__Content--after-open pie-button:has-text("Add")' 10000 true
```

If `has-text()` times out, the element might not be visible. Use `scroll_to_element` first.

## Disabled Add Button
Check if Add button is disabled:
```bash
camoufox eval '(function(){ var m=document.querySelector(".ReactModal__Content--after-open"); if(!m) return "no modal"; var b=m.querySelector("pie-button"); return JSON.stringify({text:b?.textContent?.trim(), disabled:b?.hasAttribute("disabled")}); })()'
```

If disabled, a required field is not selected. Check for "Required" text in modal.

## Basket Sidebar
Basket content is in `[class*=sidebar-style]` elements:
```bash
camoufox eval '(function(){ var sidebar=document.querySelector("[class*=sidebar-style]"); if(!sidebar) return "no sidebar"; var t=sidebar.textContent?.trim(); var checkout=t.match(/Checkout\s*\(?([^)]+)\)?/i)?.[0]; return JSON.stringify({checkout:checkout, snippet:t.slice(0,300)}); })()'
```

## Checkout Button
Checkout button is a DIV, not a button:
```bash
camoufox eval '(function(){ var all=document.querySelectorAll("*"); for(var el of all){ var t=el.textContent?.trim(); if(t && t.match(/Checkout/) && t.match(/\d/) && t.length<40){ var r=el.getBoundingClientRect(); if(r.y>0) return JSON.stringify({x:Math.round(r.x+r.width/2), y:Math.round(r.y+r.height/2)}); } } return "not found"; })()'
```

## Network Failures
If `Page.goto: NS_ERROR_CONNECTION_REFUSED`:
1. Kill Camoufox: `pkill -9 -f camoufox_server; pkill -9 -f Camoufox; rm -f /tmp/camoufox_cli.sock`
2. Wait 5 seconds
3. Restart: `env -u PYTHONPATH ~/.hermes/.venv/bin/python3.12 ~/.hermes/scripts/camoufox_server.py`
4. Reload cookies: `camoufox load_cookies /tmp/lieferando_giuli_cookies.json`

## Cookie Refresh
If `je-at` token expired (checkout redirects to login):
1. Kill Firefox: `pkill -f firefox; sleep 3`
2. Copy cookies: `cp "$PROFILE/cookies.sqlite" /tmp/ff_giuli_fresh.sqlite`
3. Extract with Python script (see main camoufox skill)
4. Load into Camoufox: `camoufox load_cookies /tmp/lieferando_giuli_cookies.json`

## Hermes Browser Tools Patterns (2026-07-17)

When using Hermes browser tools (`browser_click`, `browser_snapshot`, etc.) instead of the CLI:

### Opening item modal
Click the "Add X to the basket" button ref from `browser_snapshot`:
```
browser_click(ref="@e56")  # "Add Salami to the basket"
```

### Selecting size in configurator
The modal shows `[role="radio"]` elements. The outer radio wrapper ref works:
```
# Click Classic (25cm) radio
browser_click(ref="@e2")  # outer radio wrapper
# Verify via snapshot: should show [checked]
```

### Selecting crust and sauce (required fields)
After size selection, additional sections (Crust, Sauce) appear dynamically. Use `browser_console` to click by text when refs are ambiguous:
```python
# Crust: Klassisch
browser_console(expression='''
(() => {
  const radios = document.querySelectorAll('[role="radio"]');
  for (const r of radios) {
    const label = r.getAttribute('aria-label') || r.textContent || '';
    if (label.includes('Klassisch') && label.includes('Crust')) {
      r.click();
      return 'clicked Crust Klassisch';
    }
  }
  return 'not found';
})()
''')

# Sauce: Tomatensauce (Vegan)
browser_console(expression='''
(() => {
  const radios = document.querySelectorAll('[role="radio"]');
  for (const r of radios) {
    const label = r.getAttribute('aria-label') || r.textContent || '';
    if (label.includes('Tomatensauce') && label.includes('Vegan')) {
      r.click();
      return 'clicked Tomatensauce';
    }
  }
  return 'not found';
})()
''')
```

### Clicking Add button
After all required fields selected, the Add button activates (no longer `[disabled]`):
```
browser_click(ref="@e38")  # "Add 11,99 €"
```

### Handling "Free Item" promo modal
After first item add, a promo dialog appears:
```
browser_click(ref="@e5")  # "No, thanks" button
```

### Scrolling to vegan category
To reach "Pizza - Vegan" category:
```
browser_console(expression='''
(() => {
  const catButtons = document.querySelectorAll('button');
  for (const cb of catButtons) {
    if (cb.textContent === 'Pizza - Vegan') {
      cb.click();
      return 'clicked Pizza - Vegan category';
    }
  }
  return 'not found';
})()
''')
```

### Key differences from CLI approach
- **No `.ReactModal__Content--after-open` scoping needed**: Hermes browser tools snapshot only shows modal content when a dialog is open, so refs are already scoped to the modal.
- **`browser_press` for keyboard input**: Use individual key presses for React comboboxes (see `references/lieferando-address-input.md`).
- **`browser_console` for JS clicks**: When refs don't work for custom elements, fall back to `document.querySelectorAll('[role="radio"]')` + `.click()`.
- **`browser_snapshot` after EVERY action**: Verify state changes before proceeding.

## REST API Persistent Tab Pattern (2026-07-17)

When doing multi-step Domino's ordering (address → menu → items → basket → voucher → checkout), use the direct REST API with a persistent `userId` + `sessionKey` instead of Hermes browser tools. Hermes `browser_navigate` creates a NEW tab each time, losing the address and basket state.

### Creating a persistent tab
```bash
TAB_ID=$(curl -s -X POST http://localhost:9377/tabs \
  -H "Content-Type: application/json" \
  -d '{"userId":"agent1","sessionKey":"lieferando","url":"https://www.lieferando.de/de"}' \
  | python3 -c "import json,sys; print(json.load(sys.stdin).get('tabId',''))")
echo "$TAB_ID" > /tmp/camofox_tab_id
TAB=$(cat /tmp/camofox_tab_id)
```

### All subsequent ops use curl with the saved tab ID
```bash
# Navigate
curl -s -X POST "http://localhost:9377/tabs/$TAB/navigate" \
  -H "Content-Type: application/json" \
  -d '{"userId":"agent1","url":"https://www.lieferando.de/en/menu/dominos-pizza-teltow-potsdamer-strasse-1?c_id=019d4437-1963-7430-9767-1389d59998f5"}'

# Snapshot (get refs)
curl -s "http://localhost:9377/tabs/$TAB/snapshot?userId=agent1"

# Click by ref
curl -s -X POST "http://localhost:9377/tabs/$TAB/click" \
  -H "Content-Type: application/json" \
  -d '{"userId":"agent1","ref":"e57"}'

# Click by CSS selector
curl -s -X POST "http://localhost:9377/tabs/$TAB/click" \
  -H "Content-Type: application/json" \
  -d '{"userId":"agent1","selector":"button[aria-label=\"Add Salami to the basket\"]"}'

# Type into element by ref
curl -s -X POST "http://localhost:9377/tabs/$TAB/type" \
  -H "Content-Type: application/json" \
  -d '{"userId":"agent1","selector":"input[aria-label=\"Search for location\"]","text":"<STREET>"}'

# Evaluate JS (for SPA buttons that don't respond to Playwright click)
curl -s -X POST "http://localhost:9377/tabs/$TAB/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"userId":"agent1","expression":"(() => { const btns = document.querySelectorAll(\"button\"); for(const b of btns) { const t = b.textContent||\"\"; if(t.includes(\"Add 11,99\") && !b.disabled) { b.click(); return \"clicked\"; } } return \"not found\"; })()"}'

# Scroll
curl -s -X POST "http://localhost:9377/tabs/$TAB/scroll" \
  -H "Content-Type: application/json" \
  -d '{"userId":"agent1","direction":"down","amount":5000}'

# Check if tab still alive
curl -s "http://localhost:9377/tabs?userId=agent1"
# If tabs: [] → session lost, must recreate + re-enter address
```

### Key insight: `browser_click(ref)` returns `{"ok":true}` but item NOT added
The Domino's modal "Add" button (`pie-button` / React button) does NOT respond to Playwright native click via Hermes browser tools. The click returns success but the React onClick handler doesn't fire. **Fix**: Use the REST `evaluate` endpoint with JS `document.querySelectorAll('button')` + filter by text + `.click()`:
```bash
curl -s -X POST "http://localhost:9377/tabs/$TAB/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"userId":"agent1","expression":"(() => { const btns = document.querySelectorAll(\"button\"); for(const b of btns) { const t = b.textContent||\"\"; if(t.includes(\"Add 11,99\") && !b.disabled) { b.click(); return \"clicked: \"+t; } } return \"not found or disabled\"; })()"}'
```

If that returns "not found or disabled", the required radio fields (Size, Crust, Sauce) were not properly selected. Re-select them via `evaluate`:
```bash
# Select Classic size
curl -s -X POST "http://localhost:9377/tabs/$TAB/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"userId":"agent1","expression":"(() => { const radios = document.querySelectorAll(\"[role=\\\"radio\\\"]\"); for(const r of radios) { const t = r.textContent||\"\"; if(t.includes(\"Classic\") && t.includes(\"25cm\")) { r.click(); return \"clicked Classic\"; } } return \"not found\"; })()"}'

# Select Crust: Klassisch
curl -s -X POST "http://localhost:9377/tabs/$TAB/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"userId":"agent1","expression":"(() => { const radios = document.querySelectorAll(\"[role=\\\"radio\\\"]\"); for(const r of radios) { const t = r.textContent||\"\"; if(t.includes(\"Klassisch\") && t.includes(\"Crust\")) { r.click(); return \"clicked Klassisch\"; } } return \"not found\"; })()"}'

# Select Sauce: Tomatensauce (Vegan)
curl -s -X POST "http://localhost:9377/tabs/$TAB/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"userId":"agent1","expression":"(() => { const radios = document.querySelectorAll(\"[role=\\\"radio\\\"]\"); for(const r of radios) { const t = r.textContent||\"\"; if(t.includes(\"Tomatensauce\") && t.includes(\"Vegan\")) { r.click(); return \"clicked Tomatensauce\"; } } return \"not found\"; })()"}'

# Now click Add
curl -s -X POST "http://localhost:9377/tabs/$TAB/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"userId":"agent1","expression":"(() => { const btns = document.querySelectorAll(\"button\"); for(const b of btns) { const t = b.textContent||\"\"; if(t.includes(\"Add 11,99\") && !b.disabled) { b.click(); return \"clicked: \"+t; } } return \"not found or disabled\"; })()"}'
```

## Pitfalls
- **Promo popups block Add**: After clicking Add, a "Nice! You get this free..." popup may appear. Press Escape immediately.
- **Modal closes on radio click**: Sometimes clicking `pie-radio` closes the modal. Re-open and try again.
- **Multiple items same type**: Adding the same item twice shows quantity (e.g., "Vegan Chicken Döner x3"). Use minus button to reduce.
- **Free item not in basket**: "Free item" promotions add the item automatically at checkout — don't try to add it manually.
- **Network timeouts**: Camoufox can lose network connection. Restart fixes it.
- **Pizza - Vegan items not loaded until scrolled**: The "Pizza - Vegan" category section shows "4 items" but the actual menu items (Vegan Chicken Döner, Las Vega, Vegayaki) are NOT in the DOM until you either click the category button OR scroll to that section. Use `browser_console` to click the category tab, then `browser_snapshot` to see the item buttons.
