# Camoufox Headless/Headed Mode Setup

## Overview
Camoufox supports both headless and headed (GUI) modes. The mode is determined at server startup and cannot be changed without restarting the server.

## Mode Selection

### Headed Mode (Default)
```bash
camoufox start
```
- Full Firefox UI visible
- Better for debugging, visual verification
- Required for some Cloudflare challenges
- Default when no flags/env vars specified

### Headless Mode
```bash
# Option 1: CLI flag
camoufox start --headless

# Option 2: Environment variable
CAMOUFOX_HEADLESS=1 camoufox start

# Option 3: Explicit env unset (forces headed)
CAMOUFOX_HEADLESS=0 camoufox start
```

## Implementation Details

### Server (`camoufox_server.py`)
```python
HEADLESS = os.environ.get("CAMOUFOX_HEADLESS", "0") == "1"

browser = Camoufox(
    headless=HEADLESS,  # respects env var
    humanize=True,
    geoip=False,
    persistent_context=True,
    user_data_dir=PROFILE_DIR,
)
```

### CLI (`camoufox_cli.py`)
```python
if action == "start":
    headless = "--headless" in sys.argv
    if headless:
        os.environ["CAMOUFOX_HEADLESS"] = "1"
    else:
        os.environ.pop("CAMOUFOX_HEADLESS", None)
    # ... rest of start logic
```

## When to Use Which Mode

| Scenario | Recommended Mode | Reason |
|----------|------------------|--------|
| CI/CD pipelines | Headless | No display server, faster |
| Cloudflare Turnstile | Headed | Cloudflare detects headless fingerprint |
| Debugging | Headed | Visual inspection of page state |
| Long-running sessions | Headed | Less likely to be flagged as bot |
| Screenshot-heavy tasks | Headed | Accurate rendering |
| Background automation | Headless | Resource efficient |

## Known Issues

### Headless Mode Detection
- Cloudflare and other anti-bot services detect headless mode via:
  - `navigator.webdriver` property
  - Canvas fingerprint differences
  - WebGL vendor/renderer strings
- Camoufox's `humanize=True` mitigates most but not all
- For critical Cloudflare-protected sites, use **headed mode**

### Server Restart Required
Mode change requires full server restart:
```bash
camoufox stop
camoufox start --headless  # or CAMOUFOX_HEADLESS=1 camoufox start
```

### PYTHONPATH Contamination (Critical)
Hermes sets `PYTHONPATH` that breaks Camoufox's YAML CLoader import.
**Always** prefix commands:
```bash
env -u PYTHONPATH ~/.hermes/.venv/bin/python3.12 ~/.hermes/scripts/camoufox_server.py
env -u PYTHONPATH ~/.hermes/.venv/bin/python3.12 ~/.hermes/scripts/camoufox_cli.py <command>
```

The `camoufox` symlink (`/usr/local/bin/camoufox`) inherits shell PYTHONPATH — use explicit python path form.