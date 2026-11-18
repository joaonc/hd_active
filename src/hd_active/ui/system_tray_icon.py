from PySide6.QtCore import QObject, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QDialog, QMenu, QMessageBox, QSystemTrayIcon

from .. import __version__
from .controller import HdActiveController
from .forms import resources_rc  # noqa: F401  Registers the resources, like the icon below.
from .log_dialog import LogDialog
from .settings_dialog import SettingsDialog

APP_NAME = 'HD Active'
# Icon from https://icon-icons.com/icon/drive-harddisk-usb/36212 (GPL v3)
ICON_RESOURCE = ':/images/hard_drive_icon.png'


class SystemTrayIcon(QSystemTrayIcon):
    """
    The app's presence in the system tray: context menu, notifications and access to the dialogs.
    """

    def __init__(self, controller: HdActiveController, parent: QObject | None = None):
        super().__init__(QIcon(ICON_RESOURCE), parent)
        self._controller = controller

        # Dialogs are created when first needed and then reused, so there's only one of each.
        self._settings_dialog: SettingsDialog | None = None
        self._log_dialog: LogDialog | None = None

        # A tray icon isn't a widget, so it can't be the menu's parent. Keep a reference instead.
        self._menu = QMenu()
        self.change_state_action = self._menu.addAction('')
        self.change_state_action.triggered.connect(self.toggle)
        self._menu.addAction('Settings...').triggered.connect(self.show_settings_dialog)
        self._menu.addAction('Log').triggered.connect(self.show_log_dialog)
        self._menu.addSeparator()
        self._menu.addAction('About').triggered.connect(self.about)
        self._menu.addAction('Exit').triggered.connect(QApplication.quit)
        self.setContextMenu(self._menu)

        self.activated.connect(self._on_activated)
        self._controller.state_changed.connect(self._update_state)
        self._controller.error.connect(self._show_error)

        self._update_state(self._controller.is_running)

    @Slot()
    def toggle(self):
        if not self._controller.toggle() and not self._controller.config.drive_paths:
            self.showMessage(
                APP_NAME,
                'No drives to keep active. Add them in Settings.',
                QSystemTrayIcon.MessageIcon.Warning,
            )

    @Slot()
    def show_settings_dialog(self) -> SettingsDialog:
        if self._settings_dialog is None:
            self._settings_dialog = SettingsDialog(self._controller)
            self._settings_dialog.log_requested.connect(self.show_log_dialog)
        self._show(self._settings_dialog)
        return self._settings_dialog

    @Slot()
    def show_log_dialog(self) -> LogDialog:
        if self._log_dialog is None:
            self._log_dialog = LogDialog(self._controller)
        self._show(self._log_dialog)
        return self._log_dialog

    @Slot()
    def about(self):
        QMessageBox.about(
            None,
            f'About {APP_NAME}',
            f'{APP_NAME} {__version__}\n\nPrevent external HDs from becoming inactive (sleeping).',
        )

    @staticmethod
    def _show(dialog: QDialog):
        """
        Show a dialog (non-modal) or, if already open, bring it to the front.
        """
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()

    @Slot(QSystemTrayIcon.ActivationReason)
    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_settings_dialog()

    @Slot(bool)
    def _update_state(self, is_running: bool):
        self.change_state_action.setText('Stop' if is_running else 'Start')
        tool_tip = f'{APP_NAME}: {"running" if is_running else "stopped"}'
        if self._controller.dry_run:
            tool_tip += ' (dry run)'
        self.setToolTip(tool_tip)

    @Slot(str)
    def _show_error(self, message: str):
        self.showMessage(APP_NAME, message, QSystemTrayIcon.MessageIcon.Warning)
