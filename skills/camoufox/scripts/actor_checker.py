"""Actor-Checker browser automation with LM Studio (Gemma 4 31B).

Actor: proposes one REPL command based on current goal + screenshot + state.
Checker: verifies if the action had the intended consequence.
Only proceeds after checker confirms.

Usage:
  python scripts/actor_checker.py --url "https://www.ryanair.com/de/de" \
    --goal "Book one-way flight VLC->BER Jul 25, 1 adult, Basic fare, fill passenger details"
"""
import asyncio
import base64
import json
import os
import sys
import time
import subprocess

sys.path.insert(0, os.path.expanduser("~/.hermes/skills/devops/playwright-captcha/scripts"))

from camoufox.async_api import AsyncCamoufox
from camoufox import DefaultAddons
from curl_cffi import requests as cffi_requests

LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
MODEL = "gemma-4-31b-it-qat"
SHOT_DIR = "/tmp/actor_checker"
LOG_FILE = "/tmp/actor_checker.log"

os.makedirs(SHOT_DIR, exist_ok=True)
_log = open(LOG_FILE, "w")


def log(msg):
    msg = str(msg).replace('\x00', '').replace('\r', '')
    msg = ''.join(c for c in msg if c.isprintable() or c in '\n\t')
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    _log.write(line + "\n")
    _log.flush()


def screenshot_b64(path):
    small_path = path.replace(".png", "_small.png")
    try:
        subprocess.run(["sips", "-z", "600", "800", path, "--out", small_path],
                      capture_output=True, timeout=5)
        path = small_path
    except:
        pass
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def get_state_json(page):
    return page.evaluate("""() => ({
        url: location.href,
        title: document.title,
        inputs: Array.from(document.querySelectorAll('input')).filter(i => i.offsetParent !== null).map(i => ({
            type: i.type, name: i.name || '', value: (i.value || '').slice(0, 50),
            placeholder: i.placeholder || '', checked: i.checked, disabled: i.disabled
        })),
        buttons: Array.from(document.querySelectorAll('button')).filter(b => b.offsetParent !== null && b.textContent.trim().length > 0).map(b => ({
            text: b.textContent.trim().slice(0, 60), disabled: b.disabled,
            cls: b.className.slice(0, 40)
        })).slice(0, 20),
        visibleText: document.body.innerText.slice(0, 500)
    })""")


def call_lm_studio(messages, temperature=0.3, max_tokens=500):
    r = cffi_requests.post(LM_STUDIO_URL, json={
        "model": MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }, timeout=120)
    r.raise_for_status()
    data = r.json()
    msg = data["choices"][0]["message"]
    content = msg.get("content", "").strip()
    if not content and msg.get("reasoning_content"):
        content = msg["reasoning_content"].strip()
    return content


def actor_step(goal, state_json, screenshot_path, history, sys_prompt):
    user_msg = f"""Goal: {goal}

Current page state:
{json.dumps(state_json, indent=2)[:2000]}

Previous actions and results:
{chr(10).join(history[-10:])}

What is the NEXT single command to execute? Output ONLY the command."""
    screenshot_b64_data = screenshot_b64(screenshot_path)
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": [
            {"type": "text", "text": user_msg},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot_b64_data}"}}
        ]}
    ]
    try:
        return call_lm_studio(messages, temperature=0.3, max_tokens=500)
    except Exception as e:
        log(f"Actor error: {e}")
        try:
            text_only = [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_msg}]
            return call_lm_studio(text_only, temperature=0.3, max_tokens=500)
        except Exception as e2:
            log(f"Actor fallback error: {e2}")
            return None


def checker_step(goal, action, state_before, state_after, screenshot_path):
    sys_msg = """You are a browser automation checker. Verify if an action achieved its goal.
Respond with ONLY: SUCCESS: <reason> | FAIL: <reason> | PARTIAL: <reason>"""
    user_msg = f"""Goal: {goal}
Action: {action}
BEFORE: {json.dumps(state_before, indent=2)[:1000]}
AFTER: {json.dumps(state_after, indent=2)[:1000]}"""
    screenshot_b64_data = screenshot_b64(screenshot_path)
    messages = [
        {"role": "system", "content": sys_msg},
        {"role": "user", "content": [
            {"type": "text", "text": user_msg},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot_b64_data}"}}
        ]}
    ]
    try:
        return call_lm_studio(messages, temperature=0.1, max_tokens=100)
    except Exception as e:
        log(f"Checker error: {e}")
        return "FAIL: checker error"


BLOCK = ["usercentrics", "uc-cdn", "consent", "cookiebot", "cookielaw", "onetrust",
         "truste", "quantcast", "web-vitals", "doubleclick", "google-analytics",
         "googletagmanager"]


