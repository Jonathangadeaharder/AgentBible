# PerimeterX + Surfshark VPN — Test Results

## Skyscanner (skyscanner.de) — PX appId: PXrf8vapwA

### Test matrix (2026-06-29)

| Approach | Result |
|----------|--------|
| Camoufox headless (no VPN) | PX captcha: "Are you a person or a robot?" |
| Camoufox headless + Surfshark VPN (de-fra) | PX captcha — same block |
| Camoufox GUI + Surfshark VPN + geoip=True | PX captcha — same block |
| Camoufox GUI + Surfshark VPN + geoip + locale | PX captcha — same block |
| Playwright Firefox (vanilla) + Surfshark VPN | PX captcha — same block |
| Playwright Chromium + stealth flags + Surfshark VPN | PX captcha — same block |
| Camoufox + free SOCKS5 proxy (proxyscrape.com DE) | PX detects datacenter IP → blocked |
| curl_cffi (no browser) direct to API | 403 PX block on /api/search, /api/v3/browse |
| curl_cffi to homepage | 200 but returns empty SPA shell (JS-rendered, no data) |

### Key finding

**Surfshark VPN does NOT help with PerimeterX.** PX detects the browser automation protocol (Playwright CDP / Juggler), not just the IP. Even with a clean residential IP from Surfshark, PX blocks based on:
1. Browser fingerprint (Canvas, WebGL, navigator properties)
2. Behavioral patterns (mouse movement, timing)
3. Playwright/CDP protocol detection at network level

PX is harder than Cloudflare Turnstile. No Capsolver task type supports it (`AntiPerimeterXTaskProxyLess` returns `ERROR_TYPE_NOT_SUPPORTED`). `AntiCloudflareTask` returns "unsupported captcha type" or "Cloudflare challenge not found".

### Surfshark VPN setup

```bash
# Start VPN (residential IP)
sudo /opt/homebrew/bin/bash /opt/homebrew/bin/wg-quick up de-fra

# Verify IP
curl -sS https://api.ipify.org
# → 89.117.104.38 (Surfshark Frankfurt)

# Stop VPN
sudo /opt/homebrew/bin/bash /opt/homebrew/bin/wg-quick down de-fra
```

Config: `/etc/wireguard/de-fra.conf`

### Potential solutions (untested)

1. **RapidAPI key** — sign up at rapidapi.com for Skyscanner API (free tier). Returns JSON directly, no browser.
2. **CUA driver** — drive a real Firefox via macOS Accessibility (not Playwright). PX can't detect CDP protocol because there is none. See `macos-computer-use` skill.
3. **Paid residential proxy** — BrightData, SmartProxy. These have real residential IPs that PX doesn't flag. Free proxies (proxyscrape.com) are all datacenter.
4. **2captcha** — may support PerimeterX via custom task type (untested).

### What DOES work for Skyscanner

Nothing. The module (`scripts/skyscanner.py`) exists but returns 0 results. The `multi_search.py` orchestrator handles the empty result gracefully — other providers (Omio, Kayak, Google Flights) still return results.
