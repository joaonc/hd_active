from typing import List, Tuple
from unittest.mock import patch

import pytest

from src.hd_active.hd_active_config import HdActiveConfig


@pytest.fixture
def config_file(request, tmp_path) -> Tuple[str, List[str]]:
    """
    Fixture to be called indirectly with the INI file contents as parameter in the ``request``.

    The parameter to ``request`` should be a tuple with the contents of the INI file and a list
    with the expected drives.
    """
    file = tmp_path / 'test.ini'
    file.write_text(request.param[0])
    return str(file), request.param[1]


@patch('src.hd_active.hd_active_config.configparser.ConfigParser.read')
def test_defaults(read_mock):
    """
    Skip reading file (so defaults are not overwritten) and verify defaults.
    """
    config = HdActiveConfig('foo.ini')
    assert config.run is False
    assert config.wait == 60
    assert config.drive_paths == []


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


def test_file_doesnt_exist():
    with pytest.raises(FileNotFoundError):
        HdActiveConfig('foo_doesnt_exist.ini')


@pytest.mark.parametrize(
    'config_file',
    [
        pytest.param(
            (
                '''[HD Active]
wait_between_access = 7
drives = e:\\,f:\\''',
                'drive paths: e:\\, f:\\\nwait: 7.0s',
            ),
            id='two drives',
        ),
    ],
    indirect=True,
)
def test_str(config_file):
    file_name, expected_str = config_file
    config = HdActiveConfig(file_name)
    assert str(config) == expected_str
