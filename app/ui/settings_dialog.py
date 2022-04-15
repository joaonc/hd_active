from os import PathLike

from PySide6 import QtGui, QtWidgets

from app.hd_active import HdActive
from app.ui.forms.settings_ui import Ui_Dialog
from app.ui.log_dialog import LogDialog
from app.utils import get_asset


class SettingsDialog(QtWidgets.QDialog):
    # Using class composition instead of inheritance or `PySide6.QtUiTools.loadUiType`.
    def __init__(self, hd_active: HdActive, parent):
        super().__init__(parent)
        self.hd_active = hd_active
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self._update_change_state_button_text()

        self.setWindowIcon(
            QtGui.QIcon(str(get_asset('images', 'drive-harddisk-usb_36212_32px.png')))
        )
        self.set_values()

        # UI bindings
        self.ui.ok_button.clicked.connect(self.ok)
        self.ui.cancel_button.clicked.connect(self.close)
        self.ui.change_state_button.clicked.connect(self.change_state)
        self.ui.log_button.clicked.connect(self.show_log)

    @staticmethod
    def _path_to_str(drive_path: PathLike) -> str:
        return str(drive_path)

    def _update_change_state_button_text(self):
        self.ui.change_state_button.setText(self.hd_active.get_change_state())

    def change_state(self):
        self.hd_active.change_state()
        self._update_change_state_button_text()

    def set_values(self):
        self.ui.drives_line_edit.setText(
            ','.join(self._path_to_str(drive_path) for drive_path in self.hd_active.drive_paths)
        )
        self.ui.wait_line_edit.setText(str(self.hd_active.wait))

    def ok(self):
        # TODO: Save state to HD Active file.
        self.close()

    def show_log(self):
        log = LogDialog(self.hd_active, self)
        log.show()
