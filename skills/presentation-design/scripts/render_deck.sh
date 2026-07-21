#!/usr/bin/env bash
# =============================================================================
# render_deck.sh — build a Slidev deck to PNG + PDF and copy the results back.
#
# Usage:
#   scripts/render_deck.sh <deck-dir> [build-dir]
#
#   <deck-dir>  folder containing slides.md, styles.css, setup/, package.json
#   [build-dir] where to install the toolchain (default: $HOME/.ae-deck-build)
#
# Why a separate build dir: node_modules on a network-mounted folder is slow and
# throws ENOTEMPTY on rename. Installing on the local filesystem is fast and
# atomic. We copy the deck sources into the build dir, render there, and copy the
# PNGs/PDF back into <deck-dir>/renders and <deck-dir>/deck.pdf.
#
# Handles the sandbox quirks discovered in practice:
#   - use npm (corepack/pnpm may lack permission to symlink)
#   - Chromium needs libXdamage.so.1 which is often missing; we build a tiny
#     no-op stub with gcc and point LD_LIBRARY_PATH at it
#   - Playwright browsers install into a local cache via PLAYWRIGHT_BROWSERS_PATH
#
# Re-runnable: skips install / browser download / stub build if already present.
# =============================================================================
set -euo pipefail

DECK_DIR="${1:?usage: render_deck.sh <deck-dir> [build-dir]}"
BUILD_DIR="${2:-$HOME/.ae-deck-build}"
DECK_DIR="$(cd "$DECK_DIR" && pwd)"

PW_PATH="$BUILD_DIR/.playwright"
STUB_DIR="$BUILD_DIR/.libstub"
export PLAYWRIGHT_BROWSERS_PATH="$PW_PATH"

echo "==> deck:  $DECK_DIR"
echo "==> build: $BUILD_DIR"

# ---- 1. stage sources in the local build dir --------------------------------
mkdir -p "$BUILD_DIR/setup"
cp "$DECK_DIR/package.json" "$BUILD_DIR/" 2>/dev/null || true
cp "$DECK_DIR/slides.md"    "$BUILD_DIR/"
cp "$DECK_DIR/styles.css"   "$BUILD_DIR/" 2>/dev/null || true
[ -d "$DECK_DIR/setup" ]  && cp -r "$DECK_DIR/setup/."  "$BUILD_DIR/setup/"  || true
[ -d "$DECK_DIR/components" ] && { mkdir -p "$BUILD_DIR/components"; cp -r "$DECK_DIR/components/." "$BUILD_DIR/components/"; } || true
[ -d "$DECK_DIR/images" ] && { mkdir -p "$BUILD_DIR/images"; cp -r "$DECK_DIR/images/." "$BUILD_DIR/images/"; } || true

cd "$BUILD_DIR"

# ---- 2. install slidev (skip browser download here) -------------------------
if [ ! -x "node_modules/.bin/slidev" ]; then
  echo "==> npm install (this can take a few minutes on first run)…"
  npm install --no-audit --no-fund --ignore-scripts --loglevel=error
fi

# ---- 3. install Chromium for Playwright -------------------------------------
if [ ! -d "$PW_PATH" ] || ! ls "$PW_PATH"/chromium-*/ >/dev/null 2>&1; then
  echo "==> downloading Chromium…"
  ./node_modules/.bin/playwright install chromium
fi

