from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QDialog

from src.hd_active.hd_active import HdActive
from src.hd_active.ui.forms.ui_log_dialog import Ui_LogDialog


class LogDialog(QDialog):
    # Using class composition instead of inheritance or `PySide6.QtUiTools.loadUiType`.
    def __init__(self, hd_active: HdActive, parent):
        super().__init__(parent)
        self.hd_active = hd_active
        self.ui = Ui_LogDialog()
        self.ui.setupUi(self)

        # UI bindings
        self.ui.ok_button.clicked.connect(self.close)

    def showEvent(self, arg__1: QShowEvent):
        super().showEvent(arg__1)

        self.set_text()

    def set_text(self):
        self.ui.log_textBrowser.setText('\n'.join(self.hd_active.log))
