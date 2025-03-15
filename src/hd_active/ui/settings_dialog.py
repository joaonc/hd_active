from PySide6.QtWidgets import QDialog, QWidget

from src.hd_active.hd_active import HdActive
from src.hd_active.ui.forms.ui_settings_dialog import Ui_SettingsDialog
from src.hd_active.ui.log_dialog import LogDialog


class SettingsDialog(QDialog, Ui_SettingsDialog):
    def __init__(self, hd_active: HdActive, parent: QWidget):
        super().__init__(parent)
        self.hd_active = hd_active
        self.setupUi(self)
        self._update_change_state_button_text()

        self.set_values()

        # UI bindings
        self.ok_button.clicked.connect(self.ok)
        self.cancel_button.clicked.connect(self.close)
        self.change_state_button.clicked.connect(self.change_state)
        self.log_button.clicked.connect(self.show_log)

    def _update_change_state_button_text(self):
        self.change_state_button.setText(self.hd_active.get_change_state())

    def change_state(self):
        self.hd_active.change_state()
        self._update_change_state_button_text()

    def set_values(self):
        self.drives_line_edit.setText(
            ','.join(str(drive_path) for drive_path in self.hd_active.drive_paths)
        )
        self.wait_line_edit.setText(str(self.hd_active.wait))

    def ok(self):
        # TODO: Save state to HD Active file.
        self.close()

    def show_log(self):
        log = LogDialog(self.hd_active, self)
        log.show()
