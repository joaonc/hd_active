import configparser
import logging
import signal
import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon

from .. import __version__
from ..hd_active_config import HdActiveConfig
from .controller import HdActiveController
from .system_tray_icon import APP_NAME, ICON_RESOURCE, SystemTrayIcon

logger = logging.getLogger(__name__)


def run_gui(config_file: Path, dry_run: bool = False) -> int:
    """
    Run HD Active in the system tray.

    :param config_file: Created when settings are saved, if it doesn't exist.
    :param dry_run: Don't write to the drives.
    :return: Exit code.
    """
    # Only the program name: the other arguments are ours (already parsed), not Qt's.
    app = QApplication(sys.argv[:1])
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(__version__)
    app.setWindowIcon(QIcon(ICON_RESOURCE))
    # The app lives in the tray, closing a dialog must not exit it.
    app.setQuitOnLastWindowClosed(False)
    # Qt's event loop doesn't let Python handle Ctrl+C, so let the OS do it.
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(
            None,
            APP_NAME,
            'No system tray available.\nUse `hd_active run` to run without UI.',
        )
        return 1

    try:
        config = HdActiveConfig.load(config_file)
    except FileNotFoundError:
        logger.warning('Config file %s not found, using defaults.', config_file)
        config = HdActiveConfig()
    except (ValueError, configparser.Error) as e:
        QMessageBox.critical(
            None,
            APP_NAME,
            f'Invalid config file {config_file}:\n{e}',
        )
        return 1

    controller = HdActiveController(config, config_file, dry_run=dry_run)
    app.aboutToQuit.connect(controller.stop)

    tray_icon = SystemTrayIcon(controller)
    tray_icon.show()
    if config.run:
        controller.start()

    if not config.drive_paths:
        message = 'No drives to keep active. Add them in Settings.'
    elif controller.is_running:
        message = f'Keeping {len(config.drive_paths)} drive(s) active.'
    else:
        message = 'Stopped. Use the tray icon to start.'
    if dry_run:
        message += '\nDry run: drives are not written to.'
    tray_icon.showMessage(APP_NAME, message)

    return app.exec()
