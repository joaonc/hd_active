from collections.abc import Iterable, Sized
from decimal import Decimal, InvalidOperation
from numbers import Number
from os import PathLike
from typing import Any

FilePath = str | PathLike[str]


def is_truthy(value: Any, raise_if_unclear: bool = True, empty_means_false: bool = False) -> bool:
    """
    Returns ``True`` if the value is *truthy*.
    If the value is not *truthy*, then the behavior of this function depends on the remaining
    arguments.

    See parameters documentation for more details.

    A value is *truthy* if: (returns ``True`` always)
        * String 'true', 'yes' or 'on' (case-insensitive).
        * Number 1 or a string representation of the number 1.

    A value is *falsy* if: (returns ``False`` always)
        * String 'false', 'no' or 'off' (case-insensitive).
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
        * Any other type of value (including ``None`` unless ``empty_means_false`` is ``True``) is
          considered *unclear*.
    """
    truthy = False
    falsy = False
    if isinstance(value, str):
        value_lower = value.lower()
        if value_lower in ['true', 'yes', 'on']:
            truthy = True
        elif value_lower in ['false', 'no', 'off']:
            falsy = True
        elif value == '' and empty_means_false:
            falsy = True
        else:
            # `Decimal` instead of `float` so that values like '1.0000000000000001' aren't rounded
            # to 1.
            try:
                number = Decimal(value.strip())
            except InvalidOperation:
                pass
            else:
                if number.is_finite():
                    truthy = number == 1
                    falsy = number == 0
    elif isinstance(value, bool):
        truthy = value
        falsy = not value
    elif isinstance(value, Number):
        truthy = value == 1
        falsy = value == 0
    elif value is None:
        falsy = empty_means_false
    elif isinstance(value, Iterable):
        falsy = empty_means_false and _is_empty(value)

    if truthy:
        return True
    if not falsy and raise_if_unclear:
        raise ValueError(f'Value is neither truthy or falsy: `{value}`.')

    return False


_SENTINEL = object()


def _is_empty(iterable: Iterable) -> bool:
    """
    Whether the iterable has no items, without relying on its truthiness (an empty iterator is
    truthy) or on it having a length.

    Iterators have no length, so one is probed by taking its first item, which consumes it. That's
    acceptable here since a non-empty iterable is *unclear* regardless.
    """
    if isinstance(iterable, Sized):
        return len(iterable) == 0
    return next(iter(iterable), _SENTINEL) is _SENTINEL
