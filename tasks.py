import os
from pathlib import Path

from invoke import Collection, task

from app.utils import get_asset

PROJECT_DIR = Path()
UI_FILES = tuple(get_asset('ui').glob("**/*.ui"))
os.environ.setdefault('INVOKE_RUN_ECHO', '1')  # Show commands by default


@task(
    help={
        'file': '`.ui` file to be converted to `.py`. If not supplied, all files will be converted. Available files: '
        f'{", ".join(p.stem for p in UI_FILES)}'
    }
)
def ui_py(c, file=None):
    """
    Convert QT `.ui` files into `.py`. `.ui` extension not required in the parameter.
    """
    if file:
        file_stems = [file[:-3] if file.lower().endswith('.ui') else file]
    else:
        file_stems = [p.stem for p in UI_FILES]

    for file_stem in file_stems:
        ui_file_path = next(p for p in UI_FILES if p.stem == file_stem)
        py_file_path = PROJECT_DIR / 'app/ui/forms' / f'{file_stem}_ui.py'

        c.run(f'pyside6-uic {ui_file_path} -o {py_file_path}')


@task(help={'file': f'`.ui` file to be edited. Available files: {", ".join(p.stem for p in UI_FILES)}'})
def ui_edit(c, file):
    """
    Edit a file in QT Designer.
    """
    file_stem = file[:-3] if file.lower().endswith('.ui') else file
    file_path = next(p for p in UI_FILES if p.stem == file_stem)

    c.run(f'pyside6-designer {file_path}', asynchronous=True)


@task
def lint(c):
    """
    Run linters (isort, black).
    Config for each of the tools is in `pyproject.toml`.
    """
    c.run('isort .')
    c.run('black .')
    c.run('flake8 .')
    c.run('mypy .')
    c.run('safety check')


@task
def test(c):
    """
    Run unit tests.
    """
    c.run('python -m pytest .')


@task
def docs_serve(c):
    """
    Start documentation local server.
    """
    c.run('mkdocs serve')


@task
def docs_deploy(c):
    """
    Publish documentation to GitHub Pages at https://joaonc.github.io/hd_active.
    """
    c.run('mkdocs gh-deploy')


ns = Collection()  # Main namespace
ns.add_task(test)
ui = Collection('ui')
ui.add_task(ui_py, 'py')
ui.add_task(ui_edit, 'edit')
docs = Collection('docs')
docs.add_task(docs_serve, 'serve')
docs.add_task(docs_deploy, 'deploy')
ns.add_collection(ui)
ns.add_collection(docs)
