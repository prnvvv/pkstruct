"""
pkstruct.trees.exceptions
=========================
Custom exception hierarchy for the trees module.

All tree-specific exceptions inherit from :class:`TreeError` so callers
can catch the entire family with a single ``except TreeError`` clause
while still being able to distinguish individual error types.
"""

from __future__ import annotations

from pkstruct.shared.exceptions import SerializationError as _SharedSerializationError

__all__ = [
    "TreeError",
    "KeyNotFoundError",
    "DuplicateKeyError",
    "EmptyTreeError",
    "InvalidOrderError",
    "InvalidOperationError",
    "TreeBalanceError",
    "SerializationError",
    "InvalidIntervalError",
    "IndexOutOfBoundsError",
]


class TreeError(Exception):
    """Base exception for all tree-related errors."""


class KeyNotFoundError(TreeError):
    """Raised when a requested key does not exist in the tree."""

    def __init__(self, key: object) -> None:
        super().__init__(f"Key not found: {key!r}")
        self.key = key


class DuplicateKeyError(TreeError):
    """Raised when inserting a key that already exists (where disallowed)."""

    def __init__(self, key: object) -> None:
        super().__init__(f"Duplicate key: {key!r}")
        self.key = key


class EmptyTreeError(TreeError):
    """Raised when an operation requires a non-empty tree."""

    def __init__(self, operation: str = "operation") -> None:
        super().__init__(f"Cannot perform '{operation}' on an empty tree.")
        self.operation = operation


class InvalidOrderError(TreeError):
    """Raised when a B-Tree / B+Tree order value is invalid."""

    def __init__(self, order: int) -> None:
        super().__init__(f"Tree order must be >= 2, got {order}.")
        self.order = order


class InvalidOperationError(TreeError):
    """Raised when an unsupported operation string is requested."""

    def __init__(self, operation: str) -> None:
        super().__init__(f"Unsupported operation: {operation!r}.")
        self.operation = operation


class TreeBalanceError(TreeError):
    """Raised when an internal balance invariant is violated."""


class SerializationError(TreeError, _SharedSerializationError):
    """Raised when tree (de)serialization fails."""


class InvalidIntervalError(TreeError):
    """Raised when an interval [lo, hi] has lo > hi."""

    def __init__(self, lo: object, hi: object) -> None:
        super().__init__(f"Invalid interval: [{lo!r}, {hi!r}] (lo > hi).")
        self.lo = lo
        self.hi = hi


class IndexOutOfBoundsError(TreeError):
    """Raised when a k-th order statistic index is out of range."""

    def __init__(self, index: int, size: int) -> None:
        super().__init__(
            f"Index {index} out of bounds for tree of size {size}."
        )
        self.index = index
        self.size = size