import os

from PySide6.QtWidgets import QApplication, QMenu, QMessageBox, QSystemTrayIcon, QWidget

from .. import __version__
from ..hd_active import HdActive
from ..hd_active_config import HdActiveConfig
from ..utils import FilePath, is_truthy
from .settings_dialog import SettingsDialog

HD_ACTION_DEBUG = is_truthy(os.getenv('HD_ACTION_DEBUG', 'True'))
"""
If truthy, HDs are not accessed. Used for testing purposes.
"""

DEFAULT_HD_ACTIVE_FILE_NAME = 'hd_active.ini'


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(
        self,
        icon,
        parent: QWidget | None = None,
        hd_active_file_name: FilePath = DEFAULT_HD_ACTIVE_FILE_NAME,
    ):
        super().__init__(icon=icon, parent=parent)

        self._parent_widget = parent
        self.hd_active_file_name = hd_active_file_name
        config = HdActiveConfig(self.hd_active_file_name)
        # Don't start yet: in debug mode, writing must be disabled before the writer thread runs.
        self.hd_active = HdActive(drive_paths=config.drive_paths, run=False, wait=config.wait)
        if HD_ACTION_DEBUG:
            # Disable actual writing to HD
            self.hd_active.write_hds = lambda: None
        if config.run:
            self.hd_active.start()

        # Menu
        menu = QMenu(parent)
        self._change_state_action = menu.addAction(self.hd_active.get_change_state())
        self._change_state_action.triggered.connect(self.change_state)
        show_settings_action = menu.addAction('Settings')
        show_settings_action.triggered.connect(self._show_settings_dialog)
        menu.addSeparator()
        about_action = menu.addAction('About')
        about_action.triggered.connect(self.about)
        quit_action = menu.addAction('Exit')
        quit_action.triggered.connect(QApplication.instance().quit)  # type: ignore
        self.setContextMenu(menu)

        # Other events
        self.activated.connect(self.on_tray_icon_activated)

    def _show_settings_dialog(self):
        settings_dialog = SettingsDialog(hd_active=self.hd_active, parent=self._parent_widget)
        settings_dialog.exec()

    def about(self):
        QMessageBox.information(self._parent_widget, 'About', f'HD Active {__version__}')

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_settings_dialog()

    def change_state(self):
        next_state = self.hd_active.change_state()
        self._change_state_action.setText(next_state)
