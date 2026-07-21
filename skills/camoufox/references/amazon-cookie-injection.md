# Amazon Cookie Injection — Corrected Workflow

## Key Correction (2026-07-17)

**Previous documentation claimed Amazon's `max_auth_age` was an unbypassable server-side wall. This was WRONG.**

The real issue was **stale cookies**. Amazon's `session-token` for `.amazon.de` changes frequently. If you extract from a cached copy or from an older Firefox session, the token is stale and Amazon redirects to `/ap/signin`.

With **freshly extracted** cookies from a running Firefox (where user is logged in), `/your-orders/orders` loads successfully WITHOUT re-auth.

## Correct Workflow

### Step 1: Extract Cookies from RUNNING Firefox (No Close Needed)

Amazon's auth cookies (`at-main`, `at-acbde`, `session-token`, `x-main`, `x-acbde`) are **persistent** cookies — they ARE in `cookies.sqlite` while Firefox is running. Do NOT close Firefox.

```python
import sqlite3, json, shutil

profile = '/Users/<USER>/Library/Application Support/Firefox/Profiles/<FF_PROFILE>'
shutil.copy2(f'{profile}/cookies.sqlite', '/tmp/ff_cookies.sqlite')
try:
    shutil.copy2(f'{profile}/cookies.sqlite-wal', '/tmp/ff_cookies.sqlite-wal')
except: pass

conn = sqlite3.connect('/tmp/ff_cookies.sqlite')
rows = conn.execute('''
    SELECT host, name, value, path, expiry, isSecure, isHttpOnly, sameSite
    FROM moz_cookies WHERE host LIKE '%amazon%'
''').fetchall()
conn.close()

cookies = []
for host, name, value, path, expiry, isSecure, isHttpOnly, sameSite in rows:
    if name in ('cf_clearance', '__cf_bm'): continue
    clean = -1
    if expiry and expiry > 0:
        if expiry > 1e12: clean = int(expiry / 1000)
        elif expiry > 1e9: clean = int(expiry)
    cookies.append({
        'domain': host, 'name': name, 'value': value,
        'path': path or '/', 'expires': clean,
        'secure': bool(isSecure), 'httpOnly': bool(isHttpOnly),
        'sameSite': ['None', 'Lax', 'Strict'][sameSite] if sameSite in [0,1,2] else 'Lax'
    })

wrapped = {'cookies': cookies}
with open('/tmp/amazon_fresh.json', 'w') as f:
    json.dump(wrapped, f)
print(f'{len(cookies)} cookies extracted')
```

### Step 2: Inject to Hermes userId

```bash
# Delete old session
curl -s -X DELETE "http://localhost:9377/sessions/hermes_<HASH>"

# Inject fresh cookies
curl -s -X POST "http://localhost:9377/sessions/hermes_<HASH>/cookies" \
  -H "Content-Type: application/json" \
  -d @/tmp/amazon_fresh.json

# Create tab — check URL for /ap/signin (stale) vs /your-orders (success)
curl -s -X POST "http://localhost:9377/tabs" \
  -H "Content-Type: application/json" \
  -d '{"userId":"hermes_<HASH>","sessionKey":"amazon","url":"https://www.amazon.de/your-orders/orders"}'
```

### Step 3: Verify

- URL contains `/ap/signin` → cookies are STALE, re-extract from Firefox
- URL is `/your-orders/orders` → SUCCESS, proceed with automation
- Homepage `/` shows "Hallo, Jonathan" → cookies work for general browsing

### Key Verification: Check `session-token` Value Changes

The `session-token` for `.amazon.de` changes with each login/session. Compare:
```python
# Old (stale): AzJARCW0yF... or HMKH00FjmIKHrm8...
# Fresh:        5jE567wLYXF/NIph7WsYOs1xbPRisv5yO7LIepr4...
```

If the `session-token` hasn't changed since last extraction, you're using stale cookies.

## Extracting HttpOnly Cookies from Camoufox Storage State

After a manual login in Camoufox, the storage state file has ALL cookies including HttpOnly:

```bash
# Find the profile hash from meta.json files
for f in ~/.camofox/profiles/*/meta.json; do
  dir=$(dirname "$f")
  name=$(basename "$dir")
  ts=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$f" 2>/dev/null)
  echo "$name modified=$ts"
done

# Read cookies from the most recently modified profile
python3 -c "
import json
with open('/Users/<USER>/.camofox/profiles/<hash>/storage-state.json') as f:
    data = json.load(f)
cookies = [c for c in data.get('cookies', []) if 'amazon' in c.get('domain', '').lower()]
wrapped = {'cookies': cookies}
with open('/tmp/amazon_fresh.json', 'w') as f:
    json.dump(wrapped, f)
print(f'{len(cookies)} cookies extracted')
"
```

