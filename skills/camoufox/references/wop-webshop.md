# World of Pizza (WOP) Webshop Automation

Site: https://webshop.world-of-pizza.de/
Platform: SimplyDelivery (get-sides.de)
Account: <EMAIL>

## Login Flow

1. `goto "https://webshop.world-of-pizza.de/"` — lands on store list page
2. Cookie banner: `.cmpbox` element. Remove via JS (more reliable than clicking accept):
   `camoufox eval "() => { document.querySelector('.cmpbox').remove(); document.body.style.overflow=''; return 'removed'; }"`
3. Login trigger: click `div.tab-login` (class `tab-login btn`, text "Login").
   NOTE: `div.login` does NOT match — the class is `tab-login`, not `login`.
   3. Login trigger: click `div.login` or `.tab-login` (text "MEIN WOP" / "LOGIN" /
      "Login"). Opens login form inline. On the store list page the element is
      `.tab.tab-login.btn` — use `click_element '.tab-login'`.
      - Direct URL `https://webshop.world-of-pizza.de/customer/login` does NOT show form — must click the login tab from a page.
4. Fill `#loginUsername` (email) + `#loginPassword` (password) via `fill_element`
5. Click `input.loginButton` — button is `disabled` until both fields are filled.
   After fill, the click may timeout with "element is not enabled" but login STILL
   succeeds — the page navigates to `/customerdata/overview?checkAddress=1`.
   Check `camoufox url` to confirm login rather than trusting click result.
6. Verify: body contains account name (e.g. "Jonathan") + "LOGOUT"

## Account Pages

| Page | URL |
|------|-----|
| Overview | `/customerdata/overview` |
| VIP Gutscheine | `/customerdata/listVipVoucher` |
| Sammel Dich Satt (loyalty) | `/customerdata/loyaltySystem` |
| Bestellungen | `/customerdata/listOrder` |
| Persönliche Daten | `/customerdata/selectCustomer` |
| MyCode | `/customerdata/loginCode` |

## Store Selection

Teltow = store_id 36. Direct URL:
```
https://webshop.world-of-pizza.de/storedata/selectStore?store_id=36&deliveryarea_id=0
```
After selecting, redirects to `/storedata/selectDeliveryTime` — choose pickup time or
confirm. Store may be closed (opens 10:45). Abholzeit (pickup time) must be confirmed
even when closed — select "ÜBERNEHMEN" button.

Other stores: find via `ge 'a.menuitem'` on the overview page after clicking the
"Wähle Deinen Store aus..." dropdown.

## Click Issues on SimplyDelivery SPA

`click_element` with `force=true` times out on some WOP elements (dropdowns, nav links).
These are Bootstrap dropdowns that don't respond to Playwright clicks.

**Fallback**: `eval "() => { document.querySelector('selector').click(); return 'clicked'; }"`

For dropdowns specifically:
1. Click the dropdown toggle via `eval`
2. Wait 1-2s
3. `ge 'a.menuitem'` to find menu items
4. Click menu item via `eval` or `goto` the href directly

## Voucher Code System (IMPORTANT)

WOP has THREE separate voucher/credit systems — don't confuse them:

1. **VIP Gutscheine** (`/customerdata/listVipVoucher`): Activated vouchers stored in account.
   Table shows code + expiry. Empty table = no active vouchers.

2. **Sammel Dich Satt** (`/customerdata/loyaltySystem`): Loyalty points. 10 points per €
   spent. 100 points = 1€. Separate from vouchers.

3. **Checkout voucher codes** (from emails): Codes like `2ydn12ds` sent by
   `kundenservice@world-of-pizza.de`. These are NOT stored in the account — they must be
   entered manually at checkout in the cart/warenkorb. The email says "sofort einlösbar"
   (immediately redeemable). Codes are account-specific (tied to the email that received
   them).

**Key distinction**: When WOP support says "Gutscheincode ausgestellt" (voucher code
issued), they mean a checkout code sent via email — NOT a credit to the customer
account. When they say "den Betrag Ihrem Kundenkonto gutgeschrieben" (credited to your
account), that SHOULD appear as a VIP Gutschein or loyalty points — but may not actually
be processed correctly. Check both pages and test the code at checkout.

