import sys

from PySide6 import QtGui, QtWidgets
from utils import get_asset

from hd_active import HdActive


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, icon, parent=None, hd_active=None):
        super().__init__(icon=icon, parent=parent)
        self.is_started = True
        self.hd_active = hd_active or HdActive()

        menu = QtWidgets.QMenu(parent)
        change_state = menu.addAction('Stop' if self.is_started else 'Start')

    def onTrayIconActivated(self, reason):
        pass


def main(drive_paths=None, run=True, wait=1):
    hd_active = HdActive(drive_paths=drive_paths, run=run, wait=wait)
    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QWidget()
    tray_icon = SystemTrayIcon(
        icon=QtGui.QIcon(str(get_asset('drive-harddisk-usb_36212_32px.png'))),
        parent=widget,
        hd_active=hd_active,
    )
    tray_icon.show()
    tray_icon.showMessage('HD Active started', 'The message')
    sys.exit(app.exec())


if __name__ == '__main__':
    main(drive_paths=['e:\\'])
