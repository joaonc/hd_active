from PySide6 import QtWidgets

from app.hd_active import HdActive
from app.ui.base.settings_ui import Ui_Dialog


class SettingsDialog(QtWidgets.QDialog):

    def __init__(self, hd_active: HdActive, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.hd_active = hd_active
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.update_change_state_button_text()

        # UI bindings
        self.ui.change_state_button.clicked.connect(self.change_state)

    def update_change_state_button_text(self):
        self.ui.change_state_button.setText(self.hd_active.get_change_state())

    def change_state(self):
        ...
