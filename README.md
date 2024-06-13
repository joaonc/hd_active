# HD Active

Prevent external HD's from becoming inactive (sleeping).

**[https://joaonc.github.io/hd_active](https://joaonc.github.io/hd_active)**

## Quick start
```
python -m app.hd_active --conf app/hd_active.ini
```

## Development
Note: Best to work on a virtual environment.
This page doesn't go into how to do that.

Install the development packages:
```
python -m pip install -r dev-requirements.txt
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
