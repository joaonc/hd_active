from PySide6.QtCore import Slot
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QDialog, QWidget

from ..hd_active import LogEntry
from .controller import HdActiveController
from .forms.ui_log_dialog import Ui_LogDialog


class LogDialog(QDialog):
    """
    Shows the most recent writes, updated as they happen.
    """

    def __init__(self, controller: HdActiveController, parent: QWidget | None = None):
        super().__init__(parent)
        self._controller = controller
        self.ui = Ui_LogDialog()
        self.ui.setupUi(self)

        self._controller.log_added.connect(self._append)

    def showEvent(self, event: QShowEvent):
        # Entries are only appended while visible, so catch up with what happened meanwhile.
        self.ui.log_text_edit.setPlainText('\n'.join(str(e) for e in self._controller.log))
        scroll_bar = self.ui.log_text_edit.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())
        super().showEvent(event)

    @Slot(object)
    def _append(self, entry: LogEntry):
        if self.isVisible():
            self.ui.log_text_edit.appendPlainText(str(entry))
