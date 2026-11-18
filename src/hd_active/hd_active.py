"""
Core engine. No Qt dependency, so it can be used from the CLI and tested in isolation.
"""

import logging
import threading
from collections import deque
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import datetime
from os import urandom
from pathlib import Path

from .utils import FilePath

FILE_NAME = '_hd_active.txt'
LOG_MAX_ENTRIES = 1000
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LogEntry:
    """
    Result of one attempt at keeping a drive active.
    """

    time: datetime
    drive_path: Path
    bytes_written: int = 0
    error: str | None = None
    dry_run: bool = False

    def __str__(self) -> str:
        t = self.time.isoformat(timespec='seconds')
        if self.error is not None:
            return f'{t}: ERROR writing to {self.drive_path}: {self.error}'
        if self.dry_run:
            return f'{t}: dry run, nothing written to {self.drive_path}'
        return f'{t}: {self.bytes_written} bytes written to {self.drive_path}'


class HdActive:
    """
    Keeps drives active by periodically writing and deleting a small file in each one.

    The writing is done in a background thread, controlled with :meth:`start` and :meth:`stop`.

    :param drive_paths: Drives (or any directory) to keep active.
    :param run: Start right away.
    :param wait: Seconds to wait between rounds of writes.
    :param dry_run: Go through the motions, but don't touch the drives.
    :param on_state_changed: Called with the new value of :attr:`is_running` when it changes.
        May be called from the background thread.
    :param on_log: Called with each new :class:`LogEntry`, from the background thread.
    """

    def __init__(
        self,
        drive_paths: Iterable[FilePath] | None = None,
        run: bool = False,
        wait: int | float = 1,
        dry_run: bool = False,
        on_state_changed: Callable[[bool], None] | None = None,
        on_log: Callable[[LogEntry], None] | None = None,
    ):
        # Guards the attributes shared with the background thread.
        self._lock = threading.Lock()
        self._drive_paths: set[Path] = set()
        # `deque` instead of `list` to prevent from growing indefinitely.
        self._log: deque[LogEntry] = deque(maxlen=LOG_MAX_ENTRIES)
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._is_running = False
        self._wait: float = 1
        self.wait = wait
        self.dry_run = dry_run
        self.on_state_changed = on_state_changed
        self.on_log = on_log

        if drive_paths is not None:
            self.add_hds(drive_paths)
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

        try:
            # Binary mode required to switch buffering off.
            with file_path.open('wb', buffering=0) as f:
                for _ in range(writes_count):
                    bytes_written += f.write(urandom(bytes_per_write))
        finally:
            file_path.unlink(missing_ok=True)
        return bytes_written

    def write_hds(self) -> list[LogEntry]:
        """
        Do one round of writes, one per drive.

        A drive that can't be written to (ex: unplugged) is logged and doesn't affect the others.
        """
        drive_paths = sorted(self.drive_paths)
        logger.debug('Writing to %s HD(s).', len(drive_paths))
        entries = []
        for drive_path in drive_paths:
            now = datetime.now()
            if self.dry_run:
                entry = LogEntry(now, drive_path, dry_run=True)
            else:
                try:
                    entry = LogEntry(now, drive_path, bytes_written=self._write_hd(drive_path))
                except OSError as e:
                    entry = LogEntry(now, drive_path, error=str(e))
            logger.debug('%s', entry)

            with self._lock:
                self._log.append(entry)
            entries.append(entry)
            if self.on_log is not None:
                self.on_log(entry)
        return entries

    def _run(self, stop_event: threading.Event):
        """
        Target of the background thread.
        """
        try:
            while not stop_event.is_set():
                self.write_hds()
                # Unlike `time.sleep`, returns as soon as stop is requested.
                stop_event.wait(self.wait)
        except Exception:
            logger.exception('Unexpected error, HD Active stopped.')
        finally:
            # Only relevant when the loop died on its own; `stop` has already done this otherwise.
            if not stop_event.is_set():
                stop_event.set()
                self._set_is_running(False)

    def _set_is_running(self, value: bool):
        with self._lock:
            changed = self._is_running != value
            self._is_running = value
        if changed and self.on_state_changed is not None:
            self.on_state_changed(value)

    def add_hds(self, drive_paths: Iterable[FilePath]):
        paths = {Path(drive_path) for drive_path in drive_paths}
        with self._lock:
            self._drive_paths.update(paths)

    def add_hd(self, drive_path: FilePath):
        self.add_hds([drive_path])

    def remove_hd(self, drive_path: FilePath):
        with self._lock:
            self._drive_paths.remove(Path(drive_path))

    def set_hds(self, drive_paths: Iterable[FilePath]):
        """
        Replace all the drives.
        """
        paths = {Path(drive_path) for drive_path in drive_paths}
        with self._lock:
            self._drive_paths = paths

    @property
    def drive_paths(self) -> frozenset[Path]:
        """
        Snapshot of the drives. Use `add_hd(s)`, `remove_hd` and `set_hds` to change them.
        """
        with self._lock:
            return frozenset(self._drive_paths)

    @property
    def wait(self) -> float:
        """
        Seconds to wait between rounds of writes.

        If changed while running, takes effect after the current wait.
        """
        return self._wait

    @wait.setter
    def wait(self, value: int | float):
        if value <= 0:
            raise ValueError(f'`wait` must be greater than 0, got {value}.')
        self._wait = value

    @property
    def is_running(self) -> bool:
        """
        Use `start` and `stop` to change state.
        """
        with self._lock:
            return self._is_running

    @property
    def log(self) -> tuple[LogEntry, ...]:
        """
        Snapshot of the most recent log entries, oldest first.
        """
        with self._lock:
            return tuple(self._log)

    def start(self) -> bool:
        """
        Start writing to the drives. Does nothing if already started or if there are no drives.

        :return: Whether it's running.
        """
        if self.is_running:
            logger.info('HD Active already started, do nothing.')
            return True
        if not self.drive_paths:
            logger.warning('No drives specified.')
            return False

        logger.info('Starting HD Active.')
        self._join()
        # One event per thread, so a previous thread that's still exiting isn't revived.
        self._stop_event = threading.Event()
        # Daemon so that a write stuck on an unresponsive drive can't prevent the app from exiting.
        self._thread = threading.Thread(
            target=self._run, args=(self._stop_event,), name='hd_active', daemon=True
        )
        self._set_is_running(True)
        self._thread.start()
        return True

    def stop(self, timeout: float | None = 5):
        """
        Stop writing to the drives and wait for the background thread to exit.

        :param timeout: Max seconds to wait for a write in progress to finish. ``None`` to wait
            indefinitely.
        """
        if self.is_running:
            logger.info('Stopping HD Active.')
        self._stop_event.set()
        self._set_is_running(False)
        self._join(timeout)

    def _join(self, timeout: float | None = 5):
        thread = self._thread
        if thread is None or thread is threading.current_thread():
            return
        thread.join(timeout)
        if thread.is_alive():
            logger.warning('Timeout while waiting for thread that accesses drives to finish.')
        else:
            self._thread = None

    def toggle(self) -> bool:
        """
        Changes the current state (starts if stopped, stops if started).

        :return: Whether it's running.
        """
        if self.is_running:
            self.stop()
            return False
        return self.start()