## Common Mistakes (Verified 2026-07-17)

1. **Using cached cookies from a previous extraction** — `session-token` changes frequently. Always re-extract from the current `cookies.sqlite`.
2. **Closing Firefox first** — unnecessary for Amazon. Amazon's auth cookies are persistent, not session cookies. Firefox can stay running.
3. **Using the `extract_firefox_cookies.py` script** — it kills Firefox first (`pkill -SIGTERM -f Firefox`). For Amazon, use the inline Python extraction above instead.
4. **Injecting to `cli_user` instead of `hermes_<HASH>`** — Hermes browser tools use `hermes_<hash>`, not `cli_user`.
5. **Giving up after login redirect** — if `/your-orders/orders` redirects to `/ap/signin`, the cookies are STALE, not invalid. Re-extract from Firefox.

## Amazon a-declarative Dropdown Limitation

Amazon's return form (`/spr/returns/cart`) uses `data-action="a-dropdown-select"` on a native `<select>`. Amazon's SPA framework does NOT respond to:
- JS `element.value = x; dispatchEvent(new Event('change'))` 
- Playwright's native `selectOption()` via the `/select` endpoint
- Native value setters via `Object.getOwnPropertyDescriptor`

The SPA renders the "Weiter" button ONLY after the `a:dropdown:selected` internal event fires, which is triggered by Amazon's own JavaScript when the user interacts with the **custom dropdown UI** (not the native `<select>`).

### Workaround: Click Custom Dropdown UI

```bash
# 1. Click the custom dropdown button (NOT the native select)
curl -s -X POST "http://localhost:9377/tabs/$TAB_ID/click" \
  -H "Content-Type: application/json" \
  -d '{"userId":"cli_user","selector":".a-dropdown-container:has(#the-select-id) .a-button-text"}'

# 2. Click the option link in the dropdown list
curl -s -X POST "http://localhost:9377/tabs/$TAB_ID/click" \
  -H "Content-Type: application/json" \
  -d '{"userId":"cli_user","selector":"a.a-dropdown-link:has-text(\"Option Text\")"}'
```

This triggers Amazon's internal `a:dropdown:selected` event properly and the "Weiter" button appears.

### Cart Overlay Blocking Clicks

The Amazon cart flyout (`#ewc-compact-container`, `#ewc-content`) can appear on top of the return form and intercept clicks. Remove it before clicking "Weiter":

```bash
curl -s -X POST "http://localhost:9377/tabs/$TAB_ID/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"userId":"cli_user","expression":"document.querySelector(\"#ewc-compact-container,#ewc-content\")?.remove()"}'
```

## Amazon Return Form Workflow (Complete)

1. Navigate to `/spr/returns/cart?itemId=...&orderId=...`
2. Click checkbox to select the item
3. Click custom dropdown button (`.a-dropdown-container .a-button-text`)
4. Click option link (`a.a-dropdown-link:has-text("reason")`)
5. Fill comment textarea via `/type` endpoint
6. Remove cart overlay (`#ewc-compact-container`)
7. Get snapshot to find "Weiter" button ref
8. Click "Weiter" button — page navigates to `/spr/returns/resolutions`

**Return reasons** (value → text):
- `RO_CR-ORDERED_WRONG_ITEM` → "Irrtümlich bestellt"
- `RO_AMZ-PG-BAD-DESC` → "Entspricht nicht der Beschreibung auf der Website"
- `RO_CR-UNWANTED_ITEM` → "Gefällt mir nicht mehr"
- `RO_CR-DEFECTIVE` → "Artikel ist fehlerhaft oder funktioniert nicht"

**IMPORTANT**: Choose the correct return reason. "Entspricht nicht der Beschreibung" only applies if the product listing explicitly claimed compatibility with your device. If the product never claimed to work with your scooter, use "Irrtümlich bestellt" instead.

**User correction (2026-07-17)**: "you failed because i told you to use himalaya to find my xiaomi scooter which i bought and buy a new cable and you bought me an incompatible one that is why you failed"

**Lesson**: When buying replacement parts/accessories for a device:
1. FIRST find the device purchase in email (himalaya) to get the EXACT model
2. THEN search for compatible accessories using the exact model number
3. NEVER assume a charger is compatible based on "fits most scooters" listings
4. ALWAYS verify the exact charging port type, voltage, amperage, and connector shape before ordering
5. If the user says "find my X and buy a cable", the "find" step is MANDATORY — do not skip it
