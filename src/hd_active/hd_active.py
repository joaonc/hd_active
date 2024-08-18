import logging
import threading
import time
from collections import deque
from datetime import datetime
from os import PathLike, urandom
from pathlib import Path
from typing import Deque, Iterable, Optional, Set, Union

from src.hd_active.hd_action_state import HdActionState

FILE_NAME = '_hd_active.txt'
logger = logging.getLogger(__name__)


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
        # `deque` instead of `list` to prevent from growing indefinitely
        self._log: Deque[str] = deque(maxlen=1000)
        self.wait = wait
        if run:
            self.start()

    @staticmethod
    def _write_hd(drive_path: Path) -> int:
        """
        Does the actual writing of data to the drive.

        :return: Number of bytes written.
        """
        file_path = drive_path / FILE_NAME
        bytes_written = 0
        bytes_per_write = 1000
        writes_count = 10

        # Binary mode required to switch buffering off.
        with file_path.open('wb', buffering=0) as f:
            for _ in range(writes_count):
                f.write(urandom(bytes_per_write))
                bytes_written += bytes_per_write

        file_path.unlink()
        return bytes_written

    def write_hds(self) -> None:
        logger.debug(f'Writing to {len(self._drive_paths)} HD(s).')
        t = datetime.now().isoformat(timespec='seconds')
        for drive_path in self._drive_paths:
            b = self._write_hd(drive_path)

            msg = f'{t}: {b} bytes written to {drive_path}'
            self._log.append(msg)

    def _do_write_hd(self):
        while self.is_running:
            self.write_hds()
            time.sleep(self.wait)

    def add_hds(self, drive_paths: Iterable[PathLike]):
        self._drive_paths.update(Path(drive_path) for drive_path in drive_paths)

    def add_hd(self, drive_path: PathLike):
        self.add_hds([drive_path])

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

    @property
    def log(self):
        return self._log

    def _wait_write_hd_thread(self):
        """
        Waits for the thread that accesses the drives to exit.
        """
        if self._write_hd_thread is not None:
            logger.info('Waiting for HD write thread to finish.')
            timeout = self.wait * len(self.drive_paths) * 2
            time_sleep = self.wait
            time_waited = 0
            while self._write_hd_thread.is_alive():
                time.sleep(time_sleep)
                time_waited += time_sleep
                if time_waited > timeout:
                    raise Exception(
                        'Timeout while waiting for thread that accesses drives to finish.'
                    )

            self._write_hd_thread = None

    def start(self):
        if not self._drive_paths:
            logger.warning('No drives specified.')
            return
        if self.is_running:
            logger.info('HD Active already started, do nothing.')
        else:
            logger.info('Starting HD Active.')
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


if __name__ == '__main__':
    import argparse
    import sys

    from src.hd_active.hd_active_config import HdActiveConfig

    parser = argparse.ArgumentParser(description='Keep HDs active.')
    parser.add_argument(
        '--conf',
        default='hd_active.ini',
        help='Config file to use.',
    )
    parser.add_argument(
        '--log',
        choices=['info', 'debug'],
        required=False,
        help='Set logging for more info.',
    )

    args = parser.parse_args()
    if args.log:
        log_level = args.log.upper()
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setLevel(log_level)
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(handler)
        logger.setLevel(log_level)
    config = HdActiveConfig(args.conf)
    hd_active = HdActive(drive_paths=config.drive_paths, run=config.run, wait=config.wait)
    hd_active.start()
    print(f'HD Active started.\n{config}')
    while True:
        x = input('Type `s` to stop: ')
        if x.lower() == 's':
            break
    print('Stopping HD Active.')
    hd_active.stop(wait=True)
    print('HD Active stopped. Exiting.')
