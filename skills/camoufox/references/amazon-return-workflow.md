# Amazon Return Workflow — Complete Automation Guide

## Prerequisites
- Firefox running with active Amazon session (user logged in)
- Camoufox server running (`camoufox ping` returns ok)
- Cookies extracted from Firefox `cookies.sqlite` + WAL, injected to `hermes_<HASH>`

## Step-by-Step

### 1. Extract + Inject Cookies
```python
import sqlite3, json, shutil
profile = '~/Library/Application Support/Firefox/Profiles/<FF_PROFILE>'
shutil.copy2(f'{profile}/cookies.sqlite', '/tmp/ff_cookies.sqlite')
shutil.copy2(f'{profile}/cookies.sqlite-wal', '/tmp/ff_cookies.sqlite-wal')  # may fail, ok
conn = sqlite3.connect('/tmp/ff_cookies.sqlite')
rows = conn.execute('SELECT host, name, value, path, expiry, isSecure, isHttpOnly, sameSite FROM moz_cookies WHERE host LIKE "%amazon%"').fetchall()
conn.close()
# Normalize expiry ms→s, filter cf_clearance/__cf_bm, wrap in {"cookies": [...]}
```

### 2. Inject to hermes userId
```bash
curl -s -X DELETE "http://localhost:9377/sessions/hermes_<HASH>"
curl -s -X POST "http://localhost:9377/sessions/hermes_<HASH>/cookies" -H "Content-Type: application/json" -d @/tmp/amazon_fresh.json
```

### 3. Navigate to Order History
```bash
curl -s -X POST "http://localhost:9377/tabs" -H "Content-Type: application/json" \
  -d '{"userId":"hermes_<HASH>","sessionKey":"amazon","url":"https://www.amazon.de/your-orders/orders"}'
# Check URL: if /ap/signin → cookies stale, re-extract. If /your-orders/orders → success.
```

### 4. Find Order + Click "Rückgabe oder Widerruf"
- Get snapshot, find the order by Bestellnr
- Click the "Rückgabe oder Widerruf" button ref for that order

### 5. On Return Page (/spr/returns/cart)
1. **Click checkbox** to select the item: `#olmitsmnooktoo-...-orc-item-selection-checkbox`
2. **Select return reason** — click the custom dropdown button, NOT the native select:
   ```bash
   # Click dropdown button
   curl -s -X POST "http://localhost:9377/tabs/$TAB/click" -H "Content-Type: application/json" \
     -d '{"userId":"...","selector":".a-dropdown-container:has(#select-id) .a-button-text"}'
   # Click option link
   curl -s -X POST "http://localhost:9377/tabs/$TAB/click" -H "Content-Type: application/json" \
     -d '{"userId":"...","selector":"a.a-dropdown-link:has-text(\"Irrtümlich bestellt\")"}'
   ```
3. **Fill comment textarea** if required
4. **Remove cart overlay**: `document.querySelector('#ewc-compact-container,#ewc-content')?.remove()`
5. **Get snapshot** to find "Weiter" button ref
6. **Click "Weiter"** — filter out Rufus "Weiter zur Seite" button

### Return Reason Values
| Value | German Text | When to use |
|------|-------------|-------------|
| `RO_CR-ORDERED_WRONG_ITEM` | Irrtümlich bestellt | Wrong item ordered, not in compatibility list |
| `RO_AMZ-PG-BAD-DESC` | Entspricht nicht der Beschreibung auf der Website | Product claimed compatibility but doesn't work |
| `RO_CR-UNWANTED_ITEM` | Gefällt mir nicht mehr | Don't want it anymore |
| `RO_CR-DEFECTIVE` | Artikel ist fehlerhaft oder funktioniert nicht | Defective |

### Key Lesson
Always verify the product listing's compatibility list BEFORE choosing a return reason. If the listing never claimed to work with the user's device, use "Irrtümlich bestellt", not "Entspricht nicht der Beschreibung".
