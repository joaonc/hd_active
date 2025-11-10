#!python
"""
Create and publish documentation.
"""

import typer

from admin import PROJECT_ROOT
from admin.utils import DryAnnotation, logger, run

app = typer.Typer(
    help=__doc__,
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode='markdown',
)


@app.command(name='serve')
def docs_serve(dry: DryAnnotation = False):
    """
    Start documentation local server.
    """
    run(dry, 'mkdocs', 'serve')


@app.command(name='deploy')
def docs_deploy(dry: DryAnnotation = False):
    """
    Publish documentation to GitHub Pages at https://joaonc.github.io/hd_active
    """
    run(dry, 'mkdocs', 'gh-deploy')


@app.command(name='clean')
def docs_clean(dry: DryAnnotation = False):
    """
    Delete documentation website static files.
    """
    import shutil

    docs_dir = PROJECT_ROOT / 'site'
    logger.info(f'Deleting {docs_dir}')
    if not dry:
        shutil.rmtree(PROJECT_ROOT / 'site', ignore_errors=True)


if __name__ == '__main__':
    app()
