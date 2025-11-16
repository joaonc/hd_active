#!python
"""
Linting and static type checking.
"""

import typer

from admin.utils import DryAnnotation, logger, run

app = typer.Typer(
    help=__doc__,
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode='markdown',
)


@app.command(name='black')
def lint_black(path='.', dry: DryAnnotation = False):
    run('black', path, dry=dry)


@app.command(name='flake8')
def lint_flake8(path='.', dry: DryAnnotation = False):
    run('flake8', path, dry=dry)


@app.command(name='isort')
def lint_isort(path='.', dry: DryAnnotation = False):
    run('isort', path, dry=dry)


@app.command(name='mypy')
def lint_mypy(path='.', dry: DryAnnotation = False):
    run('mypy', path, dry=dry)


@app.command(name='all')
def lint_all(dry: DryAnnotation = False):
    """
    Run all linters.

    Config for each of the tools is in ``pyproject.toml``.
    """
    lint_isort(dry=dry)
    lint_black(dry=dry)
    lint_flake8(dry=dry)
    lint_mypy(dry=dry)

    logger.info('Done')


if __name__ == '__main__':
    app()
