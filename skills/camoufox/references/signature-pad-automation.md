# Signature Pad Automation with Camoufox

## Overview

Signature pads on forms (HEK Familienversicherung, government portals, banking) use canvas-based drawing that validates via `event.isTrusted`. Headless CDP Chromium (Hermes browser tools) **cannot** produce trusted mouse events — synthetic `dispatchEvent` is rejected.

**Solution**: Camoufox (real headed Firefox) + `page.mouse` → produces real browser mouse events that signature pads accept as trusted.

## HEK Form Case Study

Form: `https://serviceapp.hek.de/forms-26/FAMI_PRUEFBOGEN?...`
- Angular SPA with custom `SignaturePad` class (NOT standard `signature_pad` library)
- Signature pad inside `<app-signature-view>` component's shadow DOM
- Canvas in shadow root: `document.querySelector('app-signature-view').shadowRoot.querySelector('canvas')`

### Problems Encountered

1. **Shadow DOM canvas** — `browser_click` can't reach it (no ref ID in accessibility tree)
2. **Custom SignaturePad class** — not the standard library, has its own `validateSignature()` checking `allSignaturePoints.length >= minPoints`
3. **Angular form validation** — form control stays `ng-invalid` until `onDrawing({drawing: false})` callback fires with valid data URL
4. **Headless CDP `dispatchEvent`** — produces `isTrusted=false` events → signature pad ignores

### Solution: Camoufox + page.mouse

```python
# Load captured signature strokes
strokes, canvas_size = load_signature_strokes()

# Get canvas bounding box from shadow DOM
box = page.evaluate("""() => {
    const sig = document.querySelector('app-signature-view');
    if (!sig || !sig.shadowRoot) return null;
    const canvas = sig.shadowRoot.querySelector('canvas');
    if (!canvas) return null;
    const r = canvas.getBoundingClientRect();
    return {x: r.x, y: r.y, w: r.width, h: r.height};
}""")

if box:
    sx = box['w'] / canvas_size['width']
    sy = box['h'] / canvas_size['height']
    
    for stroke_idx, stroke in enumerate(strokes):
        if len(stroke) < 2:
            continue
        
        # Start stroke
        first = stroke[0]
        page.mouse.move(box['x'] + first['x'] * sx, box['y'] + first['y'] * sy)
        time.sleep(random.uniform(0.1, 0.3))
        page.mouse.down()
        time.sleep(random.uniform(0.05, 0.15))
        
        # Draw through points with original timing (clamped)
        for i in range(1, len(stroke)):
            p = stroke[i]
            x = box['x'] + p['x'] * sx + random.uniform(-0.5, 0.5)
            y = box['y'] + p['y'] * sy + random.uniform(-0.5, 0.5)
            page.mouse.move(x, y)
            
            if i < len(stroke) - 1:
                dt = stroke[i+1]['t'] - p['t']
                time.sleep(max(0.005, min(0.025, dt)))
        
        # End stroke
        last = stroke[-1]
        page.mouse.move(box['x'] + last['x'] * sx, box['y'] + last['y'] * sy)
        time.sleep(random.uniform(0.05, 0.15))
        page.mouse.up()
        
        if stroke_idx < len(strokes) - 1:
            time.sleep(random.uniform(0.3, 0.6))
```

### Key Points

1. **Use `page.evaluate` + `shadowRoot.querySelector()`** — `browser_click` can't reach shadow DOM elements
2. **Scale from source canvas** — `canvas_size` from recording, `box['w']/box['h']` from current page
3. **Add micro-jitter** — `random.uniform(-0.5, 0.5)` on each move for realism
4. **Use original timing** — clamp to 5-25ms between points
5. **Pause between strokes** — 300-600ms mimics human lifting pen

### Signature Capture

Recorded trajectory: `~/.hermes/assets/signature_strokes.json`
- 3 strokes, 689 points, 8.57s duration
- Canvas: 600×200
- Format: `{"strokes": [...], "canvas_size": {"width": 600, "height": 200}}`

### Replay Script

`~/.hermes/scripts/signature_replay.py` — renders PNG, outputs CDP JS, or cua-driver commands

```bash
# Verify rendering
python signature_replay.py --png output.png

# For CDP injection
python signature_replay.py --cdp --x 367 --y 195 --w 485 --h 242
```

## Why This Works

| Approach | Result | Why |
|----------|--------|-----|
| CDP Chromium `dispatchEvent` | ❌ Fails | `isTrusted=false` — signature pad ignores |
| JS `dispatchEvent` on canvas | ❌ Fails | Same — `isTrusted=false` |
| Camoufox `page.mouse.move/down/up` | ✅ Works | Real Firefox mouse events → `isTrusted=true` |

Camoufox runs a real patched Firefox. Its `page.mouse` API posts genuine mouse events through the browser's input system, which the SignaturePad library recognizes as trusted user input.

## Pitfalls

1. **Shadow DOM** — must use `page.evaluate` to reach into `shadowRoot` for bounding box
2. **Canvas position** — verify `box` is not null before replaying
3. **Angular form validation** — after drawing, the custom `onDrawing({drawing: false})` callback must fire to update the Angular form control. This happens automatically when the pad's internal state updates from real mouse events.
3. **Duplicate ID bug** — Angular may assign same ID to wrapper div AND inner input. Use `querySelector('input[type="date"]')` not `getElementById()`.

## Generic Shadow DOM Pattern

```python
# For ANY shadow DOM element
result = page.evaluate("""() => {
    const host = document.querySelector('app-custom-component');
    if (!host || !host.shadowRoot) return null;
    const el = host.shadowRoot.querySelector('canvas');  // or 'button', 'input'
    if (!el) return null;
    const r = el.getBoundingClientRect();
    return {x: r.x, y: r.y, w: r.width, h: r.height};
}""")

if result:
    page.mouse.move(result['x'] + result['w']/2, result['y'] + result['h']/2)
    page.mouse.down()
    # ... draw/drag ...
    page.mouse.up()
```