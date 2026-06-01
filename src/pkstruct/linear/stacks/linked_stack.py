"""
pkstruct.linear.stacks.linked_stack
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A LIFO stack backed by a ``SinglyLinkedList``.

``LinkedStack`` composes the existing production-grade linked list rather than
reimplementing node management.  Push is O(1) amortised via head insertion;
pop and peek are O(1).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import TypeVar, cast

from pkstruct._help import HelpMixin
from pkstruct._linear_shortcuts import LinearShortcutsMixin
from pkstruct._str import StrMixin
from pkstruct.linear.exceptions import EmptyStructureError
from pkstruct.linear.linked_lists.singly_linked_list import SinglyLinkedList
from pkstruct.linear.stacks.stack import Stack
from pkstruct.shared.threading import StructureLock

T = TypeVar("T")


class LinkedStack(Stack[T], StrMixin, LinearShortcutsMixin, HelpMixin):
    """
    A thread-safe stack implemented on top of ``SinglyLinkedList``.

    The internal linked list stores elements with the top of the stack at
    head position, so ``push``, ``pop``, and ``peek`` all operate at index 0.

    Parameters
    ----------
    items:
        Optional iterable of initial values (bottom-to-top order).
        If omitted the stack starts empty.

    Examples
    --------
    >>> s = LinkedStack([1, 2, 3])
    >>> s.push(4)
    >>> s.pop()
    4
    >>> s.peek()
    3
    """

    __slots__ = ("_list", "_lock")

    def __init__(self, items: list[T] | None = None) -> None:
        self._list: SinglyLinkedList[T] = SinglyLinkedList()
        self._lock: StructureLock = StructureLock()
        if items is not None:
            for item in items:
                self._list.insert(item, position=0)

    @classmethod
    def from_list(cls, items: list[T]) -> LinkedStack[T]:
        """Create a LinkedStack from a list.

        Args:
            items: Initial elements (bottom-to-top order).

        Returns:
            A new LinkedStack populated with *items*.
        """
        return cls(items)

    # ------------------------------------------------------------------ #
    #  Required operations                                                 #
    # ------------------------------------------------------------------ #

    def push(self, value: T) -> None:
        """
        Push *value* onto the top of the stack (head of the list).

        Parameters
        ----------
        value:
            The element to push.
        """
        with self._lock:
            self._list.insert(value, position=0)

    def pop(self) -> T:
        """
        Remove and return the top element.

        Returns
        -------
        T

        Raises
        ------
        EmptyStructureError
            If the stack is empty.
        """
        with self._lock:
            if self._list.is_empty():
                raise EmptyStructureError("pop from an empty stack")
            return cast(T, self._list.delete(position=0))

    def peek(self) -> T:
        """
        Return the top element without removing it.

        Returns
        -------
        T

        Raises
        ------
        EmptyStructureError
            If the stack is empty.
        """
        with self._lock:
            if self._list.is_empty():
                raise EmptyStructureError("peek at an empty stack")
            return self._list.get(0)

    # ------------------------------------------------------------------ #
    #  Query operations                                                    #
    # ------------------------------------------------------------------ #

    def is_empty(self) -> bool:
        """Return ``True`` if the stack contains no elements."""
        return self._list.is_empty()

    def size(self) -> int:
        """Return the number of elements in the stack."""
        return self._list.size()

    def clear(self) -> None:
        """Remove all elements from the stack."""
        self._list.clear()

    def copy(self) -> LinkedStack[T]:
        """
        Return a shallow copy of this stack.

        Returns
        -------
        LinkedStack[T]
        """
        with self._lock:
            new = LinkedStack[T]()
            new._list = cast(SinglyLinkedList[T], self._list.copy())
            return new

    def validate(self) -> bool:
        """Verify internal consistency. Delegates to the underlying linked list.

        Returns:
            True if the stack is in a valid state.
        """
        return self._list.validate()

    def debug(self) -> dict[str, object]:
        """Return internal state for debugging purposes."""
        with self._lock:
            return {
                "type": "LinkedStack",
                "size": self._list.size(),
                "values": self.to_list(),
            }

    def to_list(self) -> list[T]:
        """
        Return a list of all elements, from top to bottom.

        Returns
        -------
        list[T]
        """
        return self._list.to_list()

    # ------------------------------------------------------------------ #
    #  Dunder methods                                                      #
    # ------------------------------------------------------------------ #

    def __contains__(self, item: object) -> bool:
        """Return True if item is in the stack."""
        with self._lock:
            return item in self._list

    def __iter__(self) -> Iterator[T]:
        with self._lock:
            snapshot = self.to_list()
        return iter(snapshot)

    def __len__(self) -> int:
        return self.size()

    def __bool__(self) -> bool:
        return not self.is_empty()

    def __repr__(self) -> str:
        return f"LinkedStack({self.to_list()!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LinkedStack):
            return NotImplemented
        return self.to_list() == other.to_list()
