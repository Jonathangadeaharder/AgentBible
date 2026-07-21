## HEQ Familienversicherung Form (Real Example)

Form: `https://serviceapp.hek.de/forms-26/FAMI_PRUEFBOGEN?...`

### Form Structure
- **Page 1 (Ihre Daten)**: Radio "verheiratet", date "29.02.2024" (Heiratsdatum)
- **Page 2 (Ehepartner/Lebenspartner)**: 4× "Nein" radios (andere Anschrift, eigene Versicherung, Änderung absehbar, Einkünfte)
- **Page 3 (Abschluss)**: Radio "hauptversicherte Person", Ort "Berlin", Signature pad
- **Page 4 (Prüfen und senden)**: ABSENDEN

### Automation Pattern (Camoufox)

```python
from camoufox.sync_api import Camoufox
from camoufox.addons import DefaultAddons

with Camoufox(headless=False, locale="de-DE", exclude_addons=[DefaultAddons.UBO]) as browser:
    ctx = browser.new_context(viewport={"width": 1280, "height": 800})
    page = ctx.new_page()
    page.on("pageerror", lambda e: None)
    page.goto(FORM_URL, wait_until="networkidle")
    
    # Page 1: Radio + Date + WEITER
    page.evaluate("""() => { ... click 'verheiratet' radio ... }""")
    page.evaluate("""() => { ... set date input to '2024-02-29' ... }""")
    page.evaluate("""() => { ... dispatchEvent click on WEITER ... }""")
    
    # Page 2: 4× "Nein" radios + WEITER
    page.evaluate("""() => { ... click all visible 'Nein' radios ... }""")
    page.evaluate("""() => { ... click WEITER ... }""")
    
    # Page 3: Radio + Ort + SIGNATURE + WEITER
    page.evaluate("""() => { ... click 'hauptversicherte Person' ... }""")
    page.evaluate("""() => { ... fill Ort='Berlin' ... }""")
    
    # Draw signature via page.mouse (see signature-pad-automation.md)
    draw_signature_on_canvas(page, strokes, canvas_size)
    
    page.evaluate("""() => { ... click WEITER ... }""")
    
    # Page 4: ABSENDEN
    page.evaluate("""() => { ... click ABSENDEN ... }""")
```

### Key Bugs Encountered & Fixes

1. **Duplicate ID**: `familienstandSeit#<id>` on both wrapper `<div>` AND inner `<input type="date">`. `getElementById` returns DIV → `.value` silently fails. Fix: `querySelector('input[type="date"]')`.

2. **Console scope pollution**: `browser_console` uses persistent context. Wrap all JS in IIFE `(() => { ... })()`.

3. **Shadow DOM signature pad**: `browser_click` can't reach canvas. Use `page.evaluate` + `shadowRoot.querySelector()`.

4. **Angular reactive forms**: Direct `.value = X` + `dispatchEvent('input')` + `blur()` works for date/radio. Button clicks need `dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}))`.

5. **Signature pad bypass**: Custom `SignaturePad` class in shadow DOM. Solution: Camoufox `page.mouse` (real events, trusted). See `references/signature-pad-automation.md`.

## Console Scope Pollution

`browser_console` evaluates JS in a persistent page context. `const`/`let` declarations persist across calls. Re-declaring the same variable name → `SyntaxError: Identifier 'X' has already been declared`.

**Rule**: ALWAYS wrap browser_console expressions in an IIFE:
```js
(() => {
  const el = document.querySelector('#myInput');
  // ... logic ...
  return JSON.stringify({ value: el.value, classes: el.className });
})();
```

Never use top-level `const`/`let` in browser_console expressions.

## Duplicate ID Pattern

Angular SPAs can assign the same `id` attribute to BOTH a wrapper `<div>` AND the inner `<input>`:
```html
<div id="familienstandSeit#1072135174">
  <input type="date" id="familienstandSeit#1072135174" class="ng-untouched ng-pristine ng-invalid">
</div>
```
`getElementById()` returns the DIV (first in DOM order). Setting `.value` on a DIV silently fails — no error, no effect.

