# Browser Control Patterns

Headless browser control patterns — SSO access, token capture, focus-safe automation on macOS, and engine selection.

## Tool Selection — Camoufox First (with exceptions)

**DEFAULT: Camoufox** for all browser automation. Not Playwright, not Hermes browser tools.

**EXCEPTION: isTrusted CAPTCHAs** — Use **Chromium + CDP `Input.dispatchMouseEvent`** when a CAPTCHA checks `event.isTrusted` (e.g., Alibaba baxia NoCaptcha). CDP on Chromium produces `isTrusted=true` events. Camoufox/Firefox Juggler protocol does NOT. See `captcha-bypass.md`.

**EXCEPTION: Google-auth sites** — Use **Playwright Firefox `launch_persistent_context`** with a copied Firefox profile. Camoufox's `new_context()` + `add_cookies()` does NOT work for Google auth (needs full profile state: localStorage, IndexedDB). See `gemini-images` skill.

| Need | Tool | Why |
|------|------|-----|
| Cross-origin iframes | **Camoufox** | CDP Chromium blocked by same-origin policy. Camoufox (real Firefox) accesses all frames. |
| CAPTCHA solving (isTrusted) | **Chromium + CDP** | `Input.dispatchMouseEvent` produces `isTrusted=true`. Camoufox/Firefox does not. |
| CAPTCHA solving (Cloudflare) | **Camoufox** | Engine-level fingerprint spoofing. Turnstile, managed challenges. |
| Google-auth sites (Gemini, etc.) | **Playwright Firefox persistent_context** | Google auth needs full profile state, not just cookies. |
| Quick page inspection | Hermes browser tools | OK for reading snapshots, NOT for interaction with cross-origin content. |
| Cookie-only API access | curl_cffi | Fastest. No JS rendering. TLS impersonation. |

## Focus Steal Rules

- **NEVER** launch a visible browser window from automation. It steals macOS focus.
- **NEVER** use CDP clicks on Slack/Electron apps — they bring the window to foreground.
- **NEVER** use `page.goto()` on a non-headless browser — it activates the window.
- Headless = zero focus steal. Always use it.

## SSO Access Pattern (TravelPerk, Offline.tngtech.com, Timesheet)

Many TNG-internal sites use Keycloak SSO. The browser must have an active SSO session.

### Method: Copy Firefox cookies → headless Chromium

```python
from playwright.sync_api import sync_playwright
import sqlite3, shutil, tempfile

# 1. Copy cookies.sqlite (Firefox locks the original)
src = os.path.expanduser("~/Library/Application Support/Firefox/Profiles/<profile>/cookies.sqlite")
tmp = tempfile.mktemp(suffix=".sqlite")
shutil.copy2(src, tmp)

# 2. Extract ALL cookies (not filtered — need SSO cookies too)
conn = sqlite3.connect(tmp)
cur = conn.cursor()
cur.execute("SELECT host, name, value, path, isSecure FROM moz_cookies")
cookies = [{"name": n, "value": v, "domain": h, "path": p, "secure": s==1}
           for h, n, v, p, s in cur.fetchall()]
conn.close()
os.unlink(tmp)

# 3. Inject into headless Chromium
pw = sync_playwright().start()
browser = pw.chromium.launch(headless=True)
context = browser.new_context()
context.add_cookies(cookies)
page = context.new_page()

# 4. Navigate — if on login page, click SSO
page.goto("https://target-site.example.com")
if "login" in page.url:
    page.evaluate("""() => {
        document.querySelectorAll('[id*="usercentrics"]').forEach(e => e.remove());
    }""")
    page.locator("text=SSO Login").first.click(force=True)
    page.wait_for_timeout(5000)
```

### Pitfalls
- **Firefox profile is locked** by running instance — cannot use `launch_persistent_context`. Must copy cookies.sqlite.
- **Cookie consent popups** (usercentrics) intercept clicks — remove them before clicking SSO.
- **Need ALL cookies** — filtering by domain misses Keycloak SSO cookies (domain: `sso.tngtech.com`).
- **SPA content is JS-rendered** — `requests` alone won't work. Need Playwright for DOM access.
- **SSO click with `force=True`** — cookie popup may visually intercept, but `force=True` bypasses.
- **Form fields can appear dynamically** — Some forms show new fields after radio button selection. Wait for these to render before attempting to fill them.

## Bearer Token Capture Pattern

For sites that use Bearer JWT tokens (timesheet API), capture them from network requests:

```python
bearer_token = None
def on_request(req):
    global bearer_token
    auth = req.headers.get("authorization", "")
    if auth.startswith("Bearer ") and len(auth) > 20:
        bearer_token = auth

page.on("request", on_request)
page.goto("https://timesheet.tngtech.com/timesheet/2026/5",
          wait_until="networkidle", timeout=30000)
page.wait_for_timeout(5000)  # wait for API calls to fire
```

Then use the token with `requests` for pure HTTP access — zero focus steal.

## GitHub OAuth via Firefox Cookie Injection

When a headless browser needs to auth through a third-party GitHub OAuth flow (e.g. SonarCloud, Linear), inject GitHub session cookies from Firefox:

1. Copy cookies DB: `cp ~/Library/Application\\ Support/Firefox/Profiles/<profile>/cookies.sqlite /tmp/firefox_cookies.sqlite`
2. Extract session cookies: `user_session`, `__Host-user_session_same_site`, `logged_in`
3. Navigate to `github.com` in headless browser
4. Set cookies via `context.add_cookies()`
5. Navigate to target site → click GitHub OAuth → auto-authorizes

