from pathlib import Path
from unittest.mock import patch

import pytest

from hd_active import __version__, cli
from hd_active.hd_active_config import DEFAULT_CONFIG_FILE_NAME, HdActiveConfig


@pytest.fixture(autouse=True)
def no_env_dry_run(monkeypatch):
    monkeypatch.delenv(cli.ENV_DRY_RUN, raising=False)


@pytest.fixture
def config_file(tmp_path) -> Path:
    file = tmp_path / 'test.ini'
    HdActiveConfig(drive_paths=[str(tmp_path)], wait=0.05).save(file)
    return file


class TestParser:
    def test_defaults(self):
        args = cli.build_parser().parse_args([])
        assert args.command is None
        assert args.conf == DEFAULT_CONFIG_FILE_NAME
        assert args.dry_run is False
        assert args.log == 'warning'

    @pytest.mark.parametrize(
        'argv',
        [
            ['--conf', 'x.ini', '--dry-run', '--log', 'debug', 'run'],
            ['run', '--conf', 'x.ini', '--dry-run', '--log', 'debug'],
            ['--conf', 'x.ini', 'run', '--dry-run', '--log', 'debug'],
        ],
    )
    def test_common_options_before_or_after_command(self, argv):
        args = cli.build_parser().parse_args(argv)
        assert (args.command, args.conf, args.dry_run, args.log) == ('run', 'x.ini', True, 'debug')

    def test_config_requires_action(self):
        with pytest.raises(SystemExit):
            cli.build_parser().parse_args(['config'])

    def test_version(self, capsys):
        with pytest.raises(SystemExit):
            cli.build_parser().parse_args(['--version'])
        assert __version__ in capsys.readouterr().out


class TestGui:
    @pytest.mark.parametrize('argv', [[], ['gui']])
    def test_gui_is_default(self, argv, tmp_path):
        file = tmp_path / 'x.ini'
        with patch('hd_active.cli._gui', return_value=0) as gui:
            assert cli.main(['--conf', str(file), *argv]) == 0
        gui.assert_called_once_with(file, False)

    def test_dry_run_flag(self):
        with patch('hd_active.cli._gui', return_value=0) as gui:
            cli.main(['gui', '--dry-run'])
        assert gui.call_args.args[1] is True

    @pytest.mark.parametrize('value, expected', [('1', True), ('true', True), ('false', False)])
    def test_dry_run_env(self, monkeypatch, value, expected):
        monkeypatch.setenv(cli.ENV_DRY_RUN, value)
        with patch('hd_active.cli._gui', return_value=0) as gui:
            cli.main([])
        assert gui.call_args.args[1] is expected

    def test_dry_run_env_invalid(self, monkeypatch):
        monkeypatch.setenv(cli.ENV_DRY_RUN, 'foo')
        with pytest.raises(SystemExit):
            cli.main([])


class TestRun:
    def test_runs_until_interrupted(self, config_file, capsys):
        with patch('hd_active.cli.time.sleep', side_effect=[None, KeyboardInterrupt]):
            assert cli.main(['run', '--conf', str(config_file), '--dry-run']) == 0

        out = capsys.readouterr().out
        assert 'HD Active started (dry run)' in out
        assert 'HD Active stopped' in out

    def test_writes_to_drives(self, config_file, tmp_path, capsys):
        with patch('hd_active.cli.time.sleep', side_effect=KeyboardInterrupt):
            assert cli.main(['run', '--conf', str(config_file)]) == 0

        # The first write is done before stop is processed.
        assert f'10000 bytes written to {tmp_path}' in capsys.readouterr().out

    def test_no_config_file(self, tmp_path, capsys):
        assert cli.main(['run', '--conf', str(tmp_path / 'missing.ini')]) == 1
        assert 'not found' in capsys.readouterr().err

    def test_no_drives(self, tmp_path, capsys):
        file = tmp_path / 'test.ini'
        HdActiveConfig().save(file)
        assert cli.main(['run', '--conf', str(file)]) == 1
        assert 'No drives' in capsys.readouterr().err

    def test_invalid_config_file(self, tmp_path, capsys):
        file = tmp_path / 'test.ini'
        file.write_text('[HD Active]\nwait_between_access = foo')
        assert cli.main(['run', '--conf', str(file)]) == 1
        assert 'Invalid config file' in capsys.readouterr().err


class TestConfig:
    def test_show(self, config_file, tmp_path, capsys):
        assert cli.main(['config', 'show', '--conf', str(config_file)]) == 0
        out = capsys.readouterr().out
        assert str(config_file) in out
        assert str(tmp_path) in out
        assert 'run on start: False' in out

    def test_show_no_config_file(self, tmp_path):
        assert cli.main(['config', 'show', '--conf', str(tmp_path / 'missing.ini')]) == 1

    def test_init_defaults(self, tmp_path):
        file = tmp_path / 'new.ini'
        assert cli.main(['config', 'init', '--conf', str(file)]) == 0
        assert HdActiveConfig.load(file) == HdActiveConfig()

    def test_init_options(self, tmp_path):
        file = tmp_path / 'new.ini'
        argv = ['config', 'init', '--conf', str(file)]
        argv += ['--drive', 'e:\\', '--drive', 'f:\\', '--wait', '30', '--run-on-start']

        assert cli.main(argv) == 0

        expected = HdActiveConfig(drive_paths=['e:\\', 'f:\\'], wait=30, run=True)
        assert HdActiveConfig.load(file) == expected

    def test_init_doesnt_overwrite(self, config_file, capsys):
        before = config_file.read_text()
        assert cli.main(['config', 'init', '--conf', str(config_file)]) == 1
        assert 'already exists' in capsys.readouterr().err
        assert config_file.read_text() == before

    def test_init_force(self, config_file):
        assert cli.main(['config', 'init', '--conf', str(config_file), '--force']) == 0
        assert HdActiveConfig.load(config_file).drive_paths == []

    def test_init_invalid_wait(self, tmp_path, capsys):
        file = tmp_path / 'new.ini'
        assert cli.main(['config', 'init', '--conf', str(file), '--wait', '0']) == 1
        assert not file.exists()
