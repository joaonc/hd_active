import pytest
from unittest.mock import patch

from config import HdActiveConfig

import pytest_check as check


@pytest.fixture
def config_file(request, tmp_path) -> str:
    """
    Fixture to be called indirectly with the INI file contents as parameter in the ``request``.
    """
    file = tmp_path / 'test.ini'
    file.write_text(request.param)
    return str(file)


@patch('config.configparser.ConfigParser.read')
def test_defaults(read_mock):
    """
    Skip reading file (so defaults are not overwritten) and verify defaults.
    """
    config = HdActiveConfig()
    check.is_false(config.run)
    check.equal(config.wait, 60)
    check.equal(config.drive_paths, [])


@pytest.mark.parametrize(
    'config_file',
    [
        pytest.param(
            '''
            [HD Active]
            drives = e:\
            ''',
            id='one drive only'
        )
    ],
    indirect=True,
)
def test_drives(config_file):
    config = HdActiveConfig(config_file)
    # TODO: FINISH
    # TODO: Make config readable from byte stream for easier patching
