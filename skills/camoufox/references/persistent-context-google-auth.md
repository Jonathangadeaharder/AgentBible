# Persistent Context for Google-Auth Sites

Some sites (Gemini, Google services) need full Firefox profile state (localStorage + IndexedDB), not just cookies. Use Playwright `launch_persistent_context` with a copied profile.

## When to Use

- **Gemini Images** (`gemini.google.com/images`) — Google auth requires full profile state
- **Grok Imagine** (`grok.com/imagine`) — works with both Camoufox cookies AND persistent context
- Any Google property where cookie injection shows "Sign in" page instead of logged-in content

## Pattern

```python
import os, shutil, tempfile
from playwright.sync_api import sync_playwright

FIREFOX_PROFILE = os.path.expanduser(
    "~/Library/Application Support/Firefox/Profiles/<FF_PROFILE>"
)

SKIP_DIRS = {"cache2", "startupCache", "savedtelemetry", "datareporting",
             "crashes", "minidumps", "fonts", "extensions"}

def copy_profile():
    tmp_profile = tempfile.mkdtemp(prefix="ff_profile_")
    for item in os.listdir(FIREFOX_PROFILE):
        if item in ("lock", ".parentlock", "parent.lock"):
            continue
        src = os.path.join(FIREFOX_PROFILE, item)
        dst = os.path.join(tmp_profile, item)
        try:
            if os.path.isdir(src):
                if item in SKIP_DIRS:
                    continue
                shutil.copytree(src, dst, symlinks=True)
            else:
                shutil.copy2(src, dst)
        except: pass
    # CRITICAL: Remove compatibility.ini — system Firefox is newer than Playwright's bundled Firefox
    compat = os.path.join(tmp_profile, "compatibility.ini")
    if os.path.exists(compat):
        os.remove(compat)
    return tmp_profile

pw = sync_playwright().start()
tmp_profile = copy_profile()
ctx = pw.firefox.launch_persistent_context(
    tmp_profile,
    headless=True,
    viewport={"width": 1366, "height": 900},
)
page = ctx.pages[0] if ctx.pages else ctx.new_page()
page.on("pageerror", lambda e: None)

page.goto("https://gemini.google.com/images", wait_until="domcontentloaded", timeout=30000)
time.sleep(8)
# Should be logged in!
```

## Why Cookie Injection Fails for Google

Google auth depends on more than cookies:
- **SAPISIDHASH** — computed client-side from SAPISID + origin + timestamp. Needs the full JS execution context.
- **IndexedDB** — session tokens stored in IndexedDB, not cookies
- **localStorage** — auth state cached in localStorage

`context.add_cookies()` only sets cookies — it doesn't restore localStorage/IndexedDB. The persistent context with a full profile copy restores everything.

## Why Camoufox Doesn't Work for This

Camoufox creates a fresh profile — no way to inject localStorage/IndexedDB. `launch_persistent_context` is needed, but Camoufox's patched Firefox has a version mismatch with system Firefox profiles. Playwright's bundled Firefox works if `compatibility.ini` is removed.

## cleanup

```python
ctx.close()
pw.stop()
shutil.rmtree(tmp_profile, ignore_errors=True)
```
