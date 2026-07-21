---
name: camoufox
description: "Camoufox persistent browser automation — anti-bot bypass, CAPTCHA solving, SSO/cookie injection, and headless control patterns. Covers the interactive CLI server, route interception, Capsolver integration, PerimeterX/Cloudflare bypass, Angular/React SPA automation, Firefox cookie extraction, and security incident response. Use when user needs persistent browser automation on anti-bot sites or security incident handling. Triggers: Camoufox, anti-bot, CAPTCHA, Cloudflare bypass, cookie injection, stealth browser, session theft, security incident, Clerk revocation"
version: 7.3
trigger: camoufox automation, persistent browser session, web automation, browser CLI, camoufox loop, cookie rotation, firefox cookie extraction, SSO account switching, CAPTCHA solving, Cloudflare Turnstile bypass, anti-bot, headless browser, curl_cffi, security incident, session theft, Clerk session revocation, Lieferando, food delivery, online ordering, restaurant order, pizza order, voucher code
---

# Camoufox — Persistent Browser Automation & Anti-Bot Toolkit

One Camoufox engine, two interfaces. Both route through the same Node.js REST server.

## Routing — which tool for what

| Task | Use | Why |
|------|-----|-----|
| Navigate to URL | `browser_navigate` | Hermes native, auto-snapshot |
| Read page content | `browser_snapshot` | Structured aria tree + refs |
| Click element | `browser_click(ref)` | Hermes native, ref-based |
| Type into element | `browser_type(ref)` | Hermes native, ref-based |
| Keyboard press | `browser_press` | Hermes native |
| Scroll page | `browser_scroll` | Hermes native |
| Navigate back | `browser_back` | Hermes native |
| Screenshot + analysis | `browser_vision` | Hermes native, returns analysis |
| JS evaluate | `browser_console(expression=)` | Hermes native |
| List images | `browser_get_images` | Hermes native |
| **Click by CSS selector** | `camoufox click_element <sel>` | CLI-only, no aria ref needed |
| **Fill by CSS selector** | `camoufox fill_element <sel> <text>` | CLI-only |
| **Type by CSS selector** | `camoufox type_in_element <sel> <text>` | CLI-only |
| **Scroll to CSS selector** | `camoufox scroll_to_element <sel>` | CLI-only |
| **Query elements by CSS** | `camoufox get_elements <sel>` | CLI-only, returns coords+attrs |
| **Click at coordinates** | `camoufox click <x> <y>` | CLI-only, canvas/maps/signature pads |
| **Cookie file export** | `camoufox save_cookies <path>` | CLI-only |
| **Cookie file import** | `camoufox load_cookies <path>` | CLI-only |
| **Clear cookies** | `camoufox clear_cookies` | CLI-only |
| **Multi-step automation** | `camoufox loop '<json>'` | CLI-only, declarative sequencer |
| **Server lifecycle** | `camoufox start/stop/ping` | CLI-only |

**Rule**: Use Hermes browser tools by default. Drop to CLI only for CSS selector ops, coordinate clicks, cookie I/O, or loop automation.

## Architecture (Unified Backend)

One Camoufox engine, two interfaces. Both route through the same Node.js REST server.

- **REST Server** (`~/projects/camofox-browser/`): Node.js server wrapping Camoufox (Firefox fork with C++ fingerprint spoofing). Runs on `http://localhost:9377`. Downloads Camoufox binary on first install. Provides accessibility tree snapshots with element refs (e1, e2), multi-tab support, persistent profiles per userId, uBO active by default.
- **CLI** (`scripts/camoufox_cli.py`, symlinked as `/usr/local/bin/camoufox`): REST client. Same command interface as before (goto, click_element, body, etc.) but talks HTTP to :9377 instead of unix socket. Tab state persisted in `/tmp/camoufox_cli_state.json`.
- **Hermes Browser Tools** (`browser_navigate`, `browser_click`, `browser_snapshot`, etc.): When `CAMOFOX_URL` is set in `~/.hermes/.env`, Hermes browser tools auto-route through the same REST server. Full accessibility tree integration (refs, snapshots, screenshots). See `references/hermes-browser-camofox-backend.md`.
- **Config presets** (`browser.camofox` in `config.yaml`): `managed_persistence`, `adopt_existing_tab`, `rewrite_loopback_urls`, `loopback_host_alias`. These activate automatically when `CAMOFOX_URL` is set.
- **Old Python socket server** (`scripts/camoufox_server.py.retired`): Retired. Was a unix socket server with Playwright in main thread. Replaced by Node REST server for unification.

## Mode / Pattern Selection

| Need | Reference | Key Commands/Patterns |
|------|-----------|----------------------|
| Interactive browser session | **CLI Commands** (below) | `camoufox start`, `goto`, `click_element`, `body` |
| Anti-bot / cookie injection / 2FA | `references/automation-patterns.md` | Cookie extraction, BA-Secure 2FA, persistent profiles |
| SSO access / token capture / Gmail | `references/browser-ctrl.md` | SSO cookie injection, Bearer token capture, curl_cffi |
| CAPTCHA prevention & solving | `references/captcha-bypass.md` | Camoufox prevention, Capsolver, PerimeterX, baxia slider |
| Angular/React SPA forms | `references/angular-spa-form-automation.md` | `dispatchEvent`, `markAsDirty()`, `type()` vs `fill()` |
| Ryanair Angular patterns | `references/ryanair-angular-picker.md` | Country/airport picker, calendar dispatchEvent |
| Signature pad automation | `references/signature-pad-automation.md` | Shadow DOM canvas, `page.mouse` replay |
| Google-auth sites | `references/persistent-context-google-auth.md` | Playwright Firefox `launch_persistent_context` |
| GitHub profile pinning | `references/github-profile-pinning.md` | Cookie injection + pin dialog automation |
| Lovable source extraction | `references/lovable-source-extraction.md` | Vite dev server `?raw` source files |
| Lieferando checkout | `references/lieferando-checkout.md` | Order flow, cookie transfer, PayPal iframe |
| Lieferando address input | `references/lieferando-address-input.md` | React combobox keyboard typing, building number prompt, address verification |
| Lieferando menu scraping | `references/lieferando-menu-scraping.md` | Restaurant list + menu item price extraction, TreeWalker pattern |
| World of Pizza webshop | `references/wop-webshop.md` | Login, store selection, voucher system |
| Headless mode setup | `references/headless-mode.md` | Mode switching, Cloudflare considerations |
| Starlink account portal | `references/starlink-account-portal.md` | Login, order/RMA status, ticket creation |
| Stytch-based auth (Vapi/Groq) | `references/stytch-auth.md` | Fingerprint-bound vs transferable cookies |
| BA-Secure 2FA details | `references/ba-secure-2fa.md` | Full login flow, cookies, 2FA |
| uBlock Origin setup | `references/camoufox-ubo-setup.md` | Addon extraction, thread safety |
| Playwright gotchas | `references/camoufox-playwright-gotchas.md` | Threading, duplicate IDs, PyYAML CLoader |
| Engine comparison | `references/engine-test-results.md` | Camoufox vs Patchright vs Nodriver |
| CAPTCHA trajectory recorder | `references/captcha-trajectory-recorder.md` | Mouse trajectory recording + replay |
| PerimeterX + Surfshark VPN | `references/perimeterx-surfshark-vpn.md` | PX bypass, VPN integration |
| Playwright Firefox bugfix | `references/playwright-firefox-bugfix.md` | pageError.location.url crash fix |
| Actor-checker automation | `references/actor-checker-automation.md` | LLM actor-checker loop |
| Alibaba baxia CAPTCHA | `references/alibaba-baxia-captcha.md` | Full approach matrix |
| HUK24 e-scooter insurance | `references/huk24-e-scooter-insurance.md` | SYNACT SPA form flow, Friendly Captcha auto-solve, phone fallback |
| Hermes native camofox backend | `references/hermes-browser-camofox-backend.md` | How Hermes browser tools route through camofox-server, `CAMOFOX_URL` activation, config presets |
| Clerk modal automation | `references/clerk-modal-automation.md` | Clerk custom elements, session management API, GitHub OAuth auto-auth, 2FA setup |
| **Security incident response** | `references/security-incident-response.md` | Clerk session theft detection, revocation, 2FA setup, fraud report |
| **Amazon cookie injection** | `references/amazon-cookie-injection.md` | Fresh cookie extraction from running Firefox, userId matching, session-token verification |
| **Amazon return workflow** | `references/amazon-return-workflow.md` | Complete return automation: order history, return reason selection, a-declarative dropdown workaround |
| **Amazon SPA `a-declarative` limitation** | `references/amazon-spa-declarative-limitation.md` | `selectOption` doesn't trigger Weiter button render, standalone script workaround |
| **Credential rotation (token/key rotation)** | `references/credential-rotation.md` | HuggingFace token rotation, password-confirmed settings pages, no-API-bypass pattern, `~/.zshenv` update workflow |
| **Direct REST API with custom userId** | `references/direct-rest-api-custom-userid.md` | When cookies are pre-injected for a specific userId, Hermes browser tools can't be used — drive the REST server directly via curl. sessionKey gotcha, tab creation, core ops, extracting hidden values from aria snapshots |

