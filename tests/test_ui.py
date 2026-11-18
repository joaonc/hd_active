from pathlib import Path
from unittest.mock import patch

import pytest
from PySide6.QtWidgets import QDialogButtonBox, QMessageBox

from hd_active.hd_active_config import HdActiveConfig
from hd_active.ui.controller import HdActiveController
from hd_active.ui.log_dialog import LogDialog
from hd_active.ui.settings_dialog import SettingsDialog
from hd_active.ui.system_tray_icon import SystemTrayIcon

TIMEOUT = 5000


@pytest.fixture
def config_file(tmp_path) -> Path:
    return tmp_path / 'test.ini'


@pytest.fixture
def drive(tmp_path) -> Path:
    path = tmp_path / 'drive'
    path.mkdir()
    return path


@pytest.fixture
def make_controller(qapp, config_file):
    """
    Factory of controllers, stopped at the end of the test.

    They're in dry run by default and with a long wait, so there's a single write after starting.
    """
    controllers = []

    def factory(drive_paths=(), wait=60, run=False, dry_run=True) -> HdActiveController:
        config = HdActiveConfig(drive_paths=[str(p) for p in drive_paths], wait=wait, run=run)
        controller = HdActiveController(config, config_file, dry_run=dry_run)
        controllers.append(controller)
        return controller

    yield factory
    for controller in controllers:
        controller.stop()


class TestController:
    def test_start_stop_signals(self, qtbot, make_controller, drive):
        controller = make_controller([drive])

        with qtbot.waitSignal(controller.state_changed, timeout=TIMEOUT) as blocker:
            assert controller.start() is True
        assert blocker.args == [True]
        assert controller.is_running is True

        with qtbot.waitSignal(controller.state_changed, timeout=TIMEOUT) as blocker:
            controller.stop()
        assert blocker.args == [False]
        assert controller.is_running is False

    def test_log_added_from_worker_thread(self, qtbot, make_controller, drive):
        controller = make_controller([drive], dry_run=False)

        with qtbot.waitSignal(controller.log_added, timeout=TIMEOUT) as blocker:
            controller.start()

        (entry,) = blocker.args
        assert entry.drive_path == drive
        assert entry.bytes_written == 10_000
        assert controller.log == (entry,)

    def test_error_emitted_once_per_failing_drive(self, qtbot, make_controller, tmp_path):
        controller = make_controller([tmp_path / 'missing'], wait=0.01, dry_run=False)
        errors = []
        controller.error.connect(errors.append)

        controller.start()
        qtbot.waitUntil(lambda: len(controller.log) >= 3, timeout=TIMEOUT)
        controller.stop()
        qtbot.wait(50)  # Deliver what's queued.

        assert len(errors) == 1
        assert 'missing' in errors[0]

    def test_apply_config_saves_and_applies(self, qtbot, make_controller, drive, config_file):
        controller = make_controller()
        config = HdActiveConfig(drive_paths=[str(drive)], wait=7, run=True)

        with qtbot.waitSignal(controller.config_changed, timeout=TIMEOUT):
            controller.apply_config(config)

        assert controller.config == config
        assert HdActiveConfig.load(config_file) == config
        # `run` is about the next time the app starts, not about now.
        assert controller.is_running is False
        assert controller.start() is True

    def test_apply_config_keeps_running(self, qtbot, make_controller, drive, tmp_path):
        controller = make_controller([drive])
        controller.start()
        other_drive = tmp_path / 'other'

        controller.apply_config(HdActiveConfig(drive_paths=[str(other_drive)], wait=60))

        assert controller.is_running is True
        qtbot.waitUntil(lambda: controller.log[-1].drive_path == other_drive, timeout=TIMEOUT)

    def test_apply_config_without_drives_stops(self, make_controller, drive):
        controller = make_controller([drive])
        controller.start()

        controller.apply_config(HdActiveConfig())

        assert controller.is_running is False

    def test_apply_config_save_error_changes_nothing(self, make_controller, drive, tmp_path):
        controller = make_controller([drive])
        controller._config_file = tmp_path  # A directory, can't be written as a file.
        before = controller.config

        with pytest.raises(OSError):
            controller.apply_config(HdActiveConfig(drive_paths=['x'], wait=1))

        assert controller.config == before

    def test_config_is_a_copy(self, make_controller, drive):
        controller = make_controller([drive])
        controller.config.drive_paths.append('x')
        assert controller.config.drive_paths == [str(drive)]


