# CAPTCHA Bypass & Prevention

End-to-end CAPTCHA handling: **prevention first** (Camoufox + route interception), **Capsolver fallback** for when prevention fails.

## Engine Hierarchy (tested 2026-06-21)

| Engine | Turnstile Bypass | Notes |
|--------|-----------------|-------|
| **Camoufox** | ✅ YES | Patched Firefox, engine-level spoofing. DEFAULT and SOLE engine. |
| Patchright | ✅ YES | Patched Chromium. Legacy backup — use if Camoufox unavailable. |
| Nodriver | ❌ NO | Raw CDP. FAILED on REWE Turnstile. Do not use. |
| Vanilla Playwright | ❌ NO | `navigator.webdriver` + CDP leaks detected. |

### Per-Site Turnstile Results (Camoufox, tested 2026-06-21)

| Site | Has Turnstile | Camoufox Bypass | Notes |
|------|--------------|-----------------|-------|
| REWE (www.rewe.de/shop/) | YES | ✅ YES | Homepage + search both bypassed. type() for React search. |
| Apodiscounter | YES | ✅ YES | Homepage loads normally. #product-search works. |
| Medikamente-per-klick | NO | N/A | No Cloudflare. No CAPTCHA. |
| Asia-foodstore | NO | N/A | reCAPTCHA v2 lazy-loaded in Bootstrap modal on signup. Bypassed by Camoufox without Capsolver — modal never triggered. Test without Capsolver first. |
| GoAsia (goasia.net) | YES (managed) | ✅ YES (Capsolver+proxy) | Cloudflare MANAGED CHALLENGE. Camoufox alone fails. Solved via Capsolver `AntiCloudflareTask` + free SOCKS5 proxy → `cf_clearance` cookie. |
| Knuspr | NO | N/A | No Cloudflare. |
| Amazon.de | NO | N/A | No Cloudflare. |
| Alibaba Cloud (aliyun.com) | NO (baxia) | ⚠️ PARTIAL | Alibaba's own NoCaptcha slider. isTrusted bypassed via Chromium CDP. Behavioral ML detection still rejects. See `alibaba-baxia-captcha.md`. |
| Skyscanner (skyscanner.de) | NO (PerimeterX) | ⚠️ PARTIALLY SOLVED | PX blocks all Playwright/Camoufox/nodriver browsers. Real Chrome via cua-driver passes initial PX check. See `perimeterx-surfshark-vpn.md`. |
| Google Flights | NO (consent wall) | ✅ YES (button click) | `consent.google.com` wall. Click button with `jsname="b3VHJd"` to accept. |
| Lieferando (auth.lieferando.de) | YES (Turnstile) | ❌ NO | Turnstile does NOT auto-solve in Camoufox headed mode. Widget renders invisible (no iframe, no data-sitekey). Sitekey not extractable from DOM. Capsolver AntiTurnstileTaskProxyless fails — sitekey unknown. Google OAuth also fails (`/signin/rejected`). Must use pre-authenticated Firefox cookie transfer instead. See `references/lieferando-checkout.md` → "Checkout Login" section. |
| Kayak (kayak.de) | NO | ✅ YES | Camoufox + route blocking bypasses. 8-10s wait + scroll for results. |

## Strategy

1. **Prevent** — Camoufox (patched Firefox, engine-level spoofing) + route interception (blocks cookie consent banners) + human-like behavior → avoid Turnstile triggers entirely
2. **Detect** — check for Turnstile/captcha elements after page load
3. **Solve** — Capsolver API (cheapest reliable option, ~$0.001/solve)

## Prevention Layer (Primary)

### Camoufox — DEFAULT engine

