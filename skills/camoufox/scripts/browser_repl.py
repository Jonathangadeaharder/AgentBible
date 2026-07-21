#!/usr/bin/env python3
"""Interactive browser automation REPL — step by step, logged.

Usage:
  python scripts/browser_repl.py [--url URL] [--headless]

Commands:
  goto <url>            Navigate
  click <sel> [!force]  Click element (force=True bypasses stability check)
  clicktext <text>      Click element by visible text (bypasses selector quoting)
  type <sel> <text>     Click+type (keyboard events — may not work in Camoufox)
  press <sel> <text>    Force click + press_sequentially (try this for Angular)
  fill <sel> <text>     Fill element (clears first — works but may not trigger Angular)
  eval <js>             Evaluate JavaScript
  shot [name]           Screenshot → /tmp/repl_<name>.png
  state                 Print form state (inputs, values, data-refs)
  wait <seconds>        Wait
  find <selector>       Find element info (tag, visible, box)
  list <selector>       List all matching elements
  clean                 Remove cookie/consent/session overlays
  quit                  Exit

Log: /tmp/browser_repl.log
"""
import asyncio
import os
import sys
import json
import time
import readline  # noqa: F401

sys.path.insert(0, os.path.expanduser("~/.hermes/skills/devops/playwright-captcha/scripts"))

from camoufox.async_api import AsyncCamoufox
from camoufox import DefaultAddons

LOG_FILE = "/tmp/browser_repl.log"
SHOT_DIR = "/tmp"

BLOCK_SUBSTR = [
    "usercentrics", "uc-cdn", "consent", "cookiebot", "cookielaw",
    "onetrust", "truste", "quantcast", "web-vitals",
    "doubleclick", "google-analytics", "googletagmanager",
]


def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


