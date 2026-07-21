# Engine Test Results — 2026-06-21 (updated 14:15)

Tested against multiple Cloudflare Turnstile sites.

## Results

| Engine | Turnstile Bypass | Notes |
|--------|-----------------|-------|
| Camoufox (Firefox, engine-level) | YES | Default. Exclude uBO or patch coreBundle.js. |
| Patchright (Chromium, protocol-level) | YES | Legacy backup. Use Stealth().apply_stealth_sync(page) v2 API. |
| Nodriver (raw CDP, no framework) | NO | Cookie injection API broken. Turnstile still blocks. |
| Vanilla Playwright Firefox | NO | navigator.webdriver + CDP leaks detected. |
| curl_cffi (TLS impersonation) | YES (API only) | Bypasses TLS fingerprint check. No JS rendering. |

## Per-Site Turnstile Results (Camoufox)

| Site | Turnstile | Camoufox Bypass | Notes |
|------|-----------|-----------------|-------|
| REWE (www.rewe.de/shop/) | YES | YES | Homepage + search both bypassed. type() not fill() for search. |
| Apodiscounter (apodiscounter.de) | YES | YES | Homepage loads normally. Search via #product-search works. |
| Medikamente-per-klick | NO | N/A | No Cloudflare. No CAPTCHA. Direct DOM forms. |
| Asia-foodstore | NO | N/A | No Cloudflare. Has reCAPTCHA on signup (not search). |
| GoAsia (goasia.net) | YES | NO | Stricter Turnstile config. Camoufox fails. "Sicherheitsüberprüfung wird durchgeführt" persists. Needs Capsolver or manual cf_clearance cookie. |
| Knuspr (knuspr.de) | NO | N/A | No Cloudflare. Uses #searchGlobal + API interception. |
| Amazon.de | NO | N/A | No Cloudflare. Standard DOM extraction. |

## Key Learnings

### Route Interception over uBO

Camoufox's built-in uBO does NOT auto-subscribe to easylist_cookies/adguard_cookies filter lists on first run. Route interception is simpler and more reliable for blocking cookie consent banners:

```python
BLOCK_PATTERNS = [
    "usercentrics", "uc-cdn", "consent", "cookiebot", "cookielaw",
    "onetrust", "truste", "quantcast", "web-vitals",
]

def block_noise(route):
    url = route.request.url.lower()
    if any(p in url for p in BLOCK_PATTERNS):
        route.abort()
    else:
        route.continue_()

ctx.route("**/*", block_noise)
```

Use `exclude_addons=[DefaultAddons.UBO]` — uBO adds startup overhead and doesn't help with cookie banners without manual filter list config.

### React Forms: type() not fill()

React-controlled forms (REWE search, possibly others) disable submit buttons until input events fire. `fill()` sets the value but doesn't trigger React's onChange handler. `type()` with delay triggers proper input events:

```python
# WRONG — button stays disabled
search_input.fill("query")

# RIGHT — button enables after type()
search_input.click()
time.sleep(0.3)
search_input.type("query", delay=50)
time.sleep(1)
```

### REWE Search URL

- Homepage: `https://www.rewe.de/shop/` (NOT `shop.rewe.de` — that triggers Turnstile more aggressively)
- Search navigates to: `https://www.rewe.de/shop/productList?search=QUERY`
- Direct URL `search?search=QUERY` returns 404
- Must use search bar + type() + click search button

### REWE Product API

Search triggers: `GET https://www.rewe.de/shop/api/products?term=QUERY&autoCompletion=true&objectsPerPage=5&marketId=231014&serviceType=DELIVERY`

Response has `hits[].articleId`, `hits[].title`, `hits[].baseQuantity`, `hits[].quantityType`. No price in this API — price comes from body text parsing.

### 3 Parallel Camoufox Instances

Running 3 Camoufox instances in parallel (REWE + Knuspr + Amazon) needs ~180s timeout. Each launches a full patched Firefox. Resource contention on macOS causes slower startup. Set subprocess timeout to 180s minimum.

### GoAsia Turnstile — Camoufox Fails

GoAsia has a stricter Cloudflare configuration than REWE. Camoufox does NOT bypass it:
```
Title: Nur einen Moment…
Body: Sicherheitsüberprüfung wird durchgeführt
```

Options:
1. Capsolver API (AntiTurnstileTaskProxyless) — needs CAPSOLVER_API_KEY in ~/.hermes/.env
2. Manual Firefox visit → extract cf_clearance cookie → inject into Camoufox
3. GoAsia site key: `0x4AAAAAAAAjJA_X7` (may need updating — check page source)

## Test Details

### Camoufox — PASS (REWE, Apodiscounter)

```python
from camoufox.sync_api import Camoufox
from camoufox.addons import DefaultAddons

with Camoufox(headless=True, locale="de-DE", exclude_addons=[DefaultAddons.UBO]) as browser:
    ctx = browser.new_context(viewport={"width": 1366, "height": 900})
    # Route interception for cookie consent
    def block_noise(route):
        url = route.request.url.lower()
        if any(p in url for p in BLOCK_PATTERNS):
            route.abort()
        else:
            route.continue_()
    ctx.route("**/*", block_noise)
    ctx.add_cookies(cookies)
    page = ctx.new_page()
    page.on("pageerror", lambda e: None)
    page.goto("https://www.rewe.de/shop/")
    # Turnstile NOT triggered. Page loads normally.
```

### Camoufox — FAIL (GoAsia)

```python
page.goto("https://www.goasia.net")
# Result: "Sicherheitsüberprüfung wird durchgeführt" — Turnstile still blocking
# Camoufox engine-level spoofing insufficient for GoAsia's Turnstile config
```

### Nodriver — FAIL

```python
import nodriver as uc
browser = await uc.start(headless=True)
page = await browser.get("https://shop.rewe.de")
# Result: "Zeig uns, dass du ein Mensch bist" — Turnstile still blocking
```

Cookie injection via `browser.cookies.set_all()` did not work.
Nodriver's raw CDP approach does NOT fool Cloudflare Turnstile on REWE.

### REWE Full Flow

1. Homepage loads (Turnstile bypassed)
2. PLZ <PLZ> already set via cookies
3. Search input `input.rs-qa-header-search-input` filled with type()
4. Search button `button.rs-qa-header-search-button` clicked
5. Results page loads: "Deine Suche nach X ergab N Treffer"
6. Products extracted from body text via regex
7. NOT from `[data-price]` elements (products are in web components/shadow DOM)

### Body Text Product Extraction (REWE)

Products appear as:
```
REWE Beste Wahl Artischocken ganze Herzen 165g
165g (1 kg = 13,27 €)
2,19 €
```

Regex: `(\d+(?:,\d+)?)\s*(g|kg|ml|l|Stk)?\s*\(1\s*(kg|l|Stk)\s*=\s*(\d+,\d{2})\s*€\)`

Then look for price `(\d+,\d{2})\s*€` in next 1-3 lines.

### Asia-Foodstore Product Extraction

Body text pattern:
```
BRAND
Product Name SIZE
PRICE € *
UNIT_PRICE € pro 1 UNIT
Schnellkauf
```

DOM selectors: `.price-main` → "3,99 € *", `.price-note` → "19,95 € pro 1 l"