```python
from camoufox.sync_api import Camoufox
from camoufox.addons import DefaultAddons
import os, shutil, sqlite3, tempfile, time, random

BLOCK_PATTERNS = [
    "usercentrics", "uc-cdn", "consent", "cookiebot", "cookielaw",
    "onetrust", "truste", "quantcast", "web-vitals",
]

def get_firefox_cookies(domain, profile_path=None):
    """Extract cookies from Firefox profile for a domain."""
    profile = profile_path or os.path.expanduser(
        "~/Library/Application Support/Firefox/Profiles/<FF_PROFILE>")
    src = os.path.join(profile, "cookies.sqlite")
    tmp = tempfile.mktemp(suffix=".sqlite")
    shutil.copy2(src, tmp)
    conn = sqlite3.connect(tmp)
    ss_map = {0: "None", 1: "Lax", 2: "Strict", 3: "None"}
    rows = conn.execute(
        "SELECT host, name, value, path, isSecure, isHttpOnly, sameSite "
        "FROM moz_cookies WHERE host LIKE ?", (f"%{domain}%",)
    ).fetchall()
    conn.close()
    os.unlink(tmp)
    return [{"name": n, "value": v, "domain": h, "path": p,
             "secure": s == 1, "httpOnly": h2 == 1,
             "sameSite": ss_map.get(ss, "None")}
            for h, n, v, p, s, h2, ss in rows if v]

def create_browser(domain=None, cookies=None):
    """Create Camoufox browser with route interception. Returns (browser, ctx, page)."""
    browser = Camoufox(
        headless=True,
        locale="de-DE",
        exclude_addons=[DefaultAddons.UBO],
    ).__enter__()
    ctx = browser.new_context(viewport={"width": 1366, "height": 900})
    def block_noise(route):
        url = route.request.url.lower()
        if any(p in url for p in BLOCK_PATTERNS):
            route.abort()
        else:
            route.continue_()
    ctx.route("**/*", block_noise)
    if cookies:
        ctx.add_cookies(cookies)
    elif domain:
        ctx.add_cookies(get_firefox_cookies(domain))
    page = ctx.new_page()
    page.on("pageerror", lambda e: None)  # suppress JS errors
    return browser, ctx, page

def navigate(page, url, wait=6):
    """Navigate with human-like behavior after page load."""
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(wait)
    for _ in range(random.randint(2, 4)):
        page.mouse.move(
            random.randint(100, 1200), random.randint(100, 800),
            steps=random.randint(10, 25)
        )
        time.sleep(random.uniform(0.1, 0.4))
```

### React form fix: type() not fill()

React-controlled forms disable submit buttons until input events fire. `fill()` doesn't trigger React state — `type()` does:

```python
# WRONG — button stays disabled
search_input.fill("query")

# RIGHT — button enables after type()
search_input.click()
time.sleep(0.3)
search_input.type("query", delay=50)
time.sleep(1)
```

### Human Behavior
```python
import time, random

def human_delay():
    time.sleep(random.uniform(0.5, 2.0))

def human_type(page, selector, text):
    for char in text:
        page.type(selector, char, delay=random.randint(50, 150))
    human_delay()

def human_scroll(page):
    page.mouse.wheel(0, random.randint(100, 500))
    time.sleep(random.uniform(0.3, 0.8))
```

## Capsolver Integration (Fallback)

API key: `~/.hermes/.env` → `CAPSOLVER_API_KEY`.

### Solve Cloudflare Turnstile
```python
def solve_turnstile(site_key: str, page_url: str) -> str:
    r = requests.post("https://api.capsolver.com/createTask", json={
        "clientKey": CAPSOLVER_API_KEY,
        "task": {
            "type": "AntiTurnstileTaskProxyless",
            "websiteURL": page_url,
            "websiteKey": site_key,
        }
    })
    task_id = r.json()["taskId"]
    for _ in range(60):
        time.sleep(3)
        r2 = requests.post("https://api.capsolver.com/getTaskResult", json={
            "clientKey": CAPSOLVER_API_KEY,
            "taskId": task_id,
        })
        data = r2.json()
        if data["status"] == "ready":
            return data["solution"]["token"]
    raise TimeoutError("Capsolver timed out")
```

### Solve reCAPTCHA v2
```python
def solve_recaptcha_v2(site_key: str, page_url: str) -> str:
    r = requests.post("https://api.capsolver.com/createTask", json={
        "clientKey": CAPSOLVER_API_KEY,
        "task": {
            "type": "ReCaptchaV2TaskProxyless",
            "websiteURL": page_url,
            "websiteKey": site_key,
        }
    })
    # ... poll for result, return data["solution"]["gRecaptchaResponse"]
```

