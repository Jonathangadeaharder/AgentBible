# Camoufox Automation Patterns

Detailed patterns for anti-bot bypass, persistent profiles, cookie injection, 2FA flows, and uBlock Origin integration.

## Core Principles
- **ALWAYS uBlock Origin** with cookie lists (Easylist Cookie, I Don't Care About Cookies)
- **Cookie injection > persistent profile** for fresh sessions
- **Persistent profile** only when session must survive restarts
- **humanize=True** always for anti-bot evasion

## Setup

### Camoufox with uBlock Origin
```python
from camoufox.sync_api import Camoufox

with Camoufox(
    headless=False,
    humanize=True,
    geoip=False,
    addons=["ublock-origin"],  # MUST include
) as browser:
    page = browser.new_page()
    # uBlock auto-loads with default filter lists
```

### Add Cookie Filter Lists to uBlock
```python
# In page context after launch
page.evaluate("""() => {
    // uBlock Origin API to add filter lists
    // Easylist Cookie, I Don't Care About Cookies
}""")
```

## Persistent Profile Handling

### Profile Path (no spaces!)
```python
# Symlink to avoid spaces in path
profile_path = "/tmp/giuli_profile"  # symlink to actual Firefox profile
```

### Version Mismatch Dialog Fix
```bash
# Remove compatibility.ini so Camoufox creates fresh one
rm /tmp/giuli_profile/compatibility.ini
```
Camoufox will recreate with its own version on first launch.

### Don't Run Firefox + Camoufox Simultaneously
- Firefox holds profile lock → Camoufox fails
- Session cookies only in Firefox memory, not cookies.sqlite
- Kill Firefox before Camoufox persistent context

## Cookie Injection (Preferred for Fresh Sessions)

### Extract from Firefox cookies.sqlite
```python
import sqlite3, shutil, tempfile, os

profile_path = os.path.expanduser("~/Library/Application Support/Firefox/Profiles/xxx")
cookies_db = os.path.join(profile_path, "cookies.sqlite")
tmp = os.path.join(tempfile.gettempdir(), "cookies_copy.sqlite")
shutil.copy2(cookies_db, tmp)

conn = sqlite3.connect(tmp)
cur = conn.cursor()
cur.execute("""
    SELECT name, value, host, path, expiry, isSecure, isHttpOnly, sameSite
    FROM moz_cookies WHERE host LIKE '%domain%'
""")
rows = cur.fetchall()
conn.close()

# Firefox cookies.sqlite stores expiry in MILLISECONDS (13 digits) on modern Firefox.
# Playwright add_cookies expects SECONDS since epoch.
# Playwright rejects expires=0 — use -1 for session cookies.
def normalize_expiry(expiry):
    if not expiry or expiry == 0:
        return -1  # session cookie (Playwright convention)
    if expiry > 1e15: return int(expiry / 1e6)  # microseconds (16 digits)
    if expiry > 1e12: return int(expiry / 1e3)  # milliseconds (13 digits)
    return int(expiry)  # already seconds

# Inject into Camoufox
for name, value, host, path, expiry, is_secure, is_http_only, same_site in rows:
    cookie = {
        "name": name, "value": value, "domain": host,
        "path": path or "/", "secure": bool(is_secure),
        "httpOnly": bool(is_http_only),
        "sameSite": {0: "None", 1: "Lax", 2: "Strict"}.get(same_site, "None"),
        "expires": normalize_expiry(expiry),  # always set — -1 for session
    }
    page.context.add_cookies([cookie])
```

### CRITICAL: cookies.sqlite Does NOT Contain Session Cookies While Firefox Is Running

Firefox stores **session cookies** (expiry=0, no `expires` attribute) in **memory only**.
They are **NOT** in `cookies.sqlite` while Firefox is running. The `cookies.sqlite-wal`
(WAL log) may have some uncommitted entries, but the main auth cookies for many sites
(Cerebras, Zhipu/BigModel, Google AI Studio, etc.) are session cookies that never
get persisted to disk unless Firefox is closed gracefully.

**What this means for cookie injection:**
- If you copy `cookies.sqlite` while Firefox is running, you will only get **persistent**
  cookies (analytics, consent banners, etc.) — NOT the auth session cookies you need.
- Sites like Cerebras (`cloud.cerebras.ai`) use Auth0/Clerk session cookies that are
  HttpOnly + session-only → invisible in `cookies.sqlite` while Firefox runs.
- Sites like Google AI Studio (`aistudio.google.com`) store their auth in Google's
  standard `SID`/`__Secure-1PSID` cookies which ARE persistent (in `cookies.sqlite`).

### Three-Tier Cookie Extraction Strategy

When extracting cookies for a target domain, check ALL THREE sources in order:

**Tier 1: cookies.sqlite (persistent cookies)**
```bash
# Copy while Firefox is running (WAL included for uncommitted entries)
cp "$PROFILE/cookies.sqlite" /tmp/ff_cookies.sqlite
cp "$PROFILE/cookies.sqlite-wal" /tmp/ff_cookies.sqlite-wal 2>/dev/null
sqlite3 /tmp/ff_cookies.sqlite "SELECT name, host, expiry FROM moz_cookies WHERE host LIKE '%target-domain%';"
```
Works for: Google (SID/HSID/SSID are persistent), HuggingFace (token cookie is persistent).

**Tier 2: Session store recovery.jsonlz4 (session cookies for ACTIVE tabs)**
Firefox's session store backup contains cookies for **currently open tabs only**.
If the target site's tab is open in Firefox, its session cookies will be here.
```bash
# Requires lz4 decompression. Python lz4 often broken in venvs — use Node.js:
cd ~/projects/camofox-browser && eval "$(fnm env)" && fnm use 22
node -e "
const fs = require('fs');
const lz4 = require('lz4');
const data = fs.readFileSync('$PROFILE/sessionstore-backups/recovery.jsonlz4');
const decompSize = data.readUInt32LE(8);
const output = Buffer.alloc(decompSize);
const result = lz4.decodeBlock(data.slice(12), output);
const session = JSON.parse(output.toString('utf8', 0, result));
const cookies = session.cookies || [];
const target = cookies.filter(c => (c.host||'').includes('target-domain'));
console.log(JSON.stringify(target, null, 2));
"
```
**NOTE**: The `lz4` npm package must be installed: `cd ~/projects/camofox-browser && npm install lz4`.
Python `lz4` package frequently fails with `ModuleNotFoundError: No module named 'lz4._version'`
in the Hermes venv due to binary incompatibility. Use Node.js instead.

**Tier 3: Close Firefox and re-extract (session cookies flushed to disk)**
If the target site's cookies aren't in Tier 1 or Tier 2, the only option is to
close Firefox (which flushes session cookies to `cookies.sqlite`), then re-extract:
```bash
# Gracefully close Firefox (SIGTERM, not SIGKILL)
osascript -e 'tell application "Firefox" to quit'
sleep 3
# Now cookies.sqlite has ALL cookies including session ones
cp "$PROFILE/cookies.sqlite" /tmp/ff_cookies_closed.sqlite
sqlite3 /tmp/ff_cookies_closed.sqlite "SELECT count(*) FROM moz_cookies WHERE host LIKE '%target-domain%';"
```
**WARNING**: Never use `pkill -9 firefox` — SIGKILL skips the graceful shutdown
that flushes session cookies to disk. Always use SIGTERM or AppleScript.

### Checking Which Firefox Profile Has Cookies for a Domain
```bash
for profile_dir in ~/Library/Application\ Support/Firefox/Profiles/*/; do
  if [ -f "$profile_dir/cookies.sqlite" ]; then
    name=$(basename "$profile_dir")
    count=$(sqlite3 "$profile_dir/cookies.sqlite" \
      "SELECT count(*) FROM moz_cookies WHERE host LIKE '%target-domain%';" 2>/dev/null)
    if [ "$count" -gt 0 ] 2>/dev/null; then
      echo "$name: $count cookies"
    fi
  fi
done
```

### REST API Cookie Injection (when using Camoufox server)
When using the Camoufox REST server, inject cookies via the sessions endpoint
(NOT via `document.cookie` which can't set HttpOnly cookies):
```bash
# Extract cookies as JSON, wrap in {"cookies": [...]} field
python3 -c "
import json, sqlite3
conn = sqlite3.connect('/tmp/ff_cookies.sqlite')
rows = conn.execute('''
    SELECT name, value, host, path, expiry, isSecure, isHttpOnly, sameSite
    FROM moz_cookies WHERE host LIKE ? OR host LIKE ?
''', ('%domain%', '%.domain%')).fetchall()
conn.close()
cookies = []
for name, value, host, path, expiry, is_secure, is_http_only, same_site in rows:
    if name in ('cf_clearance', '__cf_bm'): continue  # filter Cloudflare
    if expiry > 1e12: expiry = int(expiry / 1000)  # ms → s
    if expiry == 0: expiry = -1  # session cookie
    cookies.append({
        'name': name, 'value': value, 'domain': host, 'path': path or '/',
        'secure': bool(is_secure), 'httpOnly': bool(is_http_only),
        'sameSite': {0: 'None', 1: 'Lax', 2: 'Strict'}.get(same_site, 'None'),
        'expires': int(expiry)
    })
print(json.dumps({'cookies': cookies}))
" > /tmp/cookies.json

curl -s -X POST "http://localhost:9377/sessions/USERID/cookies" \
  -H 'Content-Type: application/json' -d @/tmp/cookies.json
```

## BA-Secure App 2FA Flow

### Login Sequence
1. Navigate to `https://web.arbeitsagentur.de/profil/profil-ui/pd/`
2. Cookie banner: remove `bahf-cookie-disclaimer-dpl3` via JS
3. Click first "Anmelden" link (for persons, username/password)
4. Fill username (email) + password
5. Submit → redirects to SSO → shows "Anmeldung in der BA-Secure App bestätigen"
6. **4-minute window** for push confirmation on phone
7. **After 2FA confirmed: "Weiter" button appears on SSO page — MUST click it ONCE.** Page does NOT auto-redirect.
8. After Weiter: redirects to `web.arbeitsagentur.de/profil/profil-ui/pd/?state=...` — logged in

### CRITICAL: Weiter Button Detection (Root Cause of 6+ Failed Logins)
The Weiter button detection is the single hardest part of this flow. Two traps:

1. **"Weiter" appears in body text BEFORE 2FA is confirmed** — it's in page navigation/footer.
   `if "Weiter" in page.inner_text("body")` fires immediately → clicks Weiter too early → kills SSO flow.

2. **"bestätigen" NEVER disappears from body text** after 2FA confirmation.
   `if "bestätigen" not in body.lower()` as precondition for Weiter → never fires → Weiter never clicked → loops until timeout.

**Correct approach**: Poll for the Weiter BUTTON as a clickable element, not body text. Wait until the 2FA timer text disappears (indicating confirmation), THEN click the Weiter button:
```python
weiter_clicked = False
for i in range(48):  # 4 min max, 5s intervals
    time.sleep(5)
    url = page.url
    if "sso.arbeitsagentur.de" not in url and "login-actions" not in url:
        print("LOGIN_SUCCESS!")
        break
    # Check for Weiter button via DOM (not body text!)
    has_weiter = page.evaluate("""() => {
        const btns = document.querySelectorAll('button, a, input[type="submit"]');
        for (const btn of btns) {
            if (btn.textContent.trim() === 'Weiter') return true;
        }
        return false;
    }""")
    if has_weiter and not weiter_clicked:
        # Click Weiter ONCE — never click it multiple times
        page.evaluate("""() => {
            const btns = document.querySelectorAll('button, a, input[type="submit"]');
            for (const btn of btns) {
                if (btn.textContent.trim() === 'Weiter') { btn.click(); return; }
            }
        }""")
        weiter_clicked = True
        time.sleep(5)
```

### RULE: One Login Attempt Per Session
NEVER ask the user for 2FA confirmation twice in the same session. If the first attempt fails (2FA timer expires, Weiter not clicked, etc.), do NOT retry. User frustration is extremely high. One attempt, one chance. If it fails, note it and move on.

### False "ALREADY_LOGGED_IN" Trap
`web.arbeitsagentur.de/portal/mittellungen/` returns HTTP 200 with `robots.txt` body (`User-agent: * Disallow: /`) when NOT authenticated. Anti-bot block, NOT success. Always verify body contains expected content (e.g. "Kundennummer" for profile page).

### Persistent Profile Does NOT Help for BA SSO
BA SSO cookies expire between sessions. `persistent_context=True` + `user_data_dir` does NOT preserve SSO session. Fresh 2FA login required each time.

### Push vs TOTP
- BA-Secure App = **push notification** (not TOTP)
- User MUST have app open and confirm
- Alternative: set up TOTP as second factor in portal settings
- If TOTP enabled: can automate with `pyotp`

### Automation Options
| Approach | Pros | Cons |
|----------|------|------|
| Manual push once → grab cookie | Simple, works | Cookie expires ~24-48h |
| Switch to TOTP | Fully automatable | User must configure in portal |
| ADB/macOS automation to click "Bestätigen" | No user needed | Complex, brittle |

## Cookie Banner Dismissal (CRITICAL)

User correction: "es kann nicht so schwer einfach immer den banner wegzuclicken sobald er kommt, einmal händisch dann automatisiert."

### Rule: Dismiss inline, proactively, every time
Cookie banners (Usercentrics, OneTrust, etc.) reappear on SPA navigation.
Dismiss them **inline** before every interaction step, not as an afterthought.

### Inline dismiss function (reuse in every script)
```python
def dismiss_cookie_banner(page):
    """Call this after every page.goto() and after every click that might navigate."""
    try:
        page.evaluate("""() => {
            const btns = document.querySelectorAll('button, a, [role="button"]');
            for (const btn of btns) {
                const text = (btn.textContent || '').trim().toLowerCase();
                if (text === 'alle akzeptieren' || text === 'accept all' || text === 'alle erlauben') {
                    btn.click(); return true;
                }
            }
            if (typeof UC_UI !== 'undefined' && UC_UI.acceptAll) { UC_UI.acceptAll(); return true; }
            return false;
        }""")
    except:
        pass
```

### NEVER use a background thread for cookie dismissal
Playwright sync API is NOT thread-safe. A `threading.Thread` that calls
`page.evaluate()` will crash with:
```
greenlet.error: Cannot switch to a different thread
```
This produces hundreds of lines of traceback noise and silently breaks the
cookie dismissal. Always call `dismiss_cookie_banner(page)` inline from the
main thread, after each navigation step.

## Common Pitfalls

1. **Profile path with spaces** → symlink to `/tmp/short_name`
2. **Firefox running** → kills Camoufox persistent context
3. **Compatibility.ini mismatch** → delete it, let Camoufox recreate
4. **Cookie expiry in milliseconds** → Firefox cookies.sqlite stores 13-digit ms timestamps. Playwright expects seconds. Normalize: `>1e15 → /1e6 (µs)`, `>1e12 → /1e3 (ms)`, else seconds. `expires=0` → use `-1` (session cookie). Playwright rejects `expires=0` with "Cookie should have a valid expires".
5. **SSO session cookies expire fast** → KC_AUTH_SESSION_HASH ~24-48h
6. **No uBlock** → immediate bot detection on Cloudflare/Akamai
7. **Cookie banner intercepts clicks** → remove via JS before clicking. Dismiss INLINE after every navigation, never via background thread.
8. **Version dialog blocks launch** → delete compatibility.ini
9. **Weiter button body-text detection = ALWAYS WRONG** → "Weiter" appears in body text before 2FA is confirmed; "bestätigen" never disappears after confirmation. Use DOM `querySelectorAll` to find the button element, not `page.inner_text`. This caused 6+ consecutive login failures.
10. **Weiter loop bug** → after login success (URL changed to web.arbeitsagentur.de/profil/...), script continued clicking Weiter because body still contained "Weiter". Use `weiter_clicked` flag, click exactly ONCE, break immediately when URL leaves sso.arbeitsagentur.de.
11. **One 2FA attempt per session** → NEVER ask user for 2FA twice in same session. If login fails, note it and move on. User frustration is extremely high.
12. **Camoufox addons need extracted dir, not .xpi** → `confirm_paths()` checks `os.path.isdir()` + `manifest.json`. Download .xpi, `unzip` to directory, pass directory path.
13. **Playwright sync API greenlet constraint** → cannot call `page.evaluate()` from socket handler thread. Use queue-based dispatch: socket thread enqueues `(cmd, args)`, main thread executes + returns result via response queue.
14. **One-off scripts vs persistent server** → every one-off script starts from zero, loses session, requires fresh 2FA. ALWAYS prefer the interactive CLI server pattern. User explicitly frustrated by repeated from-scratch scripts.
15. **Weiter button is ALWAYS in DOM** → even on 2FA page, Weiter exists as a clickable element. Clicking it before 2FA confirmation kills SSO flow. Wait for user to confirm in BA-Secure app, THEN click Weiter. In interactive CLI mode: ask user "bestätigt?", then click Weiter manually.
16. **Duplicate DOM IDs → Playwright strict mode violation** → sites like World of Pizza render the same `#loginUsername` / `#loginPassword` twice (one hidden, one in a modal). `locator("#id").click()` fails with "strict mode violation: resolved to 2 elements". Fix: use `.last` (the visible one in the modal) + `force=True` to skip visibility checks: `page.locator("input#loginUsername").last.fill(email, force=True)`.
17. **Playwright threading = greenlet death** → `page.evaluate()` from a `threading.Thread` crashes Playwright sync API with `greenlet.error: Cannot switch to a different thread`. Never use background threads for page interaction. All page operations must run on the main thread.
18. **Cookie banner reappears on SPA navigation** → Usercentrics CMP re-renders after every client-side route change. Dismiss inline after every `page.goto()` and after any click that triggers navigation. See `dismiss_cookie_banner()` above.
19. **`page.evaluate()` with arguments** → Playwright sync API `page.evaluate(expression, arg)` takes exactly 2 positional args (expression + arg), not multiple. Pass multiple values as a JSON array: `page.evaluate("([a, b]) => {...}", [val1, val2])`.
20. **PyYAML CLoader missing → Camoufox import fails** → If `from camoufox.sync_api import Camoufox` fails with `ImportError: cannot import name 'CLoader' from 'yaml'`, the venv has a pure-Python PyYAML shadowing the C-extended one. Fix: `LDFLAGS="-L/opt/homebrew/lib" CPPFLAGS="-I/opt/homebrew/include" uv pip install --python <venv-python> --force-reinstall --no-binary :all: pyyaml`. Then verify: `python -c "import yaml; print(yaml.__with_libyaml__)"` must be `True`. Also check for shadowing: if `yaml.__file__` points to a different Python version's site-packages, delete that path.
21. **Cross-browser cookie transfer: filter Cloudflare cookies** → When transferring session cookies between browsers, **NEVER** include `cf_clearance` or `__cf_bm`. These are bound to User-Agent + IP address of the originating browser. Only inject application session cookies.
22. **Direct Firefox→Camoufox cookie transfer works** → No Playwright Firefox intermediate step needed. Workflow: `pkill -f firefox` → wait 3s → copy `cookies.sqlite` → extract domain cookies (excl. `cf_clearance`/`__cf_bm`) → normalize expiry (ms→s, 0→-1) → `camoufox load_cookies` → navigate.
23. **cookies.sqlite missing session cookies while Firefox runs** → Firefox stores session cookies (expiry=0) in memory only. Copying `cookies.sqlite` while Firefox is running gives you only persistent cookies (analytics, consent, etc.) — NOT auth session cookies. Many sites (Cerebras, Zhipu/BigModel) use HttpOnly session cookies that are invisible in `cookies.sqlite` until Firefox closes gracefully. See "Three-Tier Cookie Extraction Strategy" above.
24. **Session store recovery.jsonlz4 only has cookies for ACTIVE tabs** → Firefox's session store backup (`sessionstore-backups/recovery.jsonlz4`) contains session cookies ONLY for currently open tabs. If the target site's tab was closed, its session cookies won't be here either. This is a secondary source, not a primary one.
25. **Python lz4 broken in Hermes venv — use Node.js** → `import lz4.block` fails with `ModuleNotFoundError: No module named 'lz4._version'` in the Hermes venv (binary incompatibility). To decompress Firefox `.jsonlz4` files, use Node.js: `cd ~/projects/camofox-browser && npm install lz4 && node -e "..."`. The mozLz4 format is: 8-byte magic header + 4-byte LE decompressed size + lz4 compressed data.
26. **Never `pkill -9` Firefox for cookie extraction** → SIGKILL skips graceful shutdown, session cookies are NOT flushed to `cookies.sqlite`. Always use `osascript -e 'tell application "Firefox" to quit'` or `pkill firefox` (SIGTERM) and wait 3-5 seconds.
27. **REST API cookie injection requires {"cookies": [...]} wrapper** → The Camoufox server `POST /sessions/:userId/cookies` endpoint expects `{"cookies": [...]}`, not a bare array. Also: `expires` must be in seconds (not ms), and `expires=0` is rejected — use `-1` for session cookies.
## Quick Reference URLs

| Purpose | URL |
|---------|-----|
| BA Profile (entry) | https://web.arbeitsagentur.de/profil/profil-ui/pd/ |
| BA Login | https://www.arbeitsagentur.de/login |
| SSO Auth | https://sso.arbeitsagentur.de/auth/realms/OCP/... |
| BA-Secure App info | https://www.arbeitsagentur.de/ba-secure-app |
| 2FA Setup | https://www.arbeitsagentur.de/en/two-factor-authentication |

## Debugging Commands

```bash
# Check running processes
ps aux | grep -i camoufox
ps aux | grep -i firefox

# Check profile locks
ls -la /path/to/profile/.parentlock /path/to/profile/lock

# Check cookies.sqlite
sqlite3 cookies.sqlite "SELECT name, host, expiry FROM moz_cookies WHERE host LIKE '%arbeitsagentur%';"

# Camoufox version
PYTHONPATH="" python3 -c "from camoufox.pkgman import installed_verstr; print(installed_verstr())"
```

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/camoufox_cli.py` | CLI client (REST, talks to :9377). Symlinked as `/usr/local/bin/camoufox`. |
| `scripts/camoufox_server.py.retired` | Old Python socket server. Retired — replaced by Node REST server at `~/projects/camofox-browser/`. |
| `scripts/camoufox-cookie-injection.py` | Generic Camoufox cookie injection template |
| `scripts/prevention.py` | Camoufox browser context creation + route interception |
| `scripts/capsolver.py` | Capsolver API integration (Turnstile, reCAPTCHA, hCaptcha, FunCaptcha) |
| `scripts/captcha_flow.py` | Combined prevention → detect → solve flow |
| `scripts/browser_repl.py` | Interactive REPL for exploring new sites |
| `scripts/actor_checker.py` | Actor-Checker LLM automation loop |
| `scripts/ryanair.py` | Deterministic Ryanair booking |
| `scripts/ba_login_camoufox.py` | Full automated BA login with 2FA wait |
| `scripts/inject_ba_cookies.py` | Extract & inject BA cookies from Firefox |
| `scripts/record_mouse.swift` | CGEvent tap mouse trajectory recorder |
| `scripts/hold_click.swift` | Swift CGEvent press-and-hold for PerimeterX bypass |
| `scripts/extract_firefox_cookies.py` | Extract session cookies from Firefox profile for Camoufox. Kills Firefox, normalizes expiry ms→s, filters Cloudflare cookies. Usage: `python3 scripts/extract_firefox_cookies.py "<FF_PROFILE>.Profil 4" /tmp/giuli_cookies.json` |
| `scripts/lieferando_extract_menu.js` | TreeWalker JS — extracts all menu items + prices from a Lieferando restaurant page. Pass to `camoufox eval`. See `references/lieferando-checkout.md` → "Menu Price Scraping". |
