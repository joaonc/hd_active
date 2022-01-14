from PySide6 import QtWidgets

from app.hd_active import HdActive
from app.ui.forms.settings_ui import Ui_Dialog


class SettingsDialog(QtWidgets.QDialog):
    # Technical note: Using class composition instead of inheritance or `PySide6.QtUiTools.loadUiType`.
    def __init__(self, hd_active: HdActive, parent):
        super().__init__(parent)
        self.hd_active = hd_active
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self._update_change_state_button_text()

        # UI bindings
        self.ui.change_state_button.clicked.connect(self.change_state)

    def _update_change_state_button_text(self):
        self.ui.change_state_button.setText(self.hd_active.get_change_state())

    def change_state(self):
        self.hd_active.change_state()
        self._update_change_state_button_text()
