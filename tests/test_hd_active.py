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

import time
from pathlib import Path
from unittest.mock import patch, MagicMock

from hd_active.hd_active import HdActive

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
        hd_active = HdActiveTest(drive_paths=['foo.txt'], run=False)

        # Verify didn't start
        time.sleep(WAIT_TEST)
        assert hd_active.is_running is False
        mock_open.assert_not_called()
        mock_unlink.assert_not_called()

    def test_instantiate_default_not_started(self, mock_unlink, mock_open):
        """
        `run` argument not specified and defaults to `False`.
        """
        # Note that `HdActive` if used and not `HdActiveTest`
        # to make sure it's the default for `HdActive` that's tested.
        hd_active = HdActive(drive_paths=['foo.txt'], wait=0.1)

        # Verify didn't start
        time.sleep(WAIT_TEST)
        assert hd_active.is_running is False
        mock_open.assert_not_called()
        mock_unlink.assert_not_called()

    def test_instantiate_starts_single_path(self, mock_unlink, mock_open):
        hd_active = HdActiveTest(drive_paths=['foo.txt'], run=True)

        # Verify started
        time.sleep(WAIT_TEST)
        assert hd_active.is_running is True
        hd_active.stop()
        mock_open.assert_called()
        mock_unlink.assert_called()

    def test_instantiate_starts_multiple_paths(self, mock_unlink, mock_open):
        hd_active = HdActiveTest