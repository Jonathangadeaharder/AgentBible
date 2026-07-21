# Security Incident Response — Clerk Session Theft

When a user reports unauthorized API usage or session compromise on a Clerk-based platform (OpenRouter, Vapi, etc.), follow this workflow.

## Detection Signals

- Unexpected API charges or usage spikes
- User reports "I got scammed" or "unauthorized usage"
- Suspicious login locations in Clerk security panel

## Response Workflow

### Phase 1: Session Revocation (Immediate)

**Goal**: Kill the attacker's active sessions before they can create new API keys.

1. **Extract Clerk session cookies from Firefox**:
   ```bash
   # Find Firefox profile with target site cookies
   find ~/Library/Application\ Support/Firefox/Profiles -name "cookies.sqlite" | xargs -I {} sqlite3 {} "SELECT host, name FROM moz_cookies WHERE host LIKE '%clerk%'"
   
   # Extract session cookies (need __client, __session, __refresh_*)
   sqlite3 "$PROFILE/cookies.sqlite" "SELECT name, value FROM moz_cookies WHERE host LIKE '%clerk%' AND name IN ('__client', '__session', '__refresh_*')"
   ```

2. **Decode session JWT to get session ID**:
   ```python
   import base64, json
   jwt = '<__session_cookie_value>'
   payload = jwt.split('.')[1] + '==='
   data = json.loads(base64.urlsafe_b64decode(payload))
   session_id = data['sid']  # e.g., "sess_3Dis1mwybYDA8xWQtw0r8clFDVu"
   user_id = data['sub']     # e.g., "user_2tG8tLjpAzAmEUOGgK5UbSI5Xar"
   ```

3. **Revoke session via Clerk API**:
   ```bash
   # Endpoint: POST /v1/client/sessions/{sid}/remove
   # NOT /revoke (returns 404)
   curl -s -X POST "https://clerk.<domain>/v1/client/sessions/$SESSION_ID/remove" \
     -H "Cookie: __client=$CLIENT_JWT; __session=$SESSION_JWT; __refresh_$KEY=$TOKEN" \
     -H "Content-Type: application/json" \
     -H "Origin: https://<domain>"
   ```

4. **Verify revocation**:
   ```bash
   # List active sessions — should be empty or only show current device
   curl -s "https://clerk.<domain>/v1/client" \
     -H "Cookie: __client=$CLIENT_JWT; __session=$SESSION_JWT"
   ```

**Critical**: Revoking API keys alone is INSUFFICIENT. The attacker can create new keys from the active web session. Must revoke the Clerk session itself.

### Phase 2: Browser Automation for 2FA Setup

**Goal**: Enable TOTP 2FA to prevent future session theft.

1. **Inject Firefox cookies into Camoufox**:
   ```python
   # Extract GitHub + Clerk cookies from Firefox
   # Inject via REST API (HttpOnly cookies can't be set via JS)
   curl -X POST "http://localhost:9377/sessions/agent1/cookies" \
     -H "Content-Type: application/json" \
     -d '{"cookies": [...]}'
   ```

2. **Login via GitHub OAuth** (auto-auth when cookies injected):
   ```bash
   # Navigate to sign-in page
   browser_navigate "https://<domain>/sign-in"
   
   # Click "Sign in with GitHub" — auto-authorizes if GitHub cookies injected
   browser_click "@e18"  # GitHub button ref
   
   # If authorize prompt appears, click it
   browser_click "@e5"   # "Authorize <App>" button
   ```

3. **Handle email verification** (Clerk may require it):
   ```bash
   # Check for verification code input
   browser_snapshot  # Look for "Enter verification code"
   
   # Read code from Gmail via himalaya
   himalaya envelope list --account gmail | grep "verification code"
   
   # Extract 6-digit code from subject line
   # e.g., "175562 is your verification code"
   
   # Enter code
   browser_type "@e18" "175562"
   browser_click "@e20"  # Continue button
   ```

4. **Navigate to security settings**:
   ```bash
   # Go to preferences page
   browser_navigate "https://<domain>/settings/preferences"
   
   # Click "Manage" to open Clerk modal
   browser_click "@e37"  # Manage button
   
   # Click "Security" tab in Clerk modal
   browser_click "@e46"  # Security button
   ```

