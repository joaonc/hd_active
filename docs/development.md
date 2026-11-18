# Development

To get started with development of this project:

1. Clone
2. Install [uv](https://docs.astral.sh/uv/getting-started/installation/), which manages the Python
   version, virtual environment (`.venv`) and dependencies.
3. `uv sync`
4. `uv run inv precommit install`

Prefix commands with `uv run` (ex: `uv run inv --help`) or activate the `.venv` first.

## UI
This project uses [Qt 6](https://www.qt.io) for its UI components.

`Qt Designer` is used to create the UI, which outputs a `.ui` file (XML content that describes the
UI). This file is then transformed into a `.py` file.

All the required tools are available by installing `pyside6`:

* `Qt Designer`: `pyside6-designer`
* `.ui > .py` Converter: `pyside6-uic`
* `.qrc > .py` Converter (resources, like images): `pyside6-rcc`

These are wrapped in `inv` tasks:
```
uv run inv ui edit settings_dialog   # Open in Qt Designer
uv run inv ui py                     # assets/ui/*.ui  > src/hd_active/ui/forms/ui_*.py
uv run inv ui rc                     # assets/*.qrc    > src/hd_active/ui/forms/*_rc.py
```
The generated files under `src/hd_active/ui/forms` should not be edited by hand.

### Structure
* `HdActive` (`hd_active.py`) is the engine. It doesn't depend on Qt and does the writing in a
  background thread.
* `HdActiveController` (`ui/controller.py`) wraps the engine in a `QObject` and exposes what
  happens in it as Qt signals, delivered in the GUI thread.
* The tray icon and the dialogs only talk to the controller: they call its slots and connect to
  its signals, never polling the engine nor touching widgets from the background thread.
* Dialogs _have_ a generated form (`self.ui = Ui_...()`) instead of inheriting from it.
* Images are loaded from Qt resources (`:/images/...`), so they work regardless of how the app is
  installed.

To try the UI without writing to any drive: `uv run hd_active --dry-run`.

!!! Note

    Qt is not necessarily required, something like Tkinter could have been used (more open and
    included in Python), and the latest version of Qt (6) isn't necessary, something more
    established like Qt 5 could have been used, but I wanted to dip my toes into the Qt world and
    figured using the latest version would give me more lasting knowledge.

## Test
[pytest](https://pytest.org) is used for testing and main features used are fixtures, parameters
and markers. When working on test cases, make sure you're familiar with how these work.

### Markers
Markers are used to distinguish tests with `pytest.mark.<marker_name>`.

List of markers used, defined in `pyproject.toml`

| Marker | Description                                       |
|:-------|:--------------------------------------------------|
| `windows` | Test case valid on Windows operating system only. |

## Linting and type checking
[Ruff](https://docs.astral.sh/ruff/) is used for linting and formatting and
[ty](https://docs.astral.sh/ty/) for type checking. Configuration for both is in `pyproject.toml`.

```
uv run inv lint all           # Fix and format (ruff), then type check (ty)
uv run inv lint all --check   # Check only, as done in CI
```

## Dependencies
Dependencies are declared in `pyproject.toml` and locked in `uv.lock`.

```
uv add <package>                  # Add a runtime dependency
uv add --group dev <package>      # Add a dev dependency
uv lock --upgrade                 # Upgrade all dependencies
uv lock --upgrade-package <pkg>   # Upgrade one dependency
uv sync                           # Sync the environment with the lock file
```

## Development tasks
This project uses [typer-invoke](https://github.com/joaonc/typer-invoke) (`inv`) to facilitate
executing miscellaneous tasks that help with development.

### Using inv
List all available tasks:
```
uv run inv --help
```

Help with a certain task:
```
uv run inv lint --help
```

Use `--dry` to see what the task does without executing it.

## Documentation
Install documentation requirements with:
```
uv sync --group docs
```

You can then edit the `.md` files under the `docs` directory and, if more need to be added, update
`mkdocs.yml`.

### View locally

* Web server (recommended)
  ```
  mkdocs serve
  ```
* Static files
  ```
  mkdocs build
  ```
  This generates a static website under `/site`, which is in `.gitignore`.

### Update in GitHub

Simply run the command below to push the documentation to GitHub pages.

```
mkdocs gh-deploy
```

More instructions [here](https://www.mkdocs.org/user-guide/deploying-your-docs/#github-pages).

The first time `gh-deploy` is used, authorization needs to be granted to publish to GitHub Pages.
A _GitHubCredentials_ widget appears and follow the prompts.

Documentation available here: [https://joaonc.github.io/hd_active](https://joaonc.github.io/hd_active)

When running this command, it's this website that needs to be updated (unless working in a forked
project). Until a process is established for other people to update this GitHub Page location,
please contact me and I'll push the documentation changes as needed.
