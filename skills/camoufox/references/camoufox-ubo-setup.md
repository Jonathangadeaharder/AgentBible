# uBlock Origin Addon Setup for Camoufox

## Problem
Camoufox `addons=[]` parameter requires **extracted directory** with `manifest.json`, NOT .xpi files.

`confirm_paths()` in `camoufox/addons.py`:
```python
def confirm_paths(paths):
    for path in paths:
        if not os.path.isdir(path):
            raise InvalidAddonPath(path)
        if not os.path.exists(os.path.join(path, 'manifest.json')):
            raise InvalidAddonPath('manifest.json is missing.')
```

## Setup

```bash
# 1. Download uBO XPI
curl -sL "https://addons.mozilla.org/firefox/downloads/latest/ublock-origin/addon-607138-latest.xpi" -o /tmp/ubo.xpi

# 2. Extract to persistent location
mkdir -p ~/.hermes/camoufox_profiles/addons/uBlock0
cd ~/.hermes/camoufox_profiles/addons/uBlock0
unzip /tmp/ubo.xpi

# 3. Verify
ls manifest.json
```

## Usage in Camoufox

```python
UBO_ADDON = os.path.expanduser("~/.hermes/camoufox_profiles/addons/uBlock0")

with Camoufox(
    headless=False,
    humanize=True,
    geoip=False,
    persistent_context=True,
    user_data_dir=PROFILE_DIR,
    addons=[UBO_ADDON],  # extracted dir, NOT .xpi
) as browser:
    ...
```

## Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `InvalidAddonPath: /tmp/ubo.xpi` | Passed .xpi file, not directory | Extract .xpi, pass directory |
| `InvalidAddonPath: manifest.json is missing` | Directory without manifest.json | Ensure unzip ran correctly |
| `InvalidAddonPath: /tmp/ubo.xpi` (path exists) | /tmp path works but Camoufox rejects it | Use ~/.hermes/ path |

## Thread Safety (Playwright Sync API)

Playwright sync API uses greenlets. Cannot call `page.evaluate()` from a
different thread than the one that launched the browser.

**Wrong**: Socket handler thread calls `page.goto()` directly.
**Right**: Socket handler enqueues command, main thread executes it.

See `scripts/camoufox_server.py` for the queue-based pattern.
