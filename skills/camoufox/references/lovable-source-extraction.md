# Lovable.dev Source Code Extraction

Lovable.dev projects expose source code through a Vite dev server. The Code tab in the editor is paywalled ("Read only" + empty `.code-editor-wrapper`), but the deployed preview app at `<project-id>.lovableproject.com` serves all source files.

## Access Method

1. Extract Firefox cookies for `lovable.dev` (scan profiles to find the one with session)
2. Load cookies into Camoufox → navigate to `lovable.dev/projects/<id>`
3. Find the preview iframe src: `document.getElementById("live-preview-panel").src` → `<project-id>.lovableproject.com/?__lovable_token=...`
4. No token needed for curl — cookies from Firefox work directly

## Cookie Extraction

```bash
# Scan profiles for lovable.dev session
for p in ~/Library/Application\ Support/Firefox/Profiles/*/; do
  n=$(basename "$p")
  f="$p/cookies.sqlite"
  [ -f "$f" ] || continue
  tmp=$(mktemp /tmp/ff_XXXX.sqlite)
  cp "$f" "$tmp" 2>/dev/null || continue
  count=$(sqlite3 "$tmp" "SELECT count(*) FROM moz_cookies WHERE host LIKE '%lovable%';" 2>/dev/null)
  echo "$n: $count lovable cookies"
  rm -f "$tmp"
done
```

Build a Netscape cookie jar for curl:

```python
import sqlite3, json

conn = sqlite3.connect('/tmp/ff_cookies.sqlite')
rows = conn.execute('''
    SELECT name, value, host, path, expiry, isSecure, isHttpOnly, sameSite
    FROM moz_cookies WHERE host LIKE '%lovable%'
''').fetchall()
conn.close()

ss_map = {0: 'None', 1: 'Lax', 2: 'Strict', 3: 'None'}
cookies = []
for name, value, host, path, expiry, is_secure, is_http_only, same_site in rows:
    if not value: continue
    c = {'name': name, 'value': value, 'domain': host, 'path': path or '/',
         'secure': is_secure == 1, 'httpOnly': is_http_only == 1,
         'sameSite': ss_map.get(same_site, 'None')}
    if expiry and expiry > 0:
        if expiry > 1e15: expiry = int(expiry / 1e6)
        elif expiry > 1e12: expiry = int(expiry / 1e3)
        c['expires'] = expiry
    else:
        c['expires'] = -1
    cookies.append(c)

with open('/tmp/lovable_cookies.json', 'w') as f:
    json.dump(cookies, f, indent=2)
```

Or build a Netscape cookie jar for curl:

```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('/tmp/ff_cookies.sqlite')
rows = conn.execute(\"SELECT host, name, value, path, isSecure, expiry FROM moz_cookies WHERE host LIKE '%lovable%'\").fetchall()
conn.close()
lines = ['# Netscape HTTP Cookie File']
for host, name, value, path, secure, expiry in rows:
    flag = 'TRUE' if host.startswith('.') else 'FALSE'
    exp = str(int(expiry / 1000) if expiry > 1e12 else (expiry if expiry > 0 else 0))
    lines.append(f'{host}\t{flag}\t{path or \"/\"}\t{\"TRUE\" if secure else \"FALSE\"}\t{exp}\t{name}\t{value}')
print('\n'.join(lines))
" > /tmp/lovable_cookie_jar.txt
```

## Source Discovery

### Method 1: `data-tsd-source` attributes

The deployed HTML contains `data-tsd-source="/src/routes/index.tsx:4:10"` attributes that reveal source file paths:

```bash
curl -s -b /tmp/lovable_cookie_jar.txt "https://<id>.lovableproject.com/" | \
  grep -oP 'data-tsd-source="[^"]+"' | cut -d'"' -f2 | cut -d: -f1 | sort -u
```

### Method 2: Import chain traversal

Fetch each `.tsx`/`.ts` file and extract `from "..."` imports starting with `/src/`:

```bash
# Fetch CoverGenerator.tsx, find imports
curl -s -b /tmp/lovable_cookie_jar.txt "https://<id>.lovableproject.com/src/components/CoverGenerator.tsx" | \
  grep -oP 'from "(/src/[^"]+)"' | cut -d'"' -f2 | sort -u
```

### Method 3: Config file probing

```bash
PATHS=(
  "/package.json"
  "/vite.config.ts"
  "/tsconfig.json"
  "/eslint.config.js"
  "/components.json"
  "/.gitignore"
  "/src/server.ts"
  "/src/lib/utils.ts"
  "/src/lib/lovable-error-reporting.ts"
  "/src/lib/error-capture.ts"
  "/src/lib/error-page.ts"
  "/src/hooks/use-mobile.ts"
  "/src/hooks/use-toast.ts"
)
for f in "${PATHS[@]}"; do
  status=$(curl -s -o /dev/null -w "%{http_code}" -b /tmp/lovable_cookie_jar.txt "https://<id>.lovableproject.com$f")
  [ "$status" = "200" ] && echo "FOUND: $f"
done
```

