# HD Active

[![pypi](https://img.shields.io/pypi/v/hd_active.svg)](https://pypi.org/project/hd_active/)
[![Project License - MIT](https://img.shields.io/pypi/l/hd_active.svg)](https://github.com/joaonc/show_dialog/blob/main/LICENSE.txt)

Prevent external HD's from becoming inactive (sleeping).

In a world of SSD's, an app like this is not as needed, but if you still have an HD hooked up that
goes to sleep and takes a while to access, this app can help.

In my particular case, have an HD that constantly goes to sleep and can't find the drivers to
prevent that. Wanted to learn a bit more about Qt, so went ahead and made this.

**[https://joaonc.github.io/hd_active](https://joaonc.github.io/hd_active)**

## Quick start
```
hd_active                  # Run in the system tray (same as `hd_active gui`)
hd_active run              # Run in the console, without UI, until Ctrl+C
hd_active config init --drive e:\ --drive f:\ --wait 30
hd_active config show
```

Options common to all commands: `--conf FILE` (default: `hd_active.ini` in the current directory)
and `--log LEVEL`. `gui` and `run` also accept `--dry-run`, to not write to the drives.
See `hd_active --help` for more.

## Development
This project is managed with [uv](https://docs.astral.sh/uv/getting-started/installation/), which
needs to be installed first.

Create the virtual environment and install the development packages:
```
uv sync
```

This project uses [typer-invoke](https://github.com/joaonc/typer-invoke) to facilitate common tasks.
For a list of tasks:
```
uv run inv --help
```

## Licensing
Even though I'm providing this code under the MIT license, [Qt](https://www.qt.io) is used for the
UI component, meaning you'll be bound to its GPL/LGPL license (more info
[here](https://www.qt.io/licensing/open-source-lgpl-obligations)).

I'm not an expert on these things, so be advised.
