# Ryanair SPA Selector Catalog (Angular, tested 2026-06-28)

Ryanair is an Angular SPA, NOT React. No typeahead input — uses a country/airport picker overlay.

## Search Form

| Element | Selector | Method |
|---------|----------|--------|
| One-way radio | `span:has-text("Nur Hinflug")` | clicktext |
| Origin field | `[data-ref="input-button__display-value"]` | click !force |
| Origin input (actual) | `#input-button__departure` | — read only |
| Destination field | `document.querySelectorAll('[data-ref="input-button__display-value"]')[1]` | eval .click() |
| Date field | `[data-ref="input-button__dates-from"]` | eval dispatchEvent(click) |
| Calendar day | `div.calendar-body__cell` (filter by text + not disabled) | eval dispatchEvent(click) |
| Search button | `[data-ref="flight-search-widget__cta"]` | click !force |

## Country/Airport Picker

After clicking origin/destination field, a 2-panel overlay appears:
- Left: countries as `[data-ref="country__name"]` span elements
- Right: airports as `[data-ref="airport-item__name"]` span elements
- Also: `[data-ref="airport-item__mac-name"]` for metro area (e.g. "Barcelona (Alle Flughäfen)")

Select country: `clicktext Spanien`
Select airport: `eval Array.from(document.querySelectorAll('[data-ref="airport-item__name"]')).find(e => e.textContent.trim() === 'Valencia').click()`

**Note**: "Valencia" and "Castellon (Valencia)" are separate entries. Filter by exact match.

## Flight Results Page (/trip/flights/select)

| Element | Selector | Method |
|---------|----------|--------|
| Flight card | `flight-card-new` | custom Angular element |
| Select button | `flight-card-new button.flight-card-summary__select-btn` | eval dispatchEvent(click) |
| Basic fare button | `.fare-footer__submit-btn` (text: "Mit dem Basic Flugpreis fortfahren") | click !force |
| Continue button | `.continue-flow__button` (text: "Fortsetzen") | click (non-force when no overlay) |

## Passenger Form

| Element | Selector | Notes |
|---------|----------|-------|
| First name | `input[name="form.passengers.ADT-0.name"]` | Angular reactive form |
| Last name | `input[name="form.passengers.ADT-0.surname"]` | Angular reactive form |
| Email | `input[type="email"]` | — |
| Terms checkbox | `input[type="checkbox"]` | — |

**Angular reactive forms issue**: `fill()` sets values but Angular keeps form `pristine`/`untouched`.
The "Fortsetzen" button stays `disabled`. Need real keyboard events to mark fields as `dirty`/`touched`.
`page.keyboard.type()` does NOT work in Camoufox (Firefox). `press_sequentially()` not yet tested.

## Overlays to Remove Before Clicks

Three overlay types intercept pointer events:
1. `.cookie-popup-with-overlay` — first-party cookie consent (uBO can't block)
2. `ry-session-expiration-popup` — session timeout warning
3. `div.overlay` — generic modal backdrop

```js
document.querySelector('.cookie-popup-with-overlay')?.remove();
document.querySelector('ry-session-expiration-popup')?.remove();
document.querySelector('flights-lazy-session-expiration-popup')?.remove();
document.querySelector('div.overlay')?.remove();
```

## Camoufox Config

```python
# WORKS
Camoufox(headless=False, exclude_addons=[DefaultAddons.UBO], humanize=True)

# FAILS — causes hangs on Ryanair SPA
Camoufox(headless=False, exclude_addons=[DefaultAddons.UBO], geoip=True, locale=['de-DE', 'en-US'], humanize=True)
```

- `geoip=True` → hangs page.goto
- `locale=['de-DE', 'en-US']` (list) → hangs
- `locale="de-DE"` (string) → OK but not needed with humanize=True
- `wait_until="networkidle"` → hangs (SPA never goes idle)
- `wait_until="domcontentloaded"` → works
- Route blocking (`page.route`) with `BLOCK_SUBSTR` → works for third-party scripts only

## Verified Flow (2026-06-28)

1. `clean` — remove cookie popup
2. `clicktext Nur Hinflug` — verified: `ry-radio-circle-button--checked`
3. `click [data-ref="input-button__display-value"] !force` — 36 countries shown
4. `clicktext Spanien` — 22 airports shown
5. `eval ...find(Valencia).click()` — verified: `value: "Valencia"`
6. `eval ...display-value')[1].click()` — destination picker opens
7. `clicktext Deutschland` → `clicktext Berlin Brandenburg` — verified: `value: "Berlin Brandenburg"`
8. `clean` → `eval ...dates-from...dispatchEvent(click)` — 63 calendar cells
9. `eval ...calendar-body__cell...filter(25,!disabled)...dispatchEvent(click)` — verified: `"Abflug  Sa., 25 Juli"`
10. `clean` → `click [data-ref="flight-search-widget__cta"] !force` — URL = `/trip/flights/select`
11. `wait 8` → `eval ...select-btn...dispatchEvent(click)` — flight card expands
12. `clean` → remove overlays → `click .fare-footer__submit-btn !force` — passenger form appears
13. `fill` name/surname/email — values set but Fortsetzen button stays disabled (Angular reactive forms)
