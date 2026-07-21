# GitHub Profile Repo Pinning — Full Automation Script

GitHub profile repo pins have no API (GraphQL `updatePinnedItems` doesn't exist).
This is the full Camoufox + cookie injection script that drives the web UI.

## Prerequisites

- Camoufox installed: `~/projects/travel-bot/.venv` (or `~/projects/shopping-bot/.venv`)
- Firefox profile with active GitHub session for the target account

## Finding the Right Firefox Profile

User has multiple Firefox profiles, each potentially logged into a different GitHub account:

```bash
for p in ~/Library/Application\ Support/Firefox/Profiles/*/; do
  name=$(basename "$p")
  tmp=$(mktemp /tmp/ff_XXXX.sqlite)
  cp "$p/cookies.sqlite" "$tmp" 2>/dev/null || continue
  result=$(sqlite3 "$tmp" "SELECT value FROM moz_cookies WHERE host LIKE '%github%' AND name='dotcom_user';" 2>/dev/null)
  echo "$name -> dotcom_user=$result"
  rm -f "$tmp"
done
```

Output example:
```
0z9sas3w.default -> dotcom_user=no github session
AbH5V1fE.Profil 3 -> dotcom_user=<GITHUB_USERNAME>        # WRONG account
<FF_PROFILE> -> dotcom_user=<GITHUB_USERNAME>  # CORRECT
```

## Full Script

```python
#!/usr/bin/env python3
"""Pin repos on GitHub profile via Camoufox + injected session cookies."""
import asyncio
import sqlite3
import os
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("gh_pin")

REPOS_TO_PIN = [
    "par-vs-batch-bench",
    "mlx-train-scaling",
    "eurobert-lemmatizer",  # NOTE: may differ from actual repo name!
    "subtitle-correction",
    "semantic-clone-detection",
    "mlx-subtitler",
]

PROFILE_URL = "https://github.com/<GITHUB_USERNAME>"
COOKIES_DB = "/tmp/gh_cookies_correct.sqlite"  # Copied from the right Firefox profile


def extract_cookies():
    """Extract GitHub cookies from Firefox cookies.sqlite."""
    conn = sqlite3.connect(COOKIES_DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT name, value, host, path, expiry, isSecure, isHttpOnly, sameSite
        FROM moz_cookies WHERE host LIKE '%github%'
    """)
    rows = cur.fetchall()
    conn.close()

    cookies = []
    sameSiteMap = {0: "None", 1: "Lax", 2: "Strict"}
    for name, value, host, path, expiry, secure, httpOnly, sameSite in rows:
        # Firefox stores expiry in MILLISECONDS, Playwright expects seconds
        expiry_sec = expiry // 1000 if expiry else -1
        if expiry_sec < 0:
            expiry_sec = -1
        cookies.append({
            "name": name,
            "value": value,
            "domain": host,
            "path": path,
            "expires": expiry_sec,
            "secure": bool(secure),
            "httpOnly": bool(httpOnly),
            "sameSite": sameSiteMap.get(sameSite, "None"),
        })
    log.info(f"Extracted {len(cookies)} GitHub cookies")
    return cookies


async def main():
    from camoufox.async_api import AsyncCamoufox

    cookies = extract_cookies()

    browser = AsyncCamoufox(
        headless=True,
        humanize=True,
        locale="en-US",
        i_know_what_im_doing=True,
    )

    async with browser as b:
        # CRITICAL: create a context — add_cookies is on context, not browser
        context = await b.new_context()
        page = await context.new_page()
        page.on("pageerror", lambda e: log.error(f"  [pageerror] {e}"))

        # Navigate to github.com first (need to be on domain to set cookies)
        log.info("Navigating to github.com")
        await page.goto("https://github.com", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)

        # Inject cookies
        log.info("Injecting session cookies")
        for cookie in cookies:
            try:
                await context.add_cookies([cookie])
            except Exception as e:
                log.warning(f"  Failed to add cookie {cookie['name']}: {e}")

        # Navigate to profile
        log.info(f"Navigating to {PROFILE_URL}")
        await page.goto(PROFILE_URL, wait_until="domcontentloaded", timeout=30000)

        # Wait for pinned items spinner to hide (JS renders pinned repos async)
        try:
            await page.wait_for_selector('.js-pinned-items-spinner', state='hidden', timeout=15000)
        except:
            log.warning("Spinner still visible or timeout")

        await asyncio.sleep(2)

        # Verify we're viewing our own profile (check for "Customize your pins" button)
        # If it says "Follow" instead, we're viewing someone else's profile
        viewer = await page.evaluate("""() => {
            const meta = document.querySelector('meta[name="octolytics-actor-login"]');
            return meta ? meta.getAttribute('content') : null;
        }""")
        log.info(f"Viewer (octolytics-actor-login): {viewer}")

        # Click "Customize your pins"
        found = await page.evaluate("""() => {
            const els = document.querySelectorAll("a, button, summary");
            for (const el of els) {
                const text = el.textContent.trim().toLowerCase();
                if (text.includes("customize") && text.includes("pin")) {
                    el.click();
                    return text;
                }
            }
            return null;
        }""")
        if not found:
            log.error("Could not find 'Customize your pins' button — wrong account?")
            return
        log.info(f"Clicked pin button: '{found}'")

        await asyncio.sleep(2)

        # Pin each repo: search → check checkbox → clear search
        for repo in REPOS_TO_PIN:
            log.info(f"--- Pinning: {repo} ---")

            # Type repo name in search input
            search_result = await page.evaluate("""(repo) => {
                const dialog = document.querySelector("dialog[open]");
                if (!dialog) return 'no-dialog';
                const inputs = dialog.querySelectorAll('input[type="text"], input[type="search"]');
                for (const inp of inputs) {
                    inp.focus();
                    inp.value = '';
                    inp.value = repo;
                    inp.dispatchEvent(new Event('input', {bubbles: true}));
                    inp.dispatchEvent(new Event('change', {bubbles: true}));
                    return 'typed';
                }
                return 'no-input';
            }""", repo)
            log.info(f"  Search: {search_result}")
            await asyncio.sleep(1)

            # Find the repo in filtered list and check it
            check_result = await page.evaluate("""(repo) => {
                const dialog = document.querySelector("dialog[open]") || document.body;
                const rows = dialog.querySelectorAll('label, .Box-row, li, [class*="item"], [class*="row"]');
                for (const row of rows) {
                    const text = row.textContent.trim();
                    if (text.includes(repo)) {
                        const checkbox = row.querySelector('input[type="checkbox"]');
                        if (checkbox) {
                            if (!checkbox.checked) { checkbox.click(); return 'checked'; }
                            return 'already-checked';
                        }
                        const btn = row.querySelector('button, [role="button"]');
                        if (btn) { btn.click(); return 'button-clicked'; }
                        row.click();
                        return 'row-clicked';
                    }
                }
                return 'not-found';
            }""", repo)
            log.info(f"  Result: {check_result}")
            await asyncio.sleep(0.5)

            # Clear search for next repo
            await page.evaluate("""() => {
                const dialog = document.querySelector("dialog[open]");
                if (!dialog) return;
                const inputs = dialog.querySelectorAll('input[type="text"], input[type="search"]');
                for (const inp of inputs) {
                    inp.focus();
                    inp.value = '';
                    inp.dispatchEvent(new Event('input', {bubbles: true}));
                }
            }""")
            await asyncio.sleep(0.5)

        # Click Save
        saved = await page.evaluate("""() => {
            const dialog = document.querySelector("dialog[open]") || document.body;
            const btns = dialog.querySelectorAll('button, [type="submit"]');
            for (const btn of btns) {
                const text = btn.textContent.trim().toLowerCase();
                if (text === 'save' || text.includes('save pin')) {
                    btn.click();
                    return true;
                }
            }
            return false;
        }""")
        log.info(f"Save clicked: {saved}")
        await asyncio.sleep(3)

        # Verify
        await page.goto(PROFILE_URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(3)
        pinned = await page.evaluate("""() => {
            const repos = [];
            const links = document.querySelectorAll('a[href*="/<GITHUB_USERNAME>/"]');
            for (const link of links) {
                const href = link.getAttribute('href');
                const name = href.split('/').pop();
                if (name && !name.includes('#') && !name.includes('?') && !repos.includes(name)) {
                    if (!['followers','following','stars','repositories','projects','packages','overview','activity'].includes(name)) {
                        repos.push(name);
                    }
                }
            }
            return repos;
        }""")
        log.info(f"Pinned repos on profile: {pinned}")
        for repo in REPOS_TO_PIN:
            if repo in pinned:
                log.info(f"  ✓ {repo} pinned")
            else:
                log.warning(f"  ✗ {repo} NOT pinned (check actual repo name)")


if __name__ == "__main__":
    asyncio.run(main())
```

## Key Lessons

1. **No API for repo pins**: GraphQL schema has `pinIssue`, `pinEnvironment`, `pinIssueComment` but NO `updatePinnedItems` or `pinRepository`. Web-UI-only by design.
2. **Cookie expiry is milliseconds, not microseconds**: `1812801257666 ÷ 1000 = 1812801257` (year 2027). Wrong conversion → Playwright rejects all cookies.
3. **Check dotcom_user per profile**: User had Profil3 logged in as `<GITHUB_USERNAME>` and default-release as `<GITHUB_USERNAME>`. Must scan all profiles.
4. **Pinned items load async**: Must wait for `.js-pinned-items-spinner` to hide before "Customize your pins" button appears.
5. **Repo names may differ**: `eurobert-lemmatizer` was actually `german-spanish-english-eurobert-lemmatizer`. Check `gh repo list` first.
6. **add_cookies is on context, not browser**: `browser.add_cookies()` → `AttributeError`. Must `context = await browser.new_context()` first.
