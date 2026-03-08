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


@app.command(name='ruff')
def lint_ruff(path='.', check: bool = False, dry: DryAnnotation = False):
    if check:
        run('ruff', 'check', path, dry=dry)
        run('ruff', 'format', '--check', path, dry=dry)
    else:
        run('ruff', 'check', '--fix', path, dry=dry)
        run('ruff', 'format', path, dry=dry)


@app.command(name='mypy')
def lint_mypy(path=None, dry: DryAnnotation = False):
    if path:
        run('mypy', path, dry=dry)
    else:
        run('mypy', 'src', dry=dry)
        run('mypy', 'tests', dry=dry)
        run('mypy', 'admin', dry=dry)


@app.command(name='all')
def lint_all(dry: DryAnnotation = False):
    """
    Run all linters.

    Config for each of the tools is in ``pyproject.toml``.
    """
    lint_ruff(check=True, dry=dry)
    lint_mypy(dry=dry)

    logger.info('Done')


if __name__ == '__main__':
    app()