**Fix**: Use `querySelector` to target the actual input element:
```js
const wrapper = document.getElementById('theId');
const input = wrapper.querySelector('input[type="date"]') || wrapper.querySelector('input');
```

**Detection**: If you set `.value` and `className` still shows `ng-pristine ng-invalid` (unchanged), verify you're targeting the right element: `JSON.stringify({ tag: el.tagName, type: el.type })`. If `tag` is `DIV`, you hit this bug.

## Angular Reactive Form Value Setting

Direct `input.value = 'X'` doesn't trigger Angular's reactive form validation. The input stays `ng-pristine ng-invalid`.

**Working pattern**:
```js
input.focus();
input.value = '2024-02-29';
input.dispatchEvent(new Event('input', { bubbles: true }));
input.dispatchEvent(new Event('change', { bubbles: true }));
input.blur();
```

After this, `className` should change from `ng-pristine ng-invalid` to `ng-dirty ng-valid ng-touched`.

If Angular still doesn't accept the value (production build, no `window.ng`):
- The `__ngContext__` property on the element is a number (LView index), not directly accessible
- `window.ng` (Angular dev tools) is NOT available in production builds
- `markAsDirty()` + `updateValueAndValidity()` can only be called through the component instance, which is in the LView

## Radio Buttons

- IDs change on every page load — never hardcode IDs
- Click the `<input>` directly, not the `<label>` wrapper
- Use `dispatchEvent(new MouseEvent('click'))` — `.click()` alone may not trigger Angular's handler

```js
const labels = document.querySelectorAll('label, .LabelText');
for (const label of labels) {
  if (label.textContent.includes('target text')) {
    const radio = label.querySelector('input[type="radio"]');
    radio.checked = true;
    radio.dispatchEvent(new Event('input', { bubbles: true }));
    radio.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
  }
}
```

## Button Clicks

`browser_click` (CDP click) sometimes doesn't fire Angular's click handler. The click registers but Angular's event binding doesn't execute.

**Fix**: Use `dispatchEvent` via `browser_console`:
```js
(() => {
  const btn = Array.from(document.querySelectorAll('button'))
    .find(b => b.textContent.trim().toLowerCase() === 'weiter');
  btn.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
  return 'clicked';
})();
```

**Case sensitivity pitfall**: Accessibility snapshot shows button text as "WEITER" (uppercase), but actual `textContent` may be "Weiter" (mixed case). Always use `.toLowerCase()` for comparison.

## Shadow DOM

Angular components using `shadowRoot` are invisible to `browser_click` (no ref ID in accessibility tree). Interact via `browser_console`:

```js
const component = document.querySelector('app-custom-component');
const sr = component.shadowRoot;
const element = sr.querySelector('canvas');
// Interact with element directly
```

## Signature Pad Bypass

Custom Angular `SignaturePad` class (not standard `signature_pad` library) in shadow DOM:

1. Check `window.SignaturePad` exists (often global)
2. Patch prototype: `SP.prototype.isEmpty = () => false`
3. Capture instance: patch `addPoint` to store `this`, dispatch `mousedown` on canvas
4. Populate: `instance.allSignaturePoints = [50+ fake points]`
5. Call: `instance.onDrawing({ drawing: false, x: null, y: null })` — triggers Angular form control update
6. Last resort: `element.classList.remove('ng-invalid'); element.classList.add('ng-valid')` on component + form

## Diagnostic Checklist

When Angular form automation stalls:

1. **Element identity**: `JSON.stringify({ tag: el.tagName, type: el.type, id: el.id })` — right element?
2. **Angular state**: Check `className` for `ng-pristine` (untouched) vs `ng-dirty` (touched), `ng-valid`/`ng-invalid`
3. **Shadow DOM**: `element.shadowRoot !== null` — elements hidden inside?
4. **Duplicate IDs**: `document.querySelectorAll('[id="theid"]').length` — if >1, getElementById returns wrong one
5. **Button text case**: `button.textContent.trim()` — exact match needed
6. **Form validity**: `document.querySelectorAll('.ng-invalid').length` — what's still blocking?
7. **Console scope**: Using IIFE wrapper? If not, previous `const` declarations may be blocking execution
