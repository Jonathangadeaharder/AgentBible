# Clerk Modal Automation

Clerk is a popular authentication service used by many SaaS platforms (OpenRouter, Vapi, etc.). Clerk renders authentication modals as custom elements that may not appear in accessibility snapshots.

## Key Characteristics

- Clerk modals use custom elements (`cl-*` prefix) and may use shadow DOM
- Standard `browser_snapshot` may not see Clerk modal content
- Must use `evaluate` with JavaScript to interact with Clerk modals
- Clerk provides a frontend API for session management (revocation, listing)

## Finding Clerk Modals

Clerk modals typically have the class `.cl-rootBox` or are nested under a container with `data-clerk-component` attribute.

```javascript
// Check if Clerk modal exists
document.querySelector('.cl-rootBox')?.innerText?.substring(0, 2000)
```

## Interacting with Clerk Modals

### Clicking Buttons

Use `evaluate` to find and click buttons by text content:

```javascript
// Click a button by exact text
Array.from(document.querySelectorAll('.cl-rootBox button')).find(function(b) { 
  return b.textContent.trim() === 'Button Text' 
})?.click() || 'not found'
```

### Filling Inputs

Clerk inputs may be React-controlled. Use the native value setter pattern:

```javascript
var input = document.querySelector('.cl-rootBox input[name="fieldName"]');
var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
nativeInputValueSetter.call(input, 'value');
input.dispatchEvent(new Event('input', { bubbles: true }));
input.dispatchEvent(new Event('change', { bubbles: true }));
```

## Clerk Session Management API

Clerk exposes a frontend API for session management. This is more reliable than browser automation for session revocation.

### List Active Sessions

```bash
curl -s "https://clerk.example.com/v1/client" \
  -H "Cookie: __client=<JWT>; __session=<JWT>" \
  -H "Content-Type: application/json"
```

Response includes all active sessions with their IDs, devices, and last active timestamps.

### Revoke a Session

```bash
curl -s -X POST \
  "https://clerk.example.com/v1/client/sessions/<SID>/remove" \
  -H "Cookie: __client=<JWT>; __session=<JWT>; __refresh_<KEY>=<TOKEN>" \
  -H "Content-Type: application/json" \
  -H "Origin: https://example.com"
```

**Important**: The endpoint is `/remove`, not `/revoke` (which returns 404).

### Extract Session ID from JWT

```python
import base64, json
jwt = '<SESSION_JWT>'
payload = jwt.split('.')[1] + '==='
data = json.loads(base64.urlsafe_b64decode(payload))
session_id = data['sid']  # Session ID
```

## Cookie Injection for Clerk

Clerk uses HttpOnly cookies (`__session`, `__client`, `__refresh_*`) that cannot be set via JavaScript `document.cookie`. Must use the REST API:

```bash
curl -s -X POST "http://localhost:9377/sessions/agent1/cookies" \
  -H "Content-Type: application/json" \
  -d '{
    "cookies": [
      {
        "name": "__session",
        "value": "<JWT>",
        "domain": "example.com",
        "path": "/",
        "secure": true,
        "httpOnly": true,
        "sameSite": "Lax"
      }
    ]
  }'
```

## GitHub OAuth Auto-Authorization

When GitHub cookies are injected into Camoufox, clicking "Sign in with GitHub" on a Clerk-protected site will auto-authorize without manual intervention:

1. Inject GitHub cookies via REST API
2. Navigate to the Clerk-protected site's login page
3. Click "Sign in with GitHub" button
4. GitHub will auto-authorize (no manual "Authorize" click needed)
5. Clerk will complete the OAuth flow and log the user in

This works because GitHub OAuth tokens are transferable across browser contexts.

## Common Clerk Patterns

### Password Reset Flow

1. Click "Forgot password?" link
2. Enter email address
3. Clerk sends password reset email
4. Extract reset link from email (via IMAP or email service API)
5. Navigate to reset link
6. Enter new password + confirm
7. Click "Reset password"

### 2FA Setup Flow

**Critical**: Clerk requires email verification BEFORE TOTP can be enabled.

