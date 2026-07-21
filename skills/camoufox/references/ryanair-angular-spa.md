# Ryanair Angular SPA — Browser Automation Reference

## Architecture

Ryanair uses Angular (not React). Key differences from React sites:
- Custom elements: `flight-card-new`, `ry-radio-button`, `ry-price`
- `data-ref` attributes for element identification (NOT `data-testid`)
- `ng-star-inserted` class on dynamically added elements
- Event handlers may ignore native `.click()` — use `dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}))`

## Cookie Popup

Ryanair's cookie consent is a FIRST-PARTY element: `.cookie-popup-with-overlay` with z-index 999999. uBO cannot block it. Must remove via JS:
```js
document.querySelector('.cookie-popup-with-overlay')?.remove()
```
The popup reappears after navigation. Run `clean` in the REPL before every click action.

## Search Form — Country/Airport Picker (NOT Typeahead)

Ryanair's search form does NOT have a text typeahead. It's a structured picker overlay:

1. **Origin field**: `#input-button__departure` or `[data-ref="input-button__display-value"]`
   - Click opens country list (36 countries): `[data-ref="country__name"]`
   - Click country → airport list appears: `[data-ref="airport-item__name"]`
   - Click airport to select

2. **Destination field**: second `[data-ref="input-button__display-value"]` element
   - Same flow as origin

3. **Important**: "Valencia" and "Castellon (Valencia)" are SEPARATE airports. Filter by exact match:
   ```js
   Array.from(document.querySelectorAll('[data-ref="airport-item__name"]'))
     .find(e => e.textContent.trim() === 'Valencia').click()
   ```

## Date Picker

- Date field: `[data-ref="input-button__dates-from"]`
- Opens via `dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}))` — NOT via `.click()` or Playwright click
- Calendar days: `div.calendar-body__cell` with text content = day number
- Disabled days have class `calendar-body__cell--disabled`
- Two months visible (e.g., June + July). Select non-disabled day:
  ```js
  Array.from(document.querySelectorAll('div.calendar-body__cell'))
    .filter(e => e.textContent.trim() === '25' && !e.className.includes('disabled'))[0]
    .dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}))
  ```

## Search Submission

- Search button: `[data-ref="flight-search-widget__cta"]`
- Use `!force` in REPL: `click [data-ref="flight-search-widget__cta"] !force`
- After search: URL changes to `/trip/flights/select?...`

## Flight Selection

- Flight cards: `flight-card-new` custom element
- Select button: `button.flight-card-summary__select-btn`
- After selecting flight, fare tiles appear with buttons:
  - "Mit dem Basic Flugpreis fortfahren" (Basic fare)
  - "Zum Regular Tarif wechseln" (Regular fare)

## Post-Fare Selection

After selecting Basic fare, Ryanair shows:
1. Email input (`input[type="email"]`) — for login/express checkout
2. Login prompt with "Später einloggen" (Login later) and "Fortsetzen" (Continue) buttons
3. Checkbox for terms acceptance

**Known issue**: JS `dispatchEvent(click)` on "Fortsetzen" may not trigger Angular routing. Try Playwright `clicktext Fortsetzen` or `click button !force` instead.

## Working REPL Sequence (verified 2026-06-28)

```
clean
clicktext Nur Hinflug
click [data-ref="input-button__display-value"] !force
clicktext Spanien
eval Array.from(document.querySelectorAll('[data-ref="airport-item__name"]')).find(e => e.textContent.trim() === 'Valencia').click()
eval document.querySelectorAll('[data-ref="input-button__display-value"]')[1].click()
clicktext Deutschland
clicktext Berlin Brandenburg
clean
eval document.querySelector('[data-ref="input-button__dates-from"]').dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}))
eval Array.from(document.querySelectorAll('div.calendar-body__cell')).filter(e => e.textContent.trim() === '25' && !e.className.includes('disabled'))[0].dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}))
clean
click [data-ref="flight-search-widget__cta"] !force
# Wait for results page
eval document.querySelector('flight-card-new button.flight-card-summary__select-btn').dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}))
# Wait for fare tiles
eval Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Basic')).click()
```

## What Does NOT Work

- `page.fill()` — times out (Angular input not recognized as editable by Playwright)
- `page.type(selector, text)` — times out (same reason)
- `element.type(text)` — runs but Angular typeahead never fires (there IS no typeahead)
- `page.keyboard.type(text)` — types but Angular doesn't register value change
- Native value setter + event dispatch — sets value but no autocomplete (wrong assumption — picker, not typeahead)
- uBO enterprise policies (`3rdparty.Extensions.uBlock0`) — cannot block first-party cookie popups
- Route interception — only blocks third-party scripts, not first-party DOM elements
