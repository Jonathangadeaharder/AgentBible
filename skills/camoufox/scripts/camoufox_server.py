#!/usr/bin/env python3
"""Camoufox persistent server with unix socket control.

Architecture: Main thread owns Playwright (greenlet constraint).
Socket handlers enqueue commands, main thread executes them.

Usage:
  python3 camoufox_server.py  # starts server, listens on /tmp/camoufox_cli.sock

Commands (via JSON over unix socket):
  goto <url>, click <text>, type <selector> <text>, body [length],
  url, screenshot [path], eval <js>, wait [seconds], stop, ping
"""
import os, json, time, threading, queue, sys
import socketserver
from camoufox.sync_api import Camoufox

PROFILE_DIR = os.path.expanduser("~/.hermes/camoufox_profiles/persistent")
SOCK = "/tmp/camoufox_cli.sock"
UBO_ADDON = os.path.expanduser("~/.hermes/camoufox_profiles/addons/uBlock0")

browser = None
page = None
_cmd_queue = queue.Queue()
_response_queue = queue.Queue()

def get_browser():
    global browser, page
    if browser is None:
        addons = []
        if os.path.exists(UBO_ADDON):
            addons = [UBO_ADDON]
        print(f"Launching Camoufox: addons={addons}, profile={PROFILE_DIR}", flush=True)
        browser = Camoufox(
            headless=False,
            humanize=True,
            geoip=False,
            persistent_context=True,
            user_data_dir=PROFILE_DIR,
            addons=addons,
        ).__enter__()
        page = browser.new_page()
        print("Browser ready", flush=True)
    return browser, page

def execute_cmd(cmd, args):
    b, p = get_browser()
    if cmd == "goto":
        p.goto(args[0], timeout=60000)
        try:
            p.wait_for_load_state("networkidle", timeout=15000)
        except:
            pass
        time.sleep(2)
        return {"url": p.url, "title": p.title()}
    elif cmd == "click":
        text = args[0].replace("'", "\\'")
        clicked = p.evaluate(f"""() => {{
            const els = document.querySelectorAll('a, button, input[type="submit"], [role="button"]');
            for (const el of els) {{
                if (el.textContent.trim() === '{text}' || el.textContent.includes('{text}')) {{
                    el.click(); return true;
                }}
            }}
            return false;
        }}""")
        time.sleep(2)
        return {"url": p.url, "clicked": clicked}
    elif cmd == "click_selector":
        p.click(args[0], timeout=10000)
        time.sleep(2)
        return {"url": p.url, "clicked": True}
    elif cmd == "type":
        p.locator(args[0]).first.fill(args[1])
        return {"filled": True}
    elif cmd == "body":
        length = int(args[0]) if args else 5000
        return {"body": p.inner_text("body")[:length]}
    elif cmd == "url":
        return {"url": p.url, "title": p.title()}
    elif cmd == "screenshot":
        path = args[0] if args else "/tmp/camoufox_screenshot.png"
        p.screenshot(path=path)
        return {"path": path}
    elif cmd == "eval":
        result = p.evaluate(args[0])
        return {"result": result}
    elif cmd == "wait":
        time.sleep(float(args[0]) if args else 5)
        return {"url": p.url}
    elif cmd == "stop":
        try:
            b.close()
        except:
            pass
        try:
            os.unlink(SOCK)
        except:
            pass
        os._exit(0)
    elif cmd == "ping":
        return {"pong": True, "url": p.url}
    return {"error": f"Unknown command: {cmd}"}

class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        data = b""
        while b"\n" not in data:
            chunk = self.request.recv(65536)
            if not chunk:
                return
            data += chunk
        line = data.strip()
        if not line:
            return
        try:
            msg = json.loads(line)
            cmd = msg.get("cmd", "")
            args = msg.get("args", [])
            _cmd_queue.put((cmd, args, threading.Event()))
            result = _response_queue.get(timeout=120)
        except Exception as e:
            result = {"error": str(e)}
        try:
            self.request.sendall(json.dumps(result).encode() + b"\n")
        except:
            pass

class ThreadedUnixServer(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True
    allow_reuse_address = True

def main_loop():
    get_browser()
    print(f"Server listening on {SOCK}", flush=True)
    server = ThreadedUnixServer(SOCK, Handler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    while True:
        cmd, args, event = _cmd_queue.get()
        try:
            result = execute_cmd(cmd, args)
        except Exception as e:
            result = {"error": str(e)}
        _response_queue.put(result)

if __name__ == "__main__":
    if os.path.exists(SOCK):
        os.unlink(SOCK)
    main_loop()
