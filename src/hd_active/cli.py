"""
Command line interface, entry point of the ``hd_active`` command.

Qt is only imported by the ``gui`` command, everything else works without a display.
"""

import argparse
import configparser
import logging
import os
import sys
import threading
import time
from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path
from typing import TextIO

from . import __version__
from .hd_active import HdActive, LogEntry
from .hd_active_config import DEFAULT_CONFIG_FILE_NAME, HdActiveConfig
from .utils import is_truthy

ENV_DRY_RUN = 'HD_ACTION_DEBUG'
"""
Environment variable that, if truthy, has the same effect as ``--dry-run``.
"""

STATUS_FLASH_SECONDS = 0.5
"""
How long the status in the `run` command stays yellow after a write.
"""

logger = logging.getLogger(__name__)


def _add_common_arguments(parser: argparse.ArgumentParser, *, top_level: bool, dry_run: bool):
    """
    Add the options shared by the commands.

    They're accepted both before and after the command name. For that to work, the ones in the
    commands can't have defaults, otherwise they'd override what was given before the command.
    """

    def default(value):
        return value if top_level else argparse.SUPPRESS

    parser.add_argument(
        '--conf',
        metavar='FILE',
        default=default(DEFAULT_CONFIG_FILE_NAME),
        help=f'Config file to use. Default: {DEFAULT_CONFIG_FILE_NAME} in the current directory.',
    )
    parser.add_argument(
        '--log',
        choices=['debug', 'info', 'warning', 'error'],
        default=default('warning'),
        help='Logging level. Default: warning.',
    )
    if dry_run:
        parser.add_argument(
            '--dry-run',
            action='store_true',
            default=default(False),
            help=f"Don't write to the drives. Also enabled by a truthy `{ENV_DRY_RUN}` env var.",
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='hd_active',
        description='Prevent external HDs from becoming inactive (sleeping). '
        'Runs the `gui` command if no command is given.',
    )
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    _add_common_arguments(parser, top_level=True, dry_run=True)
    commands = parser.add_subparsers(dest='command', metavar='COMMAND')

    gui = commands.add_parser('gui', help='Run in the system tray (default).')
    _add_common_arguments(gui, top_level=False, dry_run=True)

    run = commands.add_parser(
        'run', help='Run in the console, without UI, until interrupted with Ctrl+C.'
    )
    _add_common_arguments(run, top_level=False, dry_run=True)

    config = commands.add_parser('config', help='Show or create the config file.')
    config_commands = config.add_subparsers(dest='config_command', metavar='ACTION', required=True)
    show = config_commands.add_parser('show', help='Print the settings in the config file.')
    _add_common_arguments(show, top_level=False, dry_run=False)
    init = config_commands.add_parser('init', help='Create a config file.')
    _add_common_arguments(init, top_level=False, dry_run=False)
    init.add_argument(
        '--drive',
        action='append',
        default=[],
        metavar='PATH',
        help='Drive to keep active. Can be used multiple times.',
    )
    init.add_argument('--wait', type=float, help='Seconds to wait between writes.')
    init.add_argument(
        '--run-on-start', action='store_true', help='Start writing when the UI starts.'
    )
    init.add_argument('--force', action='store_true', help='Overwrite the file if it exists.')

    return parser


def _load_config(config_file: Path) -> HdActiveConfig | None:
    """
    :return: The config, or ``None`` (after printing the reason) if it couldn't be loaded.
    """
    try:
        return HdActiveConfig.load(config_file)
    except FileNotFoundError:
        _error(f'Config file not found: {config_file}\nCreate one with `hd_active config init`.')
    except (ValueError, configparser.Error) as e:
        _error(f'Invalid config file {config_file}: {e}')
    return None


def _error(message: str):
    print(message, file=sys.stderr)


def _gui(config_file: Path, dry_run: bool) -> int:
    try:
        from .ui.app import run_gui
    except ImportError as e:
        _error(f'Could not load the UI ({e}). Use `hd_active run` to run without it.')
        return 1
    return run_gui(config_file, dry_run=dry_run)


