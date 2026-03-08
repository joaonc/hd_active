#!python
"""
Python packages related tasks.
"""

from enum import StrEnum
from pathlib import Path
from typing import Annotated

import typer

from admin import PROJECT_ROOT
from admin.utils import DryAnnotation, logger, multiple_parameters, run

REQUIREMENTS_DIR = PROJECT_ROOT / 'admin' / 'requirements'

app = typer.Typer(
    help=__doc__,
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode='markdown',
)


class Requirements(StrEnum):
    """
    Requirements files.

    Order matters as most operations with multiple files need ``requirements.txt`` to be processed
    first.
    Add new requirements files here.
    """

    MAIN = 'requirements'
    DEV = 'requirements-dev'


class RequirementsType(StrEnum):

    IN = 'in'
    OUT = 'txt'


RequirementsAnnotation = Annotated[
    list[str] | None,
    typer.Argument(
        help='Requirement file(s) to compile. If not set, all files are compiled.\nValues can be '
        + ', '.join([f'`{x.name.lower()}`' for x in Requirements]),
        show_default=False,
    ),
]


def _get_requirements_file(
    requirements: str | Requirements, requirements_type: str | RequirementsType
) -> Path:
    """Return the full requirements file path."""
    if isinstance(requirements, Requirements):
        reqs = requirements
    else:
        try:
            reqs = Requirements[requirements.upper()]  # noqa
        except KeyError:
            try:
                reqs = Requirements(requirements.lower())
            except ValueError:
                logger.error(f'`{requirements}` is an unknown requirements file.')
                raise typer.Exit(1)

    if isinstance(requirements_type, RequirementsType):
        reqs_type = requirements_type
    else:
        reqs_type = RequirementsType(requirements_type.lstrip('.').lower())

    return REQUIREMENTS_DIR / f'{reqs.value}.{reqs_type.value}'


def _get_requirements_files(
    requirements: list[str | Requirements] | None, requirements_type: str | RequirementsType
) -> list[Path]:
    """Get full filename+extension and sort by the order defined in ``Requirements``."""
    requirements_files = list(Requirements) if requirements is None else requirements
    return [_get_requirements_file(r, requirements_type) for r in requirements_files]


@app.command(name='compile')
def pip_compile(
    requirements: RequirementsAnnotation = None,
    clean: Annotated[
        bool,
        typer.Option(
            help=f'Delete the existing requirements `{RequirementsType.OUT.value}` files, forcing '
            f'a clean compilation.',
        ),
    ] = False,
    dry: DryAnnotation = False,
):
    """
    Compile requirements file(s).
    """
    if clean and not dry:
        for filename in _get_requirements_files(requirements, RequirementsType.OUT):
            filename.unlink(missing_ok=True)

    for filename in _get_requirements_files(requirements, RequirementsType.IN):
        output_file = filename.with_suffix('.txt')
        run(
            'uv',
            'pip',
            'compile',
            '--no-header',
            '--no-strip-extras',
            filename.name,
            '-o',
            output_file.name,
            dry=dry,
            cwd=REQUIREMENTS_DIR,
        )


@app.command(name='sync')
def pip_sync(requirements: RequirementsAnnotation = None, dry: DryAnnotation = False):
    """
    Synchronize environment with requirements file.
    """
    run('uv', 'pip', 'sync', *_get_requirements_files(requirements, RequirementsType.OUT), dry=dry)


@app.command(name='package')
def pip_package(
    requirements: RequirementsAnnotation,
    package: Annotated[
        list[str], typer.Option('--package', '-p', help='One or more packages to upgrade.')
    ],
    dry: DryAnnotation = False,
):
    """
    Upgrade one or more packages.
    """
    for filename in _get_requirements_files(requirements, RequirementsType.IN):
        output_file = filename.with_suffix('.txt')
        run(
            'uv',
            'pip',
            'compile',
            *multiple_parameters('--upgrade-package', *package),
            str(filename),
            '-o',
            str(output_file),
            dry=dry,
        )


@app.command(name='upgrade')
def pip_upgrade(requirements: RequirementsAnnotation = None, dry: DryAnnotation = False):
    """
    Try to upgrade all dependencies to their latest versions.

    Equivalent to ``compile`` with ``--clean`` option.

    Use ``package`` to only upgrade individual packages,
    Ex ``pip package dev mypy ruff``.
    """
    for filename in _get_requirements_files(requirements, RequirementsType.IN):
        output_file = filename.with_suffix('.txt')
        run(
            'uv',
            'pip',
            'compile',
            '--no-strip-extras',
            '--upgrade',
            str(filename),
            '-o',
            str(output_file),
            dry=dry,
        )


@app.command(name='install')
def pip_install(requirements: RequirementsAnnotation, dry: DryAnnotation = False):
    """
    Equivalent to ``uv pip install -r <requirements*.txt>``.
    """
    requirements_files = _get_requirements_files(requirements, RequirementsType.OUT)  # type: ignore
    run('uv', 'pip', 'install', *multiple_parameters('-r', *requirements_files), dry=dry)


if __name__ == '__main__':
    app()