### Solve hCaptcha (DEPRECATED — Capsolver no longer supports hCaptcha)
**As of 2026-06-23**, Capsolver returns `ERROR_INVALID_TASK_DATA` for all hCaptcha task types.

**Workarounds for hCaptcha on Shopify sites:**
- **Preferred: Shopify Storefront API GraphQL mutations** — bypass hCaptcha entirely (`customerCreate`, `customerAccessTokenCreate`, `customerResetByUrl`)
- **Alternative: 2captcha** — supports hCaptcha via `method=hcaptcha`. Requires separate API key. Cost ~$0.003/solve.
- **Alternative: Camoufox fingerprint** — test if Camoufox alone bypasses the invisible hCaptcha.

### Solve Arkose Labs FunCaptcha
```python
def solve_funcaptcha(public_key: str, page_url: str, subdomain: str = None) -> str:
    task = {
        "type": "FunCaptchaTaskProxyless",
        "websiteURL": page_url,
        "websitePublicKey": public_key,
    }
    if subdomain:
        task["funcaptchaApiJSSubdomain"] = subdomain
    # ... create task, poll, return token
```

## Detection
```python
def detect_captcha(page) -> str | None:
    """Returns captcha type if detected, else None."""
    html = page.content()
    url = page.url
    if "challenges.cloudflare.com" in url or "turnstile" in html.lower() or "cf-turnstile" in html:
        return "turnstile"
    if "recaptcha" in html.lower() or "g-recaptcha" in html:
        return "recaptcha_v2"
    if "hcaptcha" in html.lower():
        return "hcaptcha"
    arkose_markers = ["arkoselabs", "funcaptcha", "captcha-delivery.com", "arkose.com", "data-pkey"]
    if any(m in html.lower() or m in url.lower() for m in arkose_markers):
        return "funcaptcha"
    if "zeig uns, dass du ein mensch bist" in html.lower() or "robot" in html.lower():
        return "turnstile"
    return None

def get_site_key(page) -> str | None:
    return page.evaluate("""
        () => {
            const el = document.querySelector('[data-sitekey]');
            return el ? el.getAttribute('data-sitekey') : null;
        }
    """)
```

## Cloudflare Managed Challenge Bypass

When Camoufox alone can't bypass Cloudflare (managed challenges), use Capsolver with a proxy. The `cf_clearance` cookie is IP+UA-bound — must use the SAME proxy + User-Agent in Camoufox that Capsolver used.

```python
# 1. Get free SOCKS5 proxies from proxyscrape.com
# 2. Solve via Capsolver AntiCloudflareTask
r = requests.post("https://api.capsolver.com/createTask", json={
    "clientKey": api_key,
    "task": {
        "type": "AntiCloudflareTask",
        "websiteURL": "https://target-site.com/",
        "proxy": "socks5:IP:PORT",
    }
})
# Returns {"cookies": {"cf_clearance": "..."}, "userAgent": "..."}

# 3. Use cf_clearance + same proxy in Camoufox
browser = Camoufox(
    headless=True, locale="de-DE",
    exclude_addons=[DefaultAddons.UBO],
    proxy={"server": f"socks5://{ip}:{port}"},  # SAME proxy
).__enter__()
ctx = browser.new_context(user_agent=solution["userAgent"])  # SAME UA
ctx.add_cookies([{
    "name": "cf_clearance",
    "value": solution["cookies"]["cf_clearance"],
    "domain": ".target-site.com", "path": "/",
    "secure": True, "httpOnly": True, "sameSite": "None",
}])
```

### Key points
- **Proxy must be publicly reachable** — `socks5:127.0.0.1:1080` won't work
- **cf_clearance is IP-bound** — Camoufox must use the same proxy IP
- **User-Agent must match** — Capsolver returns the UA; Camoufox must set the same
- **AntiTurnstileTaskProxyless REJECTED** for managed challenges
- **Free proxies are ephemeral** — die within hours

## PerimeterX (Skyscanner) — SOLVED via Swift CGEvent press-and-hold

PerimeterX (PX) is a bot protection system separate from Cloudflare. PX detects automation PROTOCOL (CDP/Juggler), not just fingerprint — ALL Playwright-based browsers blocked.

