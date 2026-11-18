# HD Active

Prevent external HD's from becoming inactive (sleeping).

## About
The functionality of this project, as stated above, is to prevent external mechanical Hard Drives
from sleeping and avoid waiting for them to spin up when accessing.

The _objectives_ of this project, however are the following:

* Learn some [QT](https://www.qt.io) basics for UI development in Python.
* Use [MkDocs](https://www.mkdocs.org/) and the theme
  [MkDocs-Material](https://squidfunk.github.io/mkdocs-material/) for documentation.
* Use [PyInvoke](https://www.pyinvoke.org/) for misc tasks in lieu of the more widely used Makefile.  
  This has the following advantages:
    * Avoid the use of a different language for scripting.
    * Scripts are OS independent by using Python instead of an OS specific language like bash.
    * Scripts are easier to create and maintain (because Python :smiley:).
    * Other functionality that PyInvoke provides.
* CI with GitHub Actions.

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

## Commands

| Command | Description |
|:--------|:------------|
| `hd_active gui` | Run in the system tray. This is the default if no command is given. Settings are changed in the _Settings_ dialog and saved to the config file. |
| `hd_active run` | Run in the console, without UI, until interrupted with Ctrl+C. Doesn't need a display. |
| `hd_active config show` | Print the settings in the config file. |
| `hd_active config init` | Create a config file. Options: `--drive PATH` (multiple allowed), `--wait SECONDS`, `--run-on-start`, `--force`. |

`python -m hd_active` is equivalent to `hd_active`.

**Options:**

* `--conf FILE`: Config file to use. Default is `hd_active.ini` in the current directory.
* `--dry-run`: Do everything except writing to the drives. Useful for trying things out.
  Can also be enabled by setting the `HD_ACTION_DEBUG` environment variable to `true`.
* `--log LEVEL`: One of `debug`, `info`, `warning` (default), `error`.

## Config file
The file `hd_active.ini`, in the current directory by default (use `--conf` for a different one),
is used to persist settings.

The file is created/updated when settings are changed in the UI. It can also be created with
`hd_active config init` or by hand.

**Options:**

* `run_on_start`: Whether _HD Active_ should start pinging drives when the UI starts. If `False`,
  the user needs to click _Start_. Not used by `hd_active run`, which always starts.
* `wait_between_access`: Time, in seconds, to wait between drive pings. If too long, the drives may
  go to sleep, if too short, drives will be pinged unnecessarily, although this is not a big issue.
* `drives`: Which drives to ping. This is a comma separated list and doesn't need to have quotes,
  ex: `e,f,g` or `e:\, f:\, g:\`.

**Sample:**
```
[HD Active]
run_on_start = True
wait_between_access = 30
drives = e:\, f:\, g:\
```
