# BA-Secure App 2FA Reference

## Login Flow (Working Pattern)

### 1. Entry URL
```
https://web.arbeitsagentur.de/profil/profil-ui/pd/
```
→ Redirects to SSO via `oiam-oauth-component` (Next.js SPA)

### 2. SSO Login Form
After clicking "Anmelden" (first one, for persons):
```
https://sso.arbeitsagentur.de/auth/realms/OCP/login-actions/authenticate?execution=ba-username-password-form&...
```

Fields:
- Username: email (<EMAIL>)
- Password: <BA_PASSWORD>

### 3. 2FA Push
After submit:
```
URL: https://sso.arbeitsagentur.de/auth/realms/OCP/login-actions/authenticate?execution=732f5882-...
Title: "Anmeldung | Bundesagentur für Arbeit"
Body: "Anmeldung in der BA-Secure App bestätigen"
Timer: 4 minutes (00:03:56)
```

User must open BA-Secure App on phone → tap "Bestätigen"

### 4. Weiter Button (CRITICAL — does NOT auto-redirect!)

After 2FA confirmation, page stays on SSO URL but a "Weiter" button becomes clickable.

**THE #1 BUG (caused 6+ failed logins):** Two false assumptions about detecting when to click Weiter:

1. **FALSE: `"Weiter" in page.inner_text("body")` detects 2FA completion.**
   "Weiter" appears in body text (page nav/footer) BEFORE 2FA is confirmed. This causes Weiter to be clicked too early → kills SSO flow.

2. **FALSE: `"bestätigen" not in body.lower()` detects 2FA completion.**
   "bestätigen" NEVER disappears from body text after 2FA confirmation. This condition never fires → Weiter never clicked → loops until timeout.

**CORRECT approach**: Poll for Weiter button as a DOM element, click exactly once, use a flag to prevent re-clicking:
```python
weiter_clicked = False
for i in range(48):  # 4 min max, 5s intervals
    time.sleep(5)
    url = page.url
    if "sso.arbeitsagentur.de" not in url and "login-actions" not in url:
        print("LOGIN_SUCCESS!")
        break
    # Check for Weiter button via DOM (NOT body text!)
    has_weiter = page.evaluate("""() => {
        const btns = document.querySelectorAll('button, a, input[type="submit"]');
        for (const btn of btns) {
            if (btn.textContent.trim() === 'Weiter') return true;
        }
        return false;
    }""")
    if has_weiter and not weiter_clicked:
        page.evaluate("""() => {
            const btns = document.querySelectorAll('button, a, input[type="submit"]');
            for (const btn of btns) {
                if (btn.textContent.trim() === 'Weiter') { btn.click(); return; }
            }
        }""")
        weiter_clicked = True
        time.sleep(5)
        print("URL_AFTER_WEITER:", page.url)
```

**NOTE**: This DOM-based approach may still have issues — the Weiter button element might exist in the DOM before it becomes clickable. A more reliable approach would be to check `btn.disabled` or use Playwright's `page.wait_for_selector` with `state="visible"` on a specific selector. This needs further testing in the next session.

### 5. Success Redirect
After Weiter click:
```
→ https://web.arbeitsagentur.de/profil/profil-ui/pd/?state=...
→ Shows "Profil" dashboard with "<FULL_NAME>" + "Kundennummer: <KNR>"
```

## RULE: One Login Attempt Per Session
NEVER ask the user for 2FA confirmation twice in the same session. If the first attempt fails (timer expires, Weiter bug, etc.), do NOT retry. User frustration is extremely high when repeatedly asked to confirm the BA-Secure App. One attempt, one chance. If it fails, note it and move on.

## Credentials

### Firefox Saved Login
Host: `https://sso.arbeitsagentur.de`
- Username field: empty (not saved)
- Password: `<BA_PASSWORD>` (decrypted from key4.db via NSS)
- Username for login: `<EMAIL>` (email works as username)

## Session Cookies

### Critical Cookie: KC_AUTH_SESSION_HASH
- Domain: `sso.arbeitsagentur.de`
- Expiry: ~24-48 hours (microseconds since epoch)
- This IS the SSO session — without it, redirect to login

### Other Cookies
- `.arbeitsagentur.de` → `bahf_lang`, `cookie_consent`, `personalization_consent`
- `web.arbeitsagentur.de` → `STI_WEB`, `loglevel`

## Cookie Injection Pattern (Camoufox)