### Applying a Checkout Voucher Code — Step-by-Step

The voucher input is NOT on the checkout page. It lives in the sidebar of the **menu
page** (`/c/221/aktion` or similar category pages). Procedure:

1. **Be on a menu/category page** (e.g. `goto "https://webshop.world-of-pizza.de/c/221/aktion"`)
2. **Locate the input**: `ge '#voucher-code'` — placeholder "Gutschein-Code"
3. **Fill the code**: `fill_element '#voucher-code' '<code>'` (or `fe`)
4. **Trigger the button reveal**: After filling, a hidden `»` button appears
   (`.voucher-cash.voucher-btn` changes from `display:none` → `display:block`). If it
   stays hidden after `fill_element`, dispatch an `input` event on the field.
5. **Click the einlösen button**: `click_element` on `.voucher-cash .btn` TIMES OUT
   because a `.modal-backdrop.fade.in` intercepts pointer events (Bootstrap modal
   overlay). Use JS click instead:
   ```bash
   camoufox eval "() => { const btn = document.querySelector('.voucher-cash .btn'); if (btn) { btn.click(); return 'clicked'; } return 'no btn'; }"
   ```
6. **Success modal**: A Bootstrap `.modal.show` appears with text "Dein Gutschein wurde
   eingelöst." The same modal-backdrop intercept blocks `click_element` on the "Ok"
   button. Dismiss with JS:
   ```bash
   camoufox eval "() => { const btn = document.querySelector('.modal.show .btn, .in.modal .btn'); if (btn) { btn.click(); return 'clicked ok'; } return 'no btn'; }"
   ```
7. **Verify**: `goto "/checkout"` and read body — look for "Gutschrift X,XX Euro" and
   "- X,XX €" line in the basket summary. Confirmed working code `2ydn12ds` → 3,00€
   Gutschrift.

### Removing a Voucher

