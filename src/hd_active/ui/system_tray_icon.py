import os

from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from src.hd_active.hd_active import HdActive
from src.hd_active.hd_active_config import HdActiveConfig
from src.hd_active.ui.settings_dialog import SettingsDialog
from src.hd_active.utils import is_truthy

HD_ACTION_DEBUG = is_truthy(os.getenv('HD_ACTION_DEBUG', 'True'))
"""
If truthy, HDs are not accessed. Used for testing purposes.
"""


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, icon, parent=None, hd_active_file_name: str = 'hd_active.ini'):
        super().__init__(icon=icon, parent=parent)

        self.hd_active_file_name = hd_active_file_name
        config = HdActiveConfig(self.hd_active_file_name)
        self.hd_active = HdActive(drive_paths=config.drive_paths, run=config.run, wait=config.wait)
        if HD_ACTION_DEBUG:
            # Disable actual writing to HD
            self.hd_active.write_hds = lambda: None  # type: ignore

        # Menu
        menu = QMenu(parent)
        change_state_action = menu.addAction(self.hd_active.get_change_state())
        change_state_action.triggered.connect(self.change_state)
        show_settings_action = menu.addAction('Settings')
        show_settings_action.triggered.connect(self._show_settings_dialog)
        menu.addSeparator()
        quit_action = menu.addAction('Exit')
        quit_action.triggered.connect(QApplication.instance().quit)  # type: ignore
        self.setContextMenu(menu)

        # Other events
        self.activated.connect(self.on_tray_icon_activated)

    def _show_settings_dialog(self):
        settings_dialog = SettingsDialog(hd_active=self.hd_active, parent=self.parent())
        settings_dialog.exec()

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_settings_dialog()

    def change_state(self):
        cur_menu_text = self.hd_active.get_change_state()
        next_state = self.hd_active.change_state()

        # Update menu text
        change_state_action = next(
            action for action in self.contextMenu().children() if action.text() == cur_menu_text
        )
        change_state_action.setText(next_state)
