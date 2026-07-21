# Ryanair Angular Airport Picker Pattern

## Discovery (2026-06-28)

Ryanair's search form uses an **Angular SPA** (not React) with a country/airport
selection overlay — NOT a text typeahead. This means:

- `page.fill()`, `page.type()`, `keyboard.type()`, `press_sequentially()` ALL fail
- The native value setter + event dispatch sets the value but Angular's change
  detection doesn't fire
- `document.execCommand('insertText')` also fails
- This is NOT a headless bug — same behavior in GUI mode (`headless=False`)

## The Actual Pattern

Ryanair's airport input opens a **full-screen overlay** with:
- **Left side**: Country list ("Abflugland")
- **Right side**: Airport list for selected country ("Flughafen wählen")

No `role="option"` elements. Countries and airports are plain `span`/`div` elements.

**CORRECTION (2026-06-28 interactive session)**: "Valencia" IS listed as a separate
airport in the Spanish airport list — NOT just "Castellon (Valencia)". The full
Spanish airport list includes: Alicante, Almeria, Barcelona, Castellon (Valencia),
Fuerteventura, Gran Canaria, Ibiza, Lanzarote, Madrid, Malaga, Menorca, Murcia,
Palma de Mallorca, Santander, Santiago, Saragossa, Sevilla, Teneriffa Sud,
**Valencia (Alle Flughäfen)**, **Valencia**, Vitoria. Select "Valencia" (not
"Castellon (Valencia)") for the actual VLC airport.

## Working Code

```python
from camoufox.sync_api import Camoufox
from camoufox.addons import DefaultAddons
import time

browser = Camoufox(
    headless=True,
    locale="de-DE",
    exclude_addons=[DefaultAddons.UBO],
).__enter__()
ctx = browser.new_context(viewport={"width": 1366, "height": 900})
page = ctx.new_page()
page.on("pageerror", lambda e: None)

def rm_cookie():
    """Remove cookie popup. MUST be called before every click."""
    page.evaluate(
        '() => { document.querySelectorAll('
        '"[id*=cookie], [class*=cookie-popup], [class*=overlay]"'
        ').forEach(e => e.remove()); }'
    )
    time.sleep(0.5)

def find_click(text, exclude=None, exact=False):
    """Find element by text and click with force=True."""
    rm_cookie()
    el = page.query_selector(f'span:has-text("{text}")')
    if not el:
        el = page.query_selector(f'button:has-text("{text}")')
    if not el:
        for e in page.query_selector_all('span, div, button, a, li'):
            try:
                t = e.inner_text().strip()
                if exclude and exclude.lower() in t.lower():
                    continue
                if (exact and t == text) or (
                    not exact and text in t and len(t) < 50
                ):
                    el = e
                    break
            except:
                pass
    if el:
        el.click(force=True)
        return True
    return False

# 1. Load
page.goto("https://www.ryanair.com/de/de", wait_until="domcontentloaded", timeout=30000)
time.sleep(8)

# 2. One-way
rm_cookie()
oneway = page.query_selector('span:has-text("Nur Hinflug")')
if oneway:
    oneway.click(force=True)
    time.sleep(1)

# 3. Origin: click input → picker opens
rm_cookie()
origin = page.query_selector('#input-button__departure')
if origin:
    origin.click(force=True)
    time.sleep(2)

# 4. Select country
find_click("Spanien", exact=True)
time.sleep(2)

# 5. Select airport — use exclude to avoid "Castellon (Valencia)"
find_click("Valencia", exclude="Castellon")
time.sleep(2)

# 6. Destination: click input → picker opens
rm_cookie()
dest = page.query_selector('#input-button__arrival')
if dest:
    dest.click(force=True)
    time.sleep(2)

# 7. Select country
find_click("Deutschland", exact=True)
time.sleep(2)

# 8. Select airport
find_click("Berlin Brandenburg", exact=False)
time.sleep(2)

# 9. Date: click date field → calendar opens
rm_cookie()
date_el = page.query_selector('[data-ref="input-button__dates-from"]')
if date_el:
    date_el.click(force=True)
    time.sleep(2)
    # Click day 25 in calendar — but see pitfall #8 below
    day = page.query_selector('td:has-text("25"), [class*="day"]:has-text("25")')
    if day:
        day.click(force=True)
        time.sleep(1)
    # NOTE: date may not be confirmed — see pitfall #8
```

## Full Ryanair Booking Flow (VERIFIED 2026-06-28 via browser_repl.py)

Complete step-by-step flow from homepage to fare selection:

```
# 1. Remove cookie popup (MUST do before every click)
eval document.querySelector('.cookie-popup-with-overlay')?.remove()

# 2. One-way
clicktext Nur Hinflug

# 3. Open origin picker
click [data-ref="input-button__display-value"] !force

# 4. Select country
clicktext Spanien

# 5. Select airport (JS to filter exact match)
eval Array.from(document.querySelectorAll('[data-ref="airport-item__name"]')).find(e => e.textContent.trim() === 'Valencia').click()

# 6. Open destination picker
eval document.querySelectorAll('[data-ref="input-button__display-value"]')[1].click()

# 7. Select country
clicktext Deutschland

# 8. Select airport
clicktext Berlin Brandenburg

# 9. Remove cookie popup again
eval document.querySelector('.cookie-popup-with-overlay')?.remove()

# 10. Open date picker (dispatchEvent, not force-click)
eval document.querySelector('[data-ref="input-button__dates-from"]').dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}))

# 11. Wait for calendar
wait 2

# 12. Click day 25 (filter out disabled cells for wrong month)
eval Array.from(document.querySelectorAll('div.calendar-body__cell')).filter(e => e.textContent.trim() === '25' && !e.className.includes('disabled'))[0].dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}))

# 13. Verify date set
eval document.querySelector('[data-ref="input-button__dates-from"]').textContent.trim()
# Expected: "Abflug  Sa., 25 Juli"

# 14. Remove cookie popup
eval document.querySelector('.cookie-popup-with-overlay')?.remove()

# 15. Click search
click [data-ref="flight-search-widget__cta"] !force

# 16. Wait for results
wait 10

# 17. Select cheapest flight
eval document.querySelector('flight-card-new')?.querySelector('button')?.click()

# 18. Wait for fare options
wait 3

# 19. Select Basic fare
eval Array.from(document.querySelectorAll('button.fare-tile__btn')).find(b => b.textContent.includes('Basic')).click()

# 20. Now on passenger details page — email input visible
```

