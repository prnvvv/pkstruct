"""
pkstruct.linear.linked_lists.nodes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Node definitions for all linked-list variants.

All nodes use ``__slots__`` to minimise per-object memory overhead.
"""
from __future__ import annotations

from typing import Generic, TypeVar

T = TypeVar("T")


class SinglyNode(Generic[T]):
    """A node in a singly-linked list.

    Attributes:
        value: The stored element.
        next:  Reference to the next node, or ``None`` if tail.
    """

    __slots__ = ("value", "next")

    def __init__(self, value: T) -> None:
        self.value: T = value
        self.next: SinglyNode[T] | None = None

    def __repr__(self) -> str:
        return f"SinglyNode({self.value!r})"


class DoublyNode(Generic[T]):
    """A node in a doubly-linked list.

    Attributes:
        value: The stored element.
        next:  Reference to the next node, or ``None`` if tail.
        prev:  Reference to the previous node, or ``None`` if head.
    """

    __slots__ = ("value", "next", "prev")

    def __init__(self, value: T) -> None:
        self.value: T = value
        self.next: DoublyNode[T] | None = None
        self.prev: DoublyNode[T] | None = None

    def __repr__(self) -> str:
        return f"DoublyNode({self.value!r})"


class CircularNode(Generic[T]):
    """A node in a circular singly-linked list.

    Attributes:
        value: The stored element.
        next:  Always points to a valid node (wraps to head at tail).
    """

    __slots__ = ("value", "next")

    def __init__(self, value: T) -> None:
        self.value: T = value
        self.next: CircularNode[T] | None = None  # set to self or next during build

    def __repr__(self) -> str:
        return f"CircularNode({self.value!r})"