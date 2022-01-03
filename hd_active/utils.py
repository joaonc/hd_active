from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[1].resolve()
ASSETS_ROOT = PROJECT_ROOT / 'assets'


def get_asset(*args) -> Path:
    return ASSETS_ROOT / '/'.join(args)
