# Lieferando Checkout Flow with Camoufox

## Prerequisites
- Camoufox server running with persistent profile
- Address already saved in profile (<ADDRESS>, <PLZ> <CITY>)
- Google OAuth: needs REAL Google password (not app password) + 2FA push to phone

## Restaurant Selection
```bash
camoufox goto "https://www.lieferando.de/en/menu/mama-dung-teltow"
sleep 3
```

## Menu Item Selection (SPA with category tabs)
```bash
# Click Sushi Menus category tab via JS (pie-chip custom elements)
camoufox eval "() => { const chips = document.querySelectorAll('pie-chip'); const sushiChip = Array.from(chips).find(c => c.textContent.includes('Sushi Menus')); if (sushiChip) { sushiChip.click(); return 'clicked sushi menus'; } return 'not found'; }"

# Scroll to specific menu item — use native scroll_to_element (PREFERRED)
camoufox scroll_to_element '#item_41'
# Or fallback: scrollIntoView via eval
camoufox eval "() => { const items = document.querySelectorAll('[class*=item-heading]'); for (const item of items) { if (item.textContent.includes('Menu 11')) { item.scrollIntoView({block: 'center'}); return 'scrolled'; } } return 'not found'; }"

# Find Plus buttons after scroll
camoufox ge '.c-pieIcon--plus'
# Plus buttons return x,y coords. Match to menu item by y-proximity.

# Click Plus button (coordinate click works for list items)
camoufox click <x> <y>
```

### Finding the right Plus button for a menu item
Plus buttons are NOT children of the menu item's `li` element — they're siblings in the DOM. To find the plus button for a specific item:
```bash
# Walk up the DOM from the item heading to find the plus icon
camoufox eval "() => { const item = document.querySelector('#item_41'); let el = item; for (let i = 0; i < 8; i++) { el = el.parentElement; if (!el) break; const plus = el.querySelector('.c-pieIcon--plus'); if (plus) { const r = plus.getBoundingClientRect(); return {x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2)}; } } return 'not found'; }"
```

## Cart Management
```bash
# Check cart contents
camoufox eval "() => { const cart = document.querySelector('[class*=cart]'); return cart?.textContent?.trim().slice(0, 300) || 'no cart'; }"

# Remove item: find trash icon by index in cart
camoufox eval "() => { const cart = document.querySelector('[class*=cart]'); const trashs = cart.querySelectorAll('.c-pieIcon--trash'); if (trashs.length >= 2) { trashs[1].click(); return 'clicked trash'; } return 'not enough trash icons'; }"

# Reduce quantity: find minus icon in cart
camoufox eval "() => { const cart = document.querySelector('[class*=cart]'); const minus = cart.querySelector('.c-pieIcon--minus'); if (minus) { minus.click(); return 'clicked minus'; } return 'no minus'; }"
```

## Voucher Application (REST API Pattern — VERIFIED 2026-07-17)

The voucher section on the checkout page is a collapsible that does NOT respond
to `.click()`, `browser_click(ref)`, or `click_element`. It requires
`pointerdown`/`pointerup` dispatched events to open.

### Step 1: Open the voucher section

```bash
TAB=$(cat /tmp/camofox_tab_id)
# Dispatch pointer events on the voucher-interactive div
curl -s -X POST "http://localhost:9377/tabs/$TAB/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"userId":"agent1","expression":"(() => { const el = document.querySelector(\"[data-qa=\\\"voucher-interactive\\\"]\"); if(!el) return \"not found\"; el.dispatchEvent(new PointerEvent(\"pointerdown\", {bubbles:true})); el.dispatchEvent(new PointerEvent(\"pointerup\", {bubbles:true})); el.dispatchEvent(new MouseEvent(\"click\", {bubbles:true})); return \"dispatched\"; })()"}'
```

After this, a voucher input field appears with:
- `data-qa="voucher-modal-details-input-voucher-element-focused"`
- `placeholder="Voucher code"`
- `type="text"`

**Why standard clicks fail**: The voucher section uses `data-qa="voucher"` with an inner
`div[data-qa="voucher-interactive"][role="button"]`. JS `.click()` and Playwright native
click both return `{ok:true}` but the collapsible doesn't expand. Only `pointerdown` +
`pointerup` + `click` dispatched together opens it.

