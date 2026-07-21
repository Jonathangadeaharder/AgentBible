# Credential Rotation — Token & API Key Rotation via Browser Automation

Rotate API tokens/keys for platforms that gate token management behind password-confirmed
web UIs. Covers the "no API bypass" pattern, password re-entry flow, and shell config updates.

## When This Applies

- Platform has NO public API for token/key creation/deletion (HuggingFace, Google AI Studio, etc.)
- Token management page requires password re-confirmation (HuggingFace) OR
  is accessible via session cookies alone (Google AI Studio)
- You have an existing valid token/key + the account credentials (or pre-injected cookies)
- Goal: delete old token/key, create new one, update local config files

## HuggingFace Token Rotation

### Prerequisites

- Existing `HF_TOKEN` in `~/.zshenv` (or `~/.hermes/.env`)
- Account password for the HuggingFace account
- Camoufox server running with cookies pre-injected for a userId (e.g., `rotator`)

### Step 1: Verify Old Token

```bash
OLD_TOKEN="hf_..."
curl -s -H "Authorization: Bearer $OLD_TOKEN" "https://huggingface.co/api/whoami-v2"
# Returns: {"type":"user","id":"...","name":"...","auth":{"type":"access_token","accessToken":{"displayName":"...","role":"write",...}}}
```

If this returns user info, the token is valid. Note the `displayName` — you'll need it
to identify the old token on the settings page.

### Step 2: Navigate to Tokens Page

```bash
# Create tab with pre-injected cookies
curl -s -X POST "http://localhost:9377/tabs" \
  -H "Content-Type: application/json" \
  -d '{"userId":"rotator","sessionKey":"rotator","url":"https://huggingface.co/settings/tokens"}'

# Response includes tabId — save it. URL will redirect to /security-checkup?cookieId=<id>
```

### Step 3: Handle Password Confirmation

The page redirects to `/security-checkup?cookieId=<id>` with:
- Heading: "Confirm your identity"
- Password textbox (aria ref, e.g., `@e30`)
- Confirm button (aria ref, e.g., `@e31`)

```bash
# Get snapshot to find refs
curl -s "http://localhost:9377/tabs/<tabId>/snapshot?userId=rotator"

# Type password into the password field (use aria ref from snapshot)
# Via Hermes browser tools:
browser_type "@e30" "<ACCOUNT_PASSWORD>"
browser_click "@e31"  # Confirm button

# Or via REST API directly:
curl -s -X POST "http://localhost:9377/tabs/<tabId>/type" \
  -H "Content-Type: application/json" \
  -d '{"userId":"rotator","ref":"e30","text":"<ACCOUNT_PASSWORD>"}'

curl -s -X POST "http://localhost:9377/tabs/<tabId>/click" \
  -H "Content-Type: application/json" \
  -d '{"userId":"rotator","ref":"e31"}'
```

After confirmation, the browser navigates to `/settings/tokens`.

### Step 4: Delete Old Token

On the tokens page:
1. `browser_snapshot` — find the old token by its `displayName`
2. Find the "Delete" or "Manage" button near that token
3. Click it, confirm deletion if a modal appears

### Step 5: Create New Token

