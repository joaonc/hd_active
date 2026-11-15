#!python
"""
Linting and static type checking.
"""

from typing import Annotated

import typer

from admin.utils import DryAnnotation, logger, run

app = typer.Typer(
    help=__doc__,
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode='markdown',
)


@app.command(name='ruff')
def lint_ruff(
    path: Annotated[str, typer.Argument(help='Path to directory or file to lint.')] = '.',
    check: Annotated[
        bool,
        typer.Option(
            help='Check-only mode: report violations without fixing or reformatting. '
            'Exits non-zero if any issues are found. Use this in CI.',
        ),
    ] = False,
    dry: DryAnnotation = False,
):
    if check:
        run('ruff', 'check', path, dry=dry)
        run('ruff', 'format', '--check', path, dry=dry)
    else:
        run('ruff', 'check', '--fix', path, dry=dry)
        run('ruff', 'format', path, dry=dry)


@app.command(name='ty')
def lint_ty(
    path: Annotated[
        str | None, typer.Argument(help='Path to type-check. Default is the whole project.')
    ] = None,
    dry: DryAnnotation = False,
):
    run('ty', 'check', path, dry=dry)


@app.command(name='all')
def lint_all(
    check: Annotated[
        bool,
        typer.Option(
            help='Check-only mode: report violations without fixing or reformatting. '
            'Exits non-zero if any issues are found. Use this in CI.',
        ),
    ] = False,
    dry: DryAnnotation = False,
):
    """
    Run all linters.

    Config for each of the tools is in ``pyproject.toml``.
    """
    lint_ruff(check=check, dry=dry)
    lint_ty(dry=dry)

    logger.info('Done')


if __name__ == '__main__':
    app()