# ---- 4. build no-op stubs for any missing X libs ----------------------------
# Find the chrome binary and see what shared libs the loader can't resolve.
BIN="$(ls "$PW_PATH"/chromium-*/chrome-linux/chrome 2>/dev/null | head -1 || true)"
if [ -n "$BIN" ]; then
  MISSING="$(ldd "$BIN" 2>/dev/null | awk '/not found/{print $1}' | sort -u || true)"
  if [ -n "$MISSING" ]; then
    mkdir -p "$STUB_DIR"
    for soname in $MISSING; do
      [ -f "$STUB_DIR/$soname" ] && continue
      # map the missing lib to the symbol-name prefix it provides
      case "$soname" in
        libXdamage.so*)                 prefix="XDamage" ;;
        libXcomposite.so*)              prefix="XComposite" ;;
        libXfixes.so*)                  prefix="XFixes" ;;
        libXrandr.so*)                  prefix="XRR" ;;
        libXtst.so*)                    prefix="XTest" ;;
        libXScrnSaver.so*|libXss.so*)   prefix="XScreenSaver" ;;
        *)                              prefix="" ;;
      esac
      if [ -z "$prefix" ]; then
        echo "!! missing $soname and no stub mapping known — install it or extend render_deck.sh" >&2
        continue
      fi
      syms="$(nm -D "$BIN" 2>/dev/null | awk -v p="^$prefix" '$2=="U" && $3 ~ p {print $3}' | sort -u)"
      {
        echo "/* auto-generated no-op stub for $soname (headless does not use it) */"
        for s in $syms; do echo "long $s(){return 0;}"; done
      } > "$STUB_DIR/$soname.c"
      gcc -shared -fPIC -o "$STUB_DIR/$soname" "$STUB_DIR/$soname.c"
      echo "==> built stub $soname ($(echo "$syms" | wc -w) symbols)"
    done
    export LD_LIBRARY_PATH="$STUB_DIR:${LD_LIBRARY_PATH:-}"
  fi
fi

# ---- 5. export PNG (per slide) and PDF ---------------------------------------
echo "==> exporting PNGs…"
rm -rf out_png && ./node_modules/.bin/slidev export slides.md --format png --dark --output out_png
echo "==> exporting PDF…"
./node_modules/.bin/slidev export slides.md --format pdf --dark --output deck

# ---- 6. copy results back to the deck dir -----------------------------------
mkdir -p "$DECK_DIR/renders"
# Robust copy: slidev png export produces 1.png, 2.png, ... in the output dir.
# Use a counter to avoid basename/glob/printf fragility when the glob doesn't expand or names vary.
i=1
for f in $(ls out_png/*.png 2>/dev/null | sort -V); do
  printf -v n "%02d" "$i"
  cp "$f" "$DECK_DIR/renders/slide-$n.png"
  i=$((i + 1))
done
cp deck.pdf "$DECK_DIR/deck.pdf" 2>/dev/null || true

# ---- 7. sanity check: exported slide count must match the source -------------
SRC_SLIDES="$(python3 - "$BUILD_DIR/slides.md" <<'PY'
import re, sys
text = open(sys.argv[1], encoding="utf-8").read()
chunks = [c.strip() for c in re.split(r"\n---[ \t]*\n", "\n"+text+"\n") if c.strip()]
def is_fm(c):
    for l in c.splitlines():
        s = l.strip()
        if not s: continue
        if re.match(r"^[a-zA-Z_][a-zA-Z0-9_-]*\s*:", s): continue
        if re.match(r"^\s+\S", l): continue
        return False
    return True
print(sum(1 for c in chunks if not is_fm(c)))
PY
)"
PNG_COUNT="$(ls "$DECK_DIR"/renders/slide-*.png 2>/dev/null | wc -l | tr -d ' ')"
if [ "$SRC_SLIDES" != "$PNG_COUNT" ]; then
  echo "!! SLIDE COUNT MISMATCH: source has $SRC_SLIDES slides, export produced $PNG_COUNT PNGs." >&2
  echo "!! This is almost always a '---' separator/frontmatter bug — see build-slidev.md." >&2
fi

# ---- 8. build PPTX (delivery format: only one Keynote imports with notes) ----
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 -c "import pptx" 2>/dev/null || \
  pip install python-pptx --quiet 2>/dev/null || \
  pip install python-pptx --quiet --break-system-packages
python3 "$SCRIPT_DIR/build_pptx.py" "$DECK_DIR"

echo "==> done."
echo "    PNGs: $DECK_DIR/renders/slide-*.png"
echo "    PDF:  $DECK_DIR/deck.pdf"
echo "    PPTX: $DECK_DIR/deck.pptx  (speaker notes embedded — Keynote-ready)"
echo "    Now READ each PNG and check it against the Phase 3 rubric before shipping."
