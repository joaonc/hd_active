from os import PathLike

from PySide6 import QtGui, QtWidgets

from app.hd_active import HdActive
from app.ui.forms.settings_ui import Ui_Dialog
from app.utils import get_asset


class LogDialog(QtWidgets.QDialog):
    # Using class composition instead of inheritance or `PySide6.QtUiTools.loadUiType`.
    def __init__(self, parent):
        super().__init__(parent)