## CLI Commands

Only commands NOT covered by Hermes browser tools. See routing table above.

```bash
# Server lifecycle
camoufox start [--headless]             # launch REST server
camoufox ping                           # check server health
camoufox stop                            # stop server

# CSS selector ops (when aria refs don't work — custom elements, canvas overlays)
camoufox get_elements <sel>              # query elements, return coords+attrs
camoufox ge <sel>                        # alias
camoufox click_element <sel>             # Playwright click by CSS
camoufox ce <sel>                        # alias
camoufox type_in_element <sel> <text> [delay_ms]  # keyboard type by selector
camoufox tie <sel> <text> [delay_ms]              # alias
camoufox fill_element <sel> <text>        # Playwright fill (clears first)
camoufox fe <sel> <text>                 # alias
camoufox scroll_to_element <sel>         # scroll element into view
camoufox ste <sel>                       # alias

# Coordinate ops (canvas, signature pads, maps — no aria ref available)
camoufox click <x> <y>                   # JS dispatchEvent at coordinates
camoufox move <x> <y>                    # JS mousemove

# Cookie I/O (Hermes tools have no cookie file export/import)
camoufox save_cookies <path>             # export document.cookie (non-HttpOnly)
camoufox load_cookies <path>             # import via POST /sessions/:userId/cookies
camoufox clear_cookies                   # expire cookies via JS (HttpOnly NOT cleared)

# Declarative automation (multi-step with branching, conditions, waits)
camoufox loop '<json>'                   # JSON steps
camoufox loop --file steps.json          # steps from file
camoufox loop --inline 'cmd | cmd'       # pipe-separated inline
```

## CLI vs Hermes Browser Tools — Routing Guide

Both interfaces share the same Camoufox browser via the same REST server.
Use the simplest one for each task. PREFER Hermes browser tools for common
operations; use CLI only for what Hermes tools can't do.

### Use Hermes browser tools (PREFERRED)

`browser_navigate`, `browser_snapshot`, `browser_click(@eN)`,
`browser_type(@eN, text)`, `browser_press`, `browser_scroll`,
`browser_back`, `browser_vision`, `browser_console(expression=)`,
`browser_get_images` — all auto-route through Camoufox when `CAMOFOX_URL` is set.

### Use CLI (CLI-only operations)

`click_element <css>`, `fill_element <css>`, `type_in_element <css>`,
`scroll_to_element <css>`, `get_elements <css>`, `click <x> <y>` / `move <x> <y>`,
`save_cookies` / `load_cookies` / `clear_cookies`, `loop`, `start` / `stop` / `ping`.

Full routing table: `references/hermes-browser-camofox-backend.md`.

## Interaction Model (CRITICAL)

**Action → Judge → Action → Judge** loop. This is the ONLY pattern that works.

### Interaction Priority (USER PREFERENCE — NON-NEGOTIABLE)

1. **`browser_snapshot` → `browser_click(@eN)`/`browser_type(@eN)`** — PRIMARY. Hermes browser tools, aria refs. Default for all interaction.
2. **`camoufox get_elements <css>` → `camoufox click_element <css>`** — SECONDARY. CSS selectors when aria refs don't cover the element (custom elements, `pie-button`, canvas overlays).
3. **`camoufox get_elements <css>` → coords → `camoufox click <x> <y>`** — TERTIARY. Canvas, signature pads, maps.
4. **`browser_snapshot`** — JUDGE. Verify results after every action.
5. **`browser_console(expression=)` JS** — fallback for SPA buttons that don't respond to native clicks.
6. **`browser_vision`** — LAST RESORT. When DOM text is genuinely ambiguous.

### Step-by-step loop
1. **Check for blocking modals/popups FIRST** — `browser_snapshot` and scan for modals
2. **Query**: `browser_snapshot` for refs, OR `camoufox ge 'selector'` for CSS query
3. **Act**: `browser_click(@eN)` or `camoufox click_element 'selector'` or `camoufox click <x> <y>`
4. **Judge**: `browser_snapshot` — verify result
5. Repeat

## Loop Command — Declarative Automation Sequencer

```bash
# JSON inline
camoufox loop '{"steps":[{"goto":"https://example.com"},{"sleep":3},{"body":2000,"print":true}]}'

# File
camoufox loop --file steps.json

# Inline pipe-separated
camoufox loop --inline 'goto https://example.com | sleep 3 | click_element button:has-text("Add") | body 2000'
```

### Step types (JSON)
| Step | Description |
|------|-------------|
| `{"goto": "url"}` | Navigate |
| `{"click_element": "selector"}` | Native Playwright click |
| `{"fill_element": ["selector", "text"]}` | Clear + type |
| `{"scroll_to_element": "selector"}` | Scroll into view |
| `{"sleep": seconds}` | Wait |
| `{"wait_for": "selector", "timeout": 10000}` | Poll for element |
| `{"if_exists": "selector", "then": {step}, "else": {step}}` | Conditional |
| `{"eval": "js code"}` | Read-only JS |
| `{"body": 2000, "print": true}` | Get body text |
| `{"clear_cookies": true}` | Clear cookies |
| `{"save_cookies": "/path"}` | Export cookies |

## Cookie Rotation Workflow

For switching accounts on the same site:
```bash
camoufox save_cookies /tmp/account_a.json
camoufox clear_cookies
camoufox goto "https://accounts.google.com/Logout"
# ... login with second account ...
# When done, restore:
camoufox clear_cookies
camoufox load_cookies /tmp/account_a.json
camoufox goto "https://target-site.com/"
```

## Firefox Cookie Extraction (for SSO)

**CRITICAL**: Firefox stores session cookies (expiry=0) in MEMORY, not in `cookies.sqlite`.
While Firefox is running, `cookies.sqlite` only has persistent cookies (analytics, consent).
Auth cookies for many sites (Cerebras, Zhipu, etc.) are HttpOnly session cookies → invisible
until Firefox closes gracefully. See `references/automation-patterns.md` → "Three-Tier Cookie
Extraction Strategy" for the full extraction workflow.

### Quick workflow (persistent cookies only — while Firefox runs)
```bash
# 1. Find the Firefox profile (check ~/Library/Application Support/Firefox/Profiles/)
# 2. Copy cookies.sqlite (WAL too for uncommitted entries)
cp "$PROFILE/cookies.sqlite" /tmp/ff_cookies.sqlite
cp "$PROFILE/cookies.sqlite-wal" /tmp/ff_cookies.sqlite-wal 2>/dev/null

# 3. Extract cookies as JSON (normalize expiry: ms→s, 0→-1)
python3 -c "
import sqlite3, json
conn = sqlite3.connect('/tmp/ff_cookies.sqlite')
rows = conn.execute('''
    SELECT name, value, host, path, expiry, isSecure, isHttpOnly, sameSite
    FROM moz_cookies WHERE host LIKE '%target-domain%'
''').fetchall()
conn.close()
# ... normalize and save as JSON ...
"

# 4. Load into Camoufox
camoufox clear_cookies
camoufox load_cookies /tmp/cookies.json
camoufox goto "https://target-site.com/"
```

### For session cookies (must close Firefox first)
```bash
# Graceful close (NOT pkill -9 — SIGKILL skips cookie flush)
osascript -e 'tell application "Firefox" to quit'
sleep 5
cp "$PROFILE/cookies.sqlite" /tmp/ff_cookies_closed.sqlite
# Now all session cookies are in cookies.sqlite
```

### For session store backup (cookies for active tabs only)
```bash
# Uses lz4 — Python lz4 often broken in venvs, use Node.js instead
cd ~/projects/camofox-browser && npm install lz4
node -e "
const lz4 = require('lz4'), fs = require('fs');
const data = fs.readFileSync('$PROFILE/sessionstore-backups/recovery.jsonlz4');
const output = Buffer.alloc(data.readUInt32LE(8));
const len = lz4.decodeBlock(data.slice(12), output);
const session = JSON.parse(output.toString('utf8', 0, len));
(session.cookies || []).filter(c => (c.host||'').includes('domain')).forEach(console.log);
"
```

