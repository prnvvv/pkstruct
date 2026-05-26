"""
pkstruct.shared.validators
~~~~~~~~~~~~~~~~~~~~~~~~~~
Reusable input-validation helpers for all pkstruct modules.
"""
from __future__ import annotations

from typing import Any

from pkstruct.shared.exceptions import (
    IndexOutOfRangeError,
    InvalidRangeError,
    ValidationError,
)


def validate_index(index: int, size: int, *, allow_end: bool = False) -> None:
    """Ensure *index* is a valid position in a structure of *size* elements.

    Args:
        index: The index to validate (may be negative for tail-relative access).
        size: Current number of elements.
        allow_end: If True, an index equal to *size* is permitted (append position).

    Raises:
        ValidationError: If *index* is not an ``int``.
        IndexOutOfRangeError: If *index* is out of the allowed range.
    """
    if not isinstance(index, int):
        raise ValidationError(f"Index must be an int, got {type(index).__name__!r}.")
    upper = size if allow_end else size - 1
    if size == 0 and not allow_end:
        raise IndexOutOfRangeError(index, size)
    normalised = index if index >= 0 else index + size
    if not (0 <= normalised <= upper):
        raise IndexOutOfRangeError(index, size)


def validate_range(start: int, end: int, size: int) -> tuple[int, int]:
    """Normalise and validate a [start, end] range (both inclusive).

    Args:
        start: Start index (may be negative).
        end:   End index (may be negative).
        size:  Current number of elements.

    Returns:
        Tuple ``(normalised_start, normalised_end)`` where both are ≥ 0.

    Raises:
        ValidationError: If inputs are not integers.
        InvalidRangeError: If the range is logically invalid.
    """
    if not (isinstance(start, int) and isinstance(end, int)):
        raise ValidationError("Range bounds must be integers.")
    ns = start if start >= 0 else start + size
    ne = end if end >= 0 else end + size
    if not (0 <= ns <= ne < size):
        raise InvalidRangeError(start, end, size)
    return ns, ne


def validate_non_empty_list(items: Any, param_name: str = "items") -> None:
    """Ensure *items* is a non-empty list.

    Raises:
        ValidationError: If not a list or is empty.
    """
    if not isinstance(items, list):
        raise ValidationError(
            f"'{param_name}' must be a list, got {type(items).__name__!r}."
        )
    if len(items) == 0:
        raise ValidationError(f"'{param_name}' must not be empty.")


def validate_positive_int(value: Any, param_name: str = "value") -> None:
    """Ensure *value* is a positive integer (> 0).

    Raises:
        ValidationError: If not a positive integer.
    """
    if not isinstance(value, int) or value <= 0:
        raise ValidationError(
            f"'{param_name}' must be a positive integer, got {value!r}."
        )


def validate_non_negative_int(value: Any, param_name: str = "value") -> None:
    """Ensure *value* is a non-negative integer (≥ 0).

    Raises:
        ValidationError: If not a non-negative integer.
    """
    if not isinstance(value, int) or value < 0:
        raise ValidationError(
            f"'{param_name}' must be a non-negative integer, got {value!r}."
        )