**Prerequisite**: A password must be set on the account before 2FA can be enabled. If the account was created via OAuth (Google/GitHub) and has no password, set one first.

**Full flow (tested on OpenRouter July 2026)**:

1. Login with email + password
2. Clerk sends email verification code (if first login after password set)
3. Extract verification code from email: `himalaya envelope list --account gmail | head -5` — look for "XXXXXX is your verification code"
4. Enter email verification code via `browser_type(ref, code)` where ref is `textbox "Enter verification code"`
5. Navigate to Preferences page
6. Click "Manage" button (opens Clerk modal as a `dialog` in the accessibility tree)
7. Click "Security" tab — either via `browser_click(ref)` if visible in snapshot, or via JS: `document.querySelector('.cl-navbarButton__security')?.click()`
8. Click "Add two-step verification" — via JS: `Array.from(document.querySelectorAll('.cl-rootBox button')).find(b => b.textContent.trim() === 'Add two-step verification')?.click()`
9. Select "Authenticator application" from the dropdown menu
10. Click "Can't scan QR code?" to reveal TOTP secret
11. **TOTP secret appears in the accessibility snapshot** as a disabled textbox: `textbox [eN] [disabled]: <SECRET>`. Also extractable via JS: `document.querySelector('.cl-rootBox')?.innerHTML?.match(/otpauth[^"'<]*/)?.[0]`
12. Generate TOTP code: `uv run --with pyotp python3 -c "import pyotp; print(pyotp.TOTP('<SECRET>').now())"`
13. Enter TOTP code via `browser_type(ref, code)` where ref is `textbox "Enter verification code"`
14. If "Incorrect code" appears, generate a fresh code (30-second expiry) and retry
15. Click "Continue" (may need to look for it — after TOTP verification, a "Finish" button appears)
16. Save TOTP secret to `/tmp/openrouter_2fa_secret.txt` for user to add to password manager

**TOTP code entry**: Use `browser_type(ref, code)` with the aria ref from `browser_snapshot` (look for `textbox "Enter verification code"`). This is more reliable than the old JS `evaluate` approach.

**Password requirement**: If the account was created via OAuth (Google/GitHub) and has no password, Clerk requires setting a password before 2FA can be enabled. The flow:
1. Click "Set password" in the Security tab
2. Generate a strong password: `python3 -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits + '!@#$%^&*') for _ in range(32)))"`
3. Enter in both "New password" and "Confirm password" fields (use JS native value setter for React-controlled inputs)
4. Check "Sign out of all other devices" checkbox
5. Click "Save"
6. Save password to `/tmp/or_password.txt` for the user
7. Then proceed with 2FA setup above

**Note**: Button refs vary by platform. Use `browser_snapshot` to find current refs after each navigation. Clerk modal content appears as a `dialog` in the accessibility tree with buttons like `Profile`, `Security`, `Account`, `Close modal`, etc.

### Email Verification

Clerk may require email verification before allowing certain actions (password change, 2FA setup). The flow is:

1. Trigger action requiring verification
2. Clerk sends verification code to email
3. Extract code from email
4. Enter code in verification input
5. Click "Continue" or "Verify"

## Troubleshooting

### Clerk Modal Not Visible in Snapshot

If `browser_snapshot` doesn't show Clerk modal content:

```javascript
// Check if modal exists in DOM
document.querySelector('.cl-rootBox') ? 'exists' : 'not found'

// Get modal text content
document.querySelector('.cl-rootBox')?.innerText

// Find all buttons in modal
Array.from(document.querySelectorAll('.cl-rootBox button')).map(b => b.textContent.trim())
```

### Session Revocation Fails

If `/remove` endpoint returns 401 or 403:

- Check that cookies are valid (not expired)
- Verify the session ID is correct
- Ensure `Origin` header matches the site's domain
- Try listing sessions first to confirm the session exists

### Cookie Injection Fails

If REST API returns error:

- Check cookie format (must include `name`, `value`, `domain`, `path`)
- Verify `sameSite` is one of: `Strict`, `Lax`, `None` (capitalized)
- Ensure `secure` is `true` for HttpOnly cookies
- Check that the session exists (create it first if needed)
