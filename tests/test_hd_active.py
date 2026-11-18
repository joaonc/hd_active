import threading
from pathlib import Path
from unittest.mock import patch

import pytest

from hd_active.hd_active import FILE_NAME, HdActive, LogEntry

WAIT = 0.05
TIMEOUT = 5
"""Max time to wait for something to happen in the background thread. Normally immediate."""


class Recorder:
    """
    Callbacks for ``HdActive`` that record the calls and allow waiting for them.
    """

    def __init__(self):
        self.entries: list[LogEntry] = []
        self.states: list[bool] = []
        self._condition = threading.Condition()

    def on_log(self, entry: LogEntry):
        with self._condition:
            self.entries.append(entry)
            self._condition.notify_all()

    def on_state_changed(self, is_running: bool):
        with self._condition:
            self.states.append(is_running)
            self._condition.notify_all()

    def wait_for_entries(self, count: int):
        with self._condition:
            assert self._condition.wait_for(lambda: len(self.entries) >= count, TIMEOUT), (
                f'Expected {count} log entries, got {len(self.entries)}.'
            )


@pytest.fixture
def recorder():
    return Recorder()


@pytest.fixture
def make_hd_active(recorder):
    """
    Factory of ``HdActive`` instances wired to ``recorder`` and stopped at the end of the test.
    """
    instances = []

    def factory(drive_paths=('z',), wait=WAIT, **kwargs) -> HdActive:
        hd_active = HdActive(
            drive_paths,
            wait=wait,
            on_log=recorder.on_log,
            on_state_changed=recorder.on_state_changed,
            **kwargs,
        )
        instances.append(hd_active)
        return hd_active

    yield factory
    for instance in instances:
        instance.stop()


@pytest.fixture
def mock_write_hd():
    with patch('hd_active.hd_active.HdActive._write_hd', return_value=1000) as mock:
        yield mock


class TestStartStop:
    def test_instantiate_default_not_started(self, mock_write_hd):
        hd_active = HdActive(drive_paths=['z'])

        assert hd_active.is_running is False
        assert hd_active._thread is None
        mock_write_hd.assert_not_called()

    def test_instantiate_starts(self, mock_write_hd, make_hd_active, recorder):
        hd_active = make_hd_active(run=True)

        assert hd_active.is_running is True
        recorder.wait_for_entries(1)
        mock_write_hd.assert_called_with(Path('z'))

    def test_writes_repeatedly(self, mock_write_hd, make_hd_active, recorder):
        make_hd_active(run=True)

        recorder.wait_for_entries(3)

    def test_start_without_drives_does_nothing(self, make_hd_active, recorder):
        hd_active = make_hd_active(drive_paths=())

        assert hd_active.start() is False
        assert hd_active.is_running is False
        assert recorder.states == []

    def test_start_twice_uses_one_thread(self, mock_write_hd, make_hd_active):
        hd_active = make_hd_active(wait=60)

        assert hd_active.start() is True
        thread = hd_active._thread
        assert hd_active.start() is True

        assert hd_active._thread is thread

    def test_stop_is_immediate(self, mock_write_hd, make_hd_active, recorder):
        """
        Stopping doesn't wait for the time between writes to elapse.
        """
        hd_active = make_hd_active(wait=60, run=True)
        recorder.wait_for_entries(1)
        thread = hd_active._thread
        assert thread is not None

        hd_active.stop(timeout=TIMEOUT)

        assert hd_active.is_running is False
        assert not thread.is_alive()

    def test_stop_when_not_started(self, make_hd_active):
        hd_active = make_hd_active()
        hd_active.stop()
        assert hd_active.is_running is False

    def test_restart(self, mock_write_hd, make_hd_active, recorder):
        hd_active = make_hd_active(wait=60, run=True)
        recorder.wait_for_entries(1)
        hd_active.stop()

        hd_active.start()

        recorder.wait_for_entries(2)
        assert hd_active.is_running is True

    def test_toggle(self, mock_write_hd, make_hd_active):
        hd_active = make_hd_active(wait=60)

        assert hd_active.toggle() is True
        assert hd_active.is_running is True
        assert hd_active.toggle() is False
        assert hd_active.is_running is False

    def test_state_changed_callback(self, mock_write_hd, make_hd_active, recorder):
        hd_active = make_hd_active(wait=60)

        hd_active.start()
        hd_active.start()
        hd_active.stop()
        hd_active.stop()

        assert recorder.states == [True, False]

    def test_unexpected_error_stops(self, make_hd_active, recorder):
        """
        If the background thread dies, the state reflects it.
        """
        with patch('hd_active.hd_active.HdActive._write_hd', side_effect=RuntimeError('boom')):
            hd_active = make_hd_active(wait=60, run=True)
            thread = hd_active._thread
            assert thread is not None
            thread.join(TIMEOUT)

        assert hd_active.is_running is False
        assert recorder.states == [True, False]