### Pitfalls
- **`__Host-` prefix cookies** can't be set via `document.cookie`. Use Playwright's `context.add_cookies()`.
- **Cookies expire** — extract fresh each session.
- **SonarCloud** also needs `JWT-SESSION` + `XSRF-TOKEN` + `AUTH0` cookies after GitHub OAuth. Use `sonarcloud.io/api` (not `api.sonarcloud.io` which returns 403 on Free-tier).

## Gmail — Playwright Firefox Works

Google blocks headless **Chromium** with "This browser or app may not be secure". But **headless Firefox** with cookie injection WORKS for full Gmail access.

```python
from playwright.sync_api import sync_playwright

pw = sync_playwright().start()
browser = pw.firefox.launch(headless=True)  # Firefox, not Chromium!
context = browser.new_context()
context.add_cookies(cookies)  # ALL cookies from Firefox
page = context.new_page()
page.goto("https://mail.google.com/mail/u/0/#inbox", timeout=30000)
```

### What also works:
- **Firefox cookies → curl**: Read-only access to Gmail HTML.
- **himalaya**: Full IMAP/SMTP via Gmail App Password.
- **google-workspace skill**: Full Gmail API via OAuth2.

### What does NOT work:
- Headless Chromium with cookies → Google detects, blocks.
- Hermes browser (Chromium-based) login → same block.
- Programmatic OAuth2 token exchange with cookie-stolen session → "invalid_request / unsupported browser".

## Sites and Their Access Method

| Site | Method | Notes |
|------|--------|-------|
| Slack | Web API (xoxc+d) | NEVER CDP — steals focus. See slack-catchup skill. |
| TravelPerk | Camoufox + SSO | Cookie consent popup must be dismissed. |
| Offline.tngtech.com | Camoufox + SSO | Techday cycle, absences. |
| Timesheet | Camoufox → Bearer token → HTTP API | Token from network interception. |
| Confluence | `requests` + Firefox cookies | No SSO redirect needed, cookies sufficient. |
| SonarCloud | Firefox cookies → GitHub OAuth → Camoufox | Free plan: only `sonarcloud.io/api` works. |
| Gmail | **Camoufox** or Playwright headless Firefox + cookie injection | Chromium blocked by Google bot detection. |
| REWE shop | **Camoufox** (Turnstile bypass) or **curl_cffi** `impersonate="firefox"` | Camoufox bypasses Turnstile via engine-level spoofing. |
| Amazon.de | **Camoufox** + Firefox cookies | curl_cffi works for search HTML. |
| Knuspr.de | **Camoufox** (SSR) + **curl_cffi** (API) | See grocery-shopping skill. |
| GoAsia | **Camoufox + Capsolver** (AntiCloudflareTask + proxy) | Cloudflare MANAGED CHALLENGE. |
| Gemini Images | **Playwright Firefox persistent_context** (profile copy) | Cookie injection fails — Google needs full profile state. |
| Alibaba Cloud | **Chromium + CDP** for CAPTCHA, Camoufox for form navigation | Baxia NoCaptcha slider needs `isTrusted=true`. |
| Lovable.dev | Camoufox + Firefox cookies → Vite dev server `?raw` | Source files accessible via `<project-id>.lovableproject.com/<path>?raw`. |

## Cloudflare Bypass: curl_cffi (TLS Impersonation)

When a site uses Cloudflare bot detection, Playwright headless Firefox + cookie injection is NOT enough — Cloudflare checks TLS fingerprint (JA3). `curl_cffi` with `impersonate="firefox"` mimics Firefox's TLS handshake → Cloudflare passes.

```python
from curl_cffi import requests

s = requests.Session(impersonate="firefox")
r = s.get("https://target-site.com/", cookies=cookies, timeout=15)
# Cloudflare passes! HTML returned normally.
```

## Firefox Cookie Expiry Format

Firefox `cookies.sqlite` stores expiry in **milliseconds** (e.g. `1815387659492`), NOT Unix seconds.

```python
# Correct conversion for Playwright (milliseconds → seconds)
expiry_sec = exp // 1000 if exp else -1
if expiry_sec < 0:
    expiry_sec = -1  # session cookie
cookie["expires"] = expiry_sec
```

Playwright rejects `expires=0` — use `-1` for session cookies.

## Hermes Venv PYTHONPATH Leak (CRITICAL)

Hermes sets `PYTHONPATH` globally to include `hermes-agent/` and `hermes-agent/venv/lib/python3.11/site-packages`. This leaks Python 3.11 `yaml` module into Camoufox's Python 3.12 venv → `ImportError: cannot import name 'CLoader' from 'yaml'`.

**Fix**: Always prefix Camoufox scripts with `PYTHONPATH=""`:
```bash
PYTHONPATH="" ~/.hermes/.venv/bin/python3 script.py
```

## Playwright Version Pin for Camoufox

Camoufox 0.4.11 requires **Playwright 1.49.0**. Playwright 1.61+ causes protocol error:
```
Browser.setDefaultViewport: Found property "viewport.isMobile" - false which is not described in this scheme
```

**Fix**: `uv pip install "playwright==1.49.0" -p ~/.hermes/.venv`

## SSO Session Cookie Expiry Check

Before attempting cookie injection for SSO-protected sites, check if the session cookie has expired:
```python
import time
for name, value, host, path, expiry, *_ in rows:
    exp_sec = expiry // 1000 if expiry > 1e9 else expiry  # ms → sec
    if exp_sec and exp_sec < time.time():
        print(f"EXPIRED: {name} (host={host}, expired {time.ctime(exp_sec)})")
```
If the Keycloak SSO cookie is expired, cookie injection won't work — need fresh 2FA login.
