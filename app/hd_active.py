import threading
import time
from os import PathLike
from pathlib import Path
from typing import Iterable, Optional, Set, Union

from app.hd_action_state import HdActionState

FILE_NAME = '_hd_active.txt'


class HdActive:
    def __init__(
        self,
        drive_paths=Optional[Iterable[PathLike]],
        run: bool = False,
        wait: Union[int, float] = 1,
    ):
        self._drive_paths: Set[Path] = set()
        if drive_paths is not None:
            self.add_hds(drive_paths)
        self._is_running = False
        self._write_hd_thread = None
        self.wait = wait
        if run:
            self.start()

    @staticmethod
    def _write_hd(drive_path: Path) -> None:
        file_path = drive_path / FILE_NAME
        file_path.open('w').write(str(time.time()))
        file_path.unlink()

    def write_hds(self) -> None:
        for drive_path in self._drive_paths:
            self._write_hd(drive_path)

    def _do_write_hd(self):
        while self.is_running:
            self.write_hds()
            time.sleep(self.wait)

    def add_hds(self, drive_paths: Iterable[PathLike]):
        self._drive_paths.update(Path(drive_path) for drive_path in drive_paths)

    def add_hd(self, drive_path: PathLike):
        self.add_hds((drive_path,))

    def remove_hd(self, drive_path: PathLike):
        self._drive_paths.remove(Path(drive_path))

    @property
    def drive_paths(self):
        return self._drive_paths

    @property
    def is_running(self):
        """
        Use `start` and `stop` to change state.
        """
        return self._is_running

    def _wait_write_hd_thread(self):
        """
        Waits for the thread that accesses the drives to exit.
        """
        if self._write_hd_thread is not None:
            timeout = self.wait * len(self.drive_paths) * 2
            time_sleep = self.wait
            time_waited = 0
            while self._write_hd_thread.is_alive():
                time.sleep(time_sleep)
                time_waited += time_sleep
                if time_waited > timeout:
                    raise Exception('Timeout while waiting for thread that accesses drives to finish.')

            self._write_hd_thread = None

    def start(self):
        if not self.is_running:
            self._wait_write_hd_thread()
            self._is_running = True
            self._write_hd_thread = threading.Thread(target=self._do_write_hd)
            self._write_hd_thread.start()

    def stop(self, wait=False):
        if self.is_running:
            self._is_running = False
        if wait:
            self._wait_write_hd_thread()

    def get_change_state(self) -> HdActionState:
        return HdActionState.Stop if self.is_running else HdActionState.Start

    def change_state(self) -> HdActionState:
        """
        Changes the current state (starts if stopped, stops if started).

        :return: The action required to change state again.
        """
        if self.is_running:
            self.stop()
            return HdActionState.Start
        self.start()
        return HdActionState.Stop
