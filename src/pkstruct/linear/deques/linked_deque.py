"""
pkstruct.linear.deques.linked_deque
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A double-ended queue backed by a ``DoublyLinkedList``.

``LinkedDeque`` composes the existing production-grade doubly-linked list,
giving O(1) append and pop at both ends without any node-management code.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Literal, TypeVar, cast

from pkstruct.linear.deques.deque import Deque
from pkstruct.linear.exceptions import EmptyStructureError
from pkstruct.linear.linked_lists.doubly_linked_list import DoublyLinkedList
from pkstruct.shared.threading import StructureLock

T = TypeVar("T")

_Side = Literal["left", "right"]


class LinkedDeque(Deque[T]):
    """
    A thread-safe double-ended queue implemented on top of ``DoublyLinkedList``.

    The internal list stores elements from left to right.  ``append(side="left")``
    inserts at the head, ``append(side="right")`` appends at the tail — both O(1).

    Parameters
    ----------
    items:
        Optional iterable of initial values (left-to-right order).
        If omitted the deque starts empty.

    Examples
    --------
    >>> d = LinkedDeque([1, 2, 3])
    >>> d.append(0, side="left")
    >>> d.append(4, side="right")
    >>> d.pop(side="left")
    0
    >>> d.pop(side="right")
    4
    >>> list(d)
    [1, 2, 3]
    """

    __slots__ = ("_list", "_lock")

    def __init__(self, items: list[T] | None = None) -> None:
        self._list: DoublyLinkedList[T] = DoublyLinkedList()
        self._lock: StructureLock = StructureLock()
        if items is not None:
            for item in items:
                self._list.insert(item)

    # ------------------------------------------------------------------ #
    #  Core operations                                                     #
    # ------------------------------------------------------------------ #

    def append(self, value: T, side: _Side = "right") -> None:
        """
        Add *value* to one end of the deque.

        Parameters
        ----------
        value:
            The element to add.
        side:
            ``"left"`` to prepend, ``"right"`` to append (default).
        """
        with self._lock:
            if side == "left":
                self._list.insert(value, position=0)
            else:
                self._list.insert(value)

    def pop(self, side: _Side = "right") -> T:
        """
        Remove and return an element from one end.

        Parameters
        ----------
        side:
            ``"left"`` to remove from the front, ``"right"`` to remove from
            the rear (default).

        Returns
        -------
        T

        Raises
        ------
        EmptyStructureError
            If the deque is empty.
        """
        with self._lock:
            if self._list.is_empty():
                raise EmptyStructureError("pop from an empty deque")
            if side == "left":
                return cast(T, self._list.delete(position=0))
            sz = self._list.size()
            return cast(T, self._list.delete(position=sz - 1))

    def peek(self, side: _Side = "left") -> T:
        """
        Return an element from one end without removing it.

        Parameters
        ----------
        side:
            ``"left"`` to inspect the front (default), ``"right"`` to inspect
            the rear.

        Returns
        -------
        T

        Raises
        ------
        EmptyStructureError
            If the deque is empty.
        """
        with self._lock:
            if self._list.is_empty():
                raise EmptyStructureError("peek at an empty deque")
            if side == "left":
                return self._list.get(0)
            sz = self._list.size()
            return self._list.get(sz - 1)

    # ------------------------------------------------------------------ #
    #  Bulk operations                                                     #
    # ------------------------------------------------------------------ #

    def rotate(self, steps: int = 1) -> None:
        with self._lock:
            sz = self._list.size()
            if sz <= 1:
                return
            steps = steps % sz
            if steps == 0:
                return
            for _ in range(steps):
                val: T = cast(T, self._list.delete(position=sz - 1))
                self._list.insert(val, position=0)

    def reverse(self) -> None:
        with self._lock:
            self._list.reverse()

    # ------------------------------------------------------------------ #
    #  Query operations                                                    #
    # ------------------------------------------------------------------ #

    def is_empty(self) -> bool:
        return self._list.is_empty()

    def size(self) -> int:
        return self._list.size()

    def clear(self) -> None:
        self._list.clear()

    def copy(self) -> LinkedDeque[T]:
        with self._lock:
            new = LinkedDeque[T]()
            new._list = cast(DoublyLinkedList[T], self._list.copy())
            return new

    def to_list(self) -> list[T]:
        return self._list.to_list()

    # ------------------------------------------------------------------ #
    #  Dunder methods                                                      #
    # ------------------------------------------------------------------ #

    def __iter__(self) -> Iterator[T]:
        with self._lock:
            snapshot = self.to_list()
        return iter(snapshot)

    def __len__(self) -> int:
        return self.size()

    def __bool__(self) -> bool:
        return not self.is_empty()

    def __repr__(self) -> str:
        return f"LinkedDeque({self.to_list()!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LinkedDeque):
            return NotImplemented
        return self.to_list() == other.to_list()
