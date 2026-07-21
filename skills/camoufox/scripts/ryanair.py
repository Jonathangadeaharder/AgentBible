"""Ryanair booking automation — abstracted from actor-checker validated sequence.

All subroutines proven via actor-checker loop (Gemma 4 31B + vision).
Each function = one validated step. Compose into full booking flow.

Usage:
  from ryanair import book
  await book("Spanien", "Valencia", "Deutschland", "Berlin Brandenburg", "25",
            "<FULL_NAME>", "<LAST_NAME>", "<EMAIL>", headless=True)
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.expanduser("~/.hermes/skills/devops/playwright-captcha/scripts"))
from camoufox.async_api import AsyncCamoufox

BLOCK = [
    "usercentrics", "uc-cdn", "consent", "cookiebot", "cookielaw",
    "onetrust", "truste", "quantcast", "web-vitals",
]

PATCH_ANGULAR_FORM = """
() => {
    const inputs = document.querySelectorAll('input[name*="passengers"], input[type="email"]');
    inputs.forEach(input => {
        input.dispatchEvent(new Event('input', {bubbles: true}));
        input.dispatchEvent(new Event('change', {bubbles: true}));
        input.dispatchEvent(new Event('blur', {bubbles: true}));
        const ngKey = Object.keys(input).find(k => k.startsWith('__ngContext__'));
        if (ngKey) {
            const ctx = input[ngKey];
            if (ctx && ctx.control) {
                ctx.control.markAsDirty();
                ctx.control.markAsTouched();
                ctx.control.updateValueAndValidity();
            }
        }
    });
    document.querySelectorAll('form').forEach(form => {
        const ngForm = Object.keys(form).find(k => k.startsWith('__ngContext__'));
        if (ngForm) {
            const ctx = form[ngForm];
            if (ctx && ctx.control) {
                ctx.control.markAsDirty();
                ctx.control.updateValueAndValidity();
            }
        }
    });
    return 'patched';
}
"""


async def clean(page):
    """Remove cookie popups + session expiration + generic overlays."""
    await page.evaluate("""() => {
        const selectors = [
            ".cookie-popup-with-overlay", "#cookie-popup-with-overlay",
            "[class*='cookie-consent' i]", "[class*='consent-banner' i]",
            "ry-session-expiration-popup", "flights-lazy-session-expiration-popup",
        ];
        let count = 0;
        for (const sel of selectors) {
            document.querySelectorAll(sel).forEach(e => { e.remove(); count++; });
        }
        document.querySelectorAll('div.overlay').forEach(e => e.remove());
        return count;
    }""")
    await asyncio.sleep(1)


async def clicktext(page, text):
    """Click element by visible text. Uses arg passing — no JS injection."""
    await page.evaluate(
        """(text) => {
            const els = document.querySelectorAll("span, button, a, div, label");
            for (const el of els) { if (el.textContent.trim() === text) { el.click(); return true; } }
            return false;
        }""",
        text
    )
    await asyncio.sleep(1)


async def select_airport(page, field_index, country, airport):
    """Open airport picker, select country, select airport."""
    await page.evaluate(
        f"() => document.querySelectorAll('[data-ref=\"input-button__display-value\"]')[{field_index}].click()"
    )
    await asyncio.sleep(2)
    await clicktext(page, country)
    await asyncio.sleep(2)
    await page.evaluate(
        """(airport) => Array.from(document.querySelectorAll('[data-ref="airport-item__name"]')).find(e => e.textContent.trim() === airport).click()""",
        airport
    )
    await asyncio.sleep(1)


async def select_date(page, day):
    """Open calendar and select a day."""
    await page.evaluate("() => document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape', bubbles: true}))")
    await asyncio.sleep(1)
    await clean(page)
    await page.evaluate(
        """() => document.querySelector('[data-ref="input-button__dates-from"]').dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}))"""
    )
    await asyncio.sleep(2)
    cell_count = await page.evaluate("() => document.querySelectorAll('div.calendar-body__cell').length")
    if cell_count == 0:
        await clean(page)
        await page.evaluate(
            """() => document.querySelector('[data-ref="input-button__dates-from"]').dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}))"""
        )
        await asyncio.sleep(2)
    await page.evaluate(
        f"""() => {{
            const cells = Array.from(document.querySelectorAll('div.calendar-body__cell'))
                .filter(e => e.textContent.trim() === '{day}' && !e.className.includes('disabled'));
            if (cells.length > 0) {{ cells[0].dispatchEvent(new MouseEvent('click', {{bubbles: true, cancelable: true}})); return true; }}
            return false;
        }}"""
    )
    await asyncio.sleep(1)


async def search_flights(page):
    """Clean + click search button."""
    await clean(page)
    btn = await page.query_selector('[data-ref="flight-search-widget__cta"]')
    await btn.click(force=True)
    await asyncio.sleep(12)


async def select_flight(page):
    """Wait for flight cards + click first 'Auswählen' button."""
    for attempt in range(10):
        count = await page.evaluate("() => document.querySelectorAll('flight-card-new').length")
        if count > 0:
            break
        await asyncio.sleep(3)
    await page.evaluate(
        """() => {
            const btn = document.querySelector('flight-card-new button.flight-card-summary__select-btn');
            if (btn) { btn.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true})); return true; }
            return false;
        }"""
    )
    await asyncio.sleep(3)


async def select_basic_fare(page):
    """Clean + remove overlays + click Basic fare button."""
    await clean(page)
    await page.evaluate("() => { document.querySelector('ry-session-expiration-popup')?.remove(); document.querySelector('div.overlay')?.remove(); }")
    await asyncio.sleep(0.5)
    await page.evaluate(
        """() => Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Basic')).dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}))"""
    )
    await asyncio.sleep(3)
    await page.evaluate("() => { document.querySelector('div.overlay')?.remove(); document.querySelector('.modal-container')?.remove(); }")
    await asyncio.sleep(1)
    await page.evaluate(
        """() => Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Basic')).dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}))"""
    )
    await asyncio.sleep(3)


