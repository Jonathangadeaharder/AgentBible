# Hermes Native Camofox Browser Backend

Hermes browser tools (`browser_navigate`, `browser_click`, `browser_snapshot`, etc.)
route through the same Node.js REST server as the `camoufox` CLI when `CAMOFOX_URL`
is set. One browser, two interfaces — no duplication.

## Activation

| Thing | Effect |
|-------|--------|
| `CAMOFOX_URL=http://localhost:9377` in `~/.hermes/.env` | **REAL SWITCH.** Activates camofox backend for Hermes browser tools. |
| `browser.engine: camofox` in config.yaml | **NO-OP.** Does nothing. |
| `browser.camofox.*` config presets | Activate automatically when `CAMOFOX_URL` is set. |
| `BROWSER_CDP_URL` env var or `browser.cdp_url` config | **Overrides camofox** — CDP takes priority. |

Verify activation in Python:
```python
from tools.browser_camofox import is_camofox_mode, check_camofox_available
is_camofox_mode()           # True when CAMOFOX_URL set and no CDP override
check_camofox_available()    # True when server responds on /health
```

## Config Presets (`browser.camofox` in config.yaml)

```yaml
browser:
  camofox:
    managed_persistence: false    # true = stable profile-scoped userId
    adopt_existing_tab: false     # recover existing tab on reconnect
    user_id: ''                   # override identity (external integrations)
    session_key: ''               # override session scope
    loopback_host_alias: host.docker.internal  # Docker loopback rewrite
    rewrite_loopback_urls: false  # rewrite 127.0.0.1 -> host.docker.internal
```

## CLI vs Hermes Browser Tools — When to Use Which

Both interfaces share the same Camoufox browser. Use the simplest one for each task.

### Use Hermes browser tools (PREFERRED for common operations)

| Task | Hermes tool | Why preferred |
|------|-------------|---------------|
| Navigate | `browser_navigate` | Auto-snapshot on nav, structured result |
| Read page | `browser_snapshot` | Accessibility tree with refs (e1, e2) |
| Click by ref | `browser_click(@eN)` | Refs are stable, no selector guessing |
| Type into ref | `browser_type(@eN, text)` | Ref-based, actionability checks |
| Press key | `browser_press` | Identical |
| Scroll | `browser_scroll` | Identical |
| Go back | `browser_back` | Identical |
| Screenshot | `browser_vision` | Returns analysis + screenshot path |
| Eval JS | `browser_console(expression=)` | Same /evaluate endpoint |
| Get images | `browser_get_images` | Same |

### Use CLI (for operations Hermes tools can't do)

| Task | CLI command | Why CLI-only |
|------|-------------|--------------|
| Click by CSS selector | `camoufox click_element 'selector'` | Hermes uses aria refs only, no CSS selectors |
| Fill by CSS selector | `camoufox fill_element 'selector' 'text'` | Same — CSS not refs |
| Type by CSS selector | `camoufox type_in_element 'selector' 'text'` | Same |
| Scroll to CSS element | `camoufox scroll_to_element 'selector'` | Hermes has no scroll-to-element |
| Query DOM by CSS | `camoufox get_elements 'selector'` | Returns tag/id/class/text/coords — Hermes snapshot is aria-only |
| Coordinate click | `camoufox click <x> <y>` | Canvas, signature pads, maps |
| Cookie file I/O | `camoufox save_cookies` / `load_cookies` | Hermes has no cookie export/import |
| Declarative loop | `camoufox loop '<json>'` | Multi-step sequencer with conditionals |
| Server lifecycle | `camoufox start` / `stop` / `ping` | Hermes can't start/stop the server |

### Cookie limitation note

CLI `save_cookies` uses `document.cookie` — cannot export HttpOnly cookies.
CLI `clear_cookies` expires via JS — cannot clear HttpOnly cookies.
For full HttpOnly cookie management, use `camoufox load_cookies` (POST /sessions/:userId/cookies
can inject any cookie including HttpOnly) or call the REST endpoint directly:

```bash
# Export all cookies (including HttpOnly) via REST
curl -s http://localhost:9377/sessions/cli_user/cookies -o /tmp/cookies.json
# Import cookies (including HttpOnly)
curl -s -X POST http://localhost:9377/sessions/cli_user/cookies \
  -H "Content-Type: application/json" -d @/tmp/cookies.json
```

## Server Setup

```bash
# Clone + install
git clone https://github.com/jo-inc/camofox-browser ~/projects/camofox-browser
cd ~/projects/camofox-browser && npm install

# CRITICAL: use fnm v22, not homebrew v26
eval "$(fnm env)" && fnm use 22 && node server.js

# Add to ~/.hermes/.env
# CAMOFOX_URL=http://localhost:9377
```

### fnm must be in BOTH .zshrc AND .bashrc

Hermes `terminal` tool runs `/bin/bash`, not `/bin/zsh`. If `fnm env` is only
in `.zshrc` (common — fnm installer targets zsh), bash sessions get Homebrew
node v26 → `NODE_MODULE_VERSION` mismatch with `better-sqlite3` → server fails
to start with cryptic error or never connects.

**Fix**: Add `eval "$(fnm env --use-on-cd)"` to `~/.bashrc` as well:

```bash
# Append to ~/.bashrc
echo 'eval "$(fnm env --use-on-cd)"' >> ~/.bashrc
```

Verify: `source ~/.bashrc && fnm use 22 && node --version` should show v22.x,
not v26.x. When starting the server from a background terminal, always
prepend `eval "$(fnm env)" && fnm use 22 &&` before `node server.js`.

## Stale Tab Recovery (410 Gone Errors)

When Hermes browser tools cache a dead tab ID, every `browser_navigate` call
fails with `410 Client Error: Gone for url: .../tabs/<dead-tab-id>/navigate`.
The tab was garbage-collected (session timeout, server restart) but Hermes
still references the old ID.

**Fix**: Delete the stale session via REST, then retry `browser_navigate`:

```bash
# Delete stale tab
curl -s -X DELETE "http://localhost:9377/tabs/<dead-tab-id>?userId=hermes_<hash>" --max-time 10
# Delete stale session
curl -s -X DELETE "http://localhost:9377/sessions/hermes_<hash>" --max-time 10
```

Find the userId from the 410 error URL or from `camoufox ping` output.
After deletion, `browser_navigate` creates a fresh tab automatically.

**If 410 persists after deletion**: The Hermes process caches the tab ID
in-memory. No amount of REST deletion fixes this. Workaround: use
`vision_analyze` with a local file path or HTTP URL instead of browser tools.

## Health Check

```bash
curl -s http://localhost:9377/health
# Returns: {"ok":true,"engine":"camoufox","browserConnected":true,...}
```
