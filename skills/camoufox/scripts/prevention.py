"""Camoufox browser context creation for CAPTCHA prevention.

DEFAULT and SOLE engine: Camoufox (patched Firefox, engine-level spoofing).
Bypasses Cloudflare Turnstile without any external solver.

Key design:
- exclude_addons=[DefaultAddons.UBO] — simpler than patching coreBundle.js.
  Route interception covers cookie consent blocking (uBO's default filter
  lists don't include easylist_cookies/adguard_cookies anyway).
- Route interception blocks usercentrics/consent/cookiebot/onetrust scripts.
- page.on("pageerror", lambda e: None) suppresses stray JS errors.
- type() not fill() for React-controlled forms.
"""
import random
import time
import os
import shutil
import sqlite3
import tempfile

FIREFOX_PROFILE = os.path.expanduser(
    "~/Library/Application Support/Firefox/Profiles/<FF_PROFILE>"
)

BLOCK_PATTERNS = [
    "usercentrics", "uc-cdn", "consent", "cookiebot", "cookielaw",
    "onetrust", "truste", "quantcast", "web-vitals",
]


def extract_firefox_cookies(domain: str = "rewe") -> list[dict]:
    """Extract cookies from Firefox profile for given domain."""
    cookies_db = os.path.join(FIREFOX_PROFILE, "cookies.sqlite")
    tmp = tempfile.mktemp(suffix=".sqlite")
    shutil.copy2(cookies_db, tmp)
    conn = sqlite3.connect(tmp)
    ss_map = {0: "None", 1: "Lax", 2: "Strict", 3: "None"}
    rows = conn.execute(
        "SELECT host, name, value, path, isSecure, isHttpOnly, sameSite, expiry "
        "FROM moz_cookies WHERE host LIKE ?",
        (f"%{domain}%",),
    ).fetchall()
    conn.close()
    os.unlink(tmp)
    return [{"name": n, "value": v, "domain": h, "path": p,
             "secure": s == 1, "httpOnly": h2 == 1,
             "sameSite": ss_map.get(ss, "None"),
             **({"expires": exp / 1_000_000} if exp and exp > 0 else {})}
            for h, n, v, p, s, h2, ss, exp in rows if v]


def create_browser(domain=None, cookies=None, proxy=None):
    """Create a Camoufox browser with route interception.

    Args:
        domain: extract cookies for this domain from Firefox profile
        cookies: pre-extracted cookie list (overrides domain)
        proxy: optional proxy config

    Returns:
        (browser, context, page)
    """
    from camoufox.sync_api import Camoufox
    from camoufox.addons import DefaultAddons

    browser = Camoufox(
        headless=True,
        locale="de-DE",
        exclude_addons=[DefaultAddons.UBO],
        proxy=proxy,
    ).__enter__()

    ctx = browser.new_context(
        viewport={"width": random.randint(1366, 1920),
                  "height": random.randint(768, 1080)},
    )

    def block_noise(route):
        url = route.request.url.lower()
        if any(p in url for p in BLOCK_PATTERNS):
            route.abort()
        else:
            route.continue_()

    ctx.route("**/*", block_noise)

    if cookies:
        ctx.add_cookies(cookies)
    elif domain:
        ctx.add_cookies(extract_firefox_cookies(domain))

    page = ctx.new_page()
    page.on("pageerror", lambda e: None)
    return browser, ctx, page


def apply_human_behavior(page, duration: float = 3.0):
    """Apply human-like mouse movements and scrolling."""
    for _ in range(random.randint(2, 4)):
        page.mouse.move(
            random.randint(100, 1400),
            random.randint(100, 900),
            steps=random.randint(10, 25)
        )
        time.sleep(random.uniform(0.1, 0.4))

    page.mouse.wheel(0, random.randint(100, 500))
    time.sleep(random.uniform(0.3, 0.8))


def human_delay():
    time.sleep(random.uniform(0.5, 2.0))


def human_type(page, selector, text):
    """Type character by character — triggers React state (fill() doesn't)."""
    page.click(selector)
    time.sleep(0.3)
    page.type(selector, text, delay=random.randint(50, 150))
    human_delay()


def detect_captcha(page) -> str | None:
    """Returns captcha type if detected, else None."""
    html = page.content()
    url = page.url
    if "challenges.cloudflare.com" in url or "turnstile" in html.lower() or "cf-turnstile" in html:
        return "turnstile"
    if "recaptcha" in html.lower() or "g-recaptcha" in html:
        return "recaptcha_v2"
    if "hcaptcha" in html.lower():
        return "hcaptcha"
    if "zeig uns, dass du ein mensch bist" in html.lower() or "robot" in html.lower():
        return "turnstile"
    return None


def get_site_key(page) -> str | None:
    """Extract Turnstile/reCAPTCHA site key from page."""
    return page.evaluate("""
        () => {
            const el = document.querySelector('[data-sitekey]');
            return el ? el.getAttribute('data-sitekey') : null;
        }
    """)
