"""
pkstruct.shared.exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~~
Base exception hierarchy shared across all pkstruct modules.
"""
from __future__ import annotations


class PkstructError(Exception):
    """Root exception for all pkstruct errors."""


class ValidationError(PkstructError):
    """Raised when input validation fails."""


class IndexOutOfRangeError(PkstructError, IndexError):
    """Raised when a positional index is out of valid range."""

    def __init__(self, index: int, size: int) -> None:
        super().__init__(f"Index {index} is out of range for list of size {size}.")
        self.index = index
        self.size = size


class ValueNotFoundError(PkstructError, ValueError):
    """Raised when a value is not found in the structure."""

    def __init__(self, value: object) -> None:
        super().__init__(f"Value {value!r} not found in the structure.")
        self.value = value


class EmptyStructureError(PkstructError):
    """Raised when an operation requires a non-empty structure."""

    def __init__(self, operation: str = "operation") -> None:
        super().__init__(f"Cannot perform '{operation}' on an empty structure.")
        self.operation = operation


class SerializationError(PkstructError):
    """Raised when serialization or deserialization fails."""


class ConcurrencyError(PkstructError):
    """Raised on threading/locking issues."""


class InvalidRangeError(PkstructError, ValueError):
    """Raised when a range (start, end) is logically invalid."""

    def __init__(self, start: int, end: int, size: int) -> None:
        super().__init__(
            f"Range ({start}, {end}) is invalid for structure of size {size}."
        )
        self.start = start
        self.end = end
        self.size = size