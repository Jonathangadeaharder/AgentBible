# Alibaba baxia NoCaptcha Slider — Full Approach Matrix

Tested 2026-06-22 against `passport.aliyun.com` password reset page.

## CAPTCHA Structure

- **Iframe**: `#baxia-dialog-content` (same-origin, loaded dynamically after form submit)
- **Slider handle**: `#nc_1_n1z` (span.nc_iconfont.btn_slide, role=button, tabindex=0)
- **Slider track**: `#nc_1_n1t` (div.nc_scale)
- **Progress bar**: `#nc_1__bg` (div.nc_bg, width starts at 0px)
- **Text element**: `#nc_1__scale_text` (div.scale_text.slidetounlock)

The baxia iframe loads from `passport.aliyun.com/.../punish?x5secdata=...` — it's same-origin with the parent page.

## Approach Matrix

| # | Approach | Engine | isTrusted | Handle Moves | Verification | Notes |
|---|----------|--------|-----------|-------------|-------------|-------|
| 1 | `page.mouse` drag | Camoufox (Firefox/Juggler) | ❌ false | ❌ No | Ignored | Juggler protocol doesn't set isTrusted |
| 2 | JS `dispatchEvent(MouseEvent)` | Camoufox | ❌ false | ❌ No | Ignored | All dispatched events are untrusted |
| 3 | `Object.defineProperty(Event.prototype, 'isTrusted', ...)` | Camoufox | Patched | ❌ No | Ignored | C++ enforces isTrusted, JS override has no effect |
| 4 | `page.route()` intercept nc.js + inject isTrusted patch | Camoufox | Patched | ❌ No | Ignored | Script patching doesn't bypass C++ enforcement |
| 5 | Override `addEventListener` + call listeners directly | Camoufox | ❌ false | ❌ No | Ignored | Listeners check isTrusted on the event object |
| 6 | Direct NoCaptcha API call (intercept AJAX) | Camoufox | N/A | N/A | ❌ No endpoint found | No verification POST was captured — the slider JS only sends AJAX after successful verification |
| 7 | `contentWindow.dispatchEvent` | Camoufox | ❌ false | ❌ No | Ignored | Same as #2 — events still untrusted |
| 8 | Keyboard (Arrow Right, Enter, Space, Tab) | Camoufox | N/A | ❌ No | Ignored | Handle has tabindex=0 but keys don't trigger slider |
| 9 | CDP `Input.dispatchMouseEvent` | Chromium | ✅ true | ✅ Yes (127px) | ❌ "验证失败" | Handle moves! But behavioral ML rejects trajectory |
| 10 | `page.mouse` drag | Chromium | ❌ false | ❌ No | Ignored | Playwright on Chromium also doesn't set isTrusted for page.mouse |
| 11 | `page.frame_locator().drag_to()` | Chromium | ❌ false | ❌ No | Ignored | Playwright's drag_to uses JS events, not CDP input |
| 12 | CGEvent tap recording + CDP replay | Chromium | ✅ true | ✅ Yes | ❌ "验证失败" | Real human trajectory replayed via CDP — still rejected. CDP events may lack movementX/movementY or timing differs |

## Key Findings

1. **`isTrusted` is enforced at C++ engine level** — `Object.defineProperty` on `Event.prototype.isTrusted` does NOT work in either Firefox or Chromium. This is a hard browser security boundary.

2. **CDP `Input.dispatchMouseEvent` on Chromium produces `isTrusted=true` events** — these ARE delivered to same-origin iframe content when dispatched at page-absolute coordinates. The handle MOVES (confirmed via `handle.style.left` changing from `0px` to `127px`).

3. **CDP is NOT available on Firefox/Camoufox** — `ctx.new_cdp_session(page)` fails with "CDP session is only available in Chromium". Firefox uses the Juggler protocol which doesn't have an equivalent of `Input.dispatchMouseEvent`.

4. **`page.mouse` on Chromium does NOT produce trusted events** — Playwright's `page.mouse` goes through a different code path than CDP `Input.dispatchMouseEvent`. Must use CDP explicitly.

5. **Behavioral biometrics are the remaining blocker** — even with `isTrusted=true` events and handle movement, NoCaptcha rejects the trajectory with error codes like `A1mzn`, `bXVV4n`, `ewVwn`, `8ZeF3n`, `ZjaVUn`, `s4iUAn`. The baxia JS analyzes:
   - Mouse trajectory entropy
   - Acceleration/deceleration patterns
   - Timestamp intervals between events
   - Vertical jitter patterns
   - Click position relative to handle center

6. **Recorded human trajectory replay still fails** — a real human drag recorded via macOS CGEvent tap, replayed via CDP with exact original timing, still gets "验证失败". Possible reasons:
   - CDP events lack `movementX`/`movementY` properties
   - Replay timing is subtly different from native CGEvent delivery
   - NoCaptcha detects the gap between mouse event dispatch and rendering

## Script Locations

- `scripts/record_mouse.swift` — CGEvent tap recorder (compile with `swiftc -O`)
- `~/projects/image-bot/aliyun_slider_solver.py` — All 7 approaches tested
- `~/projects/image-bot/aliyun_reset.py` — Full password reset flow with CDP slider solver

## Potential Solutions (untested)

1. **cua-driver CGEvent drag** — `cua-driver call drag` posts real OS-level CGEvents to a PID. These would have `isTrusted=true` AND native `movementX`/`movementY`. Requires a visible Firefox window on a separate Space.
2. **2captcha `method=alibaba`** — token-based solver, but may target AliyunCaptcha (newer) not AWSC/nc.js (baxia's NoCaptcha). Needs testing.
3. **Xvfb (virtual framebuffer)** — run Firefox in a virtual X display, use `xdotool` for mouse events. Linux-only.
