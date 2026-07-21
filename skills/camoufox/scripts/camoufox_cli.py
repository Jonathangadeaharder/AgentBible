#!/usr/bin/env python3
"""Interactive Camoufox CLI — sends commands to camoufox_server.py.

Usage:
  python3 camoufox_cli.py start   — launch server (background)
  python3 camoufox_cli.py goto <url>
  python3 camoufox_cli.py click <text>
  python3 camoufox_cli.py type <selector> <text>
  python3 camoufox_cli.py body [length]
  python3 camoufox_cli.py url
  python3 camoufox_cli.py screenshot [path]
  python3 camoufox_cli.py eval <js>
  python3 camoufox_cli.py wait [seconds]
  python3 camoufox_cli.py ping
  python3 camoufox_cli.py interact    — REPL mode
  python3 camoufox_cli.py stop

Socket: /tmp/camoufox_cli.sock
Profile: ~/.hermes/camoufox_profiles/persistent/
"""
import sys, os, json, time, socket, subprocess

SOCK = "/tmp/camoufox_cli.sock"
LAUNCHER = os.path.expanduser("~/.hermes/scripts/camoufox_server.py")

def send_cmd(cmd, *args):
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(120)
        s.connect(SOCK)
        msg = json.dumps({"cmd": cmd, "args": args})
        s.sendall(msg.encode() + b"\n")
        resp = b""
        while True:
            chunk = s.recv(65536)
            if not chunk:
                break
            resp += chunk
        s.close()
        return resp.decode()
    except (ConnectionRefusedError, FileNotFoundError):
        return json.dumps({"error": "Server not running. Start with 'start'."})

def start_server():
    proc = subprocess.Popen(
        [sys.executable, LAUNCHER],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env={**os.environ, "PYTHONPATH": ""}
    )
    for _ in range(30):
        if os.path.exists(SOCK):
            print(f"Server started (PID {proc.pid})")
            return
        time.sleep(1)
    print("Server failed to start")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "start":
        start_server()
    elif cmd == "stop":
        print(send_cmd("stop"))
    elif cmd == "goto":
        print(send_cmd("goto", sys.argv[2]))
    elif cmd == "click":
        print(send_cmd("click", sys.argv[2]))
    elif cmd == "type":
        print(send_cmd("type", sys.argv[2], sys.argv[3]))
    elif cmd == "body":
        length = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
        print(send_cmd("body", str(length)))
    elif cmd == "url":
        print(send_cmd("url"))
    elif cmd == "screenshot":
        path = sys.argv[2] if len(sys.argv) > 2 else "/tmp/camoufox_screenshot.png"
        print(send_cmd("screenshot", path))
    elif cmd == "eval":
        print(send_cmd("eval", sys.argv[2]))
    elif cmd == "wait":
        print(send_cmd("wait", sys.argv[2] if len(sys.argv) > 2 else "5"))
    elif cmd == "ping":
        print(send_cmd("ping"))
    elif cmd == "interact":
        print("Interactive mode. Commands: goto, click, type, body, url, screenshot, eval, wait, quit")
        while True:
            try:
                line = input("camoufox> ").strip()
                if not line:
                    continue
                if line == "quit":
                    break
                parts = line.split(" ", 1)
                subcmd = parts[0]
                subargs = parts[1] if len(parts) > 1 else ""
                if subcmd == "goto":
                    print(send_cmd("goto", subargs))
                elif subcmd == "click":
                    print(send_cmd("click", subargs))
                elif subcmd == "type":
                    sel, val = subargs.split(" ", 1)
                    print(send_cmd("type", sel, val))
                elif subcmd == "body":
                    print(send_cmd("body", subargs or "5000"))
                elif subcmd == "url":
                    print(send_cmd("url"))
                elif subcmd == "screenshot":
                    print(send_cmd("screenshot", subargs or "/tmp/camoufox_screenshot.png"))
                elif subcmd == "eval":
                    print(send_cmd("eval", subargs))
                elif subcmd == "wait":
                    print(send_cmd("wait", subargs or "5"))
                elif subcmd == "ping":
                    print(send_cmd("ping"))
                else:
                    print("Unknown:", subcmd)
            except EOFError:
                break
            except KeyboardInterrupt:
                print()
                break
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)

if __name__ == "__main__":
    main()