class _StatusLine:
    """
    One line, updated in place, that shows when a write happens: green when idle, yellow briefly
    after each write. Errors are printed above it, on lines of their own.

    :param flash_seconds: How long the line stays yellow after a write.
    :param stream: Where to print to. Must be a terminal, since it relies on ``\\r``.
    """

    IDLE = '🟢'
    WRITING = '🟡'

    def __init__(self, flash_seconds: float, stream: TextIO | None = None):
        self._flash_seconds = flash_seconds
        self._stream = stream if stream is not None else sys.stdout
        self._lock = threading.Lock()
        self._timer: threading.Timer | None = None
        self._open = False

    def _draw(self, dot: str):
        # Caller holds the lock. Emoji are the same width, so the line is fully overwritten.
        self._stream.write(f'\rstatus: {dot}')
        self._stream.flush()

    def start(self):
        with self._lock:
            self._open = True
            self._draw(self.IDLE)

    def on_log(self, entry: LogEntry):
        """
        To be used as the ``on_log`` callback of :class:`HdActive` (worker thread).
        """
        with self._lock:
            if not self._open:
                return
            if self._timer is not None:
                self._timer.cancel()
            if entry.error is not None:
                # Clear the status line, print the error, then bring the status back below it.
                self._stream.write(f'\r{" " * 20}\r{entry}\n')
            self._draw(self.WRITING)
            self._timer = threading.Timer(self._flash_seconds, self._back_to_idle)
            self._timer.daemon = True
            self._timer.start()

    def _back_to_idle(self):
        with self._lock:
            if self._open:
                self._draw(self.IDLE)

    def stop(self):
        """
        Stop updating and move to a new line, so that what's printed next doesn't overwrite it.
        """
        with self._lock:
            if not self._open:
                return
            self._open = False
            if self._timer is not None:
                self._timer.cancel()
            self._stream.write('\n')
            self._stream.flush()


def _run(config_file: Path, dry_run: bool) -> int:
    config = _load_config(config_file)
    if config is None:
        return 1
    if not config.drive_paths:
        _error(f'No drives in config file {config_file}')
        return 1

    # The in-place status line only makes sense in a terminal. When the output is redirected,
    # fall back to one line per write.
    status_line = _StatusLine(min(STATUS_FLASH_SECONDS, config.wait / 2)) if _is_tty() else None
    hd_active = HdActive(
        drive_paths=config.drive_paths,
        wait=config.wait,
        dry_run=dry_run,
        on_log=status_line.on_log if status_line else lambda entry: print(entry, flush=True),
    )
    print(f'HD Active started{" (dry run)" if dry_run else ""}. Ctrl+C to stop.\n{config}')
    if status_line:
        status_line.start()
    hd_active.start()
    try:
        while hd_active.is_running:
            # Short sleeps, so Ctrl+C is handled promptly on all platforms.
            time.sleep(0.2)
    except KeyboardInterrupt:
        if status_line:
            status_line.stop()
        print('Stopping HD Active.')
    finally:
        if status_line:
            status_line.stop()
        hd_active.stop()
    print('HD Active stopped.')
    return 0


def _is_tty() -> bool:
    return sys.stdout.isatty()


def _config_show(config_file: Path) -> int:
    config = _load_config(config_file)
    if config is None:
        return 1
    print(f'file: {config_file}\n{config}\nrun on start: {config.run}')
    return 0


def _config_init(config_file: Path, args: argparse.Namespace) -> int:
    if config_file.exists() and not args.force:
        _error(f'Config file already exists: {config_file}\nUse --force to overwrite.')
        return 1
    try:
        config = HdActiveConfig(drive_paths=args.drive, run=args.run_on_start)
        if args.wait is not None:
            config = replace(config, wait=args.wait)
        config.save(config_file)
    except (ValueError, OSError) as e:
        _error(f'Could not create config file {config_file}: {e}')
        return 1
    print(f'Created {config_file}')
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(level=args.log.upper(), format='%(levelname)s: %(message)s')
    config_file = Path(args.conf).expanduser().resolve()
    try:
        dry_run = args.dry_run or is_truthy(os.getenv(ENV_DRY_RUN, 'False'))
    except ValueError:
        parser.error(f'Invalid value for the `{ENV_DRY_RUN}` env var: {os.getenv(ENV_DRY_RUN)}')

    match args.command:
        case 'run':
            return _run(config_file, dry_run)
        case 'config' if args.config_command == 'show':
            return _config_show(config_file)
        case 'config':
            return _config_init(config_file, args)
        case _:
            return _gui(config_file, dry_run)


if __name__ == '__main__':
    sys.exit(main())
