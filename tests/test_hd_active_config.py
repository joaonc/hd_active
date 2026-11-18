import configparser

import pytest

from hd_active.hd_active_config import HdActiveConfig


@pytest.fixture
def config_file(tmp_path):
    """
    Factory that creates a config file with the given contents and returns its path.
    """

    def factory(contents: str):
        file = tmp_path / 'test.ini'
        file.write_text(contents)
        return file

    return factory


def test_defaults():
    config = HdActiveConfig()
    assert config.run is False
    assert config.wait == 60
    assert config.drive_paths == []


@pytest.mark.parametrize('contents', ['', '[Other]\nfoo = bar', '[HD Active]'])
def test_load_missing_options_get_defaults(config_file, contents):
    assert HdActiveConfig.load(config_file(contents)) == HdActiveConfig()


@pytest.mark.parametrize(
    'drives, expected_drive_paths',
    [
        pytest.param('e:\\', ['e:\\'], id='one drive only'),
        pytest.param('e:\\,f,    g/', ['e:\\', 'f', 'g/'], id='multiple drives'),
        pytest.param("""'e',''f'',"g\"""", ['e', 'f', 'g'], id='quotes are ignored'),
        pytest.param('', [], id='empty'),
        pytest.param('e,, f,', ['e', 'f'], id='empty items are ignored'),
    ],
)
def test_load_drives(config_file, drives, expected_drive_paths):
    config = HdActiveConfig.load(config_file(f'[HD Active]\ndrives = {drives}'))
    assert config.drive_paths == expected_drive_paths


def test_load_all_options(config_file):
    config = HdActiveConfig.load(
        config_file('[HD Active]\nrun_on_start = yes\nwait_between_access = 7.5\ndrives = e, f')
    )
    assert config == HdActiveConfig(drive_paths=['e', 'f'], wait=7.5, run=True)


def test_load_file_doesnt_exist(tmp_path):
    with pytest.raises(FileNotFoundError):
        HdActiveConfig.load(tmp_path / 'foo_doesnt_exist.ini')


@pytest.mark.parametrize(
    'contents',
    [
        '[HD Active]\nwait_between_access = foo',
        '[HD Active]\nwait_between_access = 0',
        '[HD Active]\nwait_between_access = -1',
        '[HD Active]\nrun_on_start = maybe',
    ],
)
def test_load_invalid_value(config_file, contents):
    with pytest.raises(ValueError):
        HdActiveConfig.load(config_file(contents))


def test_load_invalid_file(config_file):
    with pytest.raises(configparser.Error):
        HdActiveConfig.load(config_file('not an ini file'))


def test_save_creates_file(tmp_path):
    file = tmp_path / 'sub' / 'new.ini'
    config = HdActiveConfig(drive_paths=['e:\\', 'f:\\'], wait=7.5, run=True)

    config.save(file)

    assert HdActiveConfig.load(file) == config


def test_save_preserves_other_content(config_file):
    file = config_file('[Other]\nfoo = bar\n[HD Active]\ndrives = e\nextra = 1')

    HdActiveConfig(drive_paths=['f']).save(file)

    parser = configparser.ConfigParser()
    parser.read(file)
    assert parser['Other']['foo'] == 'bar'
    assert parser['HD Active']['extra'] == '1'
    assert parser['HD Active']['drives'] == 'f'


def test_str():
    config = HdActiveConfig(drive_paths=['e:\\', 'f:\\'], wait=7.0)
    assert str(config) == 'drive paths: e:\\, f:\\\nwait: 7.0s'
