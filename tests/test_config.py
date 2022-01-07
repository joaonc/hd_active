from typing import List, Tuple
from unittest.mock import patch

import pytest
import pytest_check as check
from config import HdActiveConfig


@pytest.fixture
def config_file(request, tmp_path) -> Tuple[str, List[str]]:
    """
    Fixture to be called indirectly with the INI file contents as parameter in the ``request``.

    The parameter to ``request`` should be a tuple with the contents of the INI file and a list with the expected
    drives.
    """
    file = tmp_path / 'test.ini'
    file.write_text(request.param[0])
    return str(file), request.param[1]


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
            (
                '''[HD Active]
drives = e:\\''',
                ['e:\\'],
            ),
            id='one drive only',
        ),
        pytest.param(
            (
                '''[HD Active]
drives = e:\\,f,    g/''',
                ['e:\\', 'f', 'g/'],
            ),
            id='multiple drives',
        ),
        pytest.param(
            (
                '''[HD Active]
drives = 'e',''f'',"g"''',
                ['e', 'f', 'g'],
            ),
            id='quotes are ignored',
        ),
    ],
    indirect=True,
)
def test_drives(config_file):
    file_name, expected_drives_paths = config_file
    config = HdActiveConfig(file_name)
    assert config.drive_paths == expected_drives_paths
