# Playwright Firefox Driver Bug Fix

## Problem

Playwright's Firefox driver crashes when a page generates a JavaScript error
whose `pageError.location` is `undefined`. This happens frequently with Camoufox
+ uBlock Origin (uBO generates JS errors that trigger the crash).

Error message:
```
TypeError: Cannot read properties of undefined (reading 'url')
    at FFBrowserContext.<anonymous> (coreBundle.js:49624:39)
```

## Root Cause

Playwright's Firefox driver (`coreBundle.js`) accesses `pageError.location.url`,
`pageError.location.lineNumber`, and `pageError.location.columnNumber` without
null-checking `pageError.location`. When the location is undefined (which happens
with certain types of JS errors), the driver crashes, killing the browser
connection.

## Fix

Patch `coreBundle.js` in the Playwright driver package:

```bash
DRIVER_JS="$HOME/projects/shopping-bot/.venv/lib/python3.12/site-packages/playwright/driver/package/lib/coreBundle.js"

# Guard pageError.location access (two locations: ~line 25566 and ~49624)
sed -i.bak \
  's/url: pageError.location.url/url: (pageError.location \&\& pageError.location.url) || "unknown"/g; s/line: pageError.location.lineNumber/line: (pageError.location \&\& pageError.location.lineNumber) || 0/g; s/column: pageError.location.columnNumber/column: (pageError.location \&\& pageError.location.columnNumber) || 0/g' \
  "$DRIVER_JS"
```

## Verification

After patching, verify the fix:
```bash
grep -n "pageError.location" "$DRIVER_JS"
# Should show guarded access patterns
```

## Alternative Workaround

If you can't patch the driver, exclude uBO from Camoufox:
```python
from camoufox.addons import DefaultAddons
with Camoufox(headless=True, exclude_addons=[DefaultAddons.UBO]) as browser:
    ...
```

This prevents uBO's JS errors from triggering the crash, but loses ad/tracker
blocking. Use route interception as a cookie-consent blocking alternative:
```python
def block_consent(route):
    url = route.request.url
    if any(d in url for d in ['usercentrics', 'uc-cdn', 'cookiebot', 'onetrust', 'didomi']):
        route.abort()
    else:
        route.continue_()
ctx.route('**/*', block_consent)
```

## Note

This patch must be re-applied after every `uv pip install playwright` or
`uv pip install camoufox` that updates the playwright package, since the
driver package gets overwritten.
