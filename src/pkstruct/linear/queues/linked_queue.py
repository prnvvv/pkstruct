"""
pkstruct.linear.queues.linked_queue
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A FIFO queue backed by a ``SinglyLinkedList``.

``LinkedQueue`` composes the existing production-grade linked list.  Enqueue
appends at the tail; dequeue removes from the head — both O(1).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import TypeVar, cast

from pkstruct._help import HelpMixin
from pkstruct._linear_shortcuts import LinearShortcutsMixin
from pkstruct._str import StrMixin
from pkstruct.linear.exceptions import EmptyStructureError
from pkstruct.linear.linked_lists.singly_linked_list import SinglyLinkedList
from pkstruct.linear.queues.queue import Queue
from pkstruct.shared.threading import StructureLock

T = TypeVar("T")


class LinkedQueue(Queue[T], StrMixin, LinearShortcutsMixin, HelpMixin):
    """
    A thread-safe FIFO queue implemented on top of ``SinglyLinkedList``.

    The internal list stores elements in order: front at the head, rear at
    the tail.  ``enqueue`` appends (tail), ``dequeue`` removes from the head
    — both O(1) amortised.

    Parameters
    ----------
    items:
        Optional iterable of initial values (front-to-rear order).
        If omitted the queue starts empty.

    Examples
    --------
    >>> q = LinkedQueue([1, 2, 3])
    >>> q.enqueue(4)
    >>> q.dequeue()
    1
    >>> q.front()
    2
    """

    __slots__ = ("_list", "_lock")

    def __init__(self, items: list[T] | None = None) -> None:
        self._list: SinglyLinkedList[T] = SinglyLinkedList()
        self._lock: StructureLock = StructureLock()
        if items is not None:
            for item in items:
                self._list.insert(item)

    @classmethod
    def from_list(cls, items: list[T]) -> LinkedQueue[T]:
        """Create a LinkedQueue from a list.

        Args:
            items: Initial elements (front-to-rear order).

        Returns:
            A new LinkedQueue populated with *items*.
        """
        return cls(items)

    # ------------------------------------------------------------------ #
    #  Required operations                                                 #
    # ------------------------------------------------------------------ #

    def enqueue(self, value: T) -> None:
        """
        Add *value* to the rear of the queue (tail of the list).

        Parameters
        ----------
        value:
            The element to enqueue.
        """
        with self._lock:
            self._list.insert(value)

    def dequeue(self) -> T:
        """
        Remove and return the front element (head of the list).

        Returns
        -------
        T

        Raises
        ------
        EmptyStructureError
            If the queue is empty.
        """
        with self._lock:
            if self._list.is_empty():
                raise EmptyStructureError("dequeue from an empty queue")
            return cast(T, self._list.delete(position=0))

    def front(self) -> T:
        """
        Return the front element without removing it.

        Returns
        -------
        T

        Raises
        ------
        EmptyStructureError
            If the queue is empty.
        """
        with self._lock:
            if self._list.is_empty():
                raise EmptyStructureError("front of an empty queue")
            return self._list.get(0)

    def rear(self) -> T:
        """
        Return the rear element without removing it.

        Returns
        -------
        T

        Raises
        ------
        EmptyStructureError
            If the queue is empty.
        """
        with self._lock:
            if self._list.is_empty():
                raise EmptyStructureError("rear of an empty queue")
            return self._list.get(self._list.size() - 1)

    # ------------------------------------------------------------------ #
    #  Query operations                                                    #
    # ------------------------------------------------------------------ #

    def is_empty(self) -> bool:
        """Return ``True`` if the queue contains no elements."""
        return self._list.is_empty()

    def size(self) -> int:
        """Return the number of elements in the queue."""
        return self._list.size()

    def clear(self) -> None:
        """Remove all elements from the queue."""
        self._list.clear()

    def copy(self) -> LinkedQueue[T]:
        """
        Return a shallow copy of this queue.

        Returns
        -------
        LinkedQueue[T]
        """
        with self._lock:
            new = LinkedQueue[T]()
            new._list = cast(SinglyLinkedList[T], self._list.copy())
            return new

    def validate(self) -> bool:
        """Verify internal consistency. Delegates to the underlying linked list.

        Returns:
            True if the queue is in a valid state.
        """
        return self._list.validate()

    def debug(self) -> dict[str, object]:
        """Return internal state for debugging purposes."""
        with self._lock:
            return {
                "type": "LinkedQueue",
                "size": self._list.size(),
                "values": self.to_list(),
            }

    def to_list(self) -> list[T]:
        """
        Return a list of all elements, from front to rear.

        Returns
        -------
        list[T]
        """
        return self._list.to_list()

    # ------------------------------------------------------------------ #
    #  Dunder methods                                                      #
    # ------------------------------------------------------------------ #

    def __contains__(self, item: object) -> bool:
        """Return True if item is in the queue."""
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
        return f"LinkedQueue({self.to_list()!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LinkedQueue):
            return NotImplemented
        return self.to_list() == other.to_list()