**IMPORTANT**: Filter out `cf_clearance` + `__cf_bm` (UA+IP bound) — only inject app session cookies.

## Server Internals

- **Node.js REST server** at `http://localhost:9377` — serves accessibility tree snapshots, element refs, multi-tab, cookie persistence.
- **Camoufox engine**: Firefox fork with C++ fingerprint spoofing. `humanize=True`, uBO active by default. Launched via `camoufox-js` npm package.
- **fnm v22 required**: Server must be started with `fnm use 22 && node server.js`. Homebrew node v26 causes `NODE_MODULE_VERSION` mismatch with better-sqlite3.
- **Tab state**: CLI persists `tab_id` in `/tmp/camoufox_cli_state.json` across invocations. Tab auto-created on first `goto`.
- **Hermes browser tools**: Auto-activate when `CAMOFOX_URL=http://localhost:9377` is in `~/.hermes/.env`. `is_camofox_mode()` checks this env var. Config presets (`browser.camofox.*`) activate automatically.
- **Accessibility refs**: Server builds aria snapshot via `page.locator('body').ariaSnapshot()`, assigns refs (e1, e2) to interactive elements. Refs map to `getByRole(role, {name}).nth(n)` locators. Refs reset on navigation — call snapshot after each nav.
- **Screenshot endpoint**: Returns raw PNG bytes (`Content-Type: image/png`), NOT base64 JSON.

## Key Lessons

1. **Playwright native click over coordinate click**: `click_element` (REST `/click` with selector) handles scrollIntoView, actionability checks, SPA event dispatch. Coordinate clicks via JS `dispatchEvent` are isTrusted=false — some SPAs reject them.
2. **get_elements over eval**: `get_elements` takes a CSS selector, returns structured data (tag, id, class, text, coords). No shell escaping.
3. **domcontentloaded not networkidle**: Server uses `waitForPageReady` with settle, never `networkidle`. SPAs with WebSockets/polling never reach idle.
4. **Persistent profiles**: Server persists storage state per userId in `~/.camofox/profiles/`. CLI uses `cli_user` as userId. Hermes uses `hermes_<hash>` (managed persistence) or random (ephemeral).
5. **One server instance**: Reuse the same browser for all tasks. CLI + Hermes browser tools share the same server.
6. **fnm v22 not homebrew v26**: `npm rebuild` must run with the same node version that starts the server. fnm v22.22.3 (MODULE_VERSION 127) is the runtime. **Hermes terminal tool uses `/bin/bash` not `/bin/zsh`** — if `fnm env` is only in `.zshrc`, bash sessions use Homebrew node v26 → crash. Fix: `eval "$(fnm env --use-on-cd)"` must be in `~/.bashrc` too.
7. **PREFER `click_element` over coordinate clicks** — native Playwright handles scrollIntoView, actionability checks, SPA event dispatch.
8. **`fill_element` for special chars** — `type` can mangle `@` in email fields. `fill_element` uses Playwright `fill()` which clears first then sets value atomically.
9. **FULL AUTOMATION EXPECTED** — Do NOT ask user to perform manual steps. Use browser automation for everything including login, 2FA setup, and security incident response. User feedback: "stop asking me for doing stuff".

## Top Pitfalls (see reference files for full list)

0. **NEVER write standalone Python scripts for browser automation — use Hermes browser tools interactively (USER PREFERENCE — NON-NEGOTIABLE)**: Every `python -c` or background Python script opens a NEW Camoufox browser session, losing ALL state (cookies, address, basket, login). This is the #1 cause of failed automation. The user has corrected this MULTIPLE times: "DU BENUTZT IMMERNOCH SKRIPTE STATT INTERAKTIV MIT DEM BROWSER ZU INTERAGIEREN", "du lässt x verschiedene camofox browser parallel laufen statt aufzuräumen", "was flaky ist sind deine python skripte HÖR ENDLICH DAMIT AUF", "ich sehe zwei camofox guis aber beide sind auf der lieferando startseite". **Correct approach**: Use `browser_navigate` → `browser_snapshot` → `browser_click(@eN)` → `browser_snapshot` (validate!) → repeat. ONE session, step by step, validating after every action. NEVER close the browser until the task is complete. NEVER spawn parallel browser processes. If the Hermes browser tools return 500/503, fix the Camoufox SERVER (see pitfall #45 for version.json fix) — don't fall back to Python scripts. **This pitfall has been violated in 3+ separate sessions (2026-07-12, 2026-07-15, 2026-07-17) — the user's frustration escalates each time. If you catch yourself writing `python -c` or `terminal(background=true)` with a Python script for browser interaction, STOP IMMEDIATELY and switch to Hermes browser tools.**

0a. **Validate after EVERY action — don't blindly click and hope**: After every `browser_click`, `browser_type`, or `browser_navigate`, call `browser_snapshot` or `browser_console` to VERIFY the page state changed as expected. User correction: "du musst ja validieren wo du hinkommst, deshalb ja wie gesagt interaktiv". Blindly chaining actions without validation leads to 10+ failed attempts on the wrong page. The pattern is ALWAYS: act → snapshot → judge → act → snapshot → judge.