1. Find "New token" or "Create token" button — click it
2. Type a name for the token (e.g., `HFTOKEN`)
3. Select permission level (e.g., "Write")
4. Click "Create" / "Generate"
5. The new token (`hf_...`) is displayed — **copy it immediately** (it won't be shown again)

```bash
# Extract token from page via JS
curl -s -X POST "http://localhost:9377/tabs/<tabId>/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"userId":"rotator","expression":"document.body.innerText.match(/hf_[a-zA-Z0-9]+/)?.[0] || \"not found\""}'
```

### Step 6: Update Shell Config

```bash
# Update ~/.zshenv replacing the HF_TOKEN value
python3 -c "
import re
p = '/Users/<USER>/.zshenv'
c = open(p).read()
c = re.sub(r'HF_TOKEN=.*', 'HF_TOKEN=\"<NEW_TOKEN>\"', c)
open(p, 'w').write(c)
print('done')
"

# Or use the patch tool for targeted replacement
# patch(path='~/.zshenv', old_string='HF_TOKEN=\"hf_OLD...\"', new_string='HF_TOKEN=\"hf_NEW...\"')
```

### Step 7: Verify New Token

```bash
NEW_TOKEN="hf_..."
curl -s -H "Authorization: Bearer $NEW_TOKEN" "https://huggingface.co/api/whoami-v2"
```

## Platform Reference

### HuggingFace

- **Token verify**: `GET /api/whoami-v2` with `Authorization: Bearer <token>`
- **Token management API**: NONE. `POST /api/tokens` → 404, `POST /settings/tokens/create` → 401
- **huggingface_hub Python lib**: No token management methods (only repo/model/dataset ops)
- **Password confirmation**: Required for `/settings/tokens`. Redirects to `/security-checkup?cookieId=<id>`
- **Form fields**: `csrf` (hidden), `next` (hidden), `authType` (hidden, =`password`), `password` (text)
- **Account email**: `<EMAIL>`

### Google AI Studio

- **URL**: `https://aistudio.google.com/apikey` (redirects to `/api-keys`)
- **API key management API**: Not available via public REST. Must use the web UI.
- **Password confirmation**: NOT required. Session cookies alone grant access.
- **Cloud Project requirement**: At least one imported Cloud Project is REQUIRED to create
  an API key. Dialog shows "No Cloud Projects Available" if none exist.
- **Cookie notification bar**: `glue-cookie-notification-bar` intercepts ALL clicks — hide via JS.
- **Angular Material buttons**: `mat-mdc-*` buttons may not respond to Playwright native click.
  Fall back to `element.click()` via `/evaluate`.
- **API key format**: Typically `AIza...` (35 chars after prefix). Alternative format `AQ.Ab8R...`
  also seen. Keys are masked on the page as `AIzaSy...XXXX`.
- **Google SSO**: Cookie injection cross-browser does NOT work (fingerprint-bound). Must login
  directly in Camoufox with password + 2FA.

## Google AI Studio (Gemini API Key Rotation)

Google AI Studio at `https://aistudio.google.com/apikey` (redirects to `/api-keys`)
manages Gemini API keys. Unlike HuggingFace, no password re-confirmation is needed —
the session cookies alone grant access to the API key management page.

### Prerequisites

- Camoufox server running with Google session cookies pre-injected for a userId
- The Google account must have at least one **imported Cloud Project** in AI Studio

### Key Facts

- **No password confirmation**: Cookie injection alone is sufficient (unlike HuggingFace).
- **API key table may be empty**: Keys are only listed if associated with an imported project.
  If the table is empty, keys may still exist but aren't shown.
- **API key creation requires a Cloud Project**: The "Create API key" dialog shows
  "No Cloud Projects Available" if no projects are imported. You cannot create a key
  without selecting a project. **This is a hard blocker** — the user must import a
  Cloud Project into AI Studio first (or create one via Google Cloud Console).
- **API keys on the page are masked**: Displayed as `AIzaSy...XXXX` in the page config
  (inside Angular initial data blocks), not in the table rows.

### Cookie Notification Bar (Google-specific)

Google sites show a `glue-cookie-notification-bar` that intercepts ALL button clicks.
Playwright native click returns `{"error":"Element not visible (no bounding box)"}` when
trying to click it. Hide it before interacting:

```bash
curl -s -X POST "http://localhost:9377/tabs/$TAB_ID/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"userId":"rotator","expression":"(() => { const bar = document.querySelector(\".glue-cookie-notification-bar\"); if (bar) { bar.style.display = \"none\"; return \"hidden\"; } return \"not found\"; })()"}'
```

### Angular Material Buttons Not Responding to Playwright Click

Google AI Studio uses Angular Material (`mat-mdc-*`) components. The "Crear clave de API"
(Create API key) button (`button.ms-button-primary`) did NOT respond to:
- Aria ref click (`POST /tabs/:tabId/click` with `{"ref":"e20"}`)
- CSS selector click (`POST /tabs/:tabId/click` with `{"selector":"button:has-text(\"Crear\")"}`)

But DID respond to direct JS `.click()`:

```bash
curl -s -X POST "http://localhost:9377/tabs/$TAB_ID/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"userId":"rotator","expression":"(() => { const btns = document.querySelectorAll(\"button.ms-button-primary\"); for (const b of btns) { if (b.textContent.includes(\"Crear clave\")) { b.click(); return \"clicked\"; } } return \"not found\"; })()"}'
```

**Pattern**: When Angular Material buttons don't respond to Playwright native click
(via ref or selector), fall back to direct `element.click()` via `/evaluate`. The
`click_element` Playwright click pipeline handles actionability checks that may fail
on `mat-mdc` buttons with complex overlays; the JS `.click()` bypasses these checks.

### Google API Key Format

Google AI Studio API keys typically start with `AIza` (standard Google API key format).
However, keys created via certain flows may use a different format (e.g., `AQ.Ab8R...`
seen in existing configs). When extracting keys from the page, search for both patterns:

```bash
# Search for AIza-prefixed keys (standard)
"document.body.innerText.match(/AIza[0-9A-Za-z_-]{35}/g)"

# Search for AQ.-prefixed keys (alternative format)
"document.body.innerText.match(/AQ\\.[A-Za-z0-9_-]+/g)"
```

### Google SSO Cookie Injection Cross-Browser Does NOT Work

Google binds session cookies to browser fingerprint. Cookie injection from Firefox →
Camoufox does NOT work for Google. Must do password + 2FA login flow directly inside
Camoufox. See pitfall #8 in SKILL.md.

## General Pattern: Password-Confirmed Settings Pages

Many platforms gate sensitive operations (token management, SSH keys, billing changes, account
deletion) behind a "re-enter your password" interstitial. The pattern is always:

1. Navigate to the protected settings page
2. Get redirected to a password confirmation page
3. Type the account password into the form
4. Submit the form
5. Land on the protected settings page
6. Perform the desired action

**No API bypass exists for these pages** — the password confirmation is a server-side gate,
not a client-side check. Cookie injection alone is insufficient because the server requires
the password POST to set a "verified" session flag before allowing access to the protected page.

### Key Takeaway

Before attempting browser automation for credential rotation:
1. Check if the platform has a public API for token management (most don't)
2. If not, you WILL need the account password — find it in memory/keychain/env, or ask the user
3. Do NOT waste time trying to bypass the password confirmation via API calls or JS injection