async def main(headless=False, start_url=None):
    log(f"Starting Camoufox headless={headless}")
    async with AsyncCamoufox(
        headless=headless,
        humanize=True,
    ) as browser:
        ctx = await browser.new_context(viewport={"width": 1366, "height": 900})

        async def block_noise(route):
            url = route.request.url.lower()
            if any(p in url for p in BLOCK_SUBSTR):
                await route.abort()
            else:
                await route.continue_()

        await ctx.route("**/*", block_noise)
        page = await ctx.new_page()
        page.on("pageerror", lambda e: log(f"  [pageerror] {e}"))
        log("Browser ready")

        if start_url:
            log(f"Navigating to {start_url}")
            await page.goto(start_url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(3)
            log(f"Loaded: {page.url}")

        while True:
            try:
                cmd = input("\n> ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if not cmd:
                continue

            parts = cmd.split(None, 1)
            action = parts[0].lower()
            rest = parts[1] if len(parts) > 1 else ""

            try:
                if action == "quit":
                    break

                elif action == "goto":
                    await page.goto(rest, wait_until="domcontentloaded", timeout=30000)
                    await asyncio.sleep(3)
                    log(f"Loaded: {page.url}")

                elif action == "clean":
                    removed = await page.evaluate("""() => {
                        const sels = ['.cookie-popup-with-overlay','#cookie-popup-with-overlay',
                            "[class*='cookie-consent' i]","[class*='consent-banner' i]",
                            "[id*='onetrust' i]","[id*='usercentrics' i]",
                            'ry-session-expiration-popup','flights-lazy-session-expiration-popup',
                            'div.overlay'];
                        let n=0; sels.forEach(s=>document.querySelectorAll(s).forEach(e=>{e.remove();n++}));\n                        return n;
                    }""")
                    log(f"  removed {removed} cookie/consent/overlay elements")

                elif action == "clicktext":
                    text = rest.strip().strip('"').strip("'").strip()
                    log(f"clicktext '{text}'")
                    clicked = await page.evaluate(
                        """(text) => {
                            const els = document.querySelectorAll("span, button, a, div, label");
                            for (const el of els) { if (el.textContent.trim() === text) { el.click(); return true; } }
                            return false;
                        }""", text
                    )
                    log(f"  {'clicked' if clicked else 'NOT FOUND'}")
                    if clicked:
                        await asyncio.sleep(1)

                elif action == "click":
                    sel = rest
                    force = sel.endswith(" !force")
                    if force:
                        sel = sel[:-7].strip()
                    log(f"click {sel} force={force}")
                    el = await page.query_selector(sel)
                    if el:
                        await el.click(force=force)
                        await asyncio.sleep(1)
                        log("  clicked")
                    else:
                        log("  NOT FOUND")

                elif action == "press":
                    args = rest.split(None, 1)
                    sel = args[0]
                    text = args[1] if len(args) > 1 else ""
                    log(f"press {sel} '{text}'")
                    loc = page.locator(sel)
                    try:
                        await loc.click(force=True, timeout=5000)
                    except:
                        pass
                    await asyncio.sleep(0.3)
                    await page.keyboard.press("Control+a")
                    await page.keyboard.press("Backspace")
                    await asyncio.sleep(0.2)
                    try:
                        await loc.press_sequentially(text, delay=50)
                    except Exception as e:
                        log(f"  press_sequentially error: {e}")
                    await asyncio.sleep(1)
                    val = await page.evaluate(f"() => document.querySelector('{sel}')?.value")
                    log(f"  value now: '{val}'")

                elif action == "type":
                    args = rest.split(None, 1)
                    sel = args[0]
                    text = args[1] if len(args) > 1 else ""
                    log(f"type {sel} '{text}'")
                    el = await page.query_selector(sel)
                    if el:
                        await el.click(force=True)
                        await asyncio.sleep(0.3)
                        await page.keyboard.press("Control+a")
                        await page.keyboard.press("Backspace")
                        await asyncio.sleep(0.2)
                        await page.keyboard.type(text, delay=50)
                        await asyncio.sleep(1)
                        val = await el.evaluate("e => e.value")
                        log(f"  value now: '{val}'")
                    else:
                        log("  NOT FOUND")

                elif action == "fill":
                    args = rest.split(None, 1)
                    sel = args[0]
                    text = args[1] if len(args) > 1 else ""
                    log(f"fill {sel} '{text}'")
                    el = await page.query_selector(sel)
                    if el:
                        await el.fill(text)
                        await asyncio.sleep(1)
                        log("  filled")
                    else:
                        log("  NOT FOUND")

                elif action == "eval":
                    result = await page.evaluate(rest)
                    log(f"  result: {json.dumps(result, ensure_ascii=False)[:300] if result is not None else 'null'}")

                elif action == "shot":
                    name = rest if rest else "manual"
                    path = f"{SHOT_DIR}/repl_{name}.png"
                    await page.screenshot(path=path)
                    log(f"Screenshot: {path}")

                elif action == "state":
                    log(f"URL: {page.url}")
                    log(f"Title: {await page.title()}")
                    inputs = await page.query_selector_all("input, [data-ref], [role='button']")
                    log(f"  Interactive elements: {len(inputs)}")
                    for i, inp in enumerate(inputs[:20]):
                        try:
                            tag = await inp.evaluate("e => e.tagName")
                            ref = await inp.get_attribute("data-ref") or ""
                            text = (await inp.inner_text()).strip()[:50] if tag != "INPUT" else ""
                            val = await inp.get_attribute("value") or "" if tag == "INPUT" else ""
                            ph = await inp.get_attribute("placeholder") or ""
                            if ref or text or val or ph:
                                log(f"  [{i}] {tag} ref={ref} text='{text}' val='{val}' ph='{ph}'")
                        except:
                            pass

                elif action == "wait":
                    secs = float(rest) if rest else 2.0
                    log(f"wait {secs}s")
                    await asyncio.sleep(secs)

                elif action == "find":
                    sel = rest
                    el = await page.query_selector(sel)
                    if el:
                        tag = await el.evaluate("e => e.tagName")
                        text = (await el.inner_text()).strip()[:100]
                        visible = await el.is_visible()
                        box = await el.bounding_box()
                        log(f"  FOUND: {tag} visible={visible} text='{text}' box={box}")
                    else:
                        log("  NOT FOUND")

                elif action == "list":
                    sel = rest
                    els = await page.query_selector_all(sel)
                    log(f"  Found {len(els)} elements")
                    for i, el in enumerate(els[:15]):
                        try:
                            text = (await el.inner_text()).strip()[:60]
                            tag = await el.evaluate("e => e.tagName")
                            ref = await el.get_attribute("data-ref") or ""
                            log(f"  [{i}] {tag} '{text}' ref={ref}")
                        except:
                            pass

                elif action == "help":
                    log("Commands: goto click clicktext type press fill eval shot state wait find list clean quit")

                else:
                    log(f"Unknown: {action}. Type 'help'")

            except Exception as e:
                log(f"  ERROR: {e}")

    log("Browser closed")


if __name__ == "__main__":
    headless = "--headless" in sys.argv
    url = None
    for i, arg in enumerate(sys.argv):
        if arg == "--url" and i + 1 < len(sys.argv):
            url = sys.argv[i + 1]
    open(LOG_FILE, "w").close()
    asyncio.run(main(headless=headless, start_url=url))
