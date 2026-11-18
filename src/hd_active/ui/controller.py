from dataclasses import replace
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from ..hd_active import HdActive, LogEntry
from ..hd_active_config import HdActiveConfig
from ..utils import FilePath


class HdActiveController(QObject):
    """
    Bridge between the ``HdActive`` engine and the UI.

    The engine reports from its own (non Qt) thread. Here that's turned into signals which, being
    emitted from a different thread than the one this object lives in, are delivered to the slots
    queued in the GUI thread. The UI only needs to connect to the signals.
    """

    state_changed = Signal(bool)
    """Started (``True``) or stopped (``False``)."""

    log_added = Signal(object)
    """New ``LogEntry``."""

    error = Signal(str)
    """A drive that was fine can no longer be written to. Not repeated until it recovers."""

    config_changed = Signal()

    def __init__(
        self,
        config: HdActiveConfig,
        config_file: FilePath,
        dry_run: bool = False,
        parent: QObject | None = None,
    ):
        super().__init__(parent)
        self._config = config
        self._config_file = Path(config_file)
        self._failing_drives: set[Path] = set()
        self._hd_active = HdActive(
            drive_paths=config.drive_paths,
            wait=config.wait,
            dry_run=dry_run,
            on_state_changed=self.state_changed.emit,
            on_log=self.log_added.emit,
        )
        self.log_added.connect(self._on_log_added)

    @property
    def config(self) -> HdActiveConfig:
        """
        Copy of the current config. Use ``apply_config`` to change it.
        """
        return replace(self._config, drive_paths=list(self._config.drive_paths))

    @property
    def config_file(self) -> Path:
        return self._config_file

    @property
    def dry_run(self) -> bool:
        return self._hd_active.dry_run

    @property
    def is_running(self) -> bool:
        return self._hd_active.is_running

    @property
    def log(self) -> tuple[LogEntry, ...]:
        return self._hd_active.log

    @Slot()
    def start(self) -> bool:
        return self._hd_active.start()

    @Slot()
    def stop(self):
        self._hd_active.stop()

    @Slot()
    def toggle(self) -> bool:
        return self._hd_active.toggle()

    def apply_config(self, config: HdActiveConfig):
        """
        Save the config to the config file and apply it, without changing the running state
        (unless there are no drives left, in which case it stops).

        :raises OSError: The config file couldn't be written. Nothing is applied.
        """
        config.save(self._config_file)
        self._config = replace(config, drive_paths=list(config.drive_paths))

        # Restart so that the new values are used right away instead of after the current wait.
        was_running = self.is_running
        if was_running:
            self._hd_active.stop()
        self._hd_active.set_hds(config.drive_paths)
        self._hd_active.wait = config.wait
        self._failing_drives.clear()
        if was_running:
            self._hd_active.start()
        self.config_changed.emit()

    @Slot(object)
    def _on_log_added(self, entry: LogEntry):
        if entry.error is None:
            self._failing_drives.discard(entry.drive_path)
        elif entry.drive_path not in self._failing_drives:
            self._failing_drives.add(entry.drive_path)
            self.error.emit(f'Could not write to {entry.drive_path}: {entry.error}')
