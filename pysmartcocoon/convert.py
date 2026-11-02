"""Coerce API values to the types the models declare.

The API sends decimals as strings ("21.0", "22.8"), while the models and
`types.py` declared them as floats. Consumers that check types -- the Home
Assistant integration accepts only numbers for temperatures -- silently
dropped every one of them.
"""

from typing import Any, Optional


def as_float(value: Any) -> Optional[float]:
    """Return value as a float, or None if it is missing or not numeric."""
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def as_int(value: Any) -> Optional[int]:
    """Return value as an int, or None if it is missing or not integral."""
    if value is None or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return int(number) if number.is_integer() else None