class TestDrives:
    @pytest.mark.parametrize(
        'drive_paths',
        [
            pytest.param(['a:\\', 'b:\\'], marks=pytest.mark.windows),
            (Path('a'), Path('b')),
            ['a', 'a', Path('a')],
        ],
    )
    def test_instantiate(self, drive_paths):
        hd_active = HdActive(drive_paths=drive_paths)
        assert hd_active.drive_paths == {Path(drive_path) for drive_path in drive_paths}

    def test_add_remove_set(self):
        hd_active = HdActive(drive_paths=['a'])

        hd_active.add_hd('b')
        hd_active.add_hds(['c', 'd'])
        hd_active.remove_hd('a')
        assert hd_active.drive_paths == {Path('b'), Path('c'), Path('d')}

        hd_active.set_hds(['e'])
        assert hd_active.drive_paths == {Path('e')}

    def test_drive_paths_is_a_snapshot(self):
        hd_active = HdActive(drive_paths=['a'])
        drive_paths = hd_active.drive_paths
        hd_active.add_hd('b')
        assert drive_paths == {Path('a')}

    @pytest.mark.parametrize('wait', [0, -1])
    def test_invalid_wait(self, wait):
        with pytest.raises(ValueError):
            HdActive(wait=wait)


class TestWrite:
    def test_write_hd(self, tmp_path):
        """
        The real thing: writes to the drive and cleans up.
        """
        assert HdActive._write_hd(tmp_path) == 10_000
        assert not (tmp_path / FILE_NAME).exists()

    def test_write_hds_logs(self, tmp_path):
        drive_1 = tmp_path / '1'
        drive_2 = tmp_path / '2'
        drive_1.mkdir()
        drive_2.mkdir()
        hd_active = HdActive(drive_paths=[drive_2, drive_1])

        entries = hd_active.write_hds()

        assert hd_active.log == tuple(entries)
        assert [(e.drive_path, e.bytes_written, e.error) for e in entries] == [
            (drive_1, 10_000, None),
            (drive_2, 10_000, None),
        ]
        assert str(entries[0]).endswith(f'10000 bytes written to {drive_1}')

    def test_error_in_one_drive_doesnt_affect_others(self, tmp_path):
        missing = tmp_path / 'a_missing'
        existing = tmp_path / 'b_existing'
        existing.mkdir()
        hd_active = HdActive(drive_paths=[missing, existing])

        entry_missing, entry_existing = hd_active.write_hds()

        assert entry_missing.error
        assert 'ERROR' in str(entry_missing)
        assert entry_existing.error is None
        assert entry_existing.bytes_written == 10_000

    def test_keeps_running_after_error(self, tmp_path, make_hd_active, recorder):
        hd_active = make_hd_active(drive_paths=[tmp_path / 'missing'], run=True)

        recorder.wait_for_entries(2)

        assert hd_active.is_running is True
        assert all(entry.error for entry in recorder.entries)

    def test_dry_run(self, mock_write_hd, tmp_path):
        hd_active = HdActive(drive_paths=[tmp_path], dry_run=True)

        (entry,) = hd_active.write_hds()

        mock_write_hd.assert_not_called()
        assert entry.dry_run is True
        assert 'dry run' in str(entry)

    def test_log_is_bounded(self, mock_write_hd):
        with patch('hd_active.hd_active.LOG_MAX_ENTRIES', 3):
            hd_active = HdActive(drive_paths=['z'])
        for _ in range(5):
            hd_active.write_hds()
        assert len(hd_active.log) == 3
