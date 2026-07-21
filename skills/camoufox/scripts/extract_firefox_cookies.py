#!/usr/bin/env python3
"""Extract Lieferando session cookies from a Firefox profile for Camoufox injection.

Usage:
    python3 extract_firefox_cookies.py <profile_name> <output_path> [--domain lieferando]

Example:
    python3 extract_firefox_cookies.py "<FF_PROFILE>.Profil 4" /tmp/giuli_cookies.json

Kills Firefox first (session cookies are in RAM while running), copies cookies.sqlite,
extracts all cookies matching the domain (default: lieferando + takeaway), normalizes
expiry from milliseconds to seconds, validates sameSite index, and filters out
Cloudflare cookies (cf_clearance, __cf_bm) that are UA+IP bound.

The output JSON is directly loadable via `camoufox load_cookies <output_path>`.
"""
import sqlite3, json, shutil, os, sys, subprocess, time
from pathlib import Path

def kill_firefox():
    """Kill Firefox to flush WAL into cookies.sqlite and release profile lock.

    NOTE: For sites with PERSISTENT auth cookies (e.g. Amazon), you do NOT need
    to kill Firefox. Just copy cookies.sqlite + cookies.sqlite-wal directly.
    The kill is only needed for sites that store auth as SESSION cookies
    (expiry=0, in-memory only, e.g. Lieferando's je-at, Cerebras, Zhipu).
    See references/amazon-cookie-injection.md for the no-kill workflow.
    """
    subprocess.run(["pkill", "-9", "Firefox"], capture_output=True)
    time.sleep(3)

def extract_cookies(profile_name, output_path, domain_filter="lieferando"):
    profiles_dir = Path.home() / "Library/Application Support/Firefox/Profiles"
    
    # Find matching profile
    profile_path = None
    for p in profiles_dir.iterdir():
        if profile_name in p.name:
            profile_path = p
            break
    
    if not profile_path:
        print(f"Profile '{profile_name}' not found in {profiles_dir}")
        print("Available profiles:")
        for p in profiles_dir.iterdir():
            print(f"  {p.name}")
        return False
    
    db_path = profile_path / "cookies.sqlite"
    if not db_path.exists():
        print(f"No cookies.sqlite in {profile_path}")
        return False
    
    tmp_db = "/tmp/cookies_extract_temp.sqlite"
    shutil.copy2(db_path, tmp_db)
    
    conn = sqlite3.connect(tmp_db)
    cursor = conn.cursor()
    
    # Build domain filter
    if domain_filter == "lieferando":
        domain_clause = "host LIKE '%lieferando%' OR host LIKE '%takeaway%'"
    else:
        domain_clause = f"host LIKE '%{domain_filter}%'"
    
    cursor.execute(f"""
        SELECT host, name, value, path, expiry, isSecure, isHttpOnly, sameSite
        FROM moz_cookies
        WHERE ({domain_clause})
    """)
    
    cookies = []
    for row in cursor.fetchall():
        host, name, value, path, expiry, isSecure, isHttpOnly, sameSite = row
        
        # Normalize expiry: must be -1 or positive Unix timestamp in SECONDS
        # Firefox stores expiry in different units depending on cookie source
        clean_expiry = -1
        if expiry and expiry > 0:
            if expiry > 10000000000:  # 13+ digits = milliseconds
                clean_expiry = expiry // 1000
            elif expiry > 1000000000:  # 10 digits = seconds
                clean_expiry = expiry
            # else: invalid, leave as -1 (session cookie)
        
        # Filter out Cloudflare cookies (UA+IP bound, cause cross-browser rejection)
        if name in ('cf_clearance', '__cf_bm'):
            continue
        
        cookies.append({
            "domain": host,
            "name": name,
            "value": value,
            "path": path or "/",
            "expires": clean_expiry,
            "secure": bool(isSecure),
            "httpOnly": bool(isHttpOnly),
            "sameSite": ["None", "Lax", "Strict"][sameSite] if sameSite in [0, 1, 2] else "Lax"
        })
    
    conn.close()
    os.unlink(tmp_db)
    
    if not cookies:
        print(f"No cookies matching '{domain_filter}' found in {profile_name}")
        return False
    
    with open(output_path, 'w') as f:
        json.dump(cookies, f, indent=2)
    
    # Report auth cookies
    auth_names = ('je-at', 'je-auser', 'je-rt', 'je-last-login')
    auth_cookies = [c for c in cookies if c["name"] in auth_names]
    print(f"Extracted {len(cookies)} cookies from {profile_name}")
    if auth_cookies:
        print(f"  Auth cookies ({len(auth_cookies)}):")
        for c in auth_cookies:
            val = c["value"][:30] + "..." if len(c["value"]) > 30 else c["value"]
            print(f"    {c['name']} = {val} (httpOnly={c['httpOnly']})")
    print(f"Saved to {output_path}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <profile_name> <output_path> [--domain <filter>]")
        print(f"Example: {sys.argv[0]} '<FF_PROFILE>.Profil 4' /tmp/giuli_cookies.json")
        sys.exit(1)
    
    profile = sys.argv[1]
    output = sys.argv[2]
    domain = "lieferando"
    
    if "--domain" in sys.argv:
        idx = sys.argv.index("--domain")
        if idx + 1 < len(sys.argv):
            domain = sys.argv[idx + 1]
    
    kill_firefox()
    extract_cookies(profile, output, domain)