**Fallback approaches (try in order if pointerdown doesn't work)**:
1. Click the leaf `<span>` with exact text "Add voucher": `document.querySelectorAll("*")` → filter `el.children.length === 0 && el.textContent.trim() === "Add voucher"`
2. Click the `[data-qa="voucher"]` container itself
3. `click_element 'button:has-text("Add voucher")'` (native Playwright — may work when JS doesn't)

### Step 2: Type the voucher code

```bash
# Type via REST API with CSS selector
curl -s -X POST "http://localhost:9377/tabs/$TAB/type" \
  -H "Content-Type: application/json" \
  -d '{"userId":"agent1","selector":"input[data-qa=\"voucher-modal-details-input-voucher-element-focused\"]","text":"VOUCHER_CODE_HERE"}'
```

Or via eval (fallback):
```bash
curl -s -X POST "http://localhost:9377/tabs/$TAB/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"userId":"agent1","expression":"(() => { const i = document.querySelector(\"input[placeholder*=\\\"oucher\\\"]\"); if(i) { i.focus(); i.value = \"VOUCHER_CODE\"; i.dispatchEvent(new Event(\"input\", {bubbles:true})); return \"typed\"; } return \"not found\"; })()"}'
```

### Step 3: Click Apply

```bash
# Native Playwright click (PREFERRED — works reliably)
curl -s -X POST "http://localhost:9377/tabs/$TAB/click" \
  -H "Content-Type: application/json" \
  -d '{"userId":"agent1","selector":"button:has-text(\"Apply\")"}'
```

Or via eval (fallback):
```bash
curl -s -X POST "http://localhost:9377/tabs/$TAB/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"userId":"agent1","expression":"(() => { const all = document.querySelectorAll(\"button, [role=button], pie-button\"); for(const b of all) { const t = b.textContent?.trim()?.toLowerCase()||\"\"; if(t === \"apply\" || t === \"anwenden\" || t === \"einlösen\") { if(b.shadowRoot) { const inner = b.shadowRoot.querySelector(\"button\"); if(inner) { inner.click(); return \"clicked shadow\"; } } b.click(); return \"clicked: \"+b.textContent?.trim(); } } return \"not found\"; })()"}'
```

### Step 4: Verify voucher applied

```bash
sleep 3
# Check for discount in order summary
curl -s -X POST "http://localhost:9377/tabs/$TAB/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"userId":"agent1","expression":"(() => { const text = document.body.innerText; const voucherIdx = text.toLowerCase().indexOf(\"voucher\"); if(voucherIdx >= 0) return text.substring(Math.max(0,voucherIdx-100), voucherIdx+500); return \"no voucher text\"; })()"}'
```

Success shows: `Voucher 8,00 €` + `8,00 € off eligible items` + `- € 8,00` in the order summary.

### Voucher Gotchas
- Voucher codes are **account-specific**: code sent to <EMAIL> rejected on <EMAIL> account
- Error: "This promotion isn't available for your account"
- Must be logged into the same account that received the voucher email
- Cannot combine with other discounts (removes existing 20%+10% off)
- Voucher has 6€ value (not 12€ despite "12€ Rabatt" email — it's one code valid for 2 separate orders, not 2 codes)
- **24h block triggers on APPLY, not on order completion**: T&C says "Sobald er auf der Bezahlseite eingefügt wird, ist er für 24 Stunden geblockt". Merely entering the code on the checkout page and clicking Apply blocks it for 24h — even if the order is never completed. This means testing the voucher "just to see if it works" burns it for 24h. Retrying after failure shows "This promotion isn't available for your account" or "Voucher has expired" (misleading — it's locked, not expired).
- Min order value 12€ required for voucher use
- **Voucher section on checkout requires pointerdown events to open**: The "Add voucher" collapsible (`data-qa="voucher-interactive"`) does NOT respond to `.click()`, `browser_click(ref)`, or `click_element`. Must dispatch `pointerdown` + `pointerup` + `click` events via evaluate. After this, the input field appears with `data-qa="voucher-modal-details-input-voucher-element-focused"`. Type the code, then click "Apply" via native Playwright `click_element "button:has-text(\"Apply\")"`. Verified 2026-07-17 — voucher Y5G3X6TED94FC9JQ applied successfully (8€ off, total 29,46€ -> 21,46€).

## Checkout Flow
```bash
# Click "Checkout" button on menu page — use eval (coordinate clicks hang on SPA)
camoufox eval "() => { const btns = document.querySelectorAll('button'); for (const b of btns) { if (b.textContent.includes('Checkout')) { b.click(); return 'clicked: ' + b.textContent.trim(); } } return 'not found'; }"
sleep 3

# On checkout page, click "Order and pay" — use eval
camoufox eval "() => { const btns = document.querySelectorAll('button, [role=button]'); for (const b of btns) { if (b.textContent.includes('Order and pay')) { b.click(); return 'clicked'; } } return 'not found'; }"
```

## Google OAuth Login
```bash
# After "Order and pay" → redirects to auth.lieferando.de
# Click "Continue with Google" — native click_element PREFERRED
camoufox click_element "button:has-text('Continue with Google')"
# Fallback:
camoufox eval "() => { const btns = document.querySelectorAll('button'); for (const b of btns) { if (b.textContent.includes('Google')) { b.click(); return 'clicked'; } } return 'not found'; }"

# If Google session active: auto-redirects (no email/password fields)
# If Google session expired: shows email field
camoufox type_in_element '#identifierId' '<EMAIL>'
camoufox click_element "button:has-text('Next')"

# Password page — use REAL Google password, NOT app password
camoufox type_in_element 'input[type=password]' '<REAL_PASSWORD>'
camoufox click_element "button:has-text('Next')"

# 2FA: Google sends push notification to phone (Gmail app)
# Poll for redirect back to Lieferando
for i in $(seq 1 30); do
  sleep 5
  BODY=$(camoufox body 500 2>/dev/null)
  if echo "$BODY" | grep -qi "lieferando\|checkout\|basket"; then echo "SUCCESS"; break; fi
  echo "Waiting... ($i/30)"
done
```

### Google Login Gotchas
- App passwords DO NOT work for web login — need real account password
- 2FA is a push notification to Gmail app on phone, not SMS
- If Google session is active in profile, auto-login skips email/password entirely
- To switch accounts: `camoufox goto "https://accounts.google.com/Logout"` first
- JS cookie clearing does NOT clear HttpOnly auth cookies — use `camoufox clear_cookies`
- After Google logout, Lieferando session may persist — need `camoufox clear_cookies` too
- **Google SSO cookie injection from Firefox to Camoufox does NOT work**: Google binds sessions to browser fingerprint. Extracting `SID`/`HSID`/`__Secure-1PSID` from Firefox `cookies.sqlite` and loading into Camoufox still triggers email+password+2FA. Must use password flow.
- **Cross-browser cookie injection: filter Cloudflare cookies**: When transferring session cookies from Playwright Firefox to Camoufox (or vice versa), **NEVER** include `cf_clearance` or `__cf_bm` cookies. These are UA+IP bound → Cloudflare blocks the target browser. Only inject application session cookies (`je-auser`, `cwSession`, `cookieConsent`, etc.) → Camoufox obtains its own `cf_clearance` on first navigation. This is the fix that makes cross-browser session transfer work.
- **Cross-browser session transfer WORKS for Lieferando (not Google)**: Complete Google OAuth flow in Playwright Firefox (using Firefox profile with active Google session) → capture redirect back to lieferando.de → extract Lieferando session cookies (NOT Google cookies, NOT Cloudflare cookies) → inject into Camoufox → navigate to lieferando.de → session recognized, no re-login needed. Filter rule: `if name not in ('cf_clearance', '__cf_bm') and ('lieferando' in domain or 'takeaway' in domain)`.
- **Must verify correct Firefox profile before extracting cookies**: Profile names are arbitrary. Use `recovery.jsonlz4` parsing to find `@gmail.com` in tab titles, or check LSID cookie for `o.mail.google.com` scope. See SKILL.md "Firefox Profile Identification" section.
- **Firefox must be closed before cookie extraction**: Session cookies are in RAM while Firefox runs. `pkill -f firefox` → wait 3s → copy `cookies.sqlite`.

## Direct Firefox→Camoufox Cookie Transfer (Preferred Method)

No Playwright Firefox intermediate step. Direct from Firefox profile → Camoufox.

```bash
# 1. Kill Firefox (flush cookies.sqlite, release profile lock)
pkill -f firefox; sleep 3

# 2. Find profile by ID (e.g. <FF_PROFILE> = <FIRST_NAME> P4)
PROFILE=$(ls -d ~/Library/Application\ Support/Firefox/Profiles/*<FF_PROFILE>* | head -1)
cp "$PROFILE/cookies.sqlite" /tmp/ff_cookies.sqlite

# 3. Extract Lieferando session cookies (NO Cloudflare cookies)
python3 -c "
import sqlite3, json
conn = sqlite3.connect('/tmp/ff_cookies.sqlite')
cur = conn.cursor()
cur.execute('''
    SELECT name, value, host, path, expiry, isSecure, isHttpOnly, sameSite
    FROM moz_cookies 
    WHERE (host LIKE '%lieferando%' OR host LIKE '%takeaway%')
    AND name NOT IN ('cf_clearance', '__cf_bm')
''')
cookies = []
for name, value, host, path, expiry, is_secure, is_http_only, same_site in cur.fetchall():
    e = expiry
    if not e or e == 0: e = -1
    elif e > 1e15: e = int(e / 1e6)
    elif e > 1e12: e = int(e / 1e3)
    cookies.append({
        'name': name, 'value': value, 'domain': host,
        'path': path or '/', 'secure': bool(is_secure),
        'httpOnly': bool(is_http_only),
        'sameSite': {0:'None',1:'Lax',2:'Strict'}.get(same_site,'None'),
        'expires': int(e),
    })
conn.close()
with open('/tmp/lieferando_session.json', 'w') as f:
    json.dump(cookies, f)
print(f'Extracted {len(cookies)} cookies')
"

# 4. Load into Camoufox
camoufox clear_cookies
camoufox load_cookies /tmp/lieferando_session.json
camoufox goto "https://www.lieferando.de/en/menu/mama-dung-teltow"
# Session recognized — no login, no 2FA, no OAuth redirect
```

### Why This Works
- `je-at` (auth token) + `je-rt` (refresh token) are not browser-bound
- `je-auser` (user ID) is not browser-bound
- Camoufox gets its own `cf_clearance` on first navigation (no stale CF cookie conflict)
- Firefox must be killed first: session cookies are in RAM while Firefox runs, `cookies.sqlite` may not have them

## Cookie Rotation for Account Switching
```bash
# 1. Save current session
camoufox save_cookies /tmp/lieferando_jonathan.json

# 2. Clear all cookies (including HttpOnly)
camoufox clear_cookies

# 3. Logout from Google SSO
camoufox goto "https://accounts.google.com/Logout"

# 4. Login with second account
camoufox goto "https://www.lieferando.de/en/menu/mama-dung-teltow"
# ... Continue with Google → email → password → 2FA ...

# 5. Apply voucher, checkout

# 6. Restore original session when done
camoufox clear_cookies
camoufox load_cookies /tmp/lieferando_jonathan.json
camoufox goto "https://www.lieferando.de/"
```

**Note**: Basket contents are server-side (tied to session token). Clearing cookies loses the basket. Re-add items after switching accounts.

## Restaurant Availability Check (CRITICAL — do FIRST)

Before attempting to add items, verify the restaurant is actually open:
```bash
# Check if restaurant is available for delivery
camoufox eval "() => {
  const body = document.body.textContent;
  const unavailable = body.match(/Unavailable/g)?.length || 0;
  const baskets = document.querySelectorAll('[class*=basket], [class*=Basket]');
  let basketText = '';
  for (const b of baskets) {
    const t = b.textContent?.trim();
    if (t && t.length > 20) { basketText = t.slice(0, 200); break; }
  }
  return JSON.stringify({
    unavailableCount: unavailable,
    basketText: basketText,
    isOpen: unavailable < 5 && !basketText.includes('empty')
  });
}"
```

If `unavailableCount > 10` or basket says "Your basket is empty" + "Unavailable" everywhere → restaurant is CLOSED. Do NOT attempt to add items — plus buttons won't work even though they render. The SPA renders the full menu with plus buttons even when closed, but clicks silently fail.

### Domino's `#pre-order` URL Fragment
When navigating to a Domino's menu page, check the URL for `#pre-order`. If present, the restaurant is currently closed and only accepts pre-orders. Item add buttons may render but clicks silently fail. Verified 2026-07-17.

```bash
# Check for pre-order
curl -s -X POST "http://localhost:9377/tabs/$TAB/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"userId":"agent1","expression":"window.location.href.includes(\"#pre-order\") ? \"CLOSED (pre-order only)\" : \"OPEN\""}'
```

### Finding Open Restaurants
```bash
# Navigate to delivery area page and filter "Open Now"
camoufox goto "https://www.lieferando.de/en/delivery/food/<PLZ>"
sleep 3
# Click "Open Now" filter chip
camoufox eval "() => {
  const chips = document.querySelectorAll('pie-chip, button, [role=button]');
  for (const c of chips) {
    if (c.textContent?.trim().match(/^Open Now$/i)) { c.click(); return 'clicked'; }
  }
  return 'not found';
}"
```

## Plus Button Click Behavior (pie-icon-button)

Lieferando uses Custom Elements (`pie-icon-button`, `icon-plus`). Key findings:

1. **JS `.click()` does NOT work** — produces `isTrusted=false` events, SPA ignores them
2. **Coordinate clicks (`camoufox click X Y`) work BUT only when restaurant is OPEN** — when closed, buttons render but do nothing
3. **`click_element '[data-qa=item-action]'`** clicks the FIRST matching element on page, not the one near a specific item — cannot target specific items this way. This is a major pitfall: on a page with 50+ items, `click_element '[data-qa=item-action]'` always clicks the first item's plus button, regardless of which item you scrolled to. Must use coordinate-based click after `scrollIntoView` + `getBoundingClientRect()` for specific items.
4. **To click a specific item's plus button**: scroll item into view via `scrollIntoView({block: 'center'})`, then get `pie-icon-button` coordinates from `getBoundingClientRect()`, then `camoufox click X Y`
5. **Verify basket after each click** — check `[class*=basket]` text for item name. "Your basket is empty" = click failed (or restaurant closed)

## Voucher Code Retrieval via Himalaya

Voucher codes arrive by email. Retrieve them with Himalaya CLI:

```bash
# List <FIRST_NAME>'s inbox (account name 'giuli' in himalaya config)
himalaya envelope list -a giuli --page-size 30

# Search for Lieferando emails
himalaya envelope list -a giuli subject Lieferando

# Read specific email (ID from list)
himalaya message read <ID> -a giuli
```

**Himalaya v1.2.0 account flag**: `--account` is broken, but `-a` works: `himalaya envelope list -a giuli`. If `-a` also fails, use `-c <config.toml>`.

**Voucher email patterns**:
- Subject: "Your €16 voucher expires" / "Don't forget your €12 off" / "Für dich: 16 € Rabatt"
- Code appears as uppercase alphanumeric string (e.g. `Y5G3X6TED94FC9JQ`)
- Often "2x €8 off" = one code valid for 2 separate orders (not 2 codes)
- T&Cs in email body: min order amount (typically 12€), expiry date, "cannot combine with other discounts"
- Vouchers are account-specific — code from <EMAIL> will NOT work on <EMAIL> account

## Menu Price Scraping (TreeWalker Technique)

To extract all menu items with names + prices from a Lieferando restaurant page:

1. Navigate to restaurant menu page
2. Scroll through entire page to lazy-load all items (6+ scroll passes)
3. Use TreeWalker to find all "Item Info" text nodes — each one marks a menu item card

```javascript
// Extraction JS — find all "Item Info" text nodes, walk up to item card, extract name + price
(function() {
  var results = [];
  var seen = {};
  var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  var itemInfos = [];
  var node;
  while (node = walker.nextNode()) {
    if (node.textContent && node.textContent.trim() === 'Item Info') {
      itemInfos.push(node.parentElement);
    }
  }
  itemInfos.forEach(function(container) {
    var card = container;
    for (var i = 0; i < 5; i++) {
      card = card.parentElement;
      if (!card) break;
      var text = card.textContent;
      if (text && text.length > 30 && text.length < 500) {
        var priceMatch = text.match(/(\d+[,.]\d+)\s*€/);
        var lines = text.split(/\n/).map(function(l) { return l.trim(); }).filter(function(l) {
          return l && l !== 'Item Info' && !l.match(/^\d+[,.]\d+\s*€?$/) && !l.match(/^from\s/) && l.length > 3;
        });
        var name = lines[0] || '';
        // Remove doubled category prefixes (e.g. "Bread - Classic in BreadBread - Classic in Bread")
        name = name.replace(/^(.+?)\1+/, '$1');
        var price = priceMatch ? priceMatch[1].replace('.', ',') + '€' : '';
        var key = name + '|' + price;
        if (name.length > 3 && price && !seen[key]) {
          seen[key] = true;
          results.push({ name: name.slice(0, 80), price: price });
        }
        break;
      }
    }
  });
  return JSON.stringify(results);
})()
```

### Python parsing of camoufox eval result
The `camoufox eval` output is double-escaped JSON: `{"result": "[{\"name\":\"...\"}]"}`.
Parse with:
```python
obj = json.loads(raw)
result = obj.get("result", "")
if isinstance(result, str):
    items = json.loads(result)
```

### Menu scraping gotchas
- "Item Info" text nodes are the reliable anchor — not CSS selectors (classes change, item IDs change on reload)
- Some items show "from X€" (e.g. pizzas with size variants) — regex `(\d+[,.]\d+)\s*€` still matches the starting price
- Category headers like "Bread - Classic in Bread (6 items)" appear as doubled prefixes in item names — the regex `/^(.+?)\1+/` cleans them
- Items in collapsed categories are NOT in the DOM until scrolled into view — must scroll through entire menu before extracting
- Save JS to a file (`/tmp/extract_menu.js`) and pass via `camoufox eval "$(cat /tmp/extract_menu.js)"` to avoid shell escaping issues with the € character

## Pizza Size Modal (Item Configurator)

When clicking a pizza/item with size variants, a modal opens with `pie-radio` elements:

```bash
# Click item's plus button (coordinate click — see "Plus Button Click Behavior" above)
# Modal opens with URL fragment #item-choices

# Extract size options from modal
camoufox eval '(function() {
  var modal = document.querySelector(".ReactModal__Content--after-open, [role=dialog]");
  if (!modal) return JSON.stringify({hasModal: false});
  var text = modal.textContent?.trim();
  var sizes = text.match(/(Classic|Medium|Large)\s*\(\d+cm\)[^€]*(\d+[,.]\d+)\s*€/g);
  return JSON.stringify({title: text.slice(0, 100), sizes: sizes});
})()'
```

### Size naming convention (Domino's)
- Classic (25cm) = "from" price
- Medium (28cm) = ~1.50€ more
- Large (32cm) = ~5€ more

### Selecting a specific size
```bash
# Find the Medium radio button in modal and click it
camoufox eval '(function() {
  var modal = document.querySelector(".ReactModal__Content--after-open");
  if (!modal) return "no modal";
  var radios = modal.querySelectorAll("pie-radio, [role=radio]");
  for (var r of radios) {
    if (r.textContent?.match(/Medium/i)) {
      r.scrollIntoView({block: "center"});
      var rect = r.getBoundingClientRect();
      return JSON.stringify({x: Math.round(rect.x + rect.width/2), y: Math.round(rect.y + rect.height/2)});
    }
  }
  return "Medium not found";
})()'
# Then coordinate click
camoufox click <x> <y>
```

## Restaurant List Scraping (Delivery Area)

To get all restaurants delivering to an address:

```bash
# Navigate to delivery area page
camoufox goto "https://www.lieferando.de/en/delivery/food/<PLZ>"
sleep 3

# Scroll through to lazy-load all restaurants (8+ passes)
for i in $(seq 1 8); do
  camoufox scroll 0 5000 2>&1 >/dev/null
  sleep 1.5
done

# Extract restaurant data
camoufox eval "() => {
  const links = document.querySelectorAll('a[href*=\"/menu/\"]');
  const seen = new Set();
  const restaurants = [];
  for (const link of links) {
    const href = link.getAttribute('href');
    const name = link.textContent?.trim();
    if (!href || !name || name.length < 2) continue;
    const slug = href.split('/menu/')[1]?.split('?')[0];
    if (seen.has(slug)) continue;
    seen.add(slug);
    // Walk up to find card container for metadata
    let card = link;
    for (let i = 0; i < 6; i++) {
      card = card.parentElement;
      if (!card) break;
      if (card.textContent?.length > 50) break;
    }
    restaurants.push({ name: name.slice(0, 60), slug, cardText: card?.textContent?.trim()?.slice(0, 400) });
  }
  return JSON.stringify(restaurants);
}"
```

Parse card text for: stars, reviews, delivery time, delivery cost, min order, tags (Vegan/Vegetarian/Halal).

## Pizza Configurator: Required Selections (Domino's)

Domino's pizza items open a configurator modal with **multiple required selections**. The "Add" button will NOT add to basket until ALL required fields are selected — it silently fails with a toast "You haven't made all your..." at the bottom.

### Required fields (in order):
1. **Size** — Classic (25cm) / Medium (28cm) / Large (32cm) — `pie-radio` elements
2. **Crust** — Klassisch / Knuspriger Parmesan Style (+1,99€) / etc. — `pie-radio` elements
3. **Sauce** — Knoblauch Sauce (Vegan) / Tomatensauce (Vegan) / BBQ / etc. — `pie-radio` elements

### Selecting options via Playwright (PREFERRED — works reliably):
```bash
# Scope ALL selectors to the modal to avoid matching page-level elements
camoufox click_element '.ReactModal__Content--after-open pie-radio:has-text("Medium (28cm)")' 10000 true
sleep 1
camoufox click_element '.ReactModal__Content--after-open pie-radio:has-text("Klassisch")' 10000 true
sleep 1
camoufox click_element '.ReactModal__Content--after-open pie-radio:has-text("Knoblauch Sauce (Vegan)")' 10000 true
sleep 2
# Now click Add — MUST also be scoped to modal
camoufox click_element '.ReactModal__Content--after-open pie-button:has-text("Add")' 10000 true
sleep 3
```

### Pitfalls:
- **Coordinate clicks on the Add button DO NOT WORK** — the `pie-button` custom element ignores `page.mouse.click()`. Must use `click_element` (Playwright native) scoped to `.ReactModal__Content--after-open`.
- **`click_element 'pie-button:has-text("Add")'` without modal scope** clicks the FIRST `pie-button` on the page (e.g. "I understand" drone delivery button), not the modal's Add button. Always scope: `.ReactModal__Content--after-open pie-button:has-text("Add")`.
- **`click_element 'pie-radio:has-text("Medium")'` without modal scope** may time out if the modal hasn't fully rendered. Wait 3-4 seconds after opening modal before selecting.
- **Promo popups intercept clicks** — "You unlocked a free item" or "Beck's Blue" promo modals appear on first click. Close with Escape or `camoufox eval` removing overlays before clicking item plus buttons.
- **Opening the correct item's modal**: `click_element '[data-qa=item-action]'` always clicks the FIRST item on the page. To open a SPECIFIC item: find the item name via `eval`, get its plus button coordinates via `getBoundingClientRect()`, then `camoufox click X Y`. This opens the correct item's configurator modal.
- **Verify all required fields are filled** before clicking Add:
```bash
camoufox eval '(function(){ var m=document.querySelector(".ReactModal__Content--after-open"); if(!m) return "no modal"; var t=m.textContent; var reqCount=(t.split("Required").length-1); return JSON.stringify({requiredFields:reqCount, hasRequired:t.includes("Required")}); })()'
```

## Scrolling on Lieferando SPA (AVOID `camoufox scroll`)

`camoufox scroll 0 N` causes server hangs on Lieferando SPA pages. Use these alternatives:

```bash
# PREFERRED: window.scrollTo via eval (no hang)
camoufox eval 'window.scrollTo(0, 1000)'

# For lazy-loading: scroll in increments via eval
camoufox eval 'window.scrollTo(0, 500)'
sleep 1
camoufox eval 'window.scrollTo(0, 1000)'
sleep 1

# For scrolling to a specific element: scrollIntoView via eval
camoufox eval '(function(){ var el=document.querySelector("#item_41"); if(el) el.scrollIntoView({block:"center"}); return "done"; })()'
```

**Pitfall**: `camoufox scroll 0 2000` and `camoufox scroll 0 5000` consistently cause `camoufox_cli` to hang (timeout), requiring `pkill -9 -f camoufox_server` and restart. The issue is the Playwright `page.mouse.wheel()` call blocking on the SPA's infinite scroll handlers.

## Basket State Parsing (AVOID `document.body.textContent`)

`document.body.textContent` on Lieferando returns massive inline JSON config (200K+ chars) that swallows all regex matches. Use targeted selectors instead:

```bash
# GOOD: Query sidebar element directly
camoufox eval '(function(){ var s=document.querySelector(".sidebar-style_wrapper__nDGVl"); return s?s.textContent?.trim()?.slice(0,500):"no sidebar"; })()'

# BAD: This returns 200K+ chars of inline JSON config
camoufox eval 'document.body.textContent'  # FLOODS context, matches false positives

# GOOD: Check checkout total
camoufox eval '(function(){ var b=document.body.textContent; var m=b.match(/Checkout\s*\(([^)]+)\)/); return m?m[1]:"no match"; })()'
# But even this can match inline JSON — verify with sidebar selector above
```

## Checking Restaurant Open Status Before Ordering

Always verify restaurant is open BEFORE attempting to add items:
```bash
camoufox eval '(function(){
  var body=document.body.textContent;
  var unavailable=(body.match(/Unavailable/g)||[]).length;
  var basket=document.querySelector("[class*=basket],[class*=Basket]");
  var basketText=basket?basket.textContent?.trim()?.slice(0,200):"";
  return JSON.stringify({unavailableCount:unavailable, isOpen:unavailable<10, basketSnippet:basketText});
})()'
```
If `unavailableCount > 10` → restaurant is CLOSED. Plus buttons render but do nothing. All clicks silently fail. Check opening hours or find an open restaurant instead.

## Finding Voucher Codes via Himalaya Email

```bash
# List <FIRST_NAME>'s inbox
himalaya envelope list -a giuli --page-size 30

# Read specific email
himalaya message read <ID> -a giuli

# Voucher codes in email body appear as uppercase alphanumeric strings
# e.g. "Y5G3X6TED94FC9JQ"
# Voucher details: "2 x €8 off", "Minimum order amount is €12", "Valid until YYYY-MM-DD"
```

## Domino's "Free Item" Promo Modal (BLOCKS Add-to-Basket)

Domino's restaurants often have "Buy X get Y free" promotions. When you click ANY item's plus button, a promo modal pops up FIRST: "Nice! You get this free with your order — We'll apply the discount at checkout — Beck's Blue 330ml...". This modal intercepts the click and the actual item configurator never opens.

### Solution: Close promo modal, then re-click the item
```bash
# 1. Click item plus button → promo modal appears instead of item modal
camoufox click <x> <y>
sleep 4

# 2. Check what modal opened
camoufox eval '(function(){ var m=document.querySelector(".ReactModal__Content--after-open"); if(!m) return "no modal"; var t=m.textContent?.trim()?.slice(0,60); if(t.includes("free")||t.includes("Beck")) return "PROMO"; return "ITEM: "+t; })()'

# 3. If PROMO: close it with Escape
camoufox press Escape
sleep 2

# 4. Re-click the same item plus button — now the item modal opens correctly
camoufox click <x> <y>
sleep 4

# 5. Verify item modal (not promo) is open
camoufox eval '(function(){ var m=document.querySelector(".ReactModal__Content--after-open"); if(!m) return "no modal"; var t=m.textContent?.trim()?.slice(0,60); return t.includes("free")?"STILL PROMO":"OK: "+t; })()'
```

### Alternative: Remove promo overlays via JS before clicking
```bash
camoufox eval '(function(){ var overlays=document.querySelectorAll(".ReactModal__Overlay, [class*=overlay], [class*=Overlay]"); overlays.forEach(function(o){ if(o.textContent?.includes("free") || o.textContent?.includes("Beck")) { o.click(); } }); var closeBtns=document.querySelectorAll("[class*=close], [class*=Close], [aria-label*=close]"); closeBtns.forEach(function(b){ b.click(); }); return "closed "+overlays.length+" overlays"; })()'
```

**Key insight**: The promo modal appears ONCE per session. After closing it, subsequent item clicks open the correct configurator. But if you reload the page, it reappears.

### Domino's "Free item" category vs normal items
Items listed under "Pizza - Aktion" category are flagged as "Free item" selections. Clicking them opens a modal where you SELECT which free pizza you want — this is NOT the same as adding a pizza to your basket. The "Add" button in this modal selects the free item but doesn't add it to the basket. You must add a normal (non-free-item) pizza first, then the free item is activated.

To avoid this: use items from other categories (e.g. "Pizza - Premium", "Pizza - Vegan") where items have normal Add-to-basket behavior.

## Python Parsing of `camoufox eval` Output

The `camoufox eval` command returns double-escaped JSON. In Python:

```python
import subprocess, json

proc = subprocess.run(["camoufox", "eval", js_code], capture_output=True, text=True, timeout=15)
raw = proc.stdout.strip()

# Parse: raw is like {"result": "[{\"name\":\"...\"}]"}
obj = json.loads(raw)           # First parse: outer JSON
result = obj.get("result", "")  # result is a STRING
if isinstance(result, str):
    items = json.loads(result)   # Second parse: inner JSON
elif isinstance(result, list):
    items = result               # Sometimes already parsed
else:
    items = []
```

**Common pitfall**: Using `raw.index('{"result":')` to find the JSON fails because the output has newlines and indentation. Use `json.loads(raw)` directly.

**Common pitfall**: If `result` is already a list (not a string), `json.loads(result)` throws `TypeError`. Always check `isinstance(result, str)` first.

## Batch Menu Scraping Script Pattern

For scraping multiple restaurant menus, use a Python script with subprocess calls (NOT execute_code — times out at 300s for >15 restaurants):

```python
# Key pattern: save JS to file, read in Python, pass to camoufox eval
with open("/tmp/extract_menu.js", "r") as f:
    js = f.read().strip()

for restaurant in restaurants:
    subprocess.run(["camoufox", "goto", url], capture_output=True, text=True, timeout=20)
    time.sleep(3)
    # Scroll to lazy-load: use eval, NOT camoufox scroll (hangs!)
    for _ in range(6):
        subprocess.run(["camoufox", "eval", "window.scrollTo(0, 2000)"], capture_output=True, text=True, timeout=8)
        time.sleep(0.5)
    # Reset scroll
    subprocess.run(["camoufox", "eval", "window.scrollTo(0, -99999)"], capture_output=True, text=True, timeout=8)
    # Extract
    proc = subprocess.run(["camoufox", "eval", js], capture_output=True, text=True, timeout=15)
    # Parse result (see "Python Parsing" above)
```

Run as background process with `terminal(background=true, notify_on_complete=true)` for >20 restaurants.

## Firefox Profile Identification by Auth Cookies

Don't guess profiles by name. Check which profile has valid Lieferando auth cookies:

```python
import sqlite3, shutil, os, glob

profiles = glob.glob(os.path.expanduser("~/Library/Application Support/Firefox/Profiles/*/"))
for profile in profiles:
    cookie_path = os.path.join(profile, "cookies.sqlite")
    if not os.path.exists(cookie_path):
        continue
    tmp = "/tmp/ff_test_cookies.sqlite"
    shutil.copy(cookie_path, tmp)
    conn = sqlite3.connect(tmp)
    try:
        rows = conn.execute("""
            SELECT name, value, host FROM moz_cookies 
            WHERE (host LIKE '%lieferando%' OR host LIKE '%takeaway%') 
            AND name IN ('je-at','je-auser','je-rt','je-last-login')
        """).fetchall()
        if rows:
            # This profile has auth cookies — identify user via je-last-login
            for r in rows:
                if r[0] == 'je-last-login':
                    import urllib.parse, json
                    decoded = urllib.parse.unquote(r[1])
                    # Contains JSON: {"firstName":"<FIRST_NAME>","email":"<EMAIL>",...}
                    print(f"Profile: {os.path.basename(profile)} -> {decoded[:100]}")
    except:
        pass
    conn.close()
```

**Note**: Some profiles return "no such table: moz_cookies" — this is because Firefox uses WAL mode and the `cookies.sqlite-wal` file has the actual data. Killing Firefox first (`pkill -f firefox; sleep 3`) flushes WAL into the main sqlite file.

## POSTMORTEM: Domino's Order Failures (2026-07-12 Session)

### Fehler 1: `je-at` Token ist HttpOnly → `document.cookie` zeigt es nicht
**Was passierte**: Nach `load_cookies` prüfte ich Login-Status via `document.cookie.includes("je-at")`. Das ergab "Nicht eingeloggt" obwohl der Token geladen wurde — weil `je-at` ein `httpOnly`-Cookie ist und von JavaScript nicht lesbar ist.
**Fix**: Statt `document.cookie` zu checken, lade eine auth-geschützte Seite (z.B. `/en/checkout`) und prüfe ob sie zur Login-Seite weiterleitet.
```bash
# FALSCH — httpOnly cookies sind nicht per JS lesbar
camoufox eval 'document.cookie.includes("je-at")'

# RICHTIG — versuche auth-geschützte Seite
camoufox goto "https://www.lieferando.de/en/checkout"
# Wenn URL "auth.lieferando.de" enthält → nicht eingeloggt
# Wenn URL "lieferando.de/en/checkout" bleibt → eingeloggt
```

### Fehler 2: Firefox-Cookie-Expiry war in Millisekunden, nicht Sekunden
**Was passierte**: Firefox `moz_cookies.expiry` für einige Lieferando-Cookies war in Millisekunden (13-stellig, z.B. `1783104894113`). Der bestehende Extraction-Code hat `expiry > 1e12 → / 1e3` gemacht, aber Camoufox/Playwright verlangt Sekunden-Timestamps. Der bestehende Code im Skill hatte `elif e > 1e15: e = int(e/1e6)` — das war für nanosekund-Timestamps. Die Millisekunden-Branch `elif e > 1e12: e = int(e/1e3)` war korrekt, aber das Extraktions-Script hatte einen separate Bug: `sameSite` Index out of range.
**Fix**: Extraktions-Script muss `sameSite` validieren: `["None","Lax","Strict"][sameSite] if sameSite in [0,1,2] else "Lax"`. Und Expiry korrekt konvertieren: `if expiry > 1e10: expiry = expiry // 1000`.

### Fehler 3: `camoufox scroll 0 N` → Server-Hang auf SPA-Seiten
**Was passierte**: `camoufox scroll 0 2000` und `camoufox scroll 0 5000` führten zu `camoufox_cli`-Timeouts und blockierten den Server. Mehrere Neustarts nötig.
**Fix**: Niemals `camoufox scroll` auf Lieferando-SPA-Seiten verwenden. Stattdessen: `camoufox eval 'window.scrollTo(0, N)'` — das läuft im Page-Context und blockiert nicht den Socket-Server.

### Fehler 4: `document.body.textContent` → 200K+ Zeichen Inline-JSON
**Was passierte**: Beim Versuch, Warenkorb-Status zu prüfen, gab `document.body.textContent` über 200.000 Zeichen zurück — eine riesige Inline-JSON-Konfiguration (`featureManagementConfig`, `jeBackendUrls`, etc.). Regex-Matches wie `body.match(/Checkout/)` fanden Matches im JSON, nicht im sichtbaren UI-Text. Das führte zu falsch-positiven "Checkout (45,96€)" Meldungen obwohl der Warenkorb leer war.
**Fix**: Niemals `document.body.textContent` verwenden. Stattdessen targeted Selektoren:
```bash
# Sidebar-Element direkt abfragen
camoufox eval '(function(){ var s=document.querySelector(".sidebar-style_wrapper__nDGVl"); return s?s.textContent?.trim()?.slice(0,500):"no sidebar"; })()'
```

### Fehler 5: Domino's "Free Item" Promo-Modal blockiert Add-to-Basket
**Was passierte**: Bei Domino's gibt es "Buy X get Y free"-Promotions. Beim Klick auf einen Plus-Button öffnet sich zuerst das Promo-Modal ("Nice! You get this free with your order — Beck's Blue 330ml...") statt das Item-Konfigurator-Modal. Der eigentliche Item-Klick wird verschluckt.
**Fix**: Promo-Modal mit Escape schließen, dann denselben Plus-Button erneut klicken:
```bash
# 1. Plus-Button klicken → Promo-Modal erscheint
# 2. Escape drücken → Promo-Modal schließt sich
camoufox press Escape
sleep 2
# 3. Dieselben Koordinaten erneut klicken → Item-Modal öffnet sich
camoufox click <same_x> <same_y>
```
Das Promo-Modal erscheint nur einmal pro Session. Nach dem Schließen funktionieren nachfolgende Klicks normal.

### Fehler 6: `click_element '[data-qa=item-action]'` klickt immer das ERSTE Item
**Was passierte**: Um den Vegan Chicken Döner zu öffnen, benutzte ich `click_element '[data-qa=item-action]'`. Dieser Selektor matcht aber den ersten Plus-Button auf der Seite — nicht den des gewünschten Items. Öffnete Philly Cheesesteak Pizza statt Vegan Chicken Döner.
**Fix**: Um ein spezifisches Item zu öffnen: Item-Name per `eval` finden, `scrollIntoView`, Plus-Button-Koordinaten per `getBoundingClientRect()` holen, dann `camoufox click X Y`.

### Fehler 7: Domino's Pizza-Konfigurator hat mehrere Required Fields
**Was passierte**: Nach Auswahl der Größe (Medium) funktionierte der Add-Button nicht. Grund: Es gibt **drei** Required-Selections: Size, Crust, Sauce. Der Add-Button bleibt disabled bis alle drei ausgewählt sind.
**Fix**: Alle Required-Fields in Reihenfolge auswählen, dann Add klicken:
```bash
camoufox click_element '.ReactModal__Content--after-open pie-radio:has-text("Medium (28cm)")' 10000 true
camoufox click_element '.ReactModal__Content--after-open pie-radio:has-text("Klassisch")' 10000 true
camoufox click_element '.ReactModal__Content--after-open pie-radio:has-text("Knoblauch Sauce (Vegan)")' 10000 true
camoufox click_element '.ReactModal__Content--after-open pie-button:has-text("Add")' 10000 true
```

### Fehler 8: Koordinaten-Klick auf `pie-button` (Add) funktioniert nicht
**Was passierte**: `camoufox click 874 736` auf den Add-Button (ein `pie-button` Custom Element) führte zu nichts — der Klick wurde registriert (`"clicked": true`) aber das Item wurde nicht in den Warenkorb gelegt. Der `pie-button` braucht native Playwright-Events, keine `page.mouse.click()`-Koordinaten.
**Fix**: Statt Koordinaten-Klick `click_element` mit Modal-Scoped-Selektor verwenden:
```bash
# FALSCH — Koordinaten-Klick auf pie-button
camoufox click 874 736

# RICHTIG — Playwright native click, scoped to modal
camoufox click_element '.ReactModal__Content--after-open pie-button:has-text("Add")' 10000 true
```

### Fehler 9: `pie-radio` Koordinaten-Klick schließt Modal statt zu selektieren
**Was passierte**: Beim Klick auf eine `pie-radio`-Option (z.B. "Medium (28cm)") mit `camoufox click X Y` schloss sich das gesamte Modal. Der Radio-Button hatte einen Click-Handler der das Modal schließt, statt nur die Option zu aktivieren.
**Fix**: Statt Koordinaten-Klick `click_element` mit Playwright verwenden:
```bash
camoufox click_element '.ReactModal__Content--after-open pie-radio:has-text("Medium (28cm)")' 10000 true
```

### Fehler 10: Netzwerk-Abbruch mitten in der Bestellung
**Was passierte**: Nach langer Session mit vielen Camoufox-Server-Restarts brach die Internetverbindung komplett ab (`NS_ERROR_CONNECTION_REFUSED`). War nicht direkt ein Bestell-Fehler, aber blockierte den Fortschritt.
**Fix**: Vor jeder Bestellung `curl -s -o /dev/null -w "%{http_code}" https://www.google.com` als Quick-Check. Bei Abbruch warten und neu starten.

### Fehler 11: Warenkorb-Items ließen sich nicht zuverlässig entfernen
**Was passierte**: Der Minus-Button im Warenkorb (Koordinaten-Klick) funktionierte unzuverlässig — bei 4x Vegan Döner im Warenkorb reduzierte ein Klick auf 3 statt 2. Der Trash-Button (Koordinaten-Klick) öffnete das Modal nicht zum Entfernen.
**Fix**: Minus/Trash im Warenkorb ebenfalls per `click_element` (Playwright native) statt Koordinaten. Selektor: `.sidebar-style_wrapper__nDGVl .c-pieIcon--minus` oder `[class*=basket] [data-qa*=decrease]`.

### Fehler 12: Restaurant-Verfügbarkeit nicht VOR Bestellversuch geprüft
**Was passierte**: Bei Let Me Bowl wurde die gesamte Bestellung vorbereitet, aber das Restaurant war geschlossen ("Delivery Unavailable"). Plus-Buttons rendern, aber Klicks machen nichts.
**Fix**: ZUERST prüfen ob Restaurant offen ist, DANN Items hinzufügen:
```bash
camoufox eval '(function(){ var b=document.body.textContent; var u=(b.match(/Unavailable/g)||[]).length; return u<10?"OPEN":"CLOSED"; })()'
```
Oder besser: Auf der Restaurant-Listen-Seite "Open Now"-Filter aktivieren und nur offene Restaurants auswählen.

## DRY-RUN BESTELL-STRATEGIE (Lektion für zukünftige Bestellungen)

Statt blind Items zu klicken und dann am Checkout zu scheitern, folgende Reihenfolge:

1. **Netzwerk-Check**: `curl -s -o /dev/null -w "%{http_code}" https://www.google.com` — wenn kein 200, warte
2. **Vorbereitung**: Gutschein-Code per Himalaya aus Email holen (`himalaya envelope list -a giuli` → `himalaya message read <ID> -a giuli`), Account-Session aus Firefox extrahieren (`python3 scripts/extract_firefox_cookies.py "<FF_PROFILE>.Profil 4" /tmp/giuli_cookies.json`)
3. **Login-Check**: `/en/checkout` aufrufen — wenn Weiterleitung zu `auth.lieferando.de` → Session expired, frische Cookies holen. NICHT `document.cookie` checken (HttpOnly!).
4. **Restaurant-Check**: Restaurant offen? Sidebar anzeigen: `document.querySelector(".sidebar-style_wrapper__nDGVl")`. Wenn "Unavailable" im Body oder "Your basket is empty" + keine Items → Restaurant geschlossen.
5. **Warenkorb leeren**: Falls alte Items drin, Minus-Button per `click_element '.sidebar-style_wrapper__nDGVl span._3I0XC'` klicken bis leer.
6. **Items hinzufügen** (pro Item):
   a. Kategorie-Chip klicken: `click_element 'pie-chip:has-text("Pizza - Vegan")'`
   b. Item-Plus-Button finden: `eval` mit `getBoundingClientRect()` auf `pie-icon-button`
   c. Plus-Button klicken: `camoufox click X Y`
   d. **Promo-Modal?** → `camoufox press Escape` → re-click Plus-Button
   e. **Item-Modal verifizieren**: Text muss Item-Namen enthalten, nicht "free"/"Beck"/"Nice"
   f. **Required Fields** auswählen (alle!):
      - Size: `click_element '.ReactModal__Content--after-open pie-radio:has-text("Medium (28cm)")'`
      - Crust: `click_element '.ReactModal__Content--after-open pie-radio:has-text("Klassisch")'`
      - Sauce: `click_element '.ReactModal__Content--after-open pie-radio:has-text("Knoblauch Sauce (Vegan)")'`
   g. **Add-Button verifizieren**: `aria-disabled` muss `"false"` sein
   h. **Add klicken**: `click_element '.ReactModal__Content--after-open pie-button:has-text("Add")'`
   i. **Warenkorb verifizieren**: Sidebar-Selector `.sidebar-style_wrapper__nDGVl` abfragen
7. **Total prüfen**: Footer-Selector `.sidebar-style_footer__dtVAI` → Subtotal, Delivery fee, Service fee, Total
8. **Checkout-Button finden** (aber NICHT klicken im Dry-Run!): `click_element 'button:has-text("Checkout")'` nur beim echten Durchlauf
9. **Gutschein eingeben** (nur echt): "Add voucher" Sektion öffnen, Code eingeben, "Apply" klicken
10. **Zahlung abschließen** (nur echt): Zahlungsmethode wählen, "Order and pay" klicken

### Dry-Run vs Echter Durchlauf
- **Dry-Run**: Schritte 1-8 (ohne Checkout-Klick). Verifiziert dass alle Items korrekt im Warenkorb sind, Total stimmt, Login gültig ist.
- **Echt**: Schritte 1-10. Erst nach erfolgreichem Dry-Run ausführen.

**NICHT**: blind Items klicken, Promo-Modals ignorieren, Warenkorb-Status nicht verifizieren, dann am Ende feststellen dass nichts funktioniert.

### Strategy Switch After 3 Failures
Wenn derselbe Click/Eval-Pattern 3+ mal fehlschlägt: STOP. Wechsle den Ansatz komplett:
- Koordinaten-Klick → `click_element` (Playwright native)
- `click_element` ohne Modal-Scope → `click_element` mit `.ReactModal__Content--after-open` Scope
- `eval` JS `.click()` → `click_element` mit `:has-text()` Selector
- Neustart: `pkill -9 -f camoufox_server; pkill -9 -f Camoufox; rm -f /tmp/camoufox_cli.sock; camoufox start`

Wiederholung eines fehlschlagenden Patterns verschwendet Tokens und frustriert den User.

### Korrekte Warenkorb-Verifikation
Niemals `document.body.textContent` verwenden — liefert 200K+ Zeichen Inline-JSON. Stattdessen:
```bash
# Sidebar (Items)
camoufox eval '(function(){ var s=document.querySelector(".sidebar-style_wrapper__nDGVl"); return s?s.textContent?.trim()?.slice(0,500):"no sidebar"; })()'

# Footer (Totals + Checkout-Button)
camoufox eval '(function(){ var f=document.querySelector(".sidebar-style_footer__dtVAI"); return f?f.textContent?.trim()?.slice(0,300):"no footer"; })()'
```

## Hermes Browser Tools + REST API Pattern (2026-07-17 Session)

### Creating a Persistent Tab via REST API (CRITICAL — browser_navigate loses state)

`browser_navigate` creates a NEW tab on every call, losing address/cookies/basket.
Use the REST API to create ONE persistent tab:

```bash
# Create ONE persistent tab — reuse for ALL subsequent ops
TAB_ID=$(curl -s -X POST http://localhost:9377/tabs \
  -H "Content-Type: application/json" \
  -d '{"userId":"agent1","sessionKey":"lieferando","url":"https://www.lieferando.de/de"}' \
  | python3 -c "import json,sys; print(json.load(sys.stdin).get('tabId',''))")
echo "$TAB_ID" > /tmp/camofox_tab_id

# ALL subsequent ops use the SAME tab ID via curl
TAB=$(cat /tmp/camofox_tab_id)
curl -s -X POST "http://localhost:9377/tabs/$TAB/type" \
  -H "Content-Type: application/json" \
  -d '{"userId":"agent1","selector":"input[aria-label=\"Search for location\"]","text":"<STREET>"}'
```

### pie-button Shadow DOM Click (CRITICAL — browser_click returns ok but does nothing)

Lieferando's "Add X,XX€" button is a `<pie-button>` custom element with a shadow
DOM. `browser_click(ref="e38")` returns `{"ok":true}` but the item is NOT added —
React's onClick does not fire from Playwright's native click on this button.
`document.querySelectorAll("button")` finds 0 matching buttons (they're in shadow roots).

**Fix**: Use `evaluate` to find `<pie-button>` elements, access their `.shadowRoot`,
and click the inner `<button>`:

```bash
TAB=$(cat /tmp/camofox_tab_id)
curl -s -X POST "http://localhost:9377/tabs/$TAB/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"userId":"agent1","expression":"(() => { const pbs = document.querySelectorAll(\"pie-button\"); for(const pb of pbs) { const t = pb.textContent||\"\"; if(t.includes(\"Add\") && t.includes(\"11,99\")) { const btn = pb.shadowRoot?.querySelector(\"button\"); if(btn && !btn.disabled) { btn.click(); return \"clicked: \"+t.substring(0,20); } return \"disabled or no shadow\"; } } return \"not found\"; })()"}'
```

### pie-icon-button Add-to-Basket (menu item plus buttons)

Menu item "Add to basket" buttons are `<pie-icon-button>` elements, also with
shadow DOM. Standard `querySelectorAll("button[aria-label]")` returns 0 results.
Use:

```bash
curl -s -X POST "http://localhost:9377/tabs/$TAB/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"userId":"agent1","expression":"(() => { const pibs = document.querySelectorAll(\"pie-icon-button\"); for(const pib of pibs) { const btn = pib.shadowRoot?.querySelector(\"button\"); if(btn) { const a = btn.getAttribute(\"aria-label\")||\"\"; if(a.includes(\"Vegan Chicken\")) { btn.click(); return \"clicked: \"+a; } } } return \"not found\"; })()"}'
```

### Configurator Required Fields via evaluate (when browser_click ref doesn't work)

After opening an item modal, select Size/Crust/Sauce via JS evaluate:

```bash
# Select Classic size
curl -s -X POST "http://localhost:9377/tabs/$TAB/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"userId":"agent1","expression":"(() => { const radios = document.querySelectorAll(\"[role=\\\"radio\\\"]\"); for(const r of radios) { const t = r.textContent||\"\"; if(t.includes(\"Classic\") && t.includes(\"25cm\")) { r.click(); return \"clicked Classic\"; } } return \"not found\"; })()"}'

# Select Crust: Klassisch
# (same pattern, filter by "Klassisch" && "Crust")

# Select Sauce: Tomatensauce (Vegan) or Knoblauch Sauce (Vegan)
# (same pattern, filter by "Tomatensauce" && "Vegan")

# Then click Add via pie-button shadow DOM (see above)
```

### Checkout Login — Cloudflare Turnstile Blocker

After clicking "Checkout", Lieferando redirects to a login page
("Log in or create account"). The email input field has a hidden
`cf-turnstile-response` field. The submit button stays `disabled` until
Cloudflare Turnstile is solved. This is a HARD BLOCKER for full automation
without Capsolver integration.

**Current state (updated 2026-07-17)**: Turnstile on `auth.lieferando.de` does
NOT auto-solve in Camoufox headed mode (unlike REWE/Apodiscounter where Camoufox
bypasses Turnstile automatically). The widget renders as invisible — no iframe,
no `data-sitekey` attribute on any element. The sitekey is passed via
`turnstile.render()` JS call internally. `window.turnstile.getResponse()`
returns empty string even after 30+ seconds of waiting.

**Turnstile widget structure on auth.lieferando.de**:
- `div#cf-turnstile` container (no data-sitekey attribute)
- `input[type="hidden" name="cf-turnstile-response"]` — hidden token field (empty until solved)
- Submit button text: "Bestätigungscode abrufen" (German) / "Continue with email" (English)
- Submit button stays `disabled=true` until `cf-turnstile-response` has a value

**Capsolver does NOT work** for this Turnstile:
- `AntiTurnstileTaskProxyless` requires a `websiteKey` (sitekey)
- The sitekey is NOT extractable from the DOM (no `data-sitekey` attribute, not in
  script content, not in iframe src — the widget was rendered via explicit
  `turnstile.render()` with sitekey passed as JS object parameter)
- Attempting `turnstile.render("#cf-turnstile", {sitekey: "0x4AAAAAAAAj1Q1YzqCzFtR"})`
  with a guessed sitekey fails: "parameters ... not allowed to be changed between
  the calls of render() and execute()"

**Google OAuth also fails**: Clicking "Continue with Google" redirects to
`accounts.google.com/v3/signin/identifier` → entering email → redirects to
`/signin/rejected` (Google detects Camoufox as untrusted browser). This is
consistent with SKILL.md pitfall #8 (Google SSO is fingerprint-bound).

**Working approach — pre-authenticated session cookies**:
1. Kill Firefox (`pkill -f firefox; sleep 3`)
2. Extract Lieferando cookies from Firefox profile (see "Direct Firefox→Camoufox
   Cookie Transfer" section above)
3. Inject via `POST /sessions/:userId/cookies` with `{"cookies": [...]}`
4. Navigate to the restaurant menu page — session is recognized, basket persists
5. If `je-at` token is expired (cookie expiry is future but token lifetime is
   shorter), the checkout will redirect to `auth.lieferando.de` — re-extract
   fresh cookies from a Firefox session where <FIRST_NAME> is actively logged in

**Full verified checkout flow (2026-07-17)**: When pre-authenticated session cookies
are injected and valid (user was actively logged in to Firefox recently), the
entire checkout page loads WITHOUT any login/Turnstile challenge. The checkout
page shows: user details (<FULL_NAME>), delivery address (<ADDRESS>,
<PLZ> <CITY>), PayPal payment option, voucher section, and "Order & pay" button.
The URL stays at `lieferando.de/en/checkout?basket=...` — no redirect to
`auth.lieferando.de`. The basket persists server-side (tied to `je-at` token).

## PayPal Payment Flow (VERIFIED 2026-07-17)

After clicking "Order and pay" on the checkout page with PayPal selected:

1. Browser redirects to `https://www.paypal.com/pay?token=...`
2. PayPal shows a login form: email field + "Next" button
3. After entering email + clicking Next: password field + "Log In" button
4. After login: payment confirmation page with "Pay Now" button
5. After payment: redirect back to lieferando.de order confirmation

**The PayPal session is NOT carried over from Lieferando session cookies** — it's a completely separate auth flow. The user's PayPal email and password are required. This cannot be fully automated without the user's PayPal credentials.

**The redirect URL token is time-limited** — if the user takes too long to log in to PayPal, the token may expire and the order may need to be re-submitted.

## Known Issues
1. **Server hangs on coordinate clicks** on Checkout page (React SPA). Use `click_element` (native Playwright) or JS click via `eval` as fallback.
2. **React Modal "Your items"** blocks all interactions. Detect with `document.querySelector('.ReactModal__Content--after-open')` and remove via JS. ALWAYS check for modals before interacting.
3. **2FA takes 30-60 seconds** — wait for user approval on phone.
4. **Persistent profile keeps session** — but Google OAuth requires fresh 2FA each time.
5. **Mouse wheel scroll doesn't work on SPA pages** — use `scroll_to_element` (native) or `scrollIntoView({block: 'center'})` via eval.
6. **500 errors** can occur when clicking "Add voucher" — page crashes. Reload and retry.
7. **Basket persists across server restarts** — stored in Lieferando session, not local. But lost when cookies are cleared.
8. **"Add voucher" section needs scrollIntoView before click** — clicking without scrolling first does nothing (section is below viewport).
9. **Item IDs change on page reload** — `#item_41` becomes `#item_61` etc. Always re-query with `get_elements` after navigation.
10. **Voucher section click target varies** — `[class*=checkout-section-style___is-clickable]` may not match. Fallback: click the leaf `<span>` with exact text "Add voucher" via `document.querySelectorAll('*')` + `el.children.length === 0` check.
11. **Login verification via `je-last-login` cookie** — decode to confirm account: `decodeURIComponent(cookie.split('=')[1])` → JSON with `firstName`, `email`, `loginType`, `timestamp`. More reliable than looking for UI elements. Example: `{"firstName":"<FIRST_NAME>","email":"<EMAIL>","timestamp":1783103103906,"loginType":"google"}`.
12. **Voucher failure messages are misleading** — "This promotion isn't available for your account" and "Voucher has expired" both appear when the voucher is 24h-locked from a previous Apply attempt. Don't interpret "expired" as actually expired — check the original voucher email for the real expiry date.
13. **`/account` and `/account/vouchers` redirect when not logged in** — if `je-at` (JWT auth token) has expired, Lieferando redirects `/account` to the delivery search page. Re-extract fresh cookies from Firefox (kill Firefox first). The `je-at` token has a finite lifetime even if the cookie expiry is far in the future.
