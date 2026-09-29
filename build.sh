#!/bin/sh
# Reproducible, self-verifying build of the ntags binary.
# Produces dist/ntags plus dist/SHA256SUMS.
set -eu
cd "$(dirname "$0")"

rm -rf build dist

# Install deps from the pinned uv.lock when uv is available; otherwise use the
# already-synced .venv. Either way the build runs with .venv/bin/python
# directly (uv is only used for environment management).
PY=".venv/bin/python"
if command -v uv >/dev/null 2>&1; then
    echo "build.sh: uv found — syncing (lockfile-pinned)..."
    if uv sync --frozen --group dev; then
        echo "build.sh: env ready from uv.lock"
    elif uv sync --group dev; then
        echo "build.sh: env re-synced without --frozen (lockfile was stale)"
    else
        echo "build.sh: uv sync failed — falling back to existing .venv" >&2
    fi
elif [ ! -x "$PY" ]; then
    echo "build.sh: no uv and no .venv — run 'uv sync --group dev' first" >&2
    exit 1
fi

if ! "$PY" -c "import PyInstaller" >/dev/null 2>&1; then
    echo "build.sh: PyInstaller missing from .venv — run 'uv sync --group dev' and retry" >&2
    exit 1
fi

echo "build.sh: building..."
"$PY" -m PyInstaller ntags.spec --noconfirm --clean

# Smoke-test the artifact: running with no argument must exit 1 with usage.
t="$(mktemp -d)"
set +e
./dist/ntags > "$t/smoke.txt" 2>&1
rc=$?
set -e
if [ "$rc" -ne 1 ] || ! grep -q "Usage: ntags.py" "$t/smoke.txt"; then
    cat "$t/smoke.txt"
    echo "build.sh: smoke test FAILED (exit code $rc)" >&2
    rm -rf "$t"
    exit 1
fi
rm -rf "$t"

# Checksums alongside the artifact, ready for a release.
cd dist
{
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum ntags
    else
        shasum -a 256 ntags
    fi
} > SHA256SUMS
cd ..

echo "build.sh: OK — dist/ntags ready, checksums in dist/SHA256SUMS"