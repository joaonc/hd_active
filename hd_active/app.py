import sys
from typing import Optional

from PySide6 import QtGui, QtWidgets
from utils import get_asset

from hd_active import HdActive


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, icon, parent=None, hd_active: Optional[HdActive] = None):
        super().__init__(icon=icon, parent=parent)
        self.hd_active = hd_active or HdActive()

        # Menu
        menu = QtWidgets.QMenu(parent)
        change_state_action = menu.addAction('Stop' if self.hd_active.is_running else 'Start')
        change_state_action.triggered.connect(self.change_state)
        menu.addSeparator()
        quit_action = menu.addAction('Exit')
        quit_action.triggered.connect(QtWidgets.QApplication.instance().quit)
        self.setContextMenu(menu)

        # Other events
        self.activated.connect(self.onTrayIconActivated)

    def onTrayIconActivated(self, reason):
        if reason == self.DoubleClick:
            # TODO: Open Window with options
            pass

    def change_state(self):
        if self.hd_active.is_running:
            self.hd_active.stop()
        else:
            self.hd_active.start()


def main(drive_paths=None, run=False, wait=1):
    print('main entry')
    # if not QtWidgets.QSystemTrayIcon.isSystemTrayAvailable():
    #     raise Exception('System Tray not available.')

    # print('main with System Tray available')

    hd_active = HdActive(drive_paths=drive_paths, run=run, wait=wait)
    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QWidget()
    tray_icon = SystemTrayIcon(
        # Icon from https://icon-icons.com/icon/drive-harddisk-usb/36212 (GPL v3)
        icon=QtGui.QIcon(str(get_asset('drive-harddisk-usb_36212_32px.png'))),
        parent=widget,
        hd_active=hd_active,
    )
    tray_icon.show()
    tray_icon.showMessage('HD Active started', 'The message')
    sys.exit(app.exec())


if __name__ == '__main__':
    main(drive_paths=['e:\\'])
