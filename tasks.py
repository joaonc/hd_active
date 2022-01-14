from pathlib import Path

from invoke import task

from app.utils import get_asset

PROJECT_DIR = Path()
UI_FILES = tuple(get_asset('ui').glob("**/*.ui"))


@task(
    help={
        'file': '`.ui` file to be converted to `.py`. If not supplied, all files will be converted. Available files: '
        f'{", ".join(p.stem for p in UI_FILES)}'
    }
)
def ui(c, file=None):
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
