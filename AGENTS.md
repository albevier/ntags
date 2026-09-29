# AGENTS.md — Reproducible environment & testing notes for coding agents

## Project

`ntags` is a single-module Python ncurses TUI for editing audio tags (MP3/FLAC/AIFF/WAV) via
`mutagen`. Entry point: `ntags.py` → `tag_editor_tui.py` (all UI logic) → `audio_file.py`
(factory) → per-format classes (`mp3_file.py`, `flac_file.py`, `aiff_file.py`, `wav_file.py`)
extending `audio_file_base.AudioFileBase`.

## Environment: ALWAYS use uv

This project is managed with [uv](https://docs.astral.sh/uv/) — `.venv`, `uv.lock`, and
`.python-version` (3.14) are managed by it. Do not use system `python`, `pip`, or
`pip install`. Every test/run command should go through `uv run`:

```sh
uv sync            # create/update .venv from uv.lock (run once after cloning)
uv run ntags.py <file_or_dir>     # launch the TUI
uv run python -m py_compile ntags.py tag_editor_tui.py audio_file.py   # syntax check
uv run python -c "import mutagen; print(mutagen.version)"
```

Note: `.venv/bin/python` also exists and is a **fully valid** way to run code — it is the same
uv-managed environment (verified: Python 3.14.0, `mutagen 1.47.0` loaded from
`.venv/lib/python3.14/site-packages`). Prefer `uv run ...` as the first choice so the
environment stays synced; use `.venv/bin/python` directly when `uv run` is unavailable —
both are acceptable for validation, only system `python`/`pip` is off-limits.

Dependencies: runtime = `mutagen>=1.47.0` only; dev group = `pyinstaller` (used with
`ntags.spec` to build binaries in `dist/`).

## Git

Agents must not run git write operations (`git add`/`commit`/`push`, rebase, or anything
that mutates `.git`) and must never request unsandboxed access for git metadata. Read-only
inspection is fine:

```sh
git --no-optional-locks status
git --no-pager diff
git --no-pager log --oneline -5
```

When a commit is wanted, print the exact commands and let the user run them.

## Building binaries

Distribution binaries are built with PyInstaller (dev dependency group) via:

```sh
./build.sh
```

The script cleans stale artifacts, installs dependencies from the pinned `uv.lock`
(`uv sync --frozen --group dev`, falling back to the synced `.venv/bin/python` when `uv`
itself is unavailable), runs `ntags.spec`, then smoke-tests the produced `dist/ntags`
(no-args run must exit 1 with usage) and writes `dist/SHA256SUMS`.

`.github/workflows/build-binaries.yml` builds macOS and Linux binaries on `v*` tags and
attaches per-platform artifacts (plus checksums) to the GitHub release. Windows is
intentionally not targeted: `curses` is not part of the Python stdlib there.

There is no pytest suite, and none is planned — this is slated for a Rust port, where
validation moves to cargo. Validate with:

1. **Compile check** (fast, always run):
   `uv run python -m py_compile ntags.py tag_editor_tui.py audio_file.py`

2. **Ad-hoc pty-driven E2E** (when UI-level behavior changes): drive the real curses UI
   over a pty — spawn `ntags.py` with real mutagen-readable fixtures, replay keystrokes,
   and assert on-disk tag changes via mutagen. Write that script on the spot under a
   `_`-prefixed throwaway name and delete it afterwards (verified working end-to-end
   2026: select-all → background tag preload → bulk edit → bulk save → verify on disk).

## Gotchas for agent-driven tests

- `curses` needs a real pseudo-terminal: use the `pty` module, set the window size via
  `fcntl.ioctl(slave, 0x40087468, struct.pack("HHHH", rows, cols, 0, 0))`, set
  `TERM`/`LANG` env vars, then read from the master fd.
- A pty E2E test must be run as `timeout_ms`-bounded commands on its own; a hung child
  must be killed by the script, not the shell.
- Generating audio fixtures by hand is error-prone: verify frames with
  `mutagen.mp3.MP3(path)` *first*, before pointing any UI test at them.
  Known working MP3 fixture recipe (2026): an MPEG-1 Layer III frame
  `FF FB 90 C0` + 413 zero bytes, **repeated** several times (a single
  frame alone is rejected with `HeaderNotFoundError: can't sync`), then
  `mutagen.id3.ID3().save(path, v1=0)` to prepend the tag.
- Sandboxed agent terminals may fail to run `uv` itself: writes to
  `~/.cache/uv` can be blocked (`Failed to initialize cache ... ~/.cache/uv`),
  and the tool transport can error with `authorization channel closed`.
  Do not retry-spam commands that hit this; fall back to the already-synced
  `.venv/bin/python` directly for test commands and leave `uv run` for the
  user's interactive shell.