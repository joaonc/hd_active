# Copyright 2022 Joao Coelho - MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import threading
import time
from pathlib import Path

FILE_NAME = '_HD_ACTIVE.TXT'


class HdActive:
    def __init__(self, drive_paths=None, run=False, wait=1):
        self.drive_paths = drive_paths or []
        self._is_running = False
        self.wait = wait
        if run:
            self.start()

    def write_hd(self) -> None:
        for drive_path in self.drive_paths:
            file_path = Path(drive_path)
            if file_path.is_dir():
                file_path /= FILE_NAME
            if not file_path.parent.exists():
                raise FileNotFoundError(file_path)
            file_path.open('w').write(str(time.time()))
            file_path.unlink()

    def _do_write_hd(self):
        while self.is_running:
            self.write_hd()
            time.sleep(self.wait)

    @property
    def is_running(self):
        """
        Use `start` and `stop` to change state.
        """
        return self._is_running

    def start(self):
        if not self.is_running:
            self._is_running = True
            write_hd_thread = threading.Thread(target=self._do_write_hd)
            write_hd_thread.start()

    def stop(self):
        if self.is_running:
            self._is_running = False
