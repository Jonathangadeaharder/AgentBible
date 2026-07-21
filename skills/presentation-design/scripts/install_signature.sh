#!/usr/bin/env bash
# =============================================================================
# install_signature.sh — install a signature theme as a LOCAL Typst package,
# so any deck can `#import "@local/<name>:<version>": *` from anywhere, offline.
#
# Usage:
#   scripts/install_signature.sh <signature-theme-dir> [version]
#
#   <signature-theme-dir>  folder containing typst.toml and lib.typ
#   [version]              override the version (else read from typst.toml)
#
# Local packages live outside Typst's compiler sandbox, which is why this works
# across projects where a shared file path would be blocked. Verified to resolve
# through slidev-addon-typst's compiler with no network access.
# =============================================================================
set -euo pipefail

SRC="${1:?usage: install_signature.sh <signature-theme-dir> [version]}"
SRC="$(cd "$SRC" && pwd)"
[ -f "$SRC/typst.toml" ] || { echo "error: no typst.toml in $SRC" >&2; exit 1; }
[ -f "$SRC/lib.typ" ]    || { echo "error: no lib.typ in $SRC" >&2; exit 1; }

# read name/version from typst.toml (simple, tolerant of quotes/spacing)
read_toml() { grep -E "^[[:space:]]*$1[[:space:]]*=" "$SRC/typst.toml" | head -1 | sed -E 's/.*=[[:space:]]*"?([^"]*)"?[[:space:]]*$/\1/'; }
NAME="$(read_toml name)"
VERSION="${2:-$(read_toml version)}"
[ -n "$NAME" ] && [ -n "$VERSION" ] || { echo "error: could not read name/version from typst.toml" >&2; exit 1; }

# pick the OS local-package base dir
case "$(uname -s)" in
  Linux*)                    BASE="${XDG_DATA_HOME:-$HOME/.local/share}" ;;
  Darwin*)                   BASE="$HOME/Library/Application Support" ;;
  MINGW*|MSYS*|CYGWIN*)      BASE="${APPDATA:-$HOME/AppData/Roaming}" ;;
  *)                         BASE="${XDG_DATA_HOME:-$HOME/.local/share}" ;;
esac

DEST="$BASE/typst/packages/local/$NAME/$VERSION"
mkdir -p "$DEST"
cp "$SRC/"*.typ "$DEST/"
cp "$SRC/typst.toml" "$DEST/"

echo "installed $NAME:$VERSION -> $DEST"
echo "use it in a deck's typst block with:  #import \"@local/$NAME:$VERSION\": *"
