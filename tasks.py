import os
from pathlib import Path

from invoke import Collection, task

from app.utils import get_asset

PROJECT_DIR = Path()
UI_FILES = tuple(get_asset('ui').glob("**/*.ui"))
os.environ.setdefault('INVOKE_RUN_ECHO', '1')  # Show commands by default


@task(
    help={
        'file': '`.ui` file to be converted to `.py`. `.ui` extension not required. '
        f'If not supplied, all files will be converted. Available files: {", ".join(p.stem for p in UI_FILES)}'
    }
)
def ui_py(c, file=None):
    """
    Convert QT `.ui` files into `.py`.
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
def lint_all(c):
    """
    Run all linters.
    Config for each of the tools is in `pyproject.toml` and `setup.cfg`.
    """
    c.run('safety check')


@task
def lint_black(c):
    c.run('black .')


@task
def lint_flake8(c):
    c.run('flake8 .')


@task
def lint_isort(c):
    c.run('isort .')


@task
def lint_mypy(c):
    c.run('mypy .')


@task
def lint_safety(c):
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
docs = Collection('docs')
docs.add_task(docs_serve, 'serve')
docs.add_task(docs_deploy, 'deploy')
lint = Collection('lint')
lint.add_task(lint_all, 'all')
lint.add_task(lint_black, 'black')
lint.add_task(lint_flake8, 'flake8')
lint.add_task(lint_isort, 'isort')
lint.add_task(lint_mypy, 'mypy')
lint.add_task(lint_safety, 'safety')
ui = Collection('ui')
ui.add_task(ui_py, 'py')
ui.add_task(ui_edit, 'edit')
ns.add_collection(docs)
ns.add_collection(lint)
ns.add_collection(ui)