async def execute_command(page, cmd):
    parts = cmd.split(None, 1)
    action = parts[0].lower()
    rest = parts[1] if len(parts) > 1 else ""
    output = []
    try:
        if action == "clean":
            removed = await page.evaluate("""() => {
                const sels = ['.cookie-popup-with-overlay','#cookie-popup-with-overlay',
                    "[class*='cookie-consent' i]","[class*='consent-banner' i]",
                    "[id*='onetrust' i]","[id*='usercentrics' i]",
                    'ry-session-expiration-popup','flights-lazy-session-expiration-popup','div.overlay'];
                let n=0; sels.forEach(s=>document.querySelectorAll(s).forEach(e=>{e.remove();n++})); return n;
            }""")
            output.append(f"removed {removed} elements")
        elif action == "clicktext":
            text = rest.strip().strip('"').strip("'").strip()
            await page.evaluate("""(text) => {
                const els = document.querySelectorAll("span, button, a, div, label");
                for (const el of els) { if (el.textContent.trim() === text) { el.click(); return true; } } return false;
            }""", text)
            await asyncio.sleep(1)
            output.append(f"clicked '{text}'")
        elif action == "click":
            sel = rest
            force = sel.endswith(" !force")
            if force: sel = sel[:-7].strip()
            el = await page.query_selector(sel)
            if el:
                await el.click(force=force)
                await asyncio.sleep(1)
                output.append("clicked")
            else:
                output.append("NOT FOUND")
        elif action == "fill":
            args = rest.split(None, 1)
            el = await page.query_selector(args[0])
            if el:
                await el.fill(args[1] if len(args) > 1 else "")
                await asyncio.sleep(1)
                output.append("filled")
            else: output.append("NOT FOUND")
        elif action == "press":
            args = rest.split(None, 1)
            sel = args[0]; text = args[1] if len(args) > 1 else ""
            loc = page.locator(sel)
            try: await loc.click(force=True, timeout=5000)
            except: pass
            await asyncio.sleep(0.3)
            await page.keyboard.press("Control+a")
            await page.keyboard.press("Backspace")
            await asyncio.sleep(0.2)
            try: await loc.press_sequentially(text, delay=50)
            except Exception as e: output.append(f"press error: {e}")
            await asyncio.sleep(1)
            val = await page.evaluate(f"() => document.querySelector('{sel}')?.value")
            output.append(f"value: '{val}'")
        elif action == "eval":
            result = await page.evaluate(rest)
            output.append(f"result: {json.dumps(result, ensure_ascii=False)[:300] if result is not None else 'null'}")
        elif action == "wait":
            await asyncio.sleep(float(rest) if rest else 2.0)
            output.append("waited")
        elif action == "shot":
            name = rest if rest else "manual"
            await page.screenshot(path=f"{SHOT_DIR}/ac_{name}.png")
            output.append("saved")
        else:
            output.append(f"Unknown: {action}")
    except Exception as e:
        output.append(f"ERROR: {e}")
    return "\n".join(output)


async def main(url, goal, sys_prompt, max_steps=30):
    log(f"Starting actor-checker | Model: {MODEL}")
    async with AsyncCamoufox(headless=False, humanize=True) as browser:
        page = await browser.new_page()
        page.on("pageerror", lambda e: None)
        async def handler(route):
            if any(p in route.request.url.lower() for p in BLOCK):
                await route.abort()
            else:
                await route.continue_()
        await page.route("**/*", handler)
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(5)
        log(f"Loaded: {page.url}")

        history = []
        for step in range(max_steps):
            log(f"\n{'='*60}\nSTEP {step+1}/{max_steps}")
            screenshot_path = f"{SHOT_DIR}/step_{step+1}.png"
            await page.screenshot(path=screenshot_path)
            state = await get_state_json(page)
            log(f"State: url={state['url'][:60]} inputs={len(state['inputs'])} buttons={len(state['buttons'])}")

            log("Actor thinking...")
            cmd = actor_step(goal, state, screenshot_path, history, sys_prompt)
            if not cmd:
                log("Actor failed, skipping")
                continue
            cmd = cmd.strip().strip('`').strip()
            lines = [l.strip() for l in cmd.split('\n') if l.strip()]
            cmd_words = ['clean','clicktext','click','type','press','fill','eval','shot','wait','find','list','state','quit']
            cmd_lines = [l for l in lines if any(l.lower().startswith(w + ' ') or l.lower() == w for w in cmd_words)]
            cmd = cmd_lines[-1] if cmd_lines else (lines[-1] if lines else cmd)
            cmd = cmd.strip('`').strip()
            log(f"Actor command: {cmd}")
            if cmd.lower() in ('quit', 'done', 'finished'):
                log("Actor says done!")
                break

            state_before = state
            output = await execute_command(page, cmd)
            log(f"Output: {output}")
            await asyncio.sleep(2)
            screenshot_after = f"{SHOT_DIR}/step_{step+1}_after.png"
            await page.screenshot(path=screenshot_after)
            state_after = await get_state_json(page)
            history.append(f"Step {step+1}: {cmd} → {output}")

            log("Checker verifying...")
            verdict = checker_step(goal, cmd, state_before, state_after, screenshot_after)
            log(f"Checker: {verdict}")
            history.append(f"  Checker: {verdict}")

        log("\n=== AUTOMATION COMPLETE ===")
    _log.close()


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--url", required=True)
    p.add_argument("--goal", required=True)
    p.add_argument("--steps", type=int, default=30)
    p.add_argument("--sys-prompt-file", help="File with custom system prompt for actor")
    args = p.parse_args()
    sys_prompt = """You are a browser automation actor. Output ONLY one REPL command.
Commands: clean, clicktext <text>, click <sel> [!force], fill <sel> <text>, press <sel> <text>, eval <js>, wait <sec>, quit"""
    if args.sys_prompt_file:
        with open(args.sys_prompt_file) as f:
            sys_prompt = f.read()
    asyncio.run(main(args.url, args.goal, sys_prompt, args.steps))
