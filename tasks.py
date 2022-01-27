import os
from pathlib import Path

from invoke import Collection, task

from app.utils import get_asset

PROJECT_DIR = Path()
UI_FILES = tuple(get_asset('ui').glob("**/*.ui"))
REQUIREMENTS_FILES = tuple(Path().glob("*requirements.txt"))
REQUIREMENTS_MAIN = 'main'
REQUIREMENTS_FILES_MAPPING = {
    s[0] if len(s) > 1 else 'main': filename
    for s, filename in ((p.stem.split('-'), p.name) for p in REQUIREMENTS_FILES)
}
# Sort keys to make `requirements.txt` first
# In several `pip-tools` operations working with more than one requirements file, `requirements.txt` needs to be first
REQUIREMENTS_FILES_MAPPING = {
    k: REQUIREMENTS_FILES_MAPPING[k]
    for k in ([REQUIREMENTS_MAIN] + sorted(x for x in REQUIREMENTS_FILES_MAPPING if x != REQUIREMENTS_MAIN))
}
REQUIREMENTS_TASK_HELP = {
    'requirements': '`.in` file. Full name not required, just the initial name before the dash (ex. \'dev\'). '
    f'For main file use \'{REQUIREMENTS_MAIN}\'. Available requirements: {", ".join(REQUIREMENTS_FILES_MAPPING)}.'
}

os.environ.setdefault('INVOKE_RUN_ECHO', '1')  # Show commands by default


def _csstr_to_list(csstr: str) -> list[str]:
    return [s.strip() for s in csstr.split(',')]


def _get_requirements_file(requirements: str) -> str:
    filename = REQUIREMENTS_FILES_MAPPING.get(requirements, requirements)
    if filename not in REQUIREMENTS_FILES_MAPPING.values():
        raise FileNotFoundError(f'`{requirements}` is an unknown requirements file.')

    return filename


def _get_requirements_files(requirements: str | None) -> list[str]:
    if requirements is None:
        filenames = list(REQUIREMENTS_FILES_MAPPING.values())
    else:
        filenames = [_get_requirements_file(r) for r in _csstr_to_list(requirements)]
        # Sort by the order defined in `REQUIREMENTS_FILES_MAPPING`
        filenames = [f for f in REQUIREMENTS_FILES_MAPPING.values() if f in filenames]

    return filenames


@task(
    help={
        'file': '`.ui` file to be converted to `.py`. `.ui` extension not required. Can be a comma separated. '
        f'If not supplied, all files will be converted. Available files: {", ".join(p.stem for p in UI_FILES)}.'
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


@task(help={'file': f'`.ui` file to be edited. Available files: {", ".join(p.stem for p in UI_FILES)}.'})
def ui_edit(c, file):
    """
    Edit a file in QT Designer.
    """
    file_stem = file[:-3] if file.lower().endswith('.ui') else file
    file_path = next(p for p in UI_FILES if p.stem == file_stem)

    c.run(f'pyside6-designer {file_path}', asynchronous=True)


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


@task(lint_isort, lint_black, lint_flake8, lint_mypy, lint_safety)
def lint_all(c):
    """
    Run all linters.
    Config for each of the tools is in `pyproject.toml` and `setup.cfg`.
    """
    print('Done')


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


@task(help=REQUIREMENTS_TASK_HELP)
def pip_compile(c, requirements=None):
    """
    Compile requirements file.
    """
    for filename in _get_requirements_files(requirements):
        c.run(f'pip-compile {filename}')


@task(help=REQUIREMENTS_TASK_HELP)
def pip_sync(c, requirements=None):
    """
    Synchronize environment with requirements file.
    """
    c.run(f'pip-sync {" ".join(_get_requirements_files(requirements))}')


@task(help=REQUIREMENTS_TASK_HELP | {'package': 'Package to upgrade. Can be a comma separated list.'})
def pip_package(c, requirements, package):
    """
    Upgrade package.
    """
    packages = [p.strip() for p in package.split(',')]
    for filename in _get_requirements_files(requirements):
        c.run(f'pip-compile --upgrade-package {" --upgrade-package ".join(packages)} {filename}')


@task(help=REQUIREMENTS_TASK_HELP)
def pip_upgrade(c, requirements):
    """
    Try to upgrade all dependencies to their latest versions.
    """
    for filename in _get_requirements_files(requirements):
        c.run(f'pip-compile --upgrade {filename}')


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
pip = Collection('pip')
pip.add_task(pip_compile, 'compile')
pip.add_task(pip_package, 'package')
pip.add_task(pip_sync, 'sync')
pip.add_task(pip_upgrade, 'upgrade')
ui = Collection('ui')
ui.add_task(ui_py, 'py')
ui.add_task(ui_edit, 'edit')
ns.add_collection(docs)
ns.add_collection(lint)
ns.add_collection(pip)
ns.add_collection(ui)
