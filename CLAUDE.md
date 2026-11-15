# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

HD Active is a small PySide6 (Qt) desktop tray app that prevents external HDs from spinning down by
periodically writing/deleting a small file on each configured drive. It runs from a system tray
icon (`src/hd_active/main.py`) and is configured via an INI file.

## Development setup

This project uses [typer-invoke](https://github.com/joaonc/typer-invoke) (`inv`) as a task runner,
with tasks defined as Typer apps under `admin/`. Best to work in a virtual environment.

Install dev tooling and sync dependencies:
```bash
pip install typer-invoke
inv pip sync
```

`uv` manages the lock file/environment; `inv pip ...` wraps `uv lock` / `uv sync` with requirement
aliases (`requirements`, `requirements-dev`, `requirements-docs` — see `admin/pip.py`).

List all available tasks:
```bash
inv --help
```

Most `inv` commands accept `--dry` to print the underlying command instead of running it.

## Common commands

Run the app:
```bash
python -m src.hd_active.hd_active --conf src/hd_active/hd_active.ini
```
(`hd_active.py` also has a `__main__` block with a console-based start/stop loop, useful for testing
the drive-writing logic without the Qt UI. `main.py` is the actual GUI entry point / `hd_active`
console script.)

Run tests:
```bash
inv test unit
# equivalent to: pytest .
```
Run a single test file/case the normal pytest way, e.g. `pytest tests/test_hd_active.py -k some_case`.
Tests are configured in `pyproject.toml` (`testpaths = ['tests']`). A custom `windows` marker exists
for tests that only make sense on Windows (e.g. drive letters like `a:\`); CI runs `-m "not windows"`
on non-Windows runners and all tests on Windows.

Lint / format / type-check:
```bash
inv lint all            # ruff check --fix + ruff format + mypy (src, tests, admin)
inv lint all --check     # check-only mode, used in CI
inv lint ruff <path>     # just ruff
inv lint mypy [path]     # just mypy
```
Ruff line length is 100, single-quote formatting, targets py312. mypy excludes `src/ui/forms`
(generated Qt code — see below) and `tasks.py`.

Pre-commit:
```bash
inv precommit install    # run once after cloning
inv precommit run [--hook name]
```

Qt UI generation — `.ui`/`.qrc` files live under `assets/ui`; never hand-edit the generated output:
```bash
inv ui py [file]     # pyside6-uic: .ui -> src/hd_active/ui/forms/ui_<name>.py
inv ui rc [file]     # pyside6-rcc: .qrc -> src/hd_active/ui/forms/<name>_rc.py
inv ui edit <file>   # open a .ui file in Qt Designer
```

Docs (mkdocs):
```bash
inv docs serve
inv docs deploy   # publishes to https://joaonc.github.io/hd_active
```

Build/release (see `admin/build.py` for the full flow — bumps version across `pyproject.toml` and
`src/hd_active/__init__.py`, optionally commits/pushes/creates a PR via `gh`):
```bash
inv build version --bump patch|minor|major [--mode nothing|commit|pr]
inv build publish   # uv build [+ uv publish]
inv build clean
```

## Architecture

- `hd_active.py` — `HdActive`, the core engine. Holds a set of drive paths, runs a background
  `threading.Thread` that loops writing random bytes to a marker file (`_hd_active.txt`) on each
  drive then deletes it, sleeping `wait` seconds between rounds. Exposes `start()`/`stop()`/
  `change_state()` and a bounded in-memory `log` (`deque(maxlen=1000)`) of recent writes. This class
  has no Qt dependency and is unit-testable in isolation (see `tests/test_hd_active.py`).
- `hd_active_config.py` — `HdActiveConfig` reads/writes the INI config (drives, wait interval,
  run-on-start flag) using `configparser` with a custom `list` converter for comma-separated drive
  lists.
- `hd_action_state.py` — `HdActionState` enum (`Start`/`Stop`) used both as the tray menu action
  label and as the return value signaling what the *next* action would be.
- `main.py` — Qt application entry point (the `hd_active` console script). Wires up the tray icon.
- `ui/system_tray_icon.py` — `SystemTrayIcon` owns the `HdActive` instance, builds the tray context
  menu (change state / settings / about / exit), and loads config from the INI file passed on the
  command line (or `hd_active.ini` by default). Respects `HD_ACTION_DEBUG` env var (default `True`):
  when truthy, `write_hds` is stubbed to a no-op so drives aren't actually touched — important when
  testing/running the UI without real external drives attached.
- `ui/settings_dialog.py`, `ui/log_dialog.py` — dialogs built on generated `Ui_*` classes from
  `ui/forms/` (auto-generated from `assets/ui/*.ui` via `inv ui py`; don't edit these by hand).
- `utils.py` — small shared helpers: `FilePath` type alias, `get_asset()` for locating files under
  `assets/`, and `is_truthy()`, a permissive string/number/bool truthiness parser (raises on
  ambiguous input unless told not to) used for env-var flags like `HD_ACTION_DEBUG`.
- `admin/` — all `inv` task definitions (one module per concern: `build`, `docs`, `lint`, `pip`,
  `precommit`, `test`, `ui`), registered via `[tool.typer-invoke]` in `pyproject.toml`.

## Notes

- The core drive-writing logic in `HdActive` is UI-independent by design — prefer testing it
  directly rather than through the Qt layer where possible (`pytest-qt` is available for UI tests).
- CI (`tests.yml`) runs the test matrix on `windows-latest` across Python 3.12 and 3.14 (the
  supported range per `pyproject.toml`).
