#!/usr/bin/env bash
# Recall — single-command dev bootstrap (macOS / Linux).
#
# Creates the venv if missing, installs dependencies, runs the smoke
# test, then launches the desktop app. Idempotent — re-run any time.
#
#   ./scripts/dev.sh                # venv + deps + smoke + launch
#   ./scripts/dev.sh --skip-smoke   # skip the 5-second smoke test
#   ./scripts/dev.sh --demo         # launch in --demo mode (no indexing)
#   ./scripts/dev.sh --debug        # launch with --debug boot diagnostics

set -euo pipefail

SKIP_SMOKE=0
DEMO=0
DEBUG=0
for arg in "$@"; do
    case "$arg" in
        --skip-smoke) SKIP_SMOKE=1 ;;
        --demo)       DEMO=1 ;;
        --debug)      DEBUG=1 ;;
        *) echo "unknown flag: $arg"; exit 2 ;;
    esac
done

# Resolve repo root regardless of where the script is invoked from.
# The script lives at infra/scripts/, two levels deep from the repo
# root. The Python desktop tree currently sits at the root; the
# pseudo-monorepo migration plan in apps/desktop/README.md will move
# it under apps/desktop/ in a future cycle.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$ROOT"

echo
echo "Recall dev bootstrap — $ROOT"
echo

# 1. Python version
if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 not found on PATH. Install Python 3.10+."
    exit 1
fi

PY_VER=$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')
PY_MAJOR=${PY_VER%.*}
PY_MINOR=${PY_VER#*.}
if [[ $PY_MAJOR -lt 3 || ( $PY_MAJOR -eq 3 && $PY_MINOR -lt 10 ) ]]; then
    echo "Python $PY_VER detected; 3.10+ required."
    exit 1
fi
echo "  python $PY_VER"

# 2. Create venv if missing
VENV="$ROOT/.venv"
if [[ ! -d "$VENV" ]]; then
    echo "  creating venv at .venv …"
    python3 -m venv "$VENV"
fi

# 3. Activate venv
# shellcheck source=/dev/null
. "$VENV/bin/activate"

# 4. Install deps only if requirements.txt changed since last install
REQ_HASH_FILE="$VENV/.reqhash"
REQ_PATH="$ROOT/requirements.txt"
CURRENT_HASH=$(shasum -a 256 "$REQ_PATH" 2>/dev/null | awk '{print $1}' \
    || sha256sum "$REQ_PATH" | awk '{print $1}')

INSTALL_NEEDED=1
if [[ -f "$REQ_HASH_FILE" ]]; then
    if [[ "$(cat "$REQ_HASH_FILE")" == "$CURRENT_HASH" ]]; then
        INSTALL_NEEDED=0
    fi
fi

if [[ $INSTALL_NEEDED -eq 1 ]]; then
    echo "  installing dependencies …"
    pip install --quiet --upgrade pip
    pip install --quiet -r "$REQ_PATH"
    echo "$CURRENT_HASH" > "$REQ_HASH_FILE"
else
    echo "  dependencies up to date"
fi

# 5. Smoke test
if [[ $SKIP_SMOKE -eq 0 ]]; then
    echo "  running smoke test …"
    if ! python _smoke_api.py >/dev/null; then
        echo "smoke test failed. Re-run with: python _smoke_api.py"
        exit 1
    fi
    echo "  smoke test ok"
fi

# 6. Launch
echo
echo "starting Recall …"
echo

ARGS=()
[[ $DEMO  -eq 1 ]] && ARGS+=("--demo")
[[ $DEBUG -eq 1 ]] && ARGS+=("--debug")

exec python recall.py "${ARGS[@]}"
