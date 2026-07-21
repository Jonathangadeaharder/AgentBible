"""Combined CAPTCHA prevention → detection → solving flow.

Uses Camoufox (patched Firefox) as the sole browser engine.
Route interception blocks cookie consent banners.
Capsolver API as fallback when prevention fails.
"""
import os
import sys
import time
import random

# Import from sibling module
from prevention import (
    create_browser, apply_human_behavior,
    detect_captcha, get_site_key,
)
from capsolver import solve_turnstile, solve_recaptcha_v2, solve_hcaptcha


def navigate_with_captcha_handling(url: str, cookies: list = None, domain: str = None):
    """Navigate to URL. Camoufox prevention first, Capsolver fallback.

    Args:
        url: target URL
        cookies: pre-extracted cookie list
        domain: extract cookies for this domain (overrides cookies)

    Returns:
        (page, context, browser)
    """
    browser, context, page = create_browser(domain=domain, cookies=cookies)

    # Step 1: Navigate with prevention
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    time.sleep(random.uniform(6, 10))

    apply_human_behavior(page)

    # Step 2: Check if still blocked
    captcha_type = detect_captcha(page)
    if not captcha_type:
        return page, context, browser  # Success — no captcha

    print(f"CAPTCHA detected: {captcha_type}", file=sys.stderr)

    # Step 3: Solve via Capsolver
    site_key = get_site_key(page)
    if not site_key:
        print("No sitekey found", file=sys.stderr)
        return page, context, browser

    if captcha_type == "turnstile":
        token = solve_turnstile(site_key, page.url)
        page.evaluate(f"""
            document.querySelector('[name=cf-turnstile-response]').value = '{token}';
            document.querySelector('form').submit();
        """)
    elif captcha_type == "recaptcha_v2":
        token = solve_recaptcha_v2(site_key, page.url)
        page.evaluate(f"""
            document.getElementById('g-recaptcha-response').innerHTML = '{token}';
            document.querySelector('form').submit();
        """)
    elif captcha_type == "hcaptcha":
        token = solve_hcaptcha(site_key, page.url)
        page.evaluate(f"""
            document.querySelector('[name=h-captcha-response]').value = '{token}';
            document.querySelector('form').submit();
        """)

    page.wait_for_timeout(5000)
    return page, context, browser