5. **Enable TOTP 2FA**:
   ```bash
   # Click "Add two-step verification"
   browser_click "@e49"
   
   # Select "Authenticator application"
   browser_click "@e2"
   
   # Click "Can't scan QR code?" to get TOTP secret
   browser_click "@e49"
   
   # Extract TOTP secret from page
   # Look for: otpauth://totp/...?secret=<SECRET>
   # Or: textbox with secret value
   
   # Generate TOTP code
   uv run --with pyotp python3 -c "
   import pyotp
   secret = '<TOTP_SECRET>'
   totp = pyotp.TOTP(secret)
   print(totp.now())
   "
   
   # Enter TOTP code
   browser_type "@e49" "<TOTP_CODE>"
   
   # Click Continue/Verify
   browser_click "@e54"
   
   # Save TOTP secret to file
   # User must add to password manager
   ```

### Phase 3: API Key Rotation

**Goal**: Rotate all exposed API keys.

1. **Identify exposed keys**:
   - Keys in .env files
   - Keys in shell history
   - Keys in session transcripts
   - Keys in git history

2. **Rotate each key at provider dashboard**:
   - Use browser automation or provider CLI
   - Update .env files with new keys
   - Restart services using the keys

3. **Delete plaintext key files**:
   ```bash
   # Find files containing keys
   grep -rl "sk-or-v1-\|csk-\|tngai_\|xai-" ~/Documents/archive/
   
   # Delete them
   rm <files>
   ```

### Phase 4: Infrastructure Hardening

**Goal**: Prevent future session theft.

1. **Lock down Firefox cookies**:
   ```bash
   chmod 600 ~/Library/Application\ Support/Firefox/Profiles/*/cookies.sqlite
   chmod 700 ~/Library/Application\ Support/Firefox/Profiles/*/
   ```

2. **Lock down shell config files**:
   ```bash
   chmod 600 ~/.zshenv ~/.bashrc ~/.zshrc
   ```

3. **Enable macOS firewall**:
   ```bash
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setstealthmode on
   ```

4. **Bind local proxies to localhost**:
   ```bash
   # If running meta-router or similar proxy
   # Change --host 0.0.0.0 to --host 127.0.0.1
   # Restart the service
   ```

## Common Pitfalls

1. **Revoking API keys alone doesn't stop the attack**: Attacker can create new keys from active web session. Must revoke Clerk session.

2. **Clerk session revocation endpoint is /remove, not /revoke**: /revoke returns 404.

3. **HttpOnly cookies can't be set via JavaScript**: Must use Camoufox REST API `/sessions/:userId/cookies` for cookie injection.

4. **GitHub OAuth auto-authorizes when cookies injected**: No need to manually click "Authorize" if GitHub session cookies are present.

5. **Clerk may require email verification before 2FA setup**: Read verification code from email (himalaya) and enter it.

6. **TOTP code must be generated fresh**: Codes expire every 30 seconds. Generate immediately before entering.

7. **Firefox must be closed for fresh cookie extraction**: Firefox holds session cookies in RAM. Kill Firefox before extracting cookies.sqlite.

## Verification Checklist

- [ ] All Clerk sessions revoked except current device
- [ ] TOTP 2FA enabled and secret saved to password manager
- [ ] All API keys rotated
- [ ] Plaintext key files deleted
- [ ] Firefox cookies locked down (chmod 600)
- [ ] Shell config files locked down (chmod 600)
- [ ] macOS firewall enabled
- [ ] Local proxies bound to 127.0.0.1
- [ ] Fraud report sent to provider support

## Provider-Specific Notes

### OpenRouter

- Clerk domain: `clerk.openrouter.ai`
- 2FA setup: Settings → Preferences → Manage → Security → Add two-step verification
- Support email: `support@openrouter.ai`
- Fraud report template: Include account email, user ID, attack vector, timeline, remediation steps

### Vapi

- Clerk domain: `clerk.vapi.ai`
- Stytch auth (not Clerk): Cookie transfer Firefox → Camoufox does NOT work. Must do direct login.

### Other Clerk-based platforms

- Clerk domain: `clerk.<domain>`
- Session revocation: Same API pattern
- 2FA setup: Usually in Settings → Security or Account → Security