## Key Selectors Reference

| Element | Selector |
|---------|----------|
| One-way radio | `span:has-text("Nur Hinflug")` (via clicktext) |
| Origin input | `[data-ref="input-button__display-value"]` (first) or `#input-button__departure` |
| Destination input | `[data-ref="input-button__display-value"]` (second) or `#input-button__arrival` |
| Country name | `[data-ref="country__name"]` (span inside country list) |
| Airport name | `[data-ref="airport-item__name"]` (span inside airport list) |
| Date field | `[data-ref="input-button__dates-from"]` |
| Calendar day | `div.calendar-body__cell` (text = day number, class includes `--disabled` or `--weekend`) |
| Search button | `[data-ref="flight-search-widget__cta"]` |
| Flight card | `flight-card-new` (custom Angular element) |
| Fare button | `button.fare-tile__btn` (text includes "Basic" / "Plus" / "Flexi Plus") |
| Cookie popup | `.cookie-popup-with-overlay` (z-index 999999, must remove before every click) |

1. **Cookie popup reappears**: Ryanair's `cookie-popup-with-overlay` div intercepts
   ALL pointer events. Must `rm_cookie()` before EVERY click. The popup reappears
   after some Angular state changes.

2. **No `role="option"` elements**: The overlay uses plain `span`/`div` elements.
   `page.query_selector_all('[role="option"]')` returns 0. Must search by text content.

3. **`force=True` required on all clicks**: Even after cookie removal, some Angular
   overlay remnants may intercept clicks. Always use `force=True`.

4. **Sync API, not async**: The async API (`AsyncCamoufox`) with `geoip=True` and
   `locale=['de-DE','en-US']` hangs indefinitely on `page.goto()`. Use sync API
   (`Camoufox`) with `locale="de-DE"` (string, not list).

5. **Valencia IS in the airport list** (corrected 2026-06-28): The Spanish airport
   list contains both "Castellon (Valencia)" and "Valencia" as separate entries.
   Use `find_click("Valencia", exclude="Castellon")` to select the correct one.

6. **Ryanair availability API returns 409**: `GET /api/booking/v4/de-de/availability`
   returns `{"message":"Availability declined"}` even with session cookies. The
   fare-finder API (`/api/farfnd/v4/oneWayFares`) works for prices only, no booking.

7. **Date picker RESOLVED (2026-06-28)**: Calendar days are `div.calendar-body__cell`
   with day number as textContent. Multiple cells with same number exist (different months)
   — filter out disabled ones via `className.includes('disabled')`.

   **Opening the calendar**: `page.evaluate` with `dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}))`
   on `[data-ref="input-button__dates-from"]`. Playwright `element.click(force=True)` opens the
   calendar but Angular's state doesn't fully initialize. JS `dispatchEvent` triggers Angular's
   own click handler properly.

   **Selecting a day**: Once calendar is open (verify with `document.querySelectorAll('div.calendar-body__cell').length` —
   should be ~42-63), find the correct day and dispatchEvent click:
   ```javascript
   Array.from(document.querySelectorAll('div.calendar-body__cell'))
     .filter(e => e.textContent.trim() === '25' && !e.className.includes('disabled'))[0]
     .dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}))
   ```

   After selection, verify via `document.querySelector('[data-ref="input-button__dates-from"]').textContent.trim()` —
   should show e.g. "Abflug  Sa., 25 Juli" instead of "Abflug  Datum auswählen".

8. **Interactive debugging approach (MANDATORY)**: When browser automation fails
   on a new site, do NOT run blind batch scripts that try multiple approaches.
   Instead: perform ONE action → screenshot → analyze with `vision_analyze` →
   dump DOM state → adjust next action based on what vision sees. The user
   expects step-by-step visual feedback at each step.

## Interactive Debugging via PTY REPL

For step-by-step browser automation debugging, use a persistent Python REPL
via `terminal(pty=true, background=true)`:

```python
# Start persistent Camoufox session
# terminal: cd ~/projects/travel-bot && .venv/bin/python -i -u -c '
#   from camoufox.sync_api import Camoufox
#   from camoufox.addons import DefaultAddons
#   browser = Camoufox(headless=False, ...).__enter__()
#   page = browser.new_context().new_page()
#   print("ready")
# '

# Then interact step by step:
# process(action='submit', data='page.goto("https://..."); time.sleep(5)')
# process(action='submit', data='page.screenshot(path="/tmp/step.png")')
# vision_analyze(image_url='/tmp/step.png', question='What is visible?')
# process(action='submit', data='el = page.query_selector("#id"); el.click()')
```

This keeps the browser alive between commands, lets you screenshot + analyze
after each action, and adjust based on what vision sees.