The basket sidebar has a `span.basket-delete-voucher` element (trash icon). Click via
JS: `eval "() => { document.querySelector('.basket-delete-voucher').click(); return 'deleted'; }"`
A confirmation modal may appear (same `.modal.show` pattern — dismiss with JS click on
the modal's `.btn`).

### Voucher Pitfalls

- **Negative total blocks checkout**: If the discount (3,00€) exceeds the cart total
  (e.g. 2,99€ Kirschsticks), the checkout shows "Der Gesamtpreis darf nicht negativ
  sein" and blocks ordering. Always add an item > discount value to test a voucher end-
  to-end.
- **`click_element` fails on modal-backed buttons**: The Bootstrap `.modal-backdrop`
  overlay intercepts Playwright clicks. `click_element` reports "modal-backdrop
  intercepts pointer events" and times out. Use `eval` JS `.click()` as fallback for
  any WOP element inside or behind a modal.
- **Voucher codes are account-specific**: A code sent to one email will be rejected on
  another account. Must be logged into the receiving account.
- **Server crash clears basket**: If the Camoufox server crashes mid-session (e.g.
  after a modal JS click), restarting the server does NOT restore the basket — the
  SimplyDelivery server-side session may expire. Re-login and re-add items.

## Voucher Code Testing Workflow (Tested 2026-07-04)

To test a checkout voucher code without completing an order:

### 1. Add a cheap item to basket
Navigate to any product page (e.g. Pizza Margherita `/a/278/5016/pizza/world-pizza-margherita`)
and click `button.button_absenden` ("In den Warenkorb"). After adding, page redirects to
`/upselling?basket_id=0`.

### 2. Go to basket article list (NOT checkout)
```
camoufox goto "https://webshop.world-of-pizza.de/listArticle?"
```
This page has the voucher input field. The checkout page (`/basket/show`) does NOT have it.

### 3. Enter voucher code
- Input field: `#voucher-code` (placeholder "Gutschein-Code")
- `camoufox fill_element '#voucher-code' 'CODE_HERE'`

### 4. Submit voucher
The submit button is `div.voucher-btn` (shows "»"). Two issues:
- `click_element 'div.voucher-btn'` times out — `.modal-backdrop` intercepts pointer events.
- Must remove backdrop first, then click via JS:
  ```
  camoufox eval "() => { document.querySelector('.modal-backdrop')?.remove(); document.body.classList.remove('modal-open'); document.body.style.overflow=''; return 'cleared'; }"
  camoufox eval "() => { document.querySelector('div.voucher-btn').click(); return 'clicked'; }"
  ```

### 5. Read result
Wait 1-2s, then check:
```
camoufox eval "() => { const e = document.querySelector('.voucher-success-title, .voucher-error-title, .is-voucher, .is-paid-voucher, .voucher-text'); return e ? e.tagName + ': ' + e.textContent.trim().slice(0,300) : 'no result'; }"
```
- **Success**: `.is-voucher` → "Dein Gutschein wurde eingelöst."
- **Error**: `.voucher-error-title` → error message (invalid code, expired, wrong account)

### 6. Check discount amount
```
camoufox eval "() => { const items = document.querySelectorAll('.basketList .row-fluid'); return Array.from(items).map(e => e.textContent.trim().slice(0,100)).join('\\n'); }"
```
Look for "Gutschrift X,XX Euro" line with `- X,XX€` in `.voucher-value`.

### 7. Clean up — DO NOT ORDER
- Delete article: `camoufox ge 'a'` → find `btn-del-article` → `eval` click it
- Or: `camoufox eval "() => { document.querySelector('a.btn-del-article')?.click(); return 'deleted'; }"`
- Remove entire basket: `camoufox eval "() => { document.querySelector('a.remove-basket-article')?.click(); return 'removed'; }"`
- Verify empty basket via `camoufox body 500` — no items in sidebar

### Known voucher codes (account: <EMAIL>)
| Code | Status | Discount | Date tested |
|------|--------|----------|-------------|
| `2ydn12ds` | ✅ works | 3,00€ | 2026-07-04 |
| `ecgcqhHd` | untested | — | — |
| `dWG3zyDa` | untested | — | — |

## ÜBERNEHMEN Button (Pickup Time Confirmation)

After selecting a store, page redirects to `/storedata/selectDeliveryTime`. The
"ÜBERNEHMEN" button is `a.accept-preordertime` (class `btn btn-small accept-preordertime`).
- `click_element 'a.accept-preordertime'` may timeout (SPA navigation starts before click
  completes) but the action still succeeds — page navigates to the menu.
- Fallback: `eval "() => { document.querySelector('a.accept-preordertime').click(); return 'clicked'; }"`
- After clicking, the page redirects to the menu/category page (e.g. `/c/221/aktion`).

## Product Page Add-to-Cart

Product pages have a "In den Warenkorb" button with class `button_absenden`:
- Selector: `button.button_absenden`
- After clicking, page redirects to `/upselling?basket_id=0` (upsell page)
- From there, navigate to `/listArticle?` to see the basket sidebar with voucher input

## Basket Sidebar Selectors (listArticle page)

| Element | Selector |
|---------|----------|
| Voucher input | `#voucher-code` |
| Voucher submit (» button) | `div.voucher-btn` |
| Delete single article | `a.btn-del-article` |
| Remove entire basket | `a.remove-basket-article` |
| Basket total | `.basket-total-price` |
| Voucher discount line | `.row-fluid.voucher .voucher-value` |
| Success message | `.is-voucher` ("Dein Gutschein wurde eingelöst.") |
| Error message | `.voucher-error-title` |

## Cookie Banner Removal

`.cmpbox` persists even after "Alle akzeptieren" on some pages. Remove via JS:
```bash
camoufox eval "() => { const m = document.querySelector('.cmpbox'); if (m) m.remove(); const o = document.querySelector('.cmpboxok'); if (o) o.remove(); document.body.style.overflow = ''; return 'removed'; }"
```

Also remove `.cmpboxrecall` (small "Privacy settings" link bottom-left):
```bash
camoufox eval "() => { document.querySelector('.cmpboxrecall')?.remove(); return 'done'; }"
```
