# CAPTCHA Trajectory Recorder Methodology

## Overview

The trajectory recorder captures human mouse movements with full temporal dynamics, normalizes them to 0-1 coordinates relative to the CAPTCHA challenge bounding box, and stores them with rich metadata for replay at any position/scale via Camoufox `page.mouse`.

## Files

| File | Purpose |
|------|---------|
| `scripts/captcha_recorder.py` | Main recorder/replayer CLI |
| `scripts/signature_trajectory.py` | Signature-specific recorder/replayer |
| `scripts/signature_replay.py` | Low-level signature replay (PNG/CDP/cua) |

## Recording a Trajectory

```bash
# Generic CAPTCHA (slider, puzzle, drag-drop)
python captcha_recorder.py record \
  --url "https://target-site.com/captcha" \
  --type slider \
  --provider geetest \
  --selector "canvas,iframe,div[id*='slider']" \
  --style cautious

# Signature pad
python signature_trajectory.py record \
  --url "file:///path/to/signature_pad.html" \
  --selector "#sigCanvas"
```

## What Gets Recorded

### Per-Event (at ~60Hz during interaction)
- `t` — milliseconds since mousedown
- `dx, dy` — normalized (0-1) relative to challenge bbox
- `speed` — instantaneous px/ms
- `action` — `mousedown`, `mousemove`, `mouseup`
- `x_abs, y_abs` — absolute screen coordinates (for debugging)

### Per-Session Metadata
- `provider` — geetest, alibaba, recaptcha_v2, etc.
- `captcha_type` — slider, puzzle, dragdrop, image, grid
- `challenge_bbox` — {x, y, w, h} in viewport pixels
- `viewport` — {width, height}
- `start_norm`, `end_norm` — normalized start/end
- `style` — cautious, confident, corrector
- `success` — boolean (user confirms after solving)
- `browser_profile` — camoufox, etc.

## Replaying a Trajectory

```python
from captcha_recorder import replay_trajectory, list_trajectories

# Find trajectories for this CAPTCHA
records = list_trajectories(provider="geetest", captcha_type="slider")
if records:
    # Locate challenge on current page
    target_bbox = page.evaluate("""() => {
        const el = document.querySelector('canvas, .slider-track');
        const r = el.getBoundingClientRect();
        return {x: r.x, y: r.y, w: r.width, h: r.height};
    }""")
    
    # Scale and replay
    replay_trajectory(page, records[0], target_bbox, speed_multiplier=1.0)
```

## Scaling Logic

Source trajectory: recorded against `challenge_bbox` (w_s × h_s)
Target challenge: current page's `target_bbox` (w_t × h_t)

```
scale_x = w_t / w_s
scale_y = h_t / h_s
x_t = target_bbox.x + e.dx * w_t
y_t = target_bbox.y + e.dy * h_t
```

## Critical Variants (per provider/type)

For each CAPTCHA provider, record at least 3 behavioral profiles:

| Style | Profile | Characteristics |
|-------|---------|-----------------|
| **cautious** | The Slow Starter | 300-500ms dwell on handle, gradual acceleration |
| **confident** | The Confident Flick | Minimal pause, rapid linear, slight overshoot |
| **corrector** | The Hesitant Corrector | Reaches ~90%, pauses, micro-adjusts, releases |

## What to Discard

**Discard any trajectory that has:**
- Perfect straight line (constant dx/dy)
- Constant speed (no acceleration curve)
- No pauses/dwells
- Perfectly symmetric overshoot

Modern CAPTCHA engines (GeeTest, Alibaba Cloud, PerimeterX) score on **entropy and imperfection**. The most valuable data is the **wobble, speed dip, 200ms pause before final snap**.

## Signature Pad Specifics

For signature pads (HEK, government portals):

1. Record once via `signature_trajectory.py` on a blank canvas
2. Save to `~/.hermes/assets/signature_strokes.json` (689 pts, 3 strokes, 8.57s)
3. Replay in form automation via `signature_replay.py`:

```python
from signature_replay import replay_signature
replay_signature(page, selector="canvas", speed=1.0)
```

## Integration with Vision Subagent

The vision subagent should:
1. Detect CAPTCHA challenge region → return bounding box
2. Agent selects trajectory matching provider/type/style
3. Replay with scaling to detected bbox

## File Storage

```
~/.hermes/captcha_trajectories/
  geetest_slider_abc123_cautious.json
  geetest_slider_def456_confident.json
  alibaba_slider_ghi789_corrector.json
  generic_dragdrop_jkl012_natural.json

~/.hermes/assets/
  signature_strokes.json       # 689 pts, 3 strokes
  signature_trajectory.json    # signature-specific format
  signature_captured.png       # preview
  signature_strokes.json       # reusable
```

## CLI Commands

```bash
# Record
python captcha_recorder.py record --url URL --type TYPE --provider PROVIDER [--selector SEL] [--style STYLE]

# List
python captcha_recorder.py list [--provider PROVIDER] [--type TYPE]

# Show
python captcha_recorder.py show ID

# Signature record
python signature_trajectory.py record [--url URL] [--selector SEL]

# Signature replay (from form automation script)
python signature_replay.py --png output.png
python signature_replay.py --cdp --x X --y Y --w W --h H
python signature_replay.py --cua --x X --y Y --w W --h H
```

## Best Practices

1. **Record fresh per provider** — trajectories don't transfer across CAPTCHA engines
2. **Record on real page** — use the actual target site, not a replica
3. **Confirm success** — CLI prompts "Did the CAPTCHA pass?" (y/n) → stored as `success`
4. **Note style** — user can hint `--style` or let auto-classification decide
5. **Version control** — trajectories are in `.hermes/` (git-backed via hermes-config-backup skill)

## Debugging

If replay fails:
- Check `target_bbox` matches challenge element
- Verify `challenge_bbox` in JSON matches recording page
- Try different `speed_multiplier` (0.8-1.2)
- Try different style variant (cautious/confident/corrector)
- Vision subagent should screenshot and analyze the challenge region