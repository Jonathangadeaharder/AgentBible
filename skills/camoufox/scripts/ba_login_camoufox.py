#!/usr/bin/env python3
"""
BA-Arbeitsagentur login automation with Camoufox.
Handles cookie banner, login form, and waits for 2FA push confirmation.
"""

import os, time, sys
from camoufox.sync_api import Camoufox

BA_USER = os.environ.get("BA_USER", "<EMAIL>")
BA_PASS = os.environ.get("BA_PASS", "<BA_PASSWORD>")

def login_ba_camoufox():
    """Full login flow, returns page after 2FA or raises on timeout."""
    with Camoufox(
        headless=False,
        humanize=True,
        geoip=False,
        addons=["ublock-origin"],
    ) as browser:
        page = browser.new_page()
        
        # 1. Navigate to profile entry point
        page.goto("https://web.arbeitsagentur.de/profil/profil-ui/pd/", timeout=60000)
        page.wait_for_load_state("networkidle", timeout=30000)
        time.sleep(3)
        
        # 2. Remove cookie banner
        page.evaluate("""() => {
            document.querySelectorAll('bahf-cookie-disclaimer-dpl3').forEach(el => el.remove());
        }""")
        
        # 3. Click first "Anmelden" link
        clicked = page.evaluate("""() => {
            const links = document.querySelectorAll('a, button');
            for (const link of links) {
                if (link.textContent.trim() === 'Anmelden') {
                    link.click();
                    return true;
                }
            }
            return false;
        }""")
        if not clicked:
            raise RuntimeError("Could not find Anmelden link")
        time.sleep(5)
        
        # 4. Wait for SSO login form
        page.wait_for_selector("input[type='text'], input[type='email'], input[name='username']", timeout=15000)
        time.sleep(1)
        
        # 5. Fill credentials
        page.locator("input[type='text'], input[type='email'], input[name='username']").first.fill(BA_USER)
        page.locator("input[type='password'], input[name='password']").first.fill(BA_PASS)
        time.sleep(1)
        
        # 6. Submit
        page.evaluate("""() => {
            const btns = document.querySelectorAll('button[type="submit"], button, input[type="submit"]');
            for (const btn of btns) {
                if (btn.textContent.trim() === 'Anmelden' || btn.textContent.includes('Anmelden')) {
                    btn.click();
                    return true;
                }
            }
            return false;
        }""")
        
        # 7. Wait for 2FA push page
        page.wait_for_load_state("networkidle", timeout=15000)
        time.sleep(3)
        
        # Check if 2FA required
        text = page.inner_text("body")
        if "BA-Secure App bestätigen" in text:
            print(">>> 2FA REQUIRED: Confirm in BA-Secure App now! 4 minutes <<<")
            # Wait up to 4 minutes for 2FA
            for i in range(240):
                time.sleep(1)
                if i % 30 == 0:
                    print(f"  Waiting... {240-i}s remaining")
                current_url = page.url
                if "profil/profil-ui/pd" in current_url and "login" not in current_url:
                    print(">>> 2FA SUCCESS - Logged in! <<<")
                    break
            else:
                raise TimeoutError("2FA timeout - push not confirmed in time")
        
        # Verify logged in
        page.goto("https://web.arbeitsagentur.de/profil/profil-ui/pd/", timeout=60000)
        page.wait_for_load_state("networkidle", timeout=30000)
        time.sleep(3)
        
        text = page.inner_text("body")
        if "Anmelden" in text and "Profil" not in text:
            raise RuntimeError("Login failed - still shows Anmelden")
        
        print(">>> LOGIN SUCCESSFUL <<<")
        return page, browser

def main():
    try:
        page, browser = login_ba_camoufox()
        
        # Export cookies for reuse
        cookies = page.context.cookies()
        print(f"Captured {len(cookies)} cookies")
        for c in cookies:
            if "arbeitsagentur" in c.get("domain", ""):
                exp = c.get("expires", "session")
                print(f"  {c['domain']:40s} {c['name']:30s} exp={exp}")
        
        # Save cookies
        import json
        with open("/tmp/ba_session_cookies.json", "w") as f:
            json.dump(cookies, f, indent=2)
        print("Cookies saved to /tmp/ba_session_cookies.json")
        
        # Keep browser open
        print("Browser staying open. Press Ctrl+C to close.")
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            pass
        
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()