import threading
import time
from pathlib import Path
from typing import Optional, Union

FILE_NAME = '_hd_active.txt'


class HdActive:
    def __init__(self, drive_paths=Optional[list], run: bool = False, wait: Union[int, float] = 1):
        self.drive_paths = drive_paths or []
        self._is_running = False
        self.wait = wait
        if run:
            self.start()

    @staticmethod
    def _write_hd(drive_path: Path) -> None:
        file_path = Path(drive_path)
        if file_path.is_dir():
            file_path /= FILE_NAME
        if not file_path.parent.exists():
            raise FileNotFoundError(file_path)
        file_path.open('w').write(str(time.time()))
        file_path.unlink()

    def write_hds(self) -> None:
        for drive_path in self.drive_paths:
            self._write_hd(drive_path)

    def _do_write_hd(self):
        while self.is_running:
            self.write_hds()
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
