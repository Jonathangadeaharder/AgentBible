# Camoufox + Playwright Gotchas

Session-verified pitfalls when automating sites with Camoufox's sync API.

## 1. Threading + Playwright Sync API = Greenlet Death

**Symptom**: Hundreds of lines of:
```
greenlet.error: Cannot switch to a different thread
  Current:  <greenlet.greenlet object at 0x... (otid=0x...) suspended active started main>
  Expected: <greenlet.greenlet object at 0x... (otid=0x...) suspended active started main>
```

**Cause**: A `threading.Thread` (e.g. for cookie banner auto-dismissal) calls
`page.evaluate()`. Playwright's sync API uses greenlets that are pinned to the
thread that created them. Cross-thread access crashes.

**Fix**: Never use background threads for ANY page interaction. Call
`dismiss_cookie_banner(page)` inline from the main thread, after each
navigation step.

## 2. Duplicate DOM IDs → Strict Mode Violation

**Symptom**:
```
Locator.click: Error: strict mode violation: locator("input#loginUsername") resolved to 2 elements
```

**Cause**: Some sites (e.g. World of Pizza) render duplicate HTML blocks —
the same `#loginUsername` / `#loginPassword` appear twice in the DOM (one
hidden, one visible in a modal). Playwright strict mode refuses to guess.

**Fix**: Use `.last` (typically the visible one in the modal) + `force=True`:
```python
page.locator("input#loginUsername").last.fill(email, force=True)
page.locator("input#loginPassword").last.fill(password, force=True)
page.locator("input.loginButton").last.click(force=True)
```

**Debug**: Check which duplicate is visible:
```python
inputs = page.locator("input#loginUsername").all()
for i, inp in enumerate(inputs):
    print(f"  Input {i}: visible={inp.is_visible()}")
```

## 3. page.evaluate() Argument Passing

**Wrong** (4 positional args — TypeError):
```python
page.evaluate("(email, pwd) => { ... }", email, password)
```

**Right** (2 args — expression + JSON-serializable arg):
```python
page.evaluate("([email, pwd]) => { ... }", [email, password])
```

## 4. PyYAML CLoader Missing → Camoufox Import Fails

**Symptom**:
```
ImportError: cannot import name 'CLoader' from 'yaml'
```

**Cause**: PyYAML installed as pure-Python (no C extension) in the venv.
Camoufox's `pkgman.py` imports `from yaml import CLoader, load`.

**Diagnosis**:
```python
import yaml
print(yaml.__file__)  # Check which site-packages it loads from
print(yaml.__with_libyaml__)  # Must be True
```

If `__with_libyaml__` is False, the C extension wasn't built.

**Fix**:
```bash
LDFLAGS="-L/opt/homebrew/lib" CPPFLAGS="-I/opt/homebrew/include" \
  uv pip install --python ~/.hermes/.venv/bin/python \
  --force-reinstall --no-binary :all: pyyaml
```

**Shadowing trap**: If `yaml.__file__` points to a DIFFERENT Python version's
site-packages (e.g. Python 3.11 path when venv is 3.12), the old installation
shadows the new one. Delete the shadowing path:
```bash
rm -rf ~/.hermes/hermes-agent/venv/lib/python3.11/site-packages/yaml
```
Then verify: `python -c "import yaml; print(yaml.__with_libyaml__)"` → `True`.

## 5. persistent_context Syntax for Camoufox

**Wrong** (Playwright BrowserType.launch kwarg):
```python
with Camoufox(..., user_data_dir=PROFILE_DIR) as browser:
    ctx = browser.new_context()  # TypeError: unexpected 'user_data_dir'
```

**Right** (Camoufox persistent_context flag):
```python
with Camoufox(
    ...,
    persistent_context=True,
    user_data_dir=PROFILE_DIR,
) as ctx:
    page = ctx.new_page()
```

When `persistent_context=True`, Camoufox returns a `BrowserContext` directly,
not a `Browser`. The `with` block yields the context.

## 6. Cookie Banner Reappears on SPA Navigation

Usercentrics CMP re-renders after every client-side route change (hash change,
SPA navigation). Dismissing once at page load is not enough.

**Pattern**: Call `dismiss_cookie_banner(page)` after EVERY `page.goto()` and
after any click that might trigger navigation.

## 7. Playwright Firefox Profile Path with Spaces

**Symptom**:
```
[pid=NNNN][err] JavaScript error: resource://gre/modules/XULStore.sys.mjs, line 84: Error: Can't find profile directory.
<process did exit: exitCode=0, signal=null>
```
Browser launches but immediately exits.

**Cause**: `launch_persistent_context(user_data_dir=...)` with a path containing spaces (e.g. `Profiles/<FF_PROFILE>.Profil 4`). Playwright Firefox (Juggler) fails to resolve the profile directory.

**Fix**: Copy profile to a path without spaces:
```python
import shutil
shutil.copytree(
    "/Users/.../Profiles/<FF_PROFILE>.Profil 4",
    "/tmp/giuli4_clean",
    dirs_exist_ok=True,
)
# Remove lock + compatibility files
import os
for f in [".parentlock", "lock", "compatibility.ini"]:
    p = os.path.join("/tmp/giuli4_clean", f)
    if os.path.exists(p): os.remove(p)

browser = pw.firefox.launch_persistent_context(
    user_data_dir="/tmp/giuli4_clean",
    headless=False,
)
```

**Also**: Firefox must be closed (`pkill -f firefox`) before copying `cookies.sqlite` — session cookies are in RAM while Firefox runs.

## 8. `camoufox` Binary Name Conflict

**Symptom**: `camoufox start` → `Error: No such command 'start'`

**Cause**: The Camoufox Python package installs its own CLI binary called `camoufox` (commands: `fetch`, `path`, `remove`, `server`, `test`, `version`). The custom Hermes CLI is `~/.hermes/scripts/camoufox_cli.py`, symlinked as `/usr/local/bin/camoufox`. If both are on PATH, the system `camoufox` shadows the custom one.

**Fix**: Use the full path or check `camoufox --help` — if it shows `fetch/path/remove/server/test/version`, it's the wrong binary. Use `python3 ~/.hermes/scripts/camoufox_cli.py <command>` instead, or fix the symlink.

## 9. Playwright Firefox Binary Missing After Install

**Symptom**: `launch_persistent_context: Executable doesn't exist at .../ms-playwright/firefox-1466/...`

**Cause**: Playwright Python package installed but Firefox browser binary not downloaded.

**Fix**: `~/.hermes/.venv/bin/playwright install firefox` (~82MB download). This is separate from the `playwright` pip package.

## 10. Login Modal via URL Hash

Some sites (e.g. World of Pizza: `webshop.world-of-pizza.de/storedata/listStore#login`)
open a login modal via URL hash navigation. The login form inputs may be
present in the DOM but hidden until the modal is activated.

**Approach**:
1. Navigate to `URL#login` to trigger the modal
2. Dismiss cookie banner
3. Use `.last` + `force=True` for duplicate input IDs
4. Inspect with `page.evaluate()` to find exact input names/IDs if selectors fail