class TestSettingsDialog:
    @pytest.fixture
    def make_dialog(self, qtbot):
        def factory(controller) -> SettingsDialog:
            dialog = SettingsDialog(controller)
            qtbot.addWidget(dialog)
            dialog.show()
            return dialog

        return factory

    def test_shows_config(self, make_controller, make_dialog):
        controller = make_controller(['e:\\', 'f:\\'], wait=7.5, run=True)
        dialog = make_dialog(controller)

        assert dialog.drive_paths() == ['e:\\', 'f:\\']
        assert dialog.ui.wait_spin_box.value() == 7.5
        assert dialog.ui.run_on_start_check_box.isChecked() is True

    def test_ok_applies_and_saves(self, make_controller, make_dialog, config_file):
        controller = make_controller(['e'])
        dialog = make_dialog(controller)

        dialog.add_drive('f')
        dialog.add_drive('f')  # Duplicate, ignored.
        dialog.add_drive('')  # Folder selection cancelled, ignored.
        dialog.ui.wait_spin_box.setValue(30)
        dialog.ui.run_on_start_check_box.setChecked(True)
        dialog.ui.button_box.button(QDialogButtonBox.StandardButton.Ok).click()

        expected = HdActiveConfig(drive_paths=['e', 'f'], wait=30, run=True)
        assert dialog.isVisible() is False
        assert controller.config == expected
        assert HdActiveConfig.load(config_file) == expected

    def test_cancel_discards(self, make_controller, make_dialog, config_file):
        controller = make_controller(['e'])
        dialog = make_dialog(controller)

        dialog.add_drive('f')
        dialog.ui.button_box.button(QDialogButtonBox.StandardButton.Cancel).click()

        assert dialog.isVisible() is False
        assert controller.config.drive_paths == ['e']
        assert not config_file.exists()

        # Edits are gone when shown again.
        dialog.show()
        assert dialog.drive_paths() == ['e']

    def test_remove_drives(self, make_controller, make_dialog):
        dialog = make_dialog(make_controller(['e', 'f', 'g']))
        assert dialog.ui.remove_drive_button.isEnabled() is False

        dialog.ui.drives_list.item(0).setSelected(True)
        dialog.ui.drives_list.item(2).setSelected(True)
        assert dialog.ui.remove_drive_button.isEnabled() is True
        dialog.ui.remove_drive_button.click()

        assert dialog.drive_paths() == ['f']
        assert dialog.ui.remove_drive_button.isEnabled() is False

    def test_save_error_keeps_dialog_open(self, make_controller, make_dialog, tmp_path):
        controller = make_controller(['e'])
        controller._config_file = tmp_path  # A directory, can't be written as a file.
        dialog = make_dialog(controller)

        with patch.object(QMessageBox, 'critical') as critical:
            dialog.accept()

        critical.assert_called_once()
        assert dialog.isVisible() is True

    def test_change_state_button(self, make_controller, make_dialog, drive):
        controller = make_controller([drive])
        dialog = make_dialog(controller)
        assert dialog.ui.change_state_button.text() == 'Start'
        assert dialog.ui.status_label.text().startswith('Stopped')

        dialog.ui.change_state_button.click()
        assert controller.is_running is True
        assert dialog.ui.change_state_button.text() == 'Stop'
        assert dialog.ui.status_label.text().startswith('Running')

        # Changed from somewhere else, like the tray menu.
        controller.stop()
        assert dialog.ui.change_state_button.text() == 'Start'

    def test_log_button(self, qtbot, make_controller, make_dialog):
        dialog = make_dialog(make_controller())
        with qtbot.waitSignal(dialog.log_requested, timeout=TIMEOUT):
            dialog.ui.log_button.click()


class TestLogDialog:
    def test_shows_existing_and_new_entries(self, qtbot, make_controller, drive):
        controller = make_controller([drive], wait=0.01)
        controller.start()
        qtbot.waitUntil(lambda: len(controller.log) >= 2, timeout=TIMEOUT)

        dialog = LogDialog(controller)
        qtbot.addWidget(dialog)
        dialog.show()
        count = dialog.ui.log_text_edit.blockCount()
        assert count >= 2
        assert str(drive) in dialog.ui.log_text_edit.toPlainText()

        qtbot.waitUntil(lambda: dialog.ui.log_text_edit.blockCount() > count, timeout=TIMEOUT)


class TestSystemTrayIcon:
    @pytest.fixture
    def make_tray_icon(self):
        def factory(controller) -> SystemTrayIcon:
            return SystemTrayIcon(controller)

        return factory

    def test_icon_is_loaded_from_resources(self, make_controller, make_tray_icon):
        tray_icon = make_tray_icon(make_controller())
        assert not tray_icon.icon().isNull()
        assert tray_icon.icon().availableSizes()

    def test_state_is_in_sync(self, make_controller, make_tray_icon, drive):
        controller = make_controller([drive])
        tray_icon = make_tray_icon(controller)
        assert tray_icon.change_state_action.text() == 'Start'
        assert tray_icon.toolTip() == 'HD Active: stopped (dry run)'

        tray_icon.change_state_action.trigger()
        assert controller.is_running is True
        assert tray_icon.change_state_action.text() == 'Stop'
        assert tray_icon.toolTip() == 'HD Active: running (dry run)'

        # Changed from somewhere else, like the settings dialog.
        controller.stop()
        assert tray_icon.change_state_action.text() == 'Start'

    def test_start_without_drives_warns(self, make_controller, make_tray_icon):
        controller = make_controller()
        tray_icon = make_tray_icon(controller)

        with patch.object(tray_icon, 'showMessage') as show_message:
            tray_icon.change_state_action.trigger()

        assert controller.is_running is False
        assert 'No drives' in show_message.call_args.args[1]

    def test_write_error_is_notified(self, qtbot, make_controller, make_tray_icon, tmp_path):
        controller = make_controller([tmp_path / 'missing'], dry_run=False)
        tray_icon = make_tray_icon(controller)

        with patch.object(tray_icon, 'showMessage') as show_message:
            with qtbot.waitSignal(controller.error, timeout=TIMEOUT):
                controller.start()

        assert 'missing' in show_message.call_args.args[1]

    def test_dialogs_are_single_instance(self, qtbot, make_controller, make_tray_icon):
        tray_icon = make_tray_icon(make_controller())

        settings_dialog = tray_icon.show_settings_dialog()
        qtbot.addWidget(settings_dialog)
        assert settings_dialog.isVisible() is True
        assert tray_icon.show_settings_dialog() is settings_dialog

        settings_dialog.ui.log_button.click()
        log_dialog = tray_icon.show_log_dialog()
        qtbot.addWidget(log_dialog)
        assert log_dialog.isVisible() is True
