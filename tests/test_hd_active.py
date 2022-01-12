import time
from os import PathLike
from pathlib import Path
from typing import List
from unittest.mock import MagicMock, patch

import pytest
import pytest_check as check

from app.hd_action_state import HdActionState
from app.hd_active import HdActive

WAIT = 0.1
WAIT_TEST = 2 * WAIT


class HdActiveTest(HdActive):
    """
    Extend `HdActive` to change defaults for testing purposes.
    """

    def __init__(self, drive_paths=None, run=False, wait=WAIT):
        super().__init__(drive_paths, run, wait=wait)


@patch.object(Path, 'open', return_value=MagicMock())
@patch.object(Path, 'unlink', return_value=None)
class TestHdActive:
    def test_instantiate_not_started(self, mock_unlink, mock_open):
        hd_active = HdActiveTest(drive_paths=['z'], run=False)

        # Verify didn't start
        time.sleep(WAIT_TEST)
        assert hd_active.is_running is False
        mock_open.assert_not_called()
        mock_unlink.assert_not_called()

    def test_instantiate_default_not_started(self, mock_unlink, mock_open):
        """
        ``run`` argument not specified and defaults to ``False``.
        """
        # Note that `HdActive` if used and not `HdActiveTest`
        # to make sure it's the default for `HdActive` that's tested.
        hd_active = HdActive(drive_paths=['z'], wait=0.1)

        # Verify didn't start
        time.sleep(WAIT_TEST)
        assert hd_active.is_running is False
        mock_open.assert_not_called()
        mock_unlink.assert_not_called()

    def test_instantiate_starts_single_path(self, mock_unlink, mock_open):
        hd_active = HdActiveTest(drive_paths=['z'], run=True)

        # Verify started
        time.sleep(WAIT_TEST)
        assert hd_active.is_running is True
        hd_active.stop()
        mock_open.assert_called()
        mock_unlink.assert_called()

    @pytest.mark.parametrize(
        'drive_paths',
        [
            pytest.param(['a:\\', 'b:\\'], marks=pytest.mark.windows),
            (Path('a'), Path('b')),
        ],
    )
    def test_instantiate_starts_multiple_paths(self, mock_unlink, mock_open, drive_paths: List[PathLike]):
        hd_active = HdActiveTest(drive_paths=drive_paths, run=True)

        time.sleep(WAIT_TEST)
        assert hd_active.is_running is True
        hd_active.stop()

        expected_drive_paths = {Path(drive_path).drive for drive_path in drive_paths}
        assert {drive_path.drive for drive_path in hd_active.drive_paths} == expected_drive_paths

    @pytest.mark.parametrize('run, expected_change_state', [(True, HdActionState.Stop), (False, HdActionState.Start)])
    def test_get_change_state(self, mock_unlink, mock_open, run, expected_change_state):
        hd_active = HdActiveTest(drive_paths=['z'], run=run)
        assert hd_active.get_change_state() is expected_change_state

    @pytest.mark.parametrize('run, expected_change_state', [(True, HdActionState.Start), (False, HdActionState.Stop)])
    def test_change_state(self, mock_unlink, mock_open, run, expected_change_state):
        hd_active = HdActiveTest(drive_paths=['z'], run=run)
        assert hd_active.is_running is run

        actual_change_state = hd_active.change_state()

        check.equal(actual_change_state, expected_change_state)
        check.equal(hd_active.is_running, not run)
