from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).parents[2].resolve()
ASSETS_ROOT = PROJECT_ROOT / 'assets'


def get_asset(*args) -> Path:
    return ASSETS_ROOT / '/'.join(args)


def is_truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    value_lower = str(value).lower()
    if value_lower in ['true', 'yes', 'on'] or (isinstance(value, (int, float)) and value != 0):
        return True
    elif value_lower in ['false', 'no', 'off'] or (isinstance(value, (int, float)) and value == 0):
        return False
    raise ValueError(f'Undefined truthy value: {value}')
