"""
pkstruct.linear.exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~~
Re-exports the shared exception hierarchy with linear-specific aliases.
"""
from pkstruct.shared.exceptions import (
    ConcurrencyError,
    EmptyStructureError,
    IndexOutOfRangeError,
    InvalidRangeError,
    PkstructError,
    SerializationError,
    ValidationError,
    ValueNotFoundError,
)

__all__ = [
    "PkstructError",
    "ValidationError",
    "IndexOutOfRangeError",
    "ValueNotFoundError",
    "EmptyStructureError",
    "SerializationError",
    "ConcurrencyError",
    "InvalidRangeError",
]