from unittest.mock import patch

from config import HdActiveConfig

import pytest_check as check


@patch('config.HdActiveConfig.read')
def test_defaults(read_mock):
    """
    Skip reading file (so defaults are not overwritten) and verify defaults.
    """
    config = HdActiveConfig()
    check.is_false(config.run)
    check.equal(config.wait, 60)
    check.equal(config.drive_paths, [])
