#!/usr/bin/env python3
"""
Cookie injection script for BA-Arbeitsagentur SSO session.
Extracts cookies from Firefox profile and injects into Camoufox.
"""

import os, sys, sqlite3, shutil, tempfile, json

def extract_ba_cookies(profile_path):
    """Extract arbeitsagentur cookies from Firefox profile."""
    cookies_db = os.path.join(profile_path, "cookies.sqlite")
    if not os.path.exists(cookies_db):
        raise FileNotFoundError(f"cookies.sqlite not found in {profile_path}")
    
    tmp = os.path.join(tempfile.gettempdir(), "ba_cookies.sqlite")
    shutil.copy2(cookies_db, tmp)
    
    conn = sqlite3.connect(tmp)
    cur = conn.cursor()
    cur.execute("""
        SELECT name, value, host, path, expiry, isSecure, isHttpOnly, sameSite
        FROM moz_cookies WHERE host LIKE '%arbeitsagentur%'
    """)
    rows = cur.fetchall()
    conn.close()
    os.unlink(tmp)
    
    cookies = []
    for name, value, host, path, expiry, is_sec, is_http, same_site in rows:
        cookie = {
            "name": name, "value": value, "domain": host,
            "path": path or "/", "secure": bool(is_sec),
            "httpOnly": bool(is_http),
            "sameSite": {0: "None", 1: "Lax", 2: "Strict"}.get(same_site, "None"),
        }
        if expiry and expiry > 0:
            if expiry > 1e12:
                cookie["expires"] = int(expiry / 1e6)
            elif expiry > 1e9:
                cookie["expires"] = int(expiry / 1e3)
            else:
                cookie["expires"] = int(expiry)
        cookies.append(cookie)
    return cookies

def inject_cookies(page, cookies):
    """Inject cookies into Camoufox page context."""
    for cookie in cookies:
        try:
            page.context.add_cookies([cookie])
        except Exception as e:
            print(f"Failed to inject {cookie['name']}: {e}", file=sys.stderr)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True, help="Firefox profile path")
    parser.add_argument("--output", help="Output JSON file for cookies")
    args = parser.parse_args()
    
    cookies = extract_ba_cookies(args.profile)
    
    # Filter for critical SSO cookie
    sso_cookies = [c for c in cookies if "sso.arbeitsagentur" in c.get("domain", "")]
    domain_cookies = [c for c in cookies if "arbeitsagentur" in c.get("domain", "")]
    
    print(f"Found {len(domain_cookies)} arbeitsagentur cookies ({len(sso_cookies)} SSO)")
    for c in domain_cookies:
        exp = c.get("expires", "session")
        print(f"  {c['domain']:40s} {c['name']:30s} exp={exp}")
    
    if args.output:
        with open(args.output, "w") as f:
            json.dump(cookies, f, indent=2)
        print(f"Saved to {args.output}")

if __name__ == "__main__":
    main()