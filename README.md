# HD Active

[![pypi](https://img.shields.io/pypi/v/hd_active.svg)](https://pypi.python.org/pypi/hd_active)
[![Project License - MIT](https://img.shields.io/pypi/l/hd_active.svg)](https://github.com/joaonc/show_dialog/blob/main/LICENSE.txt)

Prevent external HD's from becoming inactive (sleeping).

**[https://joaonc.github.io/hd_active](https://joaonc.github.io/hd_active)**

## Quick start
```
python -m src.hd_active.hd_active --conf src/hd_active/hd_active.ini
```

## Development
Note: Best to work on a virtual environment.
This page doesn't go into how to do that.

Install the development packages:
```
python -m pip install -r requirements-def.txt
```

This project uses [pyinvoke](https://www.pyinvoke.org/) to facilitate common tasks.
For a list of tasks:
```
inv --list
```

## Licensing
Even though I'm providing this code under the MIT license, [Qt](https://www.qt.io) is used for the
UI component, meaning you'll be bound to its GPL/LGPL license (more info
[here](https://www.qt.io/licensing/open-source-lgpl-obligations)).

I'm not an expert on these things, so be advised.
