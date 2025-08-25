import sys

from PySide6 import QtGui, QtWidgets

from .ui.system_tray_icon import SystemTrayIcon
from .utils import get_asset


def main():
    """
    Run HD Active with UI.
    """
    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QWidget()
    tray_icon = SystemTrayIcon(
        # Icon from https://icon-icons.com/icon/drive-harddisk-usb/36212 (GPL v3)
        icon=QtGui.QIcon(str(get_asset('images', 'hard_drive_icon.png'))),
        parent=widget,
    )
    tray_icon.show()
    tray_icon.showMessage('HD Active started', 'The message')
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
