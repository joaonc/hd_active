#!python
"""
Precommit linting and static type checking.
"""

from typing import Annotated

import typer

from admin.utils import DryAnnotation, run

app = typer.Typer(
    help=__doc__,
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode='markdown',
)


@app.command(name='install')
def precommit_install(dry: DryAnnotation = False):
    """
    Install pre-commit into the git hooks, which will cause pre-commit to run on automatically.
    This should be the first thing to do after cloning this project and installing requirements.
    """
    run('pre-commit', 'install', dry=dry)


# `upgrade` instead of `update` to maintain similar naming to `uv lock --upgrade`
@app.command(name='upgrade')
def precommit_upgrade(dry: DryAnnotation = False):
    """
    Upgrade pre-commit config to the latest repos' versions.
    """
    run('pre-commit', 'autoupdate', dry=dry)


@app.command(name='run')
def precommit_run(
    hook: Annotated[
        str | None,
        typer.Option(help='Name of hook to run. Default is to run all.', show_default=False),
    ] = None,
    dry: DryAnnotation = False,
):
    """
    Manually run pre-commit hooks.
    """
    run('pre-commit', 'run', hook, '--all-files', dry=dry)


if __name__ == '__main__':
    app()
