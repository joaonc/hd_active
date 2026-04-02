from numbers import Number
from pathlib import Path
from typing import Any, Iterable

PROJECT_ROOT = Path(__file__).parents[2].resolve()
ASSETS_ROOT = PROJECT_ROOT / 'assets'


def get_asset(*args) -> Path:
    return ASSETS_ROOT / '/'.join(args)


def is_truthy(value: Any, raise_if_unclear: bool = True, empty_means_false: bool = False) -> bool:
    """
    Returns ``True`` if the value is *truthy*.
    If the value is not *truthy*, then the behavior of this function depends on the remaining
    arguments.

    See parameters documentation for more details.

    A value is *truthy* if: (returns ``True`` always)
        * String 'true' or 'yes' (case-insensitive).
        * Number 1 or a string representation of the number 1.

    A value is *falsy* if: (returns ``False`` always)
        * String 'false' or 'no' (case-insensitive).
        * Number 0 or a string representation of the number 0.

    :param value: The value to check for truthiness/falseness.
    :param raise_if_unclear: If ``True``, raise ``ValueError`` if unable to determine
        truthiness/falseness.
        If ``False``, then the function returns ``False`` if not truthy.
    :param empty_means_false: If ``True``, consider empty iterables (including string) or ``None``
        as ``False``.
        If ``False``, these will be considered *unclear* and ``raise_if_unclear`` will determine
        behavior of this function.

    Notes:
        * An empty iterable is considered falsy if ``empty_means_false`` is ``True``, but a
          non-empty iterable is *not* considered truthy unless it's a string that is truthy (ie,
          are considered *unclear*).
        * Numbers or string representation of numbers that are not ``1`` or ``0`` are considered
          *unclear*.
    """
    truthy = False
    falsy = False
    if isinstance(value, str):
        value_lower = value.lower()
        if value_lower in ['true', 'yes']:
            truthy = True
        elif value_lower in ['false', 'no']:
            falsy = True
        elif value == '' and empty_means_false:
            falsy = True
        else:
            try:
                return is_truthy(float(value), raise_if_unclear=raise_if_unclear)
            except (TypeError, ValueError):
                pass
    elif isinstance(value, bool):
        truthy = value
        falsy = not value
    elif isinstance(value, Number):
        truthy = value == 1
        falsy = value == 0
    elif isinstance(value, Iterable):
        if empty_means_false:
            falsy = not bool(value)
    else:
        return is_truthy(bool(value))

    if truthy:
        return True
    if not falsy and raise_if_unclear:
        raise ValueError(f'Value is neither truthy or falsy: `{value}`.')

    return False
