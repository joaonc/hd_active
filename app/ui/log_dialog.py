import time
from PySide6 import QtGui, QtWidgets

from app.hd_active import HdActive
from app.ui.forms.log_ui import Ui_LogDialog


class LogDialog(QtWidgets.QDialog):
    # Using class composition instead of inheritance or `PySide6.QtUiTools.loadUiType`.
    def __init__(self, hd_active: HdActive, parent):
        super().__init__(parent)
        self.hd_active = hd_active
        self.ui = Ui_LogDialog()
        self.ui.setupUi(self)

        # UI bindings
        self.ui.ok_button.clicked.connect(self.close)

    def showEvent(self, arg__1: QtGui.QShowEvent):
        super().showEvent(arg__1)

        self.set_text()

    def set_text(self):
        self.ui.log_textBrowser.setText('\n'.join(self.hd_active.log))
