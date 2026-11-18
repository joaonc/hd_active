# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

HD Active is a small PySide6 (Qt) desktop tray app that prevents external HDs from spinning down by
periodically writing/deleting a small file on each configured drive. It runs from a system tray
icon (`src/hd_active/main.py`) and is configured via an INI file.

## Development setup

The project is managed with [uv](https://docs.astral.sh/uv/) (install it first: it manages the
Python version, `.venv`, dependencies and `uv.lock`). Linting/formatting is done with
[ruff](https://docs.astral.sh/ruff/) and type checking with [ty](https://docs.astral.sh/ty/).
`pip`, `mypy`, `black` and `isort` are not used.

Create the environment and install dependencies (the `dev` group is the default):
```bash
uv sync
```

Dependencies live in `pyproject.toml`; change them with `uv add [--group dev|docs] <pkg>`,
`uv remove <pkg>` and `uv lock --upgrade[-package <pkg>]`, which update `uv.lock`.

Tasks are run with [typer-invoke](https://github.com/joaonc/typer-invoke) (`inv`), defined as Typer
apps under `admin/` and installed by `uv sync`. Run them with `uv run inv ...` (or activate `.venv`).

List all available tasks:
```bash
uv run inv --help
```

Most `inv` commands accept `--dry` to print the underlying command instead of running it.

## Common commands

Run the app (`hd_active` console script, same as `python -m hd_active`; see `cli.py`):
```bash
uv run hd_active [gui]            # system tray UI (default command)
uv run hd_active run              # headless in the console until Ctrl+C, doesn't import Qt
uv run hd_active config show|init
```
Common options, accepted before or after the command: `--conf FILE` (default `./hd_active.ini`),
`--log LEVEL` and, for `gui`/`run`, `--dry-run`. **Drives are written to by default**: use
`--dry-run` (or a truthy `HD_ACTION_DEBUG` env var) when trying things out without real drives,
ex `uv run hd_active --dry-run --conf src/hd_active/hd_active.ini`.

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
inv lint all            # ruff check --fix + ruff format + ty check
inv lint all --check    # check-only mode, used in CI
inv lint ruff <path>    # just ruff
inv lint ty [path]      # just ty
```
Ruff line length is 100, single-quote formatting, targets py312. ty excludes
`src/hd_active/ui/forms` (generated Qt code — see below). Both are configured in `pyproject.toml`.

Pre-commit:
```bash
inv precommit install                 # run once after cloning
inv precommit run [--hook <hook-id>]  # all files; optionally a single hook
```

Qt UI generation — `.ui`/`.qrc` files live under `assets/ui`; never hand-edit the generated output:
```bash
inv ui py [file]     # pyside6-uic: .ui -> src/hd_active/ui/forms/ui_<name>.py
inv ui rc [file]     # pyside6-rcc: .qrc -> src/hd_active/ui/forms/<name>_rc.py
inv ui edit <file>   # open a .ui file in Qt Designer
```

Docs (mkdocs):
```bash
uv sync --group docs   # docs dependencies aren't in the default groups
inv docs serve    # `mkdocs serve`
inv docs deploy   # `mkdocs gh-deploy`, publishes to https://joaonc.github.io/hd_active
```

Build/release (see `admin/build.py` for the full flow — bumps version across `pyproject.toml` and
`src/hd_active/__init__.py`, optionally commits/pushes/creates a PR via `gh`):
```bash
inv build version --bump patch|minor|major [--mode nothing|commit|pr]
inv build publish   # uv build [+ uv publish]
inv build clean
```

## Architecture

- `hd_active.py` — `HdActive`, the core engine. Holds a set of drive paths and runs a daemon
  `threading.Thread` that loops writing random bytes to a marker file (`_hd_active.txt`) on each
  drive then deleting it, waiting `wait` seconds between rounds on a `threading.Event` (so `stop()`
  is immediate and joins the thread). A drive that fails (`OSError`) is logged and doesn't affect
  the others. Exposes `start()`/`stop()`/`toggle()`, a `dry_run` flag, optional plain-Python
  callbacks (`on_state_changed`, `on_log`, the latter called from the worker thread) and a bounded
  `log` of `LogEntry` dataclasses. State shared with the thread is guarded by a lock. This class has
  no Qt dependency and is unit-testable in isolation (see `tests/test_hd_active.py`).
- `hd_active_config.py` — `HdActiveConfig`, a dataclass (drives, wait interval, run-on-start flag)
  with `load(path)`/`save(path)` for the INI file, using `configparser` with a custom `list`
  converter for comma-separated drive lists.
- `cli.py` — `argparse` entry point with the `gui` (default), `run` and `config show|init`
  commands. Only `gui` imports Qt (lazily), everything else works without a display.
- `ui/app.py` — `run_gui()`: creates the `QApplication` (`setQuitOnLastWindowClosed(False)`), checks
  for a system tray, loads the config (defaults if the file doesn't exist), wires controller and
  tray icon and stops the engine on `aboutToQuit`.
- `ui/controller.py` — `HdActiveController`, a `QObject` that owns the `HdActive` instance and the
  config. Turns the engine callbacks into signals (`state_changed`, `log_added`, `error`,
  `config_changed`), which reach the UI queued in the GUI thread. `apply_config()` saves the INI
  file and applies the settings to the running engine. **All UI code goes through the controller**:
  connect to its signals rather than polling the engine or touching widgets from the worker thread.
- `ui/system_tray_icon.py` — `SystemTrayIcon`: tray context menu (start/stop, settings, log, about,
  exit), tooltip with the state, notifications on write errors. Owns the single instance of each
  dialog.
- `ui/settings_dialog.py`, `ui/log_dialog.py` — dialogs that *have* a generated form
  (`self.ui = Ui_*()`, composition rather than inheritance) from `ui/forms/` (auto-generated from
  `assets/ui/*.ui` via `inv ui py`; don't edit these by hand). Images come from Qt resources
  (`:/images/...`, compiled into `ui/forms/resources_rc.py` with `inv ui rc`), not from file paths.
- `utils.py` — small shared helpers: `FilePath` type alias and `is_truthy()`, a permissive
  string/number/bool truthiness parser (raises on ambiguous input unless told not to) used for
  env-var flags like `HD_ACTION_DEBUG`.
- `admin/` — all `inv` task definitions (one module per concern: `build`, `docs`, `lint`,
  `precommit`, `test`, `ui`), registered via `[tool.typer-invoke]` in `pyproject.toml`.

## Notes

- The core drive-writing logic in `HdActive` is UI-independent by design — prefer testing it
  directly rather than through the Qt layer where possible. UI tests (`tests/test_ui.py`) use
  `pytest-qt` and run with the `offscreen` Qt platform (set in `tests/conftest.py`).
- Tests wait on events/signals (`threading.Condition`, `qtbot.waitSignal`), not on `time.sleep`.
- CI installs with `uv sync` and runs everything through `uv run`. `tests.yml` runs the test matrix on `windows-latest` across Python 3.12 and 3.15 (the
  min/max of the supported range per `pyproject.toml`, `>=3.12,<3.16`).
