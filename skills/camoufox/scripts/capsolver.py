"""Capsolver API integration for solving CAPTCHAs.

Supports: reCAPTCHA v2, Cloudflare Turnstile, hCaptcha.
API key from env var CAPSOLVER_API_KEY or ~/.hermes/.env
"""

import os
import sys
import time
import requests

# Try to load from .env file
_env_path = os.path.expanduser("~/.hermes/.env")
if os.path.exists(_env_path):
    with open(_env_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("CAPSOLVER_API_KEY="):
                os.environ.setdefault("CAPSOLVER_API_KEY", line.split("=", 1)[1].strip())

CAPSOLVER_API_KEY = os.environ.get("CAPSOLVER_API_KEY", "")
if not CAPSOLVER_API_KEY:
    print("WARNING: CAPSOLVER_API_KEY not set", file=sys.stderr)


def _create_task(task: dict) -> str:
    """Create a Capsolver task, return task_id."""
    r = requests.post("https://api.capsolver.com/createTask", json={
        "clientKey": CAPSOLVER_API_KEY,
        "task": task,
    }, timeout=30)
    data = r.json()
    if data.get("errorId"):
        raise RuntimeError(f"Capsolver error: {data.get('errorDescription')}")
    return data["taskId"]


def _get_result(task_id: str, timeout: int = 180) -> dict:
    """Poll Capsolver for task result."""
    for _ in range(timeout // 3):
        time.sleep(3)
        r = requests.post("https://api.capsolver.com/getTaskResult", json={
            "clientKey": CAPSOLVER_API_KEY,
            "taskId": task_id,
        }, timeout=30)
        data = r.json()
        if data.get("errorId"):
            raise RuntimeError(f"Capsolver error: {data.get('errorDescription')}")
        if data.get("status") == "ready":
            return data["solution"]
    raise TimeoutError(f"Capsolver task {task_id} timed out")


def solve_recaptcha_v2(site_key: str, page_url: str) -> str:
    """Solve reCAPTCHA v2. Returns g-recaptcha-response token."""
    task_id = _create_task({
        "type": "ReCaptchaV2TaskProxyless",
        "websiteURL": page_url,
        "websiteKey": site_key,
    })
    solution = _get_result(task_id)
    return solution["gRecaptchaResponse"]


def solve_turnstile(site_key: str, page_url: str) -> str:
    """Solve Cloudflare Turnstile. Returns cf-turnstile-response token."""
    task_id = _create_task({
        "type": "AntiTurnstileTaskProxyless",
        "websiteURL": page_url,
        "websiteKey": site_key,
    })
    solution = _get_result(task_id)
    return solution["token"]


def solve_hcaptcha(site_key: str, page_url: str) -> str:
    """Solve hCaptcha. Returns response token."""
    task_id = _create_task({
        "type": "HCaptchaTaskProxyless",
        "websiteURL": page_url,
        "websiteKey": site_key,
    })
    solution = _get_result(task_id)
    return solution["gRecaptchaResponse"]


def solve_funcaptcha(public_key: str, page_url: str, subdomain: str = None) -> str:
    """Solve Arkose Labs FunCaptcha. Returns token.

    Args:
        public_key: Arkose public key (data-pkey or from iframe URL).
        page_url: URL of the page where captcha appears.
        subdomain: Optional subdomain for the captcha (e.g. client-api.arkoselabs.com).
    """
    task = {
        "type": "FunCaptchaTaskProxyless",
        "websiteURL": page_url,
        "websitePublicKey": public_key,
    }
    if subdomain:
        task["funcaptchaApiJSSubdomain"] = subdomain
    task_id = _create_task(task)
    solution = _get_result(task_id)
    return solution["token"]


def inject_recaptcha_token(page, token: str):
    """Inject reCAPTCHA v2 token into page and submit."""
    page.evaluate(f"""
        () => {{
            const el = document.getElementById('g-recaptcha-response') ||
                       document.querySelector('textarea[name="g-recaptcha-response"]');
            if (el) {{
                el.style.display = 'block';
                el.innerHTML = '{token}';
                el.value = '{token}';
            }}
        }}
    """)


def inject_turnstile_token(page, token: str):
    """Inject Cloudflare Turnstile token."""
    page.evaluate(f"""
        () => {{
            const el = document.querySelector('[name="cf-turnstile-response"]') ||
                       document.querySelector('input[name="cf-turnstile-response"]');
            if (el) el.value = '{token}';
        }}
    """)
