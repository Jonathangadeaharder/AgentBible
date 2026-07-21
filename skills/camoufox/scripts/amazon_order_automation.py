#!/usr/bin/env python3
"""
Amazon Order History Automation — injects Firefox session cookies, navigates to order history.

Usage:
    python3 scripts/amazon_order_automation.py

Requires:
- Camoufox server running on localhost:9377
- CAMOFOX_URL=http://localhost:9377 in ~/.hermes/.env
- Firefox profile with active Amazon session (logged in)

Workflow:
1. Extract Amazon cookies from RUNNING Firefox (no close needed — Amazon auth cookies are persistent)
2. Inject cookies to hermes userId
3. Navigate to order history
4. Verify login (check for "Hallo, [Name]" not sign-in page)

Key: Amazon's auth cookies (at-main, at-acbde, session-token) are PERSISTENT in cookies.sqlite.
No need to close Firefox. Just copy cookies.sqlite + cookies.sqlite-wal.
"""

import os
import sys
import time
import requests
import json
import sqlite3
import uuid
import shutil

CAMOFOX_URL = os.getenv("CAMOFOX_URL", "http://localhost:9377")
FIREFOX_PROFILE = os.getenv("FIREFOX_PROFILE", "<FF_PROFILE>")

def get_hermes_identity():
    """Get the deterministic Hermes userId/sessionKey for this profile."""
    scope_root = os.path.expanduser("~/.hermes/browser_auth/camofox")
    user_digest = uuid.uuid5(uuid.NAMESPACE_URL, f"camofox-user:{scope_root}").hex[:10]
    session_digest = uuid.uuid5(uuid.NAMESPACE_URL, f"camofox-session:{scope_root}:default").hex[:16]
    return {"user_id": f"hermes_{user_digest}", "session_key": f"task_{session_digest}"}

def extract_amazon_cookies(profile_name, output_path):
    """Extract Amazon cookies from RUNNING Firefox (no close needed).

    Amazon auth cookies are persistent — they ARE in cookies.sqlite while Firefox runs.
    Copy both cookies.sqlite AND cookies.sqlite-wal (WAL has latest uncommitted entries).
    """
    profile_path = os.path.expanduser(f"~/Library/Application Support/Firefox/Profiles/{profile_name}")
    cookies_db = os.path.join(profile_path, "cookies.sqlite")

    if not os.path.exists(cookies_db):
        print(f"ERROR: cookies.sqlite not found at {cookies_db}")
        sys.exit(1)

    # Copy to temp location (with WAL for uncommitted entries)
    tmp_db = "/tmp/ff_cookies.sqlite"
    shutil.copy2(cookies_db, tmp_db)
    try:
        shutil.copy2(os.path.join(profile_path, "cookies.sqlite-wal"), "/tmp/ff_cookies.sqlite-wal")
    except FileNotFoundError:
        pass  # WAL may not exist if no uncommitted entries

    conn = sqlite3.connect(tmp_db)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT host, name, value, path, expiry, isSecure, isHttpOnly, sameSite
        FROM moz_cookies WHERE host LIKE '%amazon%'
    """)

    cookies = []
    for host, name, value, path, expiry, isSecure, isHttpOnly, sameSite in cursor.fetchall():
        # Normalize expiry: ms→s, 0→-1
        clean_expiry = -1
        if expiry and expiry > 0:
            if expiry > 1e12:
                clean_expiry = int(expiry / 1000)
            elif expiry > 1e9:
                clean_expiry = int(expiry)

        # Filter Cloudflare cookies
        if name in ('cf_clearance', '__cf_bm'):
            continue

        cookies.append({
            'domain': host,
            'name': name,
            'value': value,
            'path': path or '/',
            'expires': clean_expiry,
            'secure': bool(isSecure),
            'httpOnly': bool(isHttpOnly),
            'sameSite': ['None', 'Lax', 'Strict'][sameSite] if sameSite in [0, 1, 2] else 'Lax'
        })

    conn.close()
    os.unlink(tmp_db)

    with open(output_path, 'w') as f:
        json.dump(cookies, f, indent=2)

    # Verify session-token freshness
    session_tokens = [c for c in cookies if c['name'] == 'session-token']
    for st in session_tokens:
        print(f"  session-token ({st['domain']}): {st['value'][:40]}...")

    print(f"Extracted {len(cookies)} Amazon cookies to {output_path}")
    return len(cookies)

def inject_cookies(user_id, cookies_path):
    """Inject cookies to hermes userId via REST API."""
    with open(cookies_path) as f:
        cookies = json.load(f)

    payload = {"cookies": cookies}
    resp = requests.post(
        f"{CAMOFOX_URL}/sessions/{user_id}/cookies",
        json=payload,
        timeout=30
    )
    resp.raise_for_status()
    result = resp.json()
    print(f"Injected {result.get('count', 0)} cookies to {user_id}")
    return result

def create_tab(user_id, session_key, url):
    """Create a new tab with the given URL."""
    resp = requests.post(
        f"{CAMOFOX_URL}/tabs",
        json={"userId": user_id, "sessionKey": session_key, "url": url},
        timeout=30
    )
    resp.raise_for_status()
    tab_id = resp.json()["tabId"]
    print(f"Created tab: {tab_id}")
    return tab_id

def snapshot(tab_id, user_id):
    """Get page snapshot."""
    resp = requests.get(
        f"{CAMOFOX_URL}/tabs/{tab_id}/snapshot",
        params={"userId": user_id},
        timeout=30
    )
    resp.raise_for_status()
    return resp.json()

def main():
    identity = get_hermes_identity()
    user_id = identity["user_id"]
    session_key = identity["session_key"]

    print(f"Using Hermes identity: {user_id}")

    # Step 1: Extract cookies from RUNNING Firefox (no close needed)
    cookies_path = "/tmp/amazon_cookies.json"
    count = extract_amazon_cookies(FIREFOX_PROFILE, cookies_path)
    if count == 0:
        print("ERROR: No Amazon cookies found. Is Firefox logged in to Amazon?")
        sys.exit(1)

    # Step 2: Delete old session, inject fresh cookies
    try:
        requests.delete(f"{CAMOFOX_URL}/sessions/{user_id}", timeout=10)
    except:
        pass
    inject_cookies(user_id, cookies_path)

    # Step 3: Navigate to order history
    url = "https://www.amazon.de/your-orders/orders"
    print(f"Navigating to {url}")
    tab_id = create_tab(user_id, session_key, url)

    # Wait for page load
    time.sleep(3)

    # Step 4: Verify login
    snap = snapshot(tab_id, user_id)
    snap_text = snap["snapshot"]
    result_url = snap["url"]

    if "Hallo," in snap_text or "Hello," in snap_text:
        print(f"\n{'='*60}")
        print("SUCCESS: Logged in to Amazon")
        print(f"URL: {result_url}")
        print(f"{'='*60}")
    elif "/ap/signin" in result_url:
        print(f"\n{'='*60}")
        print("ERROR: Redirected to sign-in page after cookie injection")
        print("Likely cause: STALE cookies. session-token changes frequently.")
        print("Fix: Re-extract from Firefox cookies.sqlite (copy WAL too)")
        print(f"{'='*60}")
        sys.exit(1)
    else:
        print(f"\nUnexpected page state. URL: {result_url}")
        print("First 500 chars of snapshot:")
        print(snap_text[:500])

if __name__ == "__main__":
    main()