async def fill_passenger(page, first_name, last_name, email):
    """Fill passenger form fields + patch Angular validation."""
    await clean(page)
    await page.evaluate("() => { document.querySelector('ry-session-expiration-popup')?.remove(); document.querySelector('div.overlay')?.remove(); }")
    
    name_input = await page.query_selector('input[name="form.passengers.ADT-0.name"]')
    if name_input:
        await name_input.fill(first_name)
    
    surname_input = await page.query_selector('input[name="form.passengers.ADT-0.surname"]')
    if surname_input:
        await surname_input.fill(last_name)
    
    email_input = await page.query_selector('input[type="email"]')
    if email_input:
        await email_input.fill(email)
    
    await page.evaluate(PATCH_ANGULAR_FORM)


async def bypass_login(page):
    """Dismiss Ryanair login prompt by clicking 'Später einloggen'."""
    await asyncio.sleep(2)
    await clean(page)
    await clicktext(page, "Später einlognen")
    await asyncio.sleep(2)


async def click_continue(page):
    """Remove overlays + click Fortsetzen button."""
    await clean(page)
    await page.evaluate("() => { document.querySelector('ry-session-expiration-popup')?.remove(); document.querySelector('div.overlay')?.remove(); }")
    await asyncio.sleep(0.5)
    btn = await page.query_selector('.continue-flow__button')
    if btn:
        await btn.click(force=True)
        await asyncio.sleep(3)


async def book(
    origin_country="Spanien", origin_airport="Valencia",
    dest_country="Deutschland", dest_airport="Berlin Brandenburg",
    day="25", first_name="<FULL_NAME>", last_name="<LAST_NAME>",
    email="<EMAIL>", headless=True,
):
    """Full Ryanair booking flow — one-way, 1 adult, Basic fare.
    Stops before payment — user verifies + pays manually."""
    async with AsyncCamoufox(headless=headless, humanize=True) as browser:
        page = await browser.new_page()
        page.on("pageerror", lambda e: None)

        async def handler(route):
            url = route.request.url
            if any(p in url.lower() for p in BLOCK):
                await route.abort()
            else:
                await route.continue_()
        await page.route("**/*", handler)

        print("1. Load Ryanair", flush=True)
        await page.goto("https://www.ryanair.com/de/de", wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(5)

        print("2. One-way", flush=True)
        await clean(page)
        await clicktext(page, "Nur Hinflug")

        print(f"3. Origin: {origin_airport}", flush=True)
        el = await page.query_selector('[data-ref="input-button__display-value"]')
        await el.click(force=True)
        await asyncio.sleep(2)
        await clicktext(page, origin_country)
        await asyncio.sleep(2)
        await page.evaluate(
            """(airport) => Array.from(document.querySelectorAll('[data-ref="airport-item__name"]')).find(e => e.textContent.trim() === airport).click()""",
            origin_airport
        )
        await asyncio.sleep(1)

        print(f"4. Destination: {dest_airport}", flush=True)
        await select_airport(page, 1, dest_country, dest_airport)

        print(f"5. Date: Jul {day}", flush=True)
        await select_date(page, day)

        print("6. Search", flush=True)
        await search_flights(page)

        print("7. Select flight", flush=True)
        await select_flight(page)

        print("8. Basic fare", flush=True)
        await select_basic_fare(page)

        print(f"9. Passenger: {first_name} {last_name}", flush=True)
        await fill_passenger(page, first_name, last_name, email)

        print("10. Bypass login", flush=True)
        await bypass_login(page)

        print("11. Continue", flush=True)
        await click_continue(page)

        print("\n=== PAUSE — verify and pay ===", flush=True)
        print(f"URL: {page.url}", flush=True)
        await page.screenshot(path="probes/ryanair_before_payment.png")
        await asyncio.sleep(600)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--gui", action="store_true")
    args = parser.parse_args()
    asyncio.run(book(headless=not args.gui))
