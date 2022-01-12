import os
import sys
from typing import Optional

from PySide6 import QtGui, QtWidgets
from PySide6.QtWidgets import QDialog

from config import HdActiveConfig
from hd_active.hd_active import HdActive
from hd_active.hd_active_state import HdActionState
from ui.base.settings_ui import Ui_Dialog
from utils import get_asset, is_truthy

HD_ACTION_DEBUG = is_truthy(os.getenv('HD_ACTION_DEBUG', 'False'))
"""
If truthy, HDs are not accessed.
Used for testing purposes.
"""


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, icon, parent=None, hd_active: Optional[HdActive] = None):
        super().__init__(icon=icon, parent=parent)
        self.hd_active = hd_active or HdActive()

        # Menu
        menu = QtWidgets.QMenu(parent)
        change_state_action = menu.addAction(self.get_change_state())
        change_state_action.triggered.connect(self.change_state)
        show_settings_action = menu.addAction('Settings')
        show_settings_action.triggered.connect(self._show_settings_dialog)
        menu.addSeparator()
        quit_action = menu.addAction('Exit')
        quit_action.triggered.connect(QtWidgets.QApplication.instance().quit)
        self.setContextMenu(menu)

        # Other events
        self.activated.connect(self.onTrayIconActivated)

    def get_change_state(self) -> HdActionState:
        return HdActionState.Stop if self.hd_active.is_running else HdActionState.Start

    def _show_settings_dialog(self):
        dlg = QDialog(self.parent())
        settings_window = Ui_Dialog()
        settings_window.setupUi(dlg)
        dlg.exec()

    def onTrayIconActivated(self, reason):
        if reason == self.DoubleClick:
            self._show_settings_dialog()

    def change_state(self):
        cur_menu_text = self.get_change_state()
        if self.hd_active.is_running:
            self.hd_active.stop()
        else:
            self.hd_active.start()
        new_menu_text = self.get_change_state()

        # Update menu text
        change_state_action = next(action for action in self.contextMenu().children() if action.text() == cur_menu_text)
        change_state_action.setText(new_menu_text)


def main():
    config = HdActiveConfig('hd_active.ini')
    hd_active = HdActive(drive_paths=config.drive_paths, run=config.run, wait=config.wait)
    if HD_ACTION_DEBUG:
        # Disable actual writing to HD
        hd_active.write_hds = lambda: None

    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QWidget()
    tray_icon = SystemTrayIcon(
        # Icon from https://icon-icons.com/icon/drive-harddisk-usb/36212 (GPL v3)
        icon=QtGui.QIcon(str(get_asset('images', 'drive-harddisk-usb_36212_32px.png'))),
        parent=widget,
        hd_active=hd_active,
    )
    tray_icon.show()
    tray_icon.showMessage('HD Active started', 'The message')
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
