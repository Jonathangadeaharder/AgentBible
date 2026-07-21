# Stytch-based Auth Cookie Transfer (Firefox → Camoufox)

> **CORRECTION (2026-07-04)**: The original claim that "stytch cookies transfer cleanly cross-browser" is **WRONG for Vapi**. Stytch session tokens CAN be fingerprint-bound depending on provider configuration. See "Vapi Finding" section below.

## When It Works: Groq (stytch_session cookies)

Groq uses Stytch with `stytch_session` + `stytch_session_jwt` cookies on `.groq.com` and `.api.stytchb2b.groq.com`. These appear to transfer cleanly Firefox → Camoufox (tested, worked for Groq console access).

### Extract stytch Cookies for Groq

```bash
# Extract stytch cookies for Groq
cp ~/Library/Application\\ Support/Firefox/Profiles/<profile>/cookies.sqlite /tmp/ff_groq_cookies.sqlite
python3 -c "
import sqlite3, json
conn = sqlite3.connect('/tmp/ff_groq_cookies.sqlite')
rows = conn.execute('''
    SELECT name, value, host, path, expiry, isSecure, isHttpOnly, sameSite
    FROM moz_cookies WHERE host LIKE '%groq%' OR host LIKE '%stytch%'
''').fetchall()
conn.close()
ss_map = {0: 'None', 1: 'Lax', 2: 'Strict', 3: 'None'}
cookies = []
for name, value, host, path, expiry, is_secure, is_http_only, same_site in rows:
    if not value: continue
    c = {'name': name, 'value': value, 'domain': host, 'path': path or '/',
         'secure': is_secure == 1, 'httpOnly': is_http_only == 1,
         'sameSite': ss_map.get(same_site, 'None')}
    if expiry and expiry > 0:
        if expiry > 1e15: expiry = int(expiry / 1e6)
        elif expiry > 1e12: expiry = int(expiry / 1e3)
        c['expires'] = expiry
    else:
        c['expires'] = -1
    cookies.append(c)
with open('/tmp/ff_groq_cookies.json', 'w') as f:
    json.dump(cookies, f, indent=2)
print(f'Extracted {len(cookies)} cookies')
"
camoufox clear_cookies
camoufox load_cookies /tmp/ff_groq_cookies.json
camoufox goto "https://console.groq.com/keys"
```

## When It FAILS: Vapi (__sec__ cookie family)

**Tested 2026-07-04**: Vapi uses Stytch B2B with a **different cookie pattern** — `__sec__cid`, `__sec__fid`, `__sec_crid`, `__sec_id`, `__sec_peid`, plus `_db-<hash>` (contains session token UUID). These are **fingerprint-bound** — same pattern as Google SSO.

### What Was Tried
1. Extracted all 20 Vapi cookies from `<FF_PROFILE>` Firefox profile
2. Included `__cf_bm` for `.auth.vapi.ai` and `.vapi.ai`
3. `clear_cookies` → `load_cookies` → `goto https://dashboard.vapi.ai/assistants`
4. Result: **Login page shown** — session not recognized

### Why It Fails
Vapi's Stytch implementation validates the browser fingerprint against the session token. The `_db-` cookie contains a UUID token (`<SESSION_TOKEN_UUID>...`), but it's NOT a Vapi API key — it's a Stytch session token that requires fingerprint match. Loading it into a different browser (Camoufox) invalidates the session.

### Vapi Auth Cookie Pattern
| Cookie | Domain | Purpose |
|--------|--------|---------|
| `__sec__cid` | `dashboard.vapi.ai` | Stytch member/session ID |
| `__sec__fid` | `dashboard.vapi.ai` | Stytch flow ID |
| `__sec_crid` | `dashboard.vapi.ai` | Stytch credential ID |
| `_db-<hash>` | `dashboard.vapi.ai` | Session token UUID (JSON: `{token, expiry}`) |
| `__sec_id` | `.vapi.ai` | Stytch session ID |
| `__sec_peid` | `.vapi.ai` | Stytch project/entity ID |
| `dashboard-serving` | `.vapi.ai` | Dashboard routing |
| `channel` | `.vapi.ai` | Session channel |

### Vapi API Auth
Vapi API (`api.vapi.ai`) requires `Authorization: Bearer <api_key>` header. Session cookies CANNOT be used for API calls. Must create API key in dashboard settings → only accessible after direct login.

### Workaround for Vapi
Direct login (email+password) inside Camoufox is the ONLY viable path. Google OAuth inside Camoufox also works IF a Google session is already established in the Camoufox profile.

## Comparison Table (Updated 2026-07-04)

| Aspect | Google SSO | Stytch (Groq) | Stytch (Vapi) |
|--------|------------|---------------|---------------|
| Fingerprint check | Yes | **No** (works cross-browser) | **Yes** (fails cross-browser) |
| Cookies needed | `SID`, `HSID`, `__Secure-1PSID` | `stytch_session`, `stytch_session_jwt` | `__sec__cid`, `_db-<hash>`, `__sec_id` |
| Cross-browser transfer | Fails | Works | **Fails** |
| 2FA bypass | Only if same browser | Works cross-browser | Does NOT work cross-browser |
| API auth | N/A | `Authorization: Bearer <key>` | `Authorization: Bearer <key>` |

**Lesson**: Stytch is NOT a monolith — different providers configure it differently. Test before assuming cookie transfer works.
