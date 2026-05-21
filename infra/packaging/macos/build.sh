#!/usr/bin/env bash
# Recall — macOS build pipeline
# ------------------------------------------------------------------
# Produces  Recall.dmg  — the drag-to-Applications disk image.
#
#   bash infra/packaging/macos/build.sh
#
# Stages:
#   1. PyInstaller        → dist/Recall.app          (the .app bundle)
#   2. Info.plist + icon  → bundle metadata           (menu-bar app)
#   3. hdiutil            → dist/installer/Recall.dmg (the artifact)
#
# Prerequisites (build machine — must be macOS):
#   • pip install -r requirements.txt pyinstaller
#   • Xcode command-line tools (for hdiutil, codesign)
#
# This produces an UNSIGNED, UNNOTARIZED .dmg. Signing + notarisation
# (an Apple Developer ID + `notarytool`) is a separate release step;
# see RELEASE.md and SUPPORTED_PLATFORMS.md.
set -euo pipefail

if [[ "$(uname)" != "Darwin" ]]; then
  echo "error: macOS packaging must be built on macOS." >&2
  exit 1
fi

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$ROOT"
HERE="infra/packaging/macos"
echo "Recall macOS build — root: $ROOT"

# --- stage 1: PyInstaller -----------------------------------------
echo "[1/3] PyInstaller bundle..."
rm -rf dist/Recall dist/Recall.app
# recall.spec must include a BUNDLE() step on macOS so PyInstaller
# emits a .app; if it only COLLECTs, assemble the bundle here.
pyinstaller --noconfirm recall.spec
if [[ ! -d dist/Recall.app ]]; then
  echo "  no .app from spec — assembling from dist/Recall/"
  APP="dist/Recall.app"
  mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
  cp -R dist/Recall/. "$APP/Contents/MacOS/"
fi

# --- stage 2: bundle metadata -------------------------------------
echo "[2/3] Info.plist + icon..."
cp "$HERE/Info.plist" dist/Recall.app/Contents/Info.plist
if [[ -f infra/packaging/assets/recall.icns ]]; then
  cp infra/packaging/assets/recall.icns \
     dist/Recall.app/Contents/Resources/recall.icns
fi

# Universal2 (Apple Silicon + Intel) requires a universal Python and
# `target_arch='universal2'` in recall.spec. Without that the build
# is single-arch for the build machine — see this folder's README.

# --- stage 3: DMG --------------------------------------------------
echo "[3/3] DMG..."
mkdir -p dist/installer
STAGE="$(mktemp -d)"
cp -R dist/Recall.app "$STAGE/"
ln -s /Applications "$STAGE/Applications"   # drag-to-install target
hdiutil create -volname "Recall" -srcfolder "$STAGE" -ov -format UDZO \
  dist/installer/Recall.dmg
rm -rf "$STAGE"

echo ""
echo "Done. Release artifact:  $ROOT/dist/installer/Recall.dmg"
echo "Next: codesign + notarize (RELEASE.md) before publishing."
