#!python
"""
UI operations for Qt.
"""
from typing import Annotated

import typer

from admin import ASSETS_DIR, SOURCE_DIR
from admin.utils import DryAnnotation, logger, run, run_async

UI_FILES = tuple((ASSETS_DIR / 'ui').glob('**/*.ui'))
"""
Qt ``.ui`` files.
"""

QRC_FILES = tuple(ASSETS_DIR.glob('**/*.qrc'))
"""
Qt ``.qrc`` resource files.
"""

app = typer.Typer(
    help=__doc__,
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode='markdown',
)


@app.command(name='py')
def ui_py(
    file: Annotated[
        list[str] | None,
        typer.Argument(
            help='`.ui` file to be converted to `.py`. `.ui` extension not required. '
            'If not supplied, all files will be converted. '
            f'Available files: {", ".join(p.stem for p in UI_FILES)}.',
            show_default=False,
        ),
    ] = None,
    dry: DryAnnotation = False,
):
    """
    Convert Qt `.ui` files into `.py`.
    """
    if file:
        file_stems = [
            (_f2[:-3] if _f2.lower().endswith('.ui') else _f2)
            for _f2 in [_f1.strip() for _f1 in file]
        ]
    else:
        file_stems = [p.stem for p in UI_FILES]

    for file_stem in file_stems:
        try:
            file_path_in = next(p for p in UI_FILES if p.stem == file_stem)
        except StopIteration:
            logger.error(
                f'File "{file}" not found. Available files: {", ".join(p.stem for p in UI_FILES)}'
            )
            raise typer.Exit(1)

        file_path_out = SOURCE_DIR / 'ui/forms' / f'ui_{file_stem}.py'

        run(dry, 'pyside6-uic', str(file_path_in), '-o', str(file_path_out), '--from-imports')


@app.command(name='rc')
def ui_rc(
    file: Annotated[
        list[str] | None,
        typer.Argument(
            help='`.qrc` file(s) to be converted to `.py`. `.qrc` extension not required. '
            'If not supplied, all files will be converted. '
            f'Available files: {", ".join(p.stem for p in QRC_FILES)}.',
            show_default=False,
        ),
    ] = None,
    dry: DryAnnotation = False,
):
    """
    Convert Qt `.qrc` files into `.py`.
    """
    if file:
        file_stems = [
            (_f2[:-4] if _f2.lower().endswith('.qrc') else _f2)
            for _f2 in [_f1.strip() for _f1 in file]
        ]
    else:
        file_stems = [p.stem for p in QRC_FILES]

    for file_stem in file_stems:
        try:
            file_path_in = next(p for p in QRC_FILES if p.stem == file_stem)
        except StopIteration:
            logger.error(
                f'File "{file}" not found. Available files: {", ".join(p.stem for p in QRC_FILES)}'
            )
            raise typer.Exit(1)

        file_path_out = SOURCE_DIR / 'ui/forms' / f'{file_stem}_rc.py'

        run(dry, 'pyside6-rcc', str(file_path_in), '-o', str(file_path_out))


@app.command(name='edit')
def ui_edit(
    file: Annotated[
        str,
        typer.Argument(
            help=f'`.ui` file to be edited. Available files: {", ".join(p.stem for p in UI_FILES)}.'
        ),
    ],
    dry: DryAnnotation = False,
):
    """
    Edit a file in QT Designer.
    """
    file_stem = file[:-3] if file.lower().endswith('.ui') else file
    try:
        ui_file_path = next(p for p in UI_FILES if p.stem == file_stem)
    except StopIteration:
        logger.error(
            f'File "{file}" not found. Available files: {", ".join(p.stem for p in UI_FILES)}'
        )
        raise typer.Exit(1)

    run_async(dry, 'pyside6-designer', str(ui_file_path))


if __name__ == '__main__':
    app()
