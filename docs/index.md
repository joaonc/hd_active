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
python -m app.hd_active --conf app/hd_active.ini
```

## Config file
The file `hd_active.ini`, located in the same folder as the app, is used to persist settings.

The file is created/updated when settings change.

**Options:**

* `run_on_start`: Whether _HD Active_ should start pinging drives when it runs. If `False`, the
  user needs to click _Start_.
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