**What WORKS**: Real Google Chrome controlled via cua-driver (OS-level CGEvent posting) passes PX's initial fingerprint check. Solving it requires a Swift CGEvent script that:
1. Posts `leftMouseDown` at the button position
2. Posts `leftMouseDragged` events with 2px random jitter every 100ms for 5 seconds
3. Posts `leftMouseUp`

See `scripts/hold_click.swift` for the full Swift code.

### Key insights
- PX "PRESS & HOLD" checks for continuous mouse-down duration + movement entropy (jitter)
- **PX cookie does NOT persist across page navigations** — must re-solve PX on each new URL
- Button position must be found via screenshot each time (PX renders button in cross-origin iframe)
- **Swift CGEvent hold-click PASSES PX on homepage but FAILS on search page** — PX likely uses stricter behavioral ML on search pages

## Alibaba baxia NoCaptcha Slider

Alibaba's baxia NoCaptcha slider checks `event.isTrusted` at the C++ engine level AND uses behavioral biometrics.

### What DOESN'T work (all tested)
| Approach | Result |
|----------|--------|
| Playwright `page.mouse` on Firefox/Camoufox | Events not trusted (Juggler protocol) |
| JS `dispatchEvent(new MouseEvent(...))` | Always untrusted |
| `Object.defineProperty(MouseEvent.prototype, 'isTrusted', ...)` | Enforced at C++ level, cannot override |
| CDP on Firefox/Camoufox | Not available — "CDP session is only available in Chromium" |

### What PARTIALLY works
**CDP `Input.dispatchMouseEvent` on Chromium** — produces `isTrusted=true` events that reach same-origin iframes. Handle moved (127px). But NoCaptcha behavioral biometrics still rejected the trajectory ("验证失败").

**Baxia NoCaptcha is currently unsolvable via automation** — all approaches failed. 2captcha and Capsolver both fail. Only manual human drag works.

See `alibaba-baxia-captcha.md` for full approach matrix.

## Friendly Captcha (frcapi.com) — UNSOLVABLE via Capsolver

Friendly Captcha is a **Proof-of-Work** captcha (not challenge-response).
The widget loads an agent iframe that computes a Blake3 PoW puzzle client-side
via WebAssembly, then submits the solution to `eu.frcapi.com/api/v2/captcha/redeem`.

### API Flow (4 stages, all inside cross-origin iframe)
1. `./activate` — sends sitekey + browser signals, receives activation token
2. `./quote` — sends activation + more signals, receives puzzle quote + cost
3. **PoW solve** — agent solves Blake3 puzzle locally (WebAssembly, 5-15s)
4. `./redeem` — submits solution, receives `redeem_token` → sets hidden field

### Why Capsolver Fails
- `FriendlyCaptchaTaskProxyLess` task type exists in Capsolver API
- Returns `ERROR_CAPTCHA_SOLVE_FAILED` (error code 1012)
- The PoW is bound to the session (sess_id, comm_id, agent_id) — cannot be
  solved out-of-band and injected
- The solution token is tied to the specific iframe session context

### Detection
```javascript
// Look for frcapi.com iframe
const iframes = document.querySelectorAll('iframe');
for (const f of iframes) {
  if (f.src && f.src.includes('frcapi.com')) return 'friendly_captcha';
}
// Or check for sitekey in iframe src
// sitekey param in URL: FCMO4GHVOH1A (example)
```

### Workarounds
1. **Camoufox HEADED mode (PROVEN WORKS, tested 2026-07-12)** — Start server
   WITHOUT `--headless` (`camoufox start`, no flag). The PoW solves
   automatically in the iframe within 10-15 seconds. No checkbox click needed.
   The captcha token has a short TTL — after solving, submit the form
   IMMEDIATELY (do not reload or navigate away). **Capsolver fails for Friendly
   Captcha (`ERROR_CAPTCHA_SOLVE_FAILED`) — do not use it.**
2. **Manual click + wait** — In a headed browser, clicking the checkbox
   triggers the PoW solve automatically (5-15s). The spinner shows progress.
3. **Phone the institution** — For insurance/government forms with Friendly
   Captcha, calling by phone bypasses the captcha entirely.

