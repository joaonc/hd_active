#!python
"""
Python packages related tasks.
"""

from enum import StrEnum
from typing import Annotated

import typer

from admin.utils import DryAnnotation, logger, multiple_parameters, run

app = typer.Typer(
    help=__doc__,
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode='markdown',
)


class Requirements(StrEnum):
    """
    Requirement aliases.

    Keep these values and names to preserve the `inv pip ...` interface.
    """

    MAIN = 'requirements'
    DEV = 'requirements-dev'
    DOCS = 'requirements-docs'


RequirementsAnnotation = Annotated[
    list[str] | None,
    typer.Argument(
        help='Requirement alias(es). If not set, defaults to all aliases.\nValues can be '
        + ', '.join([f'`{x.name.lower()}`' for x in Requirements]),
        show_default=False,
    ),
]


def _normalize_requirement(requirement: str | Requirements) -> Requirements:
    if isinstance(requirement, Requirements):
        return requirement

    value = requirement.strip().lower()
    if value in {x.value for x in Requirements}:
        return Requirements(value)

    key = value.replace('-', '_').upper()
    try:
        return Requirements[key]  # type: ignore[index]
    except KeyError:
        logger.error(f'`{requirement}` is an unknown requirements alias.')
        raise typer.Exit(1)


def _get_requirements(requirements: list[str | Requirements] | None) -> list[Requirements]:
    if requirements is None:
        return list(Requirements)
    return [_normalize_requirement(r) for r in requirements]


def _requirements_to_groups(requirements: list[Requirements]) -> list[str]:
    groups: list[str] = []
    for requirement in requirements:
        if requirement == Requirements.DEV:
            groups.append('dev')
        elif requirement == Requirements.DOCS:
            groups.append('docs')
    return groups


@app.command(name='compile')
def pip_compile(
    requirements: RequirementsAnnotation = None,
    clean: Annotated[
        bool,
        typer.Option(
            help='Recreate lock file by deleting it first.',
        ),
    ] = False,
    dry: DryAnnotation = False,
):
    """
    Update lock file(s) based on `pyproject.toml`.
    """
    _ = _get_requirements(requirements)
    if clean:
        run('uv', 'lock', '--upgrade', dry=dry)
    else:
        run('uv', 'lock', dry=dry)


@app.command(name='sync')
def pip_sync(requirements: RequirementsAnnotation = None, dry: DryAnnotation = False):
    """
    Synchronize environment with the lock file.
    """
    resolved = _get_requirements(requirements)
    groups = _requirements_to_groups(resolved)

    run('uv', 'sync', '--no-default-groups', *multiple_parameters('--group', *groups), dry=dry)


@app.command(name='package')
def pip_package(
    requirements: RequirementsAnnotation,
    package: Annotated[
        list[str], typer.Option('--package', '-p', help='One or more packages to upgrade.')
    ],
    dry: DryAnnotation = False,
):
    """
    Upgrade one or more packages in the lock file.
    """
    _ = _get_requirements(requirements)
    run('uv', 'lock', *multiple_parameters('--upgrade-package', *package), dry=dry)


@app.command(name='upgrade')
def pip_upgrade(requirements: RequirementsAnnotation = None, dry: DryAnnotation = False):
    """
    Try to upgrade all dependencies to their latest versions.
    """
    _ = _get_requirements(requirements)
    run('uv', 'lock', '--upgrade', dry=dry)


@app.command(name='install')
def pip_install(requirements: RequirementsAnnotation = None, dry: DryAnnotation = False):
    """
    Equivalent to `uv sync` using requirements aliases.
    """
    pip_sync(requirements=requirements, dry=dry)


if __name__ == '__main__':
    app()
