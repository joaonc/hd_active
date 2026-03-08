import logging
import subprocess
import sys
from enum import Enum
from itertools import chain
from typing import Annotated

import typer
from rich.logging import RichHandler

from admin import PROJECT_ROOT

DryAnnotation = Annotated[
    bool,
    typer.Option(
        help='Show the command that would be run without running it.',
        show_default=False,
    ),
]


class OS(str, Enum):
    """Operating System."""

    Linux = 'linux'
    MacOS = 'mac'
    Windows = 'win'


def get_os() -> OS:
    """
    Similar to ``sys.platform`` and ``platform.system()``, but less ambiguous by returning an Enum
    instead of a string.

    Doesn't make granular distinctions of linux variants, OS versions, etc.
    """
    if sys.platform == 'darwin':
        return OS.MacOS
    if sys.platform == 'win32':
        return OS.Windows
    return OS.Linux


def run(*args, dry: bool = False, **kwargs) -> subprocess.CompletedProcess | None:
    """
    Run a CLI command synchronously (i.e., wait for the command to finish) and return the result.

    This function is a wrapper around ``subprocess.run(...)``.

    If you need access to the output, add the ``capture_output=True`` argument and do
    ``.stdout.decode().strip()`` to get the output as a string.
    """
    logger.info(' '.join(map(str, args)))

    if dry:
        return None

    defaults = dict(
        cwd=PROJECT_ROOT,
        capture_output=False,
        check=True,
    )

    try:
        return subprocess.run(args, **(defaults | kwargs))  # type: ignore
    except subprocess.CalledProcessError as e:
        msg = str(e)
        if e.stdout:
            msg += f'\nSTDOUT:\n{e.stdout.decode()}'
        if e.stderr:
            msg += f'\nSTDERR:\n{e.stderr.decode()}'
        logger.error(msg)
        raise typer.Exit(1)


def run_async(*args, dry: bool = False, **kwargs) -> subprocess.Popen | None:
    """
    Starts the process and continues code execution.

    Use the following checks::

        process.poll()              # Returns None if still running, else return code
        process.wait()              # Wait for completion (blocking)
        process.terminate()         # Send SIGTERM (graceful)
        process.kill()              # Send SIGKILL (force)
        process.returncode          # Access return code after completion

    See ``subprocess.Popen(...)`` for more details.
    """
    logger.info(' '.join(map(str, args)))

    if dry:
        return None

    defaults = dict(
        cwd=PROJECT_ROOT,
    )

    try:
        return subprocess.Popen(args, **(defaults | kwargs))
    except subprocess.CalledProcessError as e:
        logger.error(e)
        raise typer.Exit(1)


def is_package_installed(package_name: str) -> bool:
    """Check if a Python package is installed."""
    import importlib.util

    return importlib.util.find_spec(package_name) is not None


def install_package(package: str, package_install: str | None = None, dry: bool = False):
    """
    Install a Python package if not already installed.

    :param package: Name of the package to check/install.
    :param package_install: Name of the package to install, if different from the name to check.
    :param dry: Show the command that would be run without running it.
    """
    if is_package_installed(package):
        logger.debug(f'Package `{package}` is already installed.')
        return

    run(sys.executable, '-m', 'pip', 'install', package_install or package, dry=dry)


def multiple_parameters(parameter: str, *options) -> list[str]:
    return list(chain.from_iterable(zip([parameter] * len(options), map(str, options))))


def get_logger(name: str | None = 'typer-invoke', level=logging.DEBUG) -> logging.Logger:
    """Set up logging configuration with Rich handler and custom formatting."""

    # Create logger
    _logger = logging.getLogger(name)
    _logger.setLevel(level)
    _logger.handlers.clear()
    handler = RichHandler(
        level=level,
        show_time=False,
        show_level=True,
        show_path=False,
        markup=True,
        rich_tracebacks=False,
    )

    # Set custom format string and add handler
    formatter = logging.Formatter(fmt='%(message)s', datefmt='[%X]')  # Time format: [HH:MM:SS]
    handler.setFormatter(formatter)
    _logger.addHandler(handler)

    # Prevent logs from being handled by root logger (avoid duplicate output)
    _logger.propagate = False

    return _logger


logger = get_logger()