```python
import sqlite3, shutil, tempfile, os, base64

# 1. Copy cookies.sqlite (Firefox locks original)
profile = os.path.expanduser("~/Library/Application Support/Firefox/Profiles/<FF_PROFILE>.Profil 4")
tmp = os.path.join(tempfile.gettempdir(), "ba_cookies.sqlite")
shutil.copy2(os.path.join(profile, "cookies.sqlite"), tmp)

# 2. Query arbeitsagentur cookies
conn = sqlite3.connect(tmp)
cur = conn.cursor()
cur.execute("""
    SELECT name, value, host, path, expiry, isSecure, isHttpOnly, sameSite
    FROM moz_cookies WHERE host LIKE '%arbeitsagentur%'
""")
rows = cur.fetchall()
conn.close()

# 3. Normalize expiry (Firefox = microseconds)
def norm(exp):
    if not exp or exp == 0: return None
    if exp > 1e12: return int(exp / 1e6)
    if exp > 1e9: return int(exp / 1e3)
    return int(exp)

# 4. Inject into Camoufox page.context
same_site_map = {0: "None", 1: "Lax", 2: "Strict"}
for name, value, host, path, expiry, is_sec, is_http, same_site in rows:
    cookie = {
        "name": name, "value": value, "domain": host,
        "path": path or "/", "secure": bool(is_sec),
        "httpOnly": bool(is_http),
        "sameSite": same_site_map.get(same_site, "None"),
    }
    exp = norm(expiry)
    if exp: cookie["expires"] = exp
    page.context.add_cookies([cookie])
```

## Common Issues

| Issue | Fix |
|-------|-----|
| Weiter clicked too early (SSO flow killed) | Poll for Weiter button via DOM `querySelectorAll`, NOT body text. "Weiter" appears in body text before 2FA confirmed. |
| "bestätigen" never disappears from body | Don't use body text changes to detect 2FA confirmation. Use DOM button check instead. |
| Weiter loop (clicked repeatedly) | Use `weiter_clicked` flag. Click exactly ONCE. Break loop when URL leaves sso.arbeitsagentur.de. |
| Multiple 2FA requests in same session | NEVER ask user for 2FA twice in same session. One attempt, one chance. If fails, note and move on. |
| False "ALREADY_LOGGED_IN" | `web.arbeitsagentur.de/portal/mittellungen/` returns HTTP 200 with `robots.txt` body when NOT authenticated. Anti-bot block, NOT success. Always check body contains expected content (e.g. "Kundennummer" for profile page) |
| Persistent profile does NOT help | BA SSO cookies expire between sessions. Fresh 2FA login required each time. `persistent_context=True` + `user_data_dir` does NOT preserve SSO session |

## Automation Strategy

### Current: One-time manual 2FA → cookie reuse
1. Login with Camoufox (fresh)
2. User confirms push in BA-Secure App
3. Click Weiter (via DOM, once)
4. Export cookies: `page.context.cookies()`
5. Save KC_AUTH_SESSION_HASH + domain cookies
6. Next sessions: inject cookies → skip login

### Future: TOTP setup
1. User enables TOTP in portal settings ("Passwort und Zweiter Faktor einrichten")
2. Scan QR with Google Authenticator / 1Password
3. Automate 2FA: `pyotp.TOTP(secret).now()`
4. Fully headless login possible

## Debugging Commands

```bash
# Check Firefox saved login (password)
PYTHONPATH="" python3 -c "
import ctypes, os, json, base64
nss = ctypes.CDLL('/opt/homebrew/lib/libnss3.dylib')
nss.NSS_Init(os.path.expanduser('~/Library/Application Support/Firefox/Profiles/<FF_PROFILE>.Profil 4').encode())
class SECItem(ctypes.Structure):
    _fields_ = [('type', ctypes.c_uint), ('data', ctypes.c_char_p), ('len', ctypes.c_uint)]
nss.PK11SDR_Decrypt.argtypes = [ctypes.POINTER(SECItem), ctypes.POINTER(SECItem), ctypes.c_void_p]
with open(os.path.expanduser('~/Library/Application Support/Firefox/Profiles/<FF_PROFILE>.Profil 4/logins.json')) as f:
    for l in json.load(f)['logins']:
        if 'arbeitsagentur' in l['hostname']:
            for label, enc in [('user', l['encryptedUsername']), ('pass', l['encryptedPassword'])]:
                raw = base64.b64decode(enc)
                inp = SECItem(0, raw, len(raw))
                out = SECItem()
                nss.PK11SDR_Decrypt(ctypes.byref(inp), ctypes.byref(out), None)
                print(f'{label}: {out.data[:out.len].decode()}')
nss.NSS_Shutdown()
"

# Check cookies in profile
sqlite3 ~/Library/Application\\ Support/Firefox/Profiles/<FF_PROFILE>.Profil\\ 4/cookies.sqlite \
  "SELECT name, host, expiry FROM moz_cookies WHERE host LIKE '%arbeitsagentur%';"

# Camoufox version
PYTHONPATH="" python3 -c "from camoufox.pkgman import installed_verstr; print(installed_verstr())"
```