### Method 4: shadcn/ui components

Check `components.json` for shadcn config, then probe `src/components/ui/*.tsx`:

```bash
COMPONENTS=(
  button input card badge dialog select tabs tooltip sonner
  separator scroll-area slider switch label accordion alert-dialog
  aspect-ratio avatar checkbox collapsible context-menu dropdown-menu
  hover-card menubar navigation-menu popover progress radio-group
  toggle toggle-group resizable command drawer form input-otp
  calendar table skeleton
)
for comp in "${COMPONENTS[@]}"; do
  status=$(curl -s -o /dev/null -w "%{http_code}" -b /tmp/lovable_cookie_jar.txt \
    "https://<id>.lovableproject.com/src/components/ui/$comp.tsx")
  [ "$status" = "200" ] && echo "FOUND: $comp.tsx"
done
```

## Clean Source via `?raw`

Vite dev server transforms modules with HMR instrumentation (`__vite__createHotContext`, `import.meta.hot`, `/node_modules/.vite/deps/...`). Append `?raw` to get untransformed source:

```bash
# Fetch clean source — returns: export default "<json-encoded source>";
curl -s -b /tmp/lovable_cookie_jar.txt "https://<id>.lovableproject.com/src/lib/utils.ts?raw" | \
  python3 -c "
import json, sys
raw = sys.stdin.read()
if raw.startswith('export default '): raw = raw[len('export default '):]
raw = raw.strip().rstrip(';').strip()
print(json.loads(raw), end='')
"
```

## Full Download Script

```bash
APP_BASE="https://<id>.lovableproject.com"
DEST="$HOME/projects/<project-name>"

FILES=(
  "/package.json:package.json"
  "/vite.config.ts:vite.config.ts"
  "/tsconfig.json:tsconfig.json"
  "/src/routes/__root.tsx:src/routes/__root.tsx"
  "/src/routes/index.tsx:src/routes/index.tsx"
  "/src/components/CoverGenerator.tsx:src/components/CoverGenerator.tsx"
  "/src/lib/coverEngine.ts:src/lib/coverEngine.ts"
  # ... add more as discovered
)

for entry in "${FILES[@]}"; do
  src="${entry%%:*}"
  dst="${entry##*:}"
  mkdir -p "$(dirname "$DEST/$dst")"
  curl -s -b /tmp/lovable_cookie_jar.txt "$APP_BASE$src?raw" | \
    python3 -c "
import json, sys
raw = sys.stdin.read()
if raw.startswith('export default '): raw = raw[len('export default '):]
raw = raw.strip().rstrip(';').strip()
try:
    print(json.loads(raw), end='')
except:
    if raw.startswith('\"') and raw.endswith('\"'):
        print(raw[1:-1].replace('\\\\n','\n').replace('\\\\t','\t').replace('\\\"','\"').replace('\\\\\\\\','\\\\'), end='')
    else:
        print(raw, end='')
" > "$DEST/$dst"
  echo "$dst: $(wc -c < "$DEST/$dst") bytes"
done
```

## Pitfalls

- **Code tab shows empty wrapper**: `.code-editor-wrapper` has 0 children. "Read only" + "Upgrade" overlay. Don't waste time clicking it — go straight to the deployed preview.
- **Vite `?raw` returns JSON-encoded string**: `export default "source code here\n";` — must parse as JSON string, not just strip quotes. Naive `sed` leaves escaped `\n` and `\"` in output.
- **Token in iframe src is truncated by CLI**: `camoufox eval` truncates results at 60 chars. Token is ~1000 chars. Use chunked extraction or skip the token entirely — cookies from Firefox work directly with curl.
- **shadcn/ui components**: Lovable scaffolds ALL shadcn components, not just used ones. Found 38 `src/components/ui/*.tsx` files even though only `button`, `sonner`, `slider`, `label` were imported.
- **Import paths use `@/` alias**: Vite resolves `@/lib/coverEngine` → `/src/lib/coverEngine.ts`. The `?raw` fetch must use the resolved `/src/...` path.
- **`tsconfig.json` `paths`**: `"@/*": ["./src/*"]` — use this to resolve bare imports when traversing the import graph.
- **`vite.config.ts` references `server.ts`**: `tanstackStart: { server: { entry: "server" } }` → fetch `src/server.ts`.
- **`server.ts` imports more lib files**: `error-capture.ts`, `error-page.ts` — follow the chain.
- **Binary files (favicon.ico)**: Fetch without `?raw` — Vite serves them directly. `curl -s -b cookie_jar "$APP_BASE/public/favicon.ico" -o favicon.ico`.
