# HD Active

Prevent external HD's from becoming inactive (sleeping).

## Config file
The file `hd_active.ini`, located in the same folder as the app, is used to persist settings.

The file is created/updated when settings change.

**Options:**

* `run_on_start`: Whether _HD Active_ should start pinging drives when it runs. If `False`, the user needs to click
  _Start_.
* `wait_between_access`: Time, in seconds, to wait between drive pings. If too long, the drives may go to sleep, if too
  short, drives will be pinged unnecessarily, although this is not a big issue.
* `drives`: Which drives to ping. This is a comma separated list and doesn't need to have quotes, ex: `e,f,g` or
  `e:\, f:\, g:\`.

**Sample:**
```
[HD Active]
run_on_start = True
wait_between_access = 60
drives = e:\, f:\, g:\
```