0b. **Load the RIGHT skill — grocery-shopping ≠ Lieferando**: When the user says "Lieferando bestellen", "pizza bestellen", "lieferando gutschein", load the `camoufox` skill (which has `references/lieferando-checkout.md` + `references/lieferando-address-input.md`), NOT `grocery-shopping` (which covers REWE/Knuspr/dm/Rossmann grocery price comparison). Lieferando is restaurant food delivery, not grocery shopping. Loading the wrong skill means you miss critical pitfalls (React combobox keyboard typing, Domino's configurator required fields, promo modals, voucher 24h lock) and repeat mistakes the skill already documents. **Before starting any browser automation task, check: does a `references/` file for this specific site already exist in the `camoufox` skill?**

1. **Hermes browser tools NOW WORK through Camoufox**: When `CAMOFOX_URL=http://localhost:9377` is set in `~/.hermes/.env` and the Node server is running, `browser_navigate`, `browser_click`, `browser_snapshot` etc. auto-route through the same Camoufox backend as the CLI. No need to use the CLI exclusively anymore — Hermes browser tools and CLI share the same browser. BUT: if `CAMOFOX_URL` is NOT set, Hermes browser tools fall back to `agent-browser` (plain Chromium, no anti-detection). Always verify `CAMOFOX_URL` is set before using Hermes browser tools on anti-bot sites. See `references/hermes-browser-camofox-backend.md`.
2. **ALWAYS use Camoufox for any form with captchas or SPA forms**: This includes insurance forms, government portals, shopping checkout. Camoufox headed mode auto-solves Friendly Captcha PoW, Cloudflare Turnstile, and other browser-fingerprint-based captchas.
3. **Headed vs Headless — know when to use which**: For forms with server-side bot detection (e.g. HUK24 registration), headless mode fails with "technical error". Use headed mode (`camoufox start` without `--headless`) for registration/login flows. Headless is fine for scraping/read-only.
4. **Server process must use fnm v22**: The Node.js REST server must be started with `fnm use 22` (v22.22.3). Homebrew node v26 causes `NODE_MODULE_VERSION` mismatch with better-sqlite3. If server fails to launch browser, check `node --version` in the server process.
   - **CRITICAL — Hermes `terminal` tool uses `/bin/bash`, NOT `/bin/zsh`**: If `fnm env` is only in `~/.zshrc`, bash sessions never source it → Homebrew node v26 → `NODE_MODULE_VERSION` mismatch → server crashes silently. This is the #1 cause of `camoufox ping` returning "Cannot connect to http://localhost:9377" when you expect the server to be running. **Fix**: ensure `eval "$(fnm env --use-on-cd)"` is in `~/.bashrc` (not just `.zshrc`). Verify from a terminal tool call: `node --version` must show v22.x. When starting the server from a background terminal, prepend `eval "$(fnm env)" && fnm use 22 &&` before `node server.js`.
5. **Proactive modal detection**: ALWAYS check for blocking modals BEFORE any interaction. SPAs render modal overlays that intercept ALL clicks.
6. **Stale tab recovery**: If `goto` returns 404 (tab was GC'd), CLI auto-creates a fresh tab. No manual intervention needed.
7. **`:has-text()` is Playwright-only, NOT CSS**: `get_elements` uses `document.querySelectorAll()` which only accepts standard CSS. Use `click_element` for `:has-text()` selectors — the REST `/click` endpoint accepts both `selector` (CSS) and `ref` (aria tree ref).
8. **Google SSO cookie injection cross-browser does NOT work**: Google binds session cookies to browser fingerprint. Must do password + 2FA flow inside Camoufox.
9. **NEVER kill the server while the user has an active session**: Always `ping` first. The user may have manually completed a flow.
10. **Full automation expected**: Do NOT ask user to log in, fill forms, or click buttons. Research and try alternatives first. User feedback: "why are you being too incompetent too inject the session" — use REST API for cookie injection, not JavaScript.
11. **Use Capsolver for CAPTCHAs BEFORE giving up**: User has Capsolver + 2captcha. Detect → extract sitekey → solve → inject → submit. EXCEPTION: Friendly Captcha — Capsolver fails, use Camoufox headed mode instead.
12. **Camoufox `geoip=True` causes hangs**: Server uses `humanize=True` and omits `geoip` by default. Do not add it.
13. **Stytch auth (Vapi) is fingerprint-bound**: Cookie transfer Firefox → Camoufox does NOT work for Vapi. Must do direct login.
14. **Groq cookie transfer Firefox → Camoufox DOES work**: Extract 8 cookies, filter out `__cf_bm`, load into Camoufox.
15. **Firefox profile must be identified, not assumed**: Profile names are arbitrary. Always verify via `recovery.jsonlz4` parsing.
16. **Firefox must be closed for fresh cookie extraction**: Firefox holds session cookies in RAM.
17. **Cookie limitations via CLI**: `save_cookies` uses `document.cookie` — cannot export HttpOnly cookies. `clear_cookies` expires via JS — cannot clear HttpOnly cookies. For full cookie management, use Hermes browser tools (which can read/clear HttpOnly via Playwright context API) or the REST `/sessions/:userId/cookies` endpoint directly.
18. **`document.body.textContent` on SPAs returns massive inline JSON** (200K+ chars on Lieferando): Floods context, causes false-positive regex matches. Always use targeted CSS selectors instead.
19. **`click_element` with broad selector clicks FIRST matching element**: On pages with 50+ items, `click_element '[data-qa=item-action]'` clicks the first item's button. To target a specific item: use `get_elements` to find coordinates, then `click X Y`.
20. **`pie-button` and `pie-radio` Custom Elements need Playwright native click**: JS `dispatchEvent` clicks are isTrusted=false and ignored. Use `click_element` (REST `/click` with `selector`) which goes through Playwright's native click pipeline.
21. **HttpOnly cookies not readable via `document.cookie`**: `je-at` (Lieferando auth token) is `httpOnly=true`. Checking login via `document.cookie.includes("je-at")` always returns false. Instead, navigate to an auth-protected page and check if redirected to login.
22. **Domino's "Free Item" promo modal intercepts first item click**: Opening any item shows "You unlocked a free item" modal instead of the item configurator. Close with `Escape`, then re-click the same item. Promo appears only once per session.
23. **Domino's pizza configurator has multiple required selections**: Size, Crust, AND Sauce must all be selected before the Add button activates. Check for "Required" text in modal. Add button stays `aria-disabled="true"` until all fields are filled. Use `click_element` scoped to `.ReactModal__Content--after-open` for reliable selection. See `references/lieferando-checkout.md` → "Pizza Configurator" section.
24. **Dry-run before committing to irreversible actions**: When automating multi-step checkout/order flows, do a dry-run first: add items, verify basket, find voucher fields, locate checkout button — but DON'T click the final "Order/Pay" button. This catches issues (wrong items, expired sessions, missing fields) without wasting voucher codes or placing accidental orders. User explicitly requested this pattern: "mach einen testlauf nur ohne am ende auf kaufen zu drücken".
25. **Switch strategy after 3 failed attempts, don't repeat the same approach**: If the same click/eval pattern fails 3+ times, STOP and try a completely different approach (e.g., switch from coordinate clicks to `click_element`, or from `click_element` to `eval` JS click). Repeating the failing approach wastes tokens and frustrates the user. User feedback: "du hast es schonmal hinbekommen also mach es endlich".
26. **Hermes browser tools cache stale tabId → 410 "Gone" errors**: When the Camoufox server restarts (or a tab is GC'd), Hermes browser tools keep using the old tabId. Every `browser_navigate` returns `410 Client Error: Gone for url: .../tabs/<tabId>/navigate`. Re-navigating does NOT fix it — the tabId is cached in the Hermes process. **Fix**: Delete the stale session via REST, which forces Hermes to create a fresh tab on next navigate:
    ```bash
    curl -s -X DELETE "http://localhost:9377/sessions/hermes_a50a3f7fe5" --max-time 10
    ```
    The userId hash (`hermes_XXXXX`) can be found in server logs. After session deletion, `browser_navigate` creates a new session + tab automatically. If deletion also fails, restart the Camoufox server process entirely (`pkill -f "node server.js"` → relaunch with `eval "$(fnm env)" && fnm use 22 && node server.js`).
27. **Tab creation timeout after server restart**: If the server was killed while a persistent profile had stale storage state, new tab creation can hang for 30s then return `500 tab create timed out`. **Fix**: delete the stale profile directory before restarting: `rm -rf ~/.camofox/profiles/<hash>` (the hash can be found in server logs: "restoring persisted storage state, userId: ..., storageStatePath: ...").
28. **Hermes browser tools cache stale tabId across server restarts — unfixable from terminal**: Even after deleting the session via REST (`DELETE /sessions/hermes_XXXXX`) and restarting the Camoufox server, Hermes browser tools may STILL return `410 Gone` with the old tabId. The tabId is cached inside the Hermes process. **Workaround**: use `vision_analyze` with a local file path or HTTP URL (`python3 -m http.server <port>` + `http://localhost:<port>/image.png`) instead of `browser_vision`. `vision_analyze` doesn't depend on a browser tab.
29. **Clerk session revocation requires REST API, not browser**: When handling security incidents, use Clerk's REST API (`POST /v1/client/sessions/{sid}/remove`) to revoke sessions. Do NOT rely on browser logout — attacker may have active sessions. See `references/security-incident-response.md`.
30. **TOTP code generation for 2FA setup**: Use `uv run --with pyotp python3 -c "import pyotp; print(pyotp.TOTP('SECRET').now())"` to generate codes. Codes expire every 30 seconds — generate immediately before entering.
31. **cookies.sqlite missing session cookies while Firefox runs**: Firefox stores session cookies (expiry=0) in memory only. Copying `cookies.sqlite` while Firefox is running gives you only persistent cookies (analytics, consent) — NOT auth session cookies. Many sites (Cerebras, Zhipu/BigModel) use HttpOnly session cookies that are invisible until Firefox closes gracefully. Use the Three-Tier Cookie Extraction Strategy in `references/automation-patterns.md`. Never use `pkill -9` — SIGKILL skips cookie flush. Use `osascript -e 'tell application "Firefox" to quit'` + wait 5s.
32. **Python lz4 broken in Hermes venv — use Node.js**: `import lz4.block` fails with `ModuleNotFoundError: No module named 'lz4._version'` in the Hermes venv. To decompress Firefox `.jsonlz4` session store backups, use Node.js: `cd ~/projects/camofox-browser && npm install lz4 && node -e "..."`. The mozLz4 format is: 8-byte magic + 4-byte LE decompressed size + lz4 data.
33. **Session store recovery.jsonlz4 only has cookies for ACTIVE tabs**: Firefox's session store backup contains session cookies ONLY for currently open tabs. If the target site's tab was closed, its session cookies won't be here either. This is a secondary source, not a primary one.
34. **REST API cookie injection requires {"cookies": [...]} wrapper**: The Camoufox server `POST /sessions/:userId/cookies` endpoint expects `{"cookies": [...]}`, not a bare array. Also: `expires` must be in seconds (not ms), and `expires=0` is rejected — use `-1` for session cookies.
35. **Pre-injected cookies for a custom userId → must use direct REST API, NOT Hermes browser tools**: When cookies are injected for a specific userId (e.g., `rotator`, `cli_user`), Hermes browser tools (`browser_navigate`, `browser_click`, etc.) create their OWN `hermes_<hash>` userId — a separate session without the injected cookies. Use curl against the REST API directly: `POST /tabs` with `{"userId":"rotator","sessionKey":"rotator","url":"..."}` (sessionKey is REQUIRED — omitting it returns `{"error":"userId and sessionKey required"}`). Then use `GET /tabs/:tabId/snapshot?userId=rotator`, `POST /tabs/:tabId/click` with `{"userId":"rotator","ref":"eN"}`, etc. See `references/direct-rest-api-custom-userid.md`.
36. **Aria snapshots mask sensitive values (API keys, tokens)**: The accessibility tree returned by `/snapshot` truncates secrets — e.g., `xai-...39Hl` instead of the full key. To extract the real value, use `POST /tabs/:tabId/evaluate` with `document.body.innerText.match(/prefix-[a-zA-Z0-9]+/)` to regex-extract it from the page's full text content. For broader extraction, stringify `document.body.innerText` plus all `input.value` fields.
37. **Password-confirmed protected pages — no API bypass**: Some platforms (HuggingFace, GitHub, etc.) gate sensitive settings (token management, SSH keys, billing) behind a "Confirm your identity" password re-entry page. Navigating to `/settings/tokens` redirects to `/security-checkup?cookieId=<id>` with a form requiring the account password. Key facts:
    - **No public API for token management**: HuggingFace's `POST /api/tokens` returns 404, `POST /settings/tokens/create` returns 401. Token create/delete is ONLY via the web UI after password confirmation.
    - **huggingface_hub Python lib has NO token management methods** — only repo/model/dataset ops. `uv run --with huggingface_hub python3 -c "..."` works for `whoami()` but not for creating/deleting tokens.
    - **Token verification DOES work via API**: `GET /api/whoami-v2` with `Authorization: Bearer <token>` returns user info including token display name, role, creation date. Use this to verify a token is still valid before attempting rotation.
    - **The security-checkup form structure**: POSTs to `/security-checkup?cookieId=<id>` with fields: `csrf` (hidden), `next` (hidden, =`/settings/tokens`), `authType` (hidden, =`password`), `password` (text). The `cookieId` is in the redirect URL.
    - **Workflow**: (1) Verify old token via `GET /api/whoami-v2`. (2) Navigate to `/settings/tokens` → redirected to security-checkup. (3) Type account password into the password field, click Confirm. (4) On the tokens page, delete the old token and create a new one with the desired permission. (5) Update `~/.zshenv` or `.env` with the new token value.
    - **The account password is REQUIRED** — there is no cookie-only or API-only path. If the password is not in memory/keychain/env, ask the user for it before attempting browser automation.
38. **Google `glue-cookie-notification-bar` intercepts ALL clicks**: Google sites (AI Studio, Cloud Console, etc.) show a cookie consent bar with class `glue-cookie-notification-bar`. This overlay intercepts ALL button clicks on the page. Playwright native click on the "Accept" button returns `{"error":"Element not visible (no bounding box)"}`. **Fix**: Hide the bar via JS before any interaction: `document.querySelector('.glue-cookie-notification-bar').style.display = 'none'`. This is a Google-specific variant of the "proactive modal detection" pitfall — the bar is not a modal but a fixed-position overlay that blocks clicks.
39. **Angular Material (`mat-mdc-*`) buttons may not respond to Playwright native click**: On Google AI Studio, the "Create API key" button (`button.ms-button-primary`) did NOT respond to aria-ref click (`POST /click` with `{"ref":"e20"}`) or `:has-text()` selector click. It DID respond to direct JS `.click()` via `/evaluate`. **Pattern**: When `mat-mdc` buttons don't respond to Playwright click (ref or selector), fall back to `element.click()` via JS. The Playwright actionability checks (visible, enabled, not covered) can fail on Angular Material components with complex overlay/focus structures, while the JS `.click()` bypasses these checks. See `references/credential-rotation.md` → "Angular Material Buttons Not Responding to Playwright Click".
42. **Google AI Studio API key creation requires an imported Cloud Project**: The "Create API key" dialog on `aistudio.google.com/api-keys` shows "No Cloud Projects Available" if no Google Cloud projects are imported into AI Studio. **This is a hard blocker** — you cannot create an API key without a project. The user must import/create a Cloud Project first. Additionally, the API key table may appear empty even when keys exist (keys are only listed if associated with an imported project). API keys on the page are masked (`AIzaSy...XXXX`) in the Angular config data. See `references/credential-rotation.md` → "Google AI Studio".

43. **CRITICAL: userId matching for cookie injection — NEVER ask for passwords when session exists**: When injecting cookies from Firefox to Camoufox, the userId MUST match exactly. Hermes browser tools create their own `hermes_<hash>` userId based on the profile path. If you inject cookies to a different userId (e.g., `cli_user`), the session will NOT be recognized, and you'll be prompted to log in again. **User frustration signal**: "HOW OFTEN DO I HAVE TO REPEAT I AM ALREADY LOGGED IN ON MY FIREFOX PROFILE AND THAT IS ENOUGH". **The fix**: Always calculate the correct hermes userId using `get_camofox_identity()` from `tools/browser_camofox_state.py`, or compute it manually: `python3 -c "import uuid; print(f'hermes_{uuid.uuid5(uuid.NAMESPACE_URL, \"camofox-user:/Users/<USER>/.hermes/browser_auth/camofox\").hex[:10]}')"`. Then inject cookies to THAT userId, not `cli_user` or any other. **Rule**: If the user says they're already logged in, NEVER ask for passwords. The problem is userId mismatch, not missing credentials. See `references/amazon-cookie-injection.md` for full workflow.

44. **Amazon `max_auth_age` re-auth — NOT a hard wall with FRESH cookies**: Earlier documentation claimed Amazon's `openid.pape.max_auth_age=0` on `/your-orders/orders` was an unbypassable server-side re-auth. **This was WRONG — the issue was STALE cookies.** Verified 2026-07-17: when cookies are freshly extracted from a running Firefox session (where user is logged in), `/your-orders/orders` loads successfully WITHOUT re-auth. The `session-token` for `.amazon.de` changes frequently — if you extract from a cached `cookies.sqlite` copy or from a previous session, the token is stale and Amazon redirects to `/ap/signin`. **Correct workflow**: (1) Copy `cookies.sqlite` + WAL from the RUNNING Firefox profile (no need to close Firefox — Amazon's auth cookies are persistent, not session cookies). (2) Extract ALL Amazon cookies. (3) Inject to `hermes_<HASH>` userId. (4) Navigate to `/your-orders/orders` — if URL stays on `/your-orders/orders`, SUCCESS. If redirects to `/ap/signin`, cookies are stale — re-extract from Firefox. **Do NOT close Firefox** — Amazon's `at-main`, `at-acbde`, `session-token` are all persistent cookies stored on disk. See `references/amazon-cookie-injection.md` for full corrected workflow.

45. **Camoufox server must be restarted after `version.json` appears**: If `~/Library/Caches/camoufox/version.json` is created after the server already started (e.g., binary fetched post-startup), every `POST /tabs` returns `"Version information not found at /Users/.../Library/Caches/camoufox/version.json"`. The server caches the missing-version state at boot. **Fix**: `ps aux | grep "server.js" | grep -v grep` to find PID, then `kill <PID>` and relaunch with `cd ~/projects/camofox-browser && eval "$(fnm env)" && fnm use 22 && node server.js`. Verified 2026-07-17 — server running for days (PID 98134, started Tue09AM) failed to start browser until restarted.

45a. **camoufox-js `version.json` requires `"release"` field, not just `"build"`**: The `camoufox-js` npm package (v0.10.2) reads `version.json` and constructs a `Version` object via `new Version(versionData.release, versionData.version)`. If `release` is undefined, `this.release.split(".")` throws `TypeError: Cannot read properties of undefined (reading 'split')`. The Python `camoufox` package's `version.json` has `"build"` but NOT `"release"`. **Fix**: Copy the `build` value to a `release` key in `version.json`:
    ```bash
    # Fix version.json to include "release" field for camoufox-js compatibility
    python3 -c "
    import json
    for path in [
        '$HOME/Library/Caches/camoufox/version.json',
        '$HOME/Library/Caches/camoufox/browsers/official/152.0.4-beta.27-0ee2b71c/version.json'
    ]:
        try:
            d = json.load(open(path))
            if 'release' not in d:
                d['release'] = d.get('build', 'beta.27')
                json.dump(d, open(path, 'w'))
                print(f'Fixed: {path}')
        except: pass
    "
    ```
    Also symlink the full `Camoufox.app` bundle (not just individual files): `ln -sf ~/Library/Caches/camoufox/browsers/official/<version>/Camoufox.app ~/Library/Caches/camoufox/Camoufox.app`. Individual file symlinks for `properties.json`/`fontconfig` cause XPCOM errors (`Couldn't load XPCOM`) because the app bundle structure is incomplete. Verified 2026-07-17.

45b. **Lieferando React combobox does not respond to `fill()` or `value=` — must use keyboard `type()`**: Lieferando's address search input (`input[aria-label="Search for location"]`) is a React-controlled combobox. Setting `input.value = "..."` via `browser_console` does NOT trigger React's onChange handler — the autocomplete dropdown never appears. `browser_type` via the REST API also fails (500 errors on the `/type` endpoint for combobox elements). **Fix**: Focus the input via `browser_console(expression="document.querySelector('#combobox-input_0').focus()")`, then press keys ONE AT A TIME via `browser_press(key="S")`, `browser_press(key="t")`, etc. After typing enough characters, the autocomplete dropdown appears with `[role="option"]` elements. Click the correct option via `browser_console` JS: `document.querySelectorAll('[role="option"]')[1].click()`. Then handle the "Enter building number" prompt the same way (focus → press keys → click "Confirm address" button via `browser_console`). Verified 2026-07-17.

45c. **Lieferando restaurant direct URL redirects to homepage without address set**: Navigating to `https://www.lieferando.de/de/restaurant/dominos-pizza-berlin-stahnsdorf` WITHOUT having set a delivery address first redirects to the homepage (`/en`). The address must be set FIRST via the combobox flow (see pitfall 45b), then navigate to the delivery area page (`/en/delivery/food/<PLZ>`), then click the restaurant from the list. Direct restaurant URLs only work if the address was already set in the same browser session. Verified 2026-07-17.

45d. **Domino's pizza configurator with Hermes browser tools — aria refs work but radio labels need parent click**: When using Hermes browser tools (not CLI), the Domino's item modal shows `[role="radio"]` elements with refs like `@e3`, `@e5`, `@e8` for size options. Clicking the radio ref directly may not always select it. **Fix**: Click the parent `radio` element ref (e.g., `@e2` which wraps `@e3`), then verify via `browser_snapshot` that `[checked]` appears. After selecting Size, additional required sections (Crust, Sauce) appear dynamically. The "Add" button starts disabled (`[disabled]`) and activates only after ALL required fields are selected. For selecting radios via JS when refs are ambiguous, use `browser_console` with `document.querySelectorAll('[role="radio"]')` filtered by `aria-label.includes("Klassisch")` etc. Then click the "Add X,XX€" button ref. Verified 2026-07-17.

45e. **Domino's "Free Item" promo modal appears AFTER first item add — handle via browser_click on "No, thanks"**: After adding the first pizza, a "Nice! You get this free with your order" modal appears offering a free Beck's beer. This intercepts all subsequent clicks. In Hermes browser tools, it appears as a `dialog` with a "No, thanks" button (`@e5`). Click it to dismiss, then continue. The promo only appears once per session. Verified 2026-07-17.

45f. **Hermes browser tools create a NEW tab on every `browser_navigate` — losing session state**: Each `browser_navigate` call creates a fresh tab with a new `hermes_<hash>` userId. This means the delivery address, cookies, and basket from previous interactions are LOST. This is the #1 cause of "basket is empty" after adding items — the tab was re-created. **Fix**: Use the direct REST API with a persistent `userId` + `sessionKey` (see `references/direct-rest-api-custom-userid.md`). Create ONE tab that persists across all operations:
    ```bash
    # Create ONE persistent tab — reuse for ALL subsequent ops
    TAB_ID=$(curl -s -X POST http://localhost:9377/tabs \
      -H "Content-Type: application/json" \
      -d '{"userId":"agent1","sessionKey":"lieferando","url":"https://www.lieferando.de/de"}' \
      | python3 -c "import json,sys; print(json.load(sys.stdin).get('tabId',''))")
    echo "$TAB_ID" > /tmp/camofox_tab_id

    # ALL subsequent ops use the SAME tab ID via curl
    TAB=$(cat /tmp/camofox_tab_id)
    curl -s -X POST "http://localhost:9377/tabs/$TAB/click" \
      -H "Content-Type: application/json" \
      -d '{"userId":"agent1","ref":"e57"}'
    ```
    The key insight: `browser_navigate` is for initial navigation only. For subsequent page interactions (clicking items, scrolling, typing), use the REST API with the saved `tabId`. The `browser_snapshot`, `browser_click`, `browser_console`, `browser_press` tools also create their own tabs if the previous one was lost. **Always check**: `curl -s "http://localhost:9377/tabs?userId=agent1"` — if `tabs: []`, the session is gone. Verified 2026-07-17.

45g. **Domino's Add button: `pie-button` shadow DOM — `browser_click(ref)` returns `{ok:true}` but item NOT added**: The Lieferando Domino's modal "Add X,XX€" button is a `<pie-button>` custom element with a **shadow DOM**. `browser_click(ref="e38")` returns `{"ok":true}` but the React onClick handler does NOT fire — the item is not added. `document.querySelectorAll("button")` finds 0 matching buttons because they're inside shadow roots. **Fix**: Use REST API `POST /tabs/:tabId/evaluate` to access `pie-button.shadowRoot.querySelector("button")` and call `.click()`:
    ```bash
    curl -s -X POST "http://localhost:9377/tabs/$TAB/evaluate" \
      -H "Content-Type: application/json" \
      -d '{"userId":"agent1","expression":"(() => { const pbs = document.querySelectorAll(\"pie-button\"); for(const pb of pbs) { const t = pb.textContent||\"\"; if(t.includes(\"Add\") && t.includes(\"11,99\")) { const btn = pb.shadowRoot?.querySelector(\"button\"); if(btn && !btn.disabled) { btn.click(); return \"clicked\"; } } } return \"not found\"; })()"}'
    ```
    Same pattern for `pie-icon-button` (menu item add-to-basket buttons): `pib.shadowRoot?.querySelector("button")` + check `aria-label`. **Before clicking Add**: ensure ALL required fields (Size, Crust, Sauce) are selected via `evaluate` JS clicks on `[role="radio"]` elements filtered by text content. See `references/lieferando-checkout.md` → "Hermes Browser Tools + REST API Pattern". Verified 2026-07-17.

45h. **Lieferando checkout "Add voucher" collapsible requires pointerdown events — JS .click() does nothing**: The voucher section on the Lieferando checkout page (`data-qa="voucher"` with inner `div[data-qa="voucher-interactive"][role="button"]`) does NOT respond to `browser_click(ref)`, `click_element`, or JS `.click()`. The collapsible stays closed — no input field appears. **Fix**: Dispatch `pointerdown` + `pointerup` + `click` events via `evaluate`:
    ```bash
    curl -s -X POST "http://localhost:9377/tabs/$TAB/evaluate" \
      -H "Content-Type: application/json" \
      -d '{"userId":"agent1","expression":"(() => { const el = document.querySelector(\"[data-qa=\\\"voucher-interactive\\\"]\"); if(!el) return \"not found\"; el.dispatchEvent(new PointerEvent(\"pointerdown\", {bubbles:true})); el.dispatchEvent(new PointerEvent(\"pointerup\", {bubbles:true})); el.dispatchEvent(new MouseEvent(\"click\", {bubbles:true})); return \"dispatched\"; })()"}'
    ```
    After this, the input field appears with `data-qa="voucher-modal-details-input-voucher-element-focused"` and `placeholder="Voucher code"`. Type the code via REST API `type` with that selector, then click "Apply" via `click_element 'button:has-text("Apply")'`. Verified 2026-07-17 — voucher `Y5G3X6TED94FC9JQ` applied successfully, showing "Voucher 8,00€" and "8,00€ off eligible items" in the order summary.

45i. **Lieferando checkout login has Cloudflare Turnstile — bypassed via pre-authenticated session cookies**: After clicking "Checkout", Lieferando redirects to a login page with a `cf-turnstile-response` hidden field. The submit button stays `disabled` until Turnstile is solved. Turnstile does NOT auto-solve in Camoufox (unlike REWE/Apodiscounter). Capsolver fails because the sitekey is not extractable from the DOM. Google OAuth also fails (fingerprint-bound, redirects to `/signin/rejected`). **Working fix**: Extract fresh Lieferando session cookies from Firefox (user must be actively logged in), inject via `POST /sessions/:userId/cookies`, then navigate to restaurant menu → Checkout button → checkout page loads without any login/Turnstile challenge. Verified 2026-07-17 — full checkout with voucher applied, total 29,46€ → 21,46€ after 8€ voucher.

45j. **Camoufox server runs headless by default on macOS — must patch server.js for headed mode**: The Node.js REST server hardcodes `headless: useVirtualDisplay ? false : true` at line ~979. On macOS there is no Xvfb virtual display, so `useVirtualDisplay` is always false -> browser always launches with `-headless` flag, making it invisible to the user. **Fix**: Patch the line to read `CAMOFOX_HEADLESS` env var: replace `headless: useVirtualDisplay ? false : true,` with `headless: process.env.CAMOFOX_HEADLESS === 'false' ? false : (useVirtualDisplay ? false : true),`. Then restart: `kill $(lsof -ti :9377); cd ~/projects/camofox-browser && CAMOFOX_HEADLESS=false node server.js`. Verify with `ps aux | grep "[c]amoufox" | grep -o "\-headless"` — should output nothing (headed mode has `-foreground` instead of `-headless`). Verified 2026-07-17.

45k. **Tab reaper kills inactive tabs after 5 minutes — causes silent tab loss**: The Camoufox server has an "orphan page reaper" that closes tabs idle for >300 seconds (5 min). This silently destroys the persistent tab created via REST API, causing all subsequent `POST /tabs/:tabId/*` calls to fail with "Tab no longer exists". The reaper also closes the browser entirely when all tabs for a session are reaped. **Symptoms**: Tab created successfully, operations work for a few minutes, then suddenly all calls return 404/500. **Fix**: Keep the tab active by making a lightweight call (e.g. GET /tabs/:tabId/snapshot) every 3-4 minutes during long waits. Server logs show: "tab reaped (inactive)". Verified 2026-07-17.

45l. **Voucher section on Lieferando checkout requires pointerdown/pointerup events to open**: The "Add voucher" collapsible (`div[data-qa="voucher-interactive"][role="button"]`) does NOT respond to `.click()`, `browser_click(ref)`, or `click_element` — all return ok:true but the section stays collapsed. **Fix**: Dispatch pointerdown + pointerup + click events via evaluate. After this, an input field appears with `data-qa="voucher-modal-details-input-voucher-element-focused"` and `placeholder="Voucher code"`. Type the code and click "Apply" via native Playwright click. Verified 2026-07-17.

45m. **PayPal redirect after "Order and pay" needs password — cannot be fully automated**: After clicking "Order and pay" with PayPal selected, the browser redirects to `paypal.com/pay?token=...`. PayPal requires email + password login — the PayPal session is NOT carried over from Lieferando session cookies. Cannot complete PayPal payment automatically without the user's PayPal password. Verified 2026-07-17.

45n. **Domino's `#pre-order` URL fragment indicates restaurant is closed**: When navigating to a Domino's menu page and the URL contains `#pre-order`, the restaurant is currently closed and only accepts pre-orders. Item add buttons may render but clicks silently fail. Check for this fragment before attempting to add items. Verified 2026-07-17.

46. **No GET /sessions/.../cookies endpoint — read storage state file directly**: The Camoufox REST API has `POST /sessions/:userId/cookies` (set) but no GET endpoint (read). To extract HttpOnly cookies (like `at-main`/`at-acbde`) from an active Camoufox session — e.g., after user manually logged in and you need the new session-token — read the persistent profile file directly. Each userId has a profile at `~/.camofox/profiles/<hash>/storage-state.json` (find hash from server logs: "restoring persisted storage state, userId: <hash>"). Format is Playwright's `storageState` schema — `{"cookies":[{name,value,domain,path,expires,httpOnly,secure,sameSite}, ...]}`. The `expires` field is in seconds (NOT ms like Firefox). Storage state is written on navigation (not just on close) — but may still be stale right after a manual login. See `references/amazon-cookie-injection.md` for full extraction + re-injection workflow.

47. **Amazon SPA `a-declarative` framework does NOT respond to `selectOption` or `dispatchEvent`**: Amazon's return form (`/spr/returns/cart`) uses custom `a-declarative` dropdowns (`data-action="a-dropdown-select"`). Playwright's `selectOption()` sets the `<select>` value correctly, and `dispatchEvent(new Event('change'))` fires — but Amazon's SPA JavaScript framework does NOT render the "Weiter" (Next) button in response. The framework registers event handlers that only respond to genuine user interactions (trusted events), not programmatic ones. **Symptoms**: `select.value` is correct (`RO_AMZ-PG-BAD-DESC`), textarea is filled, but NO "Weiter" button appears in the DOM (only the Rufus chat "Weiter zur Seite" button). `form.submit()` leads to 404 because hidden CSRF/session inputs are missing. **Workaround**: Use a standalone `camoufox-js` script (run from `~/projects/camofox-browser/` with `node script.cjs`) that launches a dedicated browser, injects cookies via `page.context().addCookies()`, and uses Playwright's native `selectOption()`. Even with native `selectOption`, the Weiter button may still not render — in that case, use `HTMLFormElement.prototype.submit.call(form)` to submit the form (but this may 404 if hidden inputs are missing). **Future fix**: The camoufox-browser REST server needs a `/tabs/:tabId/selectOption` endpoint. See `references/amazon-spa-declarative-limitation.md` for the standalone script template and debugging details. Verified 2026-07-17.

## CLI Extension Philosophy

## Amazon-Specific Pitfalls

1. **Cookie extraction from running Firefox**: Copy both `cookies.sqlite` AND `cookies.sqlite-wal` — the WAL has the latest session cookies. No need to close Firefox. Amazon's auth cookies (`at-main`, `at-acbde`, `session-token`) are persistent cookies stored on disk.

2. **Amazon `max_auth_age` re-auth — NOT a hard wall with FRESH cookies**: Earlier documentation claimed Amazon's `openid.pape.max_auth_age=0` on `/your-orders/orders` was an unbypassable server-side re-auth. **This was WRONG — the issue was STALE cookies.** Verified 2026-07-17: when cookies are freshly extracted from a running Firefox session (where user is logged in), `/your-orders/orders` loads successfully WITHOUT re-auth. The `session-token` for `.amazon.de` changes frequently — if you extract from a cached `cookies.sqlite` copy or from a previous session, the token is stale and Amazon redirects to `/ap/signin`. **Correct workflow**: (1) Copy `cookies.sqlite` + `cookies.sqlite-wal` from the RUNNING Firefox profile (no need to close Firefox — Amazon's auth cookies are persistent, not session cookies). (2) Extract all Amazon cookies. (3) Inject to `hermes_<HASH>` userId. (4) Navigate to `/your-orders/orders` — if URL stays on `/your-orders/orders`, SUCCESS. If redirects to `/ap/signin`, cookies are stale — re-extract from Firefox. **Do NOT close Firefox** — Amazon's `at-main`, `at-acbde`, `session-token` are all persistent cookies stored on disk. See `references/amazon-cookie-injection.md` for full corrected workflow.

3. **Amazon `a-declarative` dropdown (a-dropdown-select) does NOT respond to Playwright `selectOption`**: Amazon's SPA framework uses `data-action="a-dropdown-select"` on a custom `<select>` element. Setting `.value` via JS or Playwright's native `selectOption` sets the value in the DOM but does NOT trigger Amazon's internal `a:dropdown:selected` event handler. This means Amazon's SPA doesn't know the dropdown changed and won't render dependent UI (e.g. the "Weiter" button on return forms). **Workaround**: None found yet for REST API. Use a standalone `camoufox-js` script (run from `~/projects/camofox-browser/` with `node script.cjs`) that launches a dedicated browser, injects cookies via `page.context().addCookies()`, and uses Playwright's native `selectOption()`. Even with native `selectOption`, the Weiter button may still not render — in that case, use `HTMLFormElement.prototype.submit.call(form)` to submit the form (but this may 404 if hidden inputs are missing). **Future fix**: The camoufox-browser REST server needs a `/tabs/:tabId/selectOption` endpoint. See `references/amazon-spa-declarative-limitation.md` for the standalone script template and debugging details.4. **Amazon return form (spr/returns/cart) "Weiter" button hidden by cart overlay**: The Amazon cart flyout overlay (`#ewc-compact-container`, `#ewc-content`) can appear on top of the return form, intercepting clicks. Must remove it via JS before clicking the "Weiter" button: `document.querySelector('#ewc-compact-container,#ewc-content').remove()`. Verified 2026-07-17.

5. **Amazon return form "Weiter" button requires `requestSubmit()` or native submit**: The form (`id="items-section-form-v2"`, `action="/spr/returns/resolutions"`, `method="post"`) does NOT have a standard `<input type="submit">` or `<button type="submit">` for the "Weiter" button — it's a styled `<button class="a-button-text">` with `type="button"`. Clicking it via Playwright's `click()` does nothing because the form's `requestSubmit()` is never called. **Fix**: Use `form.requestSubmit()` via JS evaluate, or create a synthetic submit input and click it: `form.submit()` works but doesn't trigger validation; `form.requestSubmit()` triggers validation AND submission. However, the form may be missing hidden CSRF/session inputs if the `a-declarative` dropdown wasn't properly triggered, leading to 404 on `/spr/returns/resolutions`. See pitfall #3.

### 6. **Amazon return reason for wrong model**: Use `RO_CR-ORDERED_WRONG_ITEM` ("Irrtümlich bestellt"), NOT `RO_AMZ-PG-BAD-DESC` ("Entspricht nicht der Beschreibung"). The Shiptree charger listed compatibility with M365/Pro/1S/Pro 2/Essential/3 only — it NEVER claimed Scooter 4 Lite compatibility. "Irrtümlich bestellt" is the correct reason when you ordered the wrong model. Verified 2026-07-18.

### 7. **Xiaomi Electric Scooter 4 Lite (2nd Gen) charger spec**: Uses **24.2V 1.5A** charger, NOT 42V 2A like M365/Pro/1S/Pro 2/Essential/3. The Shiptree charger (B0F8J5SBW1) is 42V 2A for M365 series — WRONG voltage. Correct charger: **LIROPAU 24.2V 1.5A** (ASIN **B0FWB7L8JH**, €31.99), explicitly lists "Xiaomi Electric Scooter 4 Lite 2nd Gen". Verified 2026-07-18.

## Extracting Large Binary Blobs from Browser Context (PDFs, Images, etc.)

**Problem**: Angular/React SPAs create blob URLs via `URL.createObjectURL()` for
downloads. Playwright's `page.on('download')` does NOT capture these (blob URLs
aren't HTTP downloads). Hermes `browser_console` truncates display output, and
`write_file` truncates at 20KB — so you can't get a 113KB+ base64 string out.

**Solution**: Call the REST `/tabs/:tabId/evaluate` endpoint directly via curl/urllib.
The evaluate endpoint's `express.json({ limit: '1mb' })` limits the REQUEST body
(the JS expression), NOT the response. The response `res.json({ ok, result })`
returns the full Playwright `page.evaluate()` result with no truncation.

### Method 1: Direct curl (simplest)
```bash
# Get tab ID
TAB_ID=$(python3 -c "import json; print(json.load(open('/tmp/camoufox_cli_state.json')).get('tab_id',''))")

# Evaluate and decode base64 to file
curl -s -X POST "http://localhost:9377/tabs/$TAB_ID/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"userId":"cli_user","expression":"window.__pdfBase64"}' \
  | python3 -c "import json,sys,base64; d=json.load(sys.stdin); r=d['result']; r=r.split(',',1)[1] if r.startswith('data:') else r; open('/tmp/file.pdf','wb').write(base64.b64decode(r)); print('wrote', len(base64.b64decode(r)), 'bytes')"
```

### Method 2: Helper scripts (robust)
```bash
# Python helper — handles data: URIs, chunked fallback, error checking
~/.hermes/scripts/extract_browser_blob.py /tmp/invoice.pdf "window.__pdfBase64"

# For very large blobs (>1MB base64), use --chunked
~/.hermes/scripts/extract_browser_blob.py /tmp/big.pdf "window.__pdfBase64" --chunked
```

### Method 3: Blob URL → base64 via in-page fetch (if you only have the blob URL)
```javascript
// Evaluate this via /tabs/:tabId/evaluate — returns base64 directly
(async () => {
  const r = await fetch('blob:https://example.com/abc-123');
  const b = await r.blob();
  return await new Promise(res => {
    const fr = new FileReader();
    fr.onload = () => res(fr.result.split(',')[1]);
    fr.readAsDataURL(b);
  });
})()
```

### Prerequisites
1. **Capture the blob**: Patch `URL.createObjectURL` to intercept the Blob and
   base64-encode it into `window.__pdfBase64`:
   ```javascript
   const _orig = URL.createObjectURL;
   URL.createObjectURL = function(blob) {
     if (blob instanceof Blob) {
       const fr = new FileReader();
       fr.onload = () => { window.__pdfBase64 = fr.result.split(',')[1]; };
       fr.readAsDataURL(blob);
     }
     return _orig.call(this, blob);
   };
   ```
2. **Trigger the download** (click the button/link that creates the blob).
3. **Wait** for `window.__pdfBase64` to populate (FileReader is async).
4. **Extract** via Method 1 or 2 above.

### Why other approaches don't work
- **Playwright `page.on('download')`**: Only fires for HTTP downloads with
  `Content-Disposition: attachment`. Blob URL downloads don't trigger it.
- **`page.pdf()`**: Generates a PDF from the PAGE content — doesn't extract a
  file that the page is trying to download.
- **`browser_console` display**: Hermes truncates the tool output display.
- **`write_file`**: Truncates at 20KB.
- **REST `/tabs/:id/screenshot`**: Returns PNG of the page, not the blob.

### Relevant endpoints (verified 2026-07-20)
- `POST /tabs/:tabId/evaluate` — **THE key endpoint**. No response size limit.
  Request body limit: 1MB (the JS expression). Response: `{ ok, result }` with
  full `page.evaluate()` return value.
- `GET /tabs/:tabId/downloads` — Lists Playwright-captured downloads (HTTP only,
  does NOT capture blob URLs).
- `GET /tabs/:tabId/screenshot` — Returns raw PNG bytes of page screenshot.
- No `/tabs/:tabId/pdf` or `/tabs/:tabId/save` endpoint exists.
- No `/tabs/:tabId/file-save` endpoint exists.

## CLI Extension Philosophy

## Memory Full Handling (USER PREFERENCE)

When memory is full (entry rejected with "would exceed the limit"):
1. Use a SINGLE `operations` batch call with `action: "remove"` for stale entries + `action: "add"` for the new one
2. Remove/shorten the least important entries first (e.g., merge TNG + TNG AI into one entry)
3. NEVER ask the user which entries to remove — just consolidate and retry
4. The `operations` array applies atomically — remove + add in one call

User correction: "well do you not know how to deal with memory full?"
8. **NEVER ask user for Amazon password**: User has explicitly stated cookies from Firefox are sufficient. Do NOT ask for password. Do NOT ask for 2FA. If `/your-orders/orders` redirects to `/ap/signin`, the cookies are STALE — re-extract from Firefox `cookies.sqlite` + WAL.
9. **Rufus "Weiter zur Seite" button vs return form "Weiter" button**: The Rufus chat panel has a "Weiter zur Seite" button that shows up in searches for "Weiter" buttons. Filter it out by checking `!btn.closest('[class*="rufus"]')` or `!btn.id.includes('Rufus')`.

When you find yourself writing `eval` JS for interaction, STOP. Ask: "Should this be a native CLI command?" If yes, add it to `camoufox_cli.py` (REST client) and consider whether the REST server needs a new endpoint.

**Already added**: `click_element`, `type_in_element`, `fill_element`, `scroll_to_element`, `save_cookies`, `load_cookies`, `clear_cookies`, `loop`, `set_input_files` (limited — REST API lacks file upload endpoint).

**REST API gaps**: The Node REST server does not expose `set_input_files` (Playwright file upload) or full HttpOnly cookie management. For these, use Hermes browser tools (which go through the same server but use Playwright context API) or the `/sessions/:userId/cookies` endpoint directly.

## SPA-Specific Patterns (see reference files for details)

### SPA Hidden Selects (rexx-systems, Alexianer portal)
Set value via `eval` with both `input` and `change` events.

### Checkbox Toggling via eval
Custom checkboxes with invisible overlays — set `checked` directly and dispatch change event.

### Cookie Banner Removal via eval
Usercentrics `#usercentrics-root` — remove the banner root element entirely.

### MUI DataGrid Row Click
Find inner cell `<div>` containing target text, dispatch native `MouseEvent`.

### React-Controlled Autocomplete Input
Use native value setter + `input` + `change` events.

### Radix UI Tabs
Focus active tab, then dispatch `KeyboardEvent` on target tab.

## Interactive REPL Methodology (USER PREFERENCE)

When automating a NEW site for the first time, NEVER write a complete script. Build an interactive REPL that does ONE action at a time, with logging + screenshots + vision analysis. Only AFTER understanding the site's interaction model should you build automation.

**User correction**: "you need an interactive tool with slow iterative approach which logs and only at the end should you build the automation and refine it."

The REPL is at `scripts/browser_repl.py`. Commands: goto, click, clicktext, type, fill, eval, shot, state, find, list, clean, wait, quit.

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
