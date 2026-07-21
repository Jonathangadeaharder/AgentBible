# Lieferando Address Setting via Hermes Browser Tools

## Problem
Lieferando's address search is a React-controlled combobox that does not respond to:
- `browser_type(ref, text)` — returns 500 error on combobox elements
- `browser_console` setting `input.value = "..."` — React's onChange never fires, autocomplete never appears
- `fill()` via REST API — same issue, React state not updated

## Solution: Character-by-character keyboard input

### Step 1: Focus the input
```python
# Via browser_console
browser_console(expression='''
(() => {
  const input = document.querySelector('input[aria-label="Search for location"]');
  if (!input) return 'not found';
  input.focus();
  return 'focused';
})()
''')
```

### Step 2: Type each character via browser_press
```
browser_press(key="S")
browser_press(key="t")
browser_press(key="r")
browser_press(key="i")
browser_press(key="e")
browser_press(key="w")
browser_press(key="i")
browser_press(key="t")
browser_press(key="z")
browser_press(key="w")
browser_press(key="e")
browser_press(key="g")
```

### Step 3: Wait for autocomplete, then select option
```python
# Via browser_console — check options appeared
browser_console(expression='''
(() => {
  const options = document.querySelectorAll('[role="option"]');
  return {
    count: options.length,
    labels: Array.from(options).map(o => o.textContent?.substring(0, 100))
  };
})()
''')

# Click the correct option (e.g., index 1 = "<STREET>, <CITY>, Germany")
browser_console(expression='''
(() => {
  const options = document.querySelectorAll('[role="option"]');
  if (options.length >= 2) {
    options[1].click();
    return 'clicked <CITY> option';
  }
  return 'no options';
})()
''')
```

### Step 4: Handle "Enter building number" prompt
After selecting the street, Lieferando shows a "Help us find you" dialog asking for the building number.

```python
# Focus the building number input
browser_console(expression='''
(() => {
  const input = document.querySelector('input[placeholder*="building"]');
  if (!input) return 'not found';
  input.focus();
  return 'focused';
})()
''')

# Type house number
browser_press(key="5")
browser_press(key="4")

# Click "Confirm address" button
browser_console(expression='''
(() => {
  const btn = Array.from(document.querySelectorAll('button')).find(
    b => b.textContent.includes('Confirm address')
  );
  if (btn) { btn.click(); return 'clicked'; }
  return 'not found';
})()
''')
```

### Step 5: Verify address is set
```python
# Check URL changed to delivery area page
browser_console(expression="window.location.href")
# Should be: https://www.lieferando.de/en/delivery/food/<PLZ>
```

### Step 6: Navigate to restaurant
Once address is set, navigate to the delivery area page and click a restaurant from the list:
```
browser_navigate(url="https://www.lieferando.de/en/delivery/food/<PLZ>")
# Then browser_snapshot to see restaurant list with refs
# Click restaurant link: browser_click(ref="@e37") etc.
```

**CRITICAL**: Direct restaurant URLs (e.g., `/de/restaurant/dominos-pizza-berlin-stahnsdorf`) redirect to homepage if address not set in current session. Always set address first, then navigate via the restaurant list page.

## Why keyboard input works but fill() doesn't

React's controlled inputs use `onChange` handlers that listen for `InputEvent` (fired by real keyboard input). `fill()` and `value=` assignment only dispatch a generic `Event('input')` which React's synthetic event system may not pick up. `browser_press` sends real keyboard events through Playwright's `page.keyboard.press()`, which produces `InputEvent` with `isTrusted=true` — React processes these correctly.

## Cookie banner handling
If the cookie consent banner is present, dismiss it FIRST before any interaction:
```
# Click "Accept all" or "Necessary only" button
browser_console(expression='''
(() => {
  const btns = Array.from(document.querySelectorAll('button'));
  for (const btn of btns) {
    if (btn.textContent.includes('Alle akzeptieren') || btn.textContent.includes('Accept all')) {
      btn.click();
      return 'accepted';
    }
  }
  for (const btn of btns) {
    if (btn.textContent.includes('Nur notwendige') || btn.textContent.includes('Necessary only')) {
      btn.click();
      return 'necessary';
    }
  }
  return 'no banner';
})()
''')
```

## Verified
2026-07-17 — Address "<ADDRESS>, <PLZ> <CITY>" successfully set via keyboard input. Delivery area page loaded with 95 restaurants. Domino's menu accessible.
