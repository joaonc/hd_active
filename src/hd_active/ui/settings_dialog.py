from PySide6.QtCore import QDir, Signal, Slot
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox, QWidget

from ..hd_active_config import HdActiveConfig
from .controller import HdActiveController
from .forms.ui_settings_dialog import Ui_SettingsDialog


class SettingsDialog(QDialog):
    """
    Edit the settings. *Ok* applies them and saves them to the config file.
    """

    log_requested = Signal()
    """The user wants to see the log."""

    def __init__(self, controller: HdActiveController, parent: QWidget | None = None):
        super().__init__(parent)
        self._controller = controller
        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)

        # UI bindings (Ok / Cancel are connected to accept / reject in the `.ui` file).
        self.ui.add_drive_button.clicked.connect(self._add_drive)
        self.ui.remove_drive_button.clicked.connect(self._remove_selected_drives)
        self.ui.drives_list.itemSelectionChanged.connect(self._update_remove_button)
        self.ui.change_state_button.clicked.connect(self._controller.toggle)
        self.ui.log_button.clicked.connect(self.log_requested)
        self._controller.state_changed.connect(self._update_state)

        self._update_state(self._controller.is_running)

    def showEvent(self, event: QShowEvent):
        # The same dialog is reused, so discard edits that were cancelled the previous time.
        self.set_config(self._controller.config)
        super().showEvent(event)

    def drive_paths(self) -> list[str]:
        return [self.ui.drives_list.item(i).text() for i in range(self.ui.drives_list.count())]

    def config(self) -> HdActiveConfig:
        """
        The config as currently shown in the dialog.
        """
        return HdActiveConfig(
            drive_paths=self.drive_paths(),
            wait=self.ui.wait_spin_box.value(),
            run=self.ui.run_on_start_check_box.isChecked(),
        )

    def set_config(self, config: HdActiveConfig):
        self.ui.drives_list.clear()
        self.ui.drives_list.addItems(config.drive_paths)
        self.ui.wait_spin_box.setValue(config.wait)
        self.ui.run_on_start_check_box.setChecked(config.run)

    def add_drive(self, drive_path: str):
        """
        Add a drive to the list, unless it's already there.
        """
        drive_path = QDir.toNativeSeparators(drive_path)
        if drive_path and drive_path not in self.drive_paths():
            self.ui.drives_list.addItem(drive_path)

    def accept(self):
        try:
            self._controller.apply_config(self.config())
        except OSError as e:
            QMessageBox.critical(
                self,
                'HD Active',
                f'Could not save settings to {self._controller.config_file}:\n{e}',
            )
            return
        super().accept()

    @Slot()
    def _add_drive(self):
        drive_path = QFileDialog.getExistingDirectory(self, 'Select drive or folder')
        self.add_drive(drive_path)

    @Slot()
    def _remove_selected_drives(self):
        for item in self.ui.drives_list.selectedItems():
            self.ui.drives_list.takeItem(self.ui.drives_list.row(item))

    @Slot()
    def _update_remove_button(self):
        self.ui.remove_drive_button.setEnabled(bool(self.ui.drives_list.selectedItems()))

    @Slot(bool)
    def _update_state(self, is_running: bool):
        status = 'Running' if is_running else 'Stopped'
        if self._controller.dry_run:
            status += ' (dry run, drives are not written to)'
        self.ui.status_label.setText(status)
        self.ui.change_state_button.setText('Stop' if is_running else 'Start')