### HUK24 Tarifrechner Full Flow (tested 2026-07-12)
- URL: `https://mofa.tarifrechner.c.huk24.de/tarifrechner/mofa?fahrzeug=escooter&herkunft=top&preselect=true&isVariantEScooter=true&fahrzeugtyp=ESCOOTER`
- SPA with custom web components (`s-choice-list-item`, `s-combobox`, `s-button`)
- **Step 1**: Versicherungsbeginn (pre-filled), select "Ja" radio for ≥23
- **Step 2**: Click "wählen" for Kfz-Haftpflicht (NOT Teilkasko), then Weiter
- **Step 3**: ABE=Ja (radio[0]), ÖffDienst=Nein (radio[3]), manufacturer=XIAOMI,
  FIN input, then Weiter
- **Step 4**: Email → Weiter (captcha auto-solves) → "Kein Benutzerkonto gefunden"
  → "Jetzt registrieren" (via `eval` JS click — `auth-root` intercepts native)
  → password → Weiter → phone number → SMS code
- **Pitfall**: "Benutzerkonto suchen" button leads to wrong path (person data
  lookup). The correct flow: type email → click "Weiter" → "Kein Benutzerkonto
  gefunden" → click "Jetzt registrieren".
- **Pitfall**: Cookie consent dialog blocks all clicks. Accept ("Zustimmen")
  FIRST before any interaction.
- **Pitfall**: "weitere Details" dialog opens on step 2, intercepts Weiter
  button. Press Escape before clicking Weiter.
- **Pitfall**: Custom radios need `eval` JS click (`element.click()`),
  not `click_element` (which finds the element but doesn't trigger SPA events).
- **Pitfall**: Headless mode causes "technisches Problem" error on registration
  submit. Headed mode works.

## CAPTCHA Trajectory Recorder

Record human mouse trajectories with temporal dynamics, normalize to 0-1, and replay at any position/scale via Camoufox `page.mouse`.

See `captcha-trajectory-recorder.md` for full details.

## Setup
```bash
# Venv (shared with shopping skills)
uv venv ~/projects/shopping-bot --python 3.12
source ~/projects/shopping-bot/bin/activate
uv pip install camoufox curl_cffi

# Browser binaries
camoufox fetch
```

## Capsolver API Key
Store in `~/.hermes/.env`:
```
CAPSOLVER_API_KEY=CAP-B3C4DE1ECA6B680985D91281C8D457E42829E9D29DDCA52D3B415C450FD74FF4
```

## Key Pitfalls
- **Camoufox `geoip=True` causes hangs** — When using `headless=False`, `geoip=True` and `locale=['de-DE','en-US']` (list) cause `page.goto()` to hang. Use `locale="de-DE"` (string) and omit `geoip`.
- **React forms: type() not fill()** — React-controlled inputs disable submit buttons until input events fire.
- **Angular reactive forms: fill() + markAsDirty()** — `fill()` sets value but Angular marks form as `pristine`/`untouched`. Inject Angular's FormControl API via JS.
- **uBO built-in doesn't block FIRST-PARTY cookie popups** — Only third-party consent scripts. Use `clean` command for first-party popups.
- **uBO built-in doesn't block cookie banners (third-party)** — Default filter lists don't include easylist_cookies. Use route interception instead.
- **Turnstile token injection into React forms may still fail** — React validates the Turnstile widget's internal rendering state, not just the hidden input value.
- **Lieferando auth.lieferando.de Turnstile is a HARD BLOCKER**: Unlike REWE/Apodiscounter where Camoufox auto-solves Turnstile, the Lieferando auth page Turnstile renders as invisible (no iframe, no `data-sitekey` attribute). The sitekey is passed internally via `turnstile.render()` JS. `window.turnstile.getResponse()` returns empty even after 30s. Capsolver `AntiTurnstileTaskProxyless` fails because the sitekey cannot be extracted from the DOM. Workaround: inject pre-authenticated Firefox session cookies (see `references/lieferando-checkout.md` → "Direct Firefox→Camoufox Cookie Transfer"). This bypasses the login page entirely.
- **Cost**: Capsolver charges ~$0.001-0.003 per solve. Don't call unless detection is positive.
- **Rate limits**: Capsolver allows 5 concurrent tasks.
- **Load captcha skill BEFORE diagnosing blockers** — check for captcha indicators in output FIRST.
