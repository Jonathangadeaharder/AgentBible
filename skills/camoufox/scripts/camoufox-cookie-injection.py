#!/usr/bin/env python3
"""
Camoufox cookie injection template for SSO-protected sites.

Usage:
  PYTHONPATH="" ~/.hermes/.venv/bin/python3 camoufox-cookie-injection.py \
    --profile "<FF_PROFILE>.Profil 4" \
    --domain "arbeitsagentur" \
    --url "https://www.arbeitsagentur.de/login" \
    --headless false \
    --wait 300

Prerequisites:
  - Camoufox 0.4.11, Playwright 1.49.0 in ~/.hermes/.venv
  - Camoufox binary symlink (Contents/Resources/camoufox → Contents/MacOS/camoufox)
  - PYTHONPATH="" prefix (avoids yaml module leak from hermes-agent venv)
"""
import os, sys, time, sqlite3, shutil, tempfile, argparse

def extract_cookies(profile_name, domain_filter):
    """Extract cookies from Firefox profile, filtered by domain."""
    profile_path = os.path.expanduser(
        f"~/Library/Application Support/Firefox/Profiles/{profile_name}"
    )
    cookies_db = os.path.join(profile_path, "cookies.sqlite")
    if not os.path.exists(cookies_db):
        raise FileNotFoundError(f"Profile not found: {profile_path}")

    tmp = os.path.join(tempfile.gettempdir(), "ff_cookies.sqlite")
    shutil.copy2(cookies_db, tmp)

    conn = sqlite3.connect(tmp)
    cur = conn.cursor()
    cur.execute(
        "SELECT name, value, host, path, expiry, isSecure, isHttpOnly, sameSite "
        "FROM moz_cookies WHERE host LIKE ?",
        (f"%{domain_filter}%",),
    )
    rows = cur.fetchall()
    conn.close()
    os.unlink(tmp)
    return rows


def normalize_expiry(expiry):
    """Firefox stores expiry in milliseconds. Playwright expects seconds."""
    if not expiry or expiry == 0:
        return None  # session cookie
    if expiry > 1e12:
        return int(expiry / 1e6)  # microseconds → seconds
    if expiry > 1e9:
        return int(expiry / 1e3)  # milliseconds → seconds
    return int(expiry)


def check_expired(rows):
    """Print warning for expired cookies."""
    now = time.time()
    for name, _, host, _, expiry, _, _, _ in rows:
        exp = normalize_expiry(expiry)
        if exp and exp < now:
            print(f"  ⚠ EXPIRED: {name} (host={host}, expired {time.ctime(exp)})")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True, help="Firefox profile dir name")
    parser.add_argument("--domain", required=True, help="Domain filter for cookies")
    parser.add_argument("--url", required=True, help="URL to navigate to")
    parser.add_argument("--headless", default="true", help="headless mode")
    parser.add_argument("--wait", type=int, default=120, help="Seconds to wait before close")
    args = parser.parse_args()

    rows = extract_cookies(args.profile, args.domain)
    print(f"Found {len(rows)} cookies for '{args.domain}'")
    check_expired(rows)

    from camoufox.sync_api import Camoufox

    same_site_map = {0: "None", 1: "Lax", 2: "Strict"}
    headless = args.headless.lower() == "true"

    with Camoufox(headless=headless, humanize=True, geoip=False) as browser:
        page = browser.new_page()
        page.on("pageerror", lambda e: None)  # suppress uBO JS errors

        # Navigate to set domain context
        page.goto(args.url, timeout=60000)
        page.wait_for_load_state("networkidle", timeout=30000)
        time.sleep(2)

        # Inject cookies
        injected = 0
        for name, value, host, path, expiry, is_secure, is_http_only, same_site in rows:
            try:
                cookie = {
                    "name": name,
                    "value": value,
                    "domain": host,
                    "path": path or "/",
                    "secure": bool(is_secure),
                    "httpOnly": bool(is_http_only),
                    "sameSite": same_site_map.get(same_site, "None"),
                }
                exp = normalize_expiry(expiry)
                if exp is not None:
                    cookie["expires"] = exp
                page.context.add_cookies([cookie])
                injected += 1
            except Exception as e:
                print(f"  skip {name}: {e}")

        print(f"Injected {injected}/{len(rows)} cookies")

        # Reload with cookies
        page.goto(args.url, timeout=60000)
        page.wait_for_load_state("networkidle", timeout=30000)
        time.sleep(5)

        print("TITLE:", page.title())
        print("URL:", page.url)

        page.screenshot(path="/tmp/camoufox_screenshot.png")
        print("SCREENSHOT: /tmp/camoufox_screenshot.png")

        text = page.inner_text("body")
        print("BODY:", text[:1000])

        time.sleep(args.wait)
        browser.close()


if __name__ == "__main__":
    main()
