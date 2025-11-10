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
    run(dry, 'pre-commit', 'install')


# `upgrade` instead of `update` to maintain similar naming to `pip-compile upgrade`
@app.command(name='upgrade')
def precommit_upgrade(dry: DryAnnotation = False):
    """
    Upgrade pre-commit config to the latest repos' versions.
    """
    run(dry, 'pre-commit', 'autoupdate')


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
    hook = hook or '--all-files'
    run(dry, 'pre-commit' 'run', hook)


if __name__ == '__main__':
    app()
