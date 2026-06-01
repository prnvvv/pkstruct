"""
pkstruct.linear.queues.circular_queue
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A fixed-capacity FIFO queue backed by a ring buffer (circular array).

``CircularQueue`` uses a pre-allocated Python ``list`` with head and tail
pointers that wrap around.  Enqueue and dequeue are O(1).  Once the buffer
is full, further enqueue operations raise ``QueueFullError``.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import TypeVar

from pkstruct._linear_shortcuts import LinearShortcutsMixin
from pkstruct._str import StrMixin
from pkstruct.linear.exceptions import EmptyStructureError
from pkstruct.linear.queues.queue import Queue
from pkstruct.shared.threading import StructureLock

T = TypeVar("T")


class QueueFullError(IndexError):
    """Raised when attempting to enqueue into a full ``CircularQueue``."""

    def __init__(self, capacity: int) -> None:
        self.capacity: int = capacity
        super().__init__(f"Queue is at capacity ({capacity}).")


class CircularQueue(Queue[T], StrMixin, LinearShortcutsMixin):
    """
    A thread-safe, fixed-capacity FIFO queue using a ring buffer.

    The underlying ``list`` is allocated once at creation.  Head and tail
    indices advance modulo capacity, avoiding the O(n) cost of shifting
    elements.

    Parameters
    ----------
    capacity:
        Maximum number of elements the queue can hold.
    items:
        Optional iterable of initial values (front-to-rear order).
        ``len(items)`` must not exceed *capacity*.

    Examples
    --------
    >>> q = CircularQueue(3, [1, 2])
    >>> q.enqueue(3)
    >>> q.dequeue()
    1
    >>> q.front()
    2
    """

    __slots__ = ("_buffer", "_capacity", "_head", "_tail", "_size", "_lock")

    def __init__(self, capacity: int, items: list[T] | None = None) -> None:
        if not isinstance(capacity, int) or capacity < 1:
            raise ValueError(f"Capacity must be a positive integer, got {capacity!r}.")
        self._capacity: int = capacity
        self._buffer: list[T | None] = [None] * capacity
        self._head: int = 0
        self._tail: int = 0
        self._size: int = 0
        self._lock: StructureLock = StructureLock()
        if items is not None:
            if len(items) > capacity:
                raise ValueError(f"Initial items ({len(items)}) exceeds capacity ({capacity}).")
            for item in items:
                self._enqueue_unsafe(item)

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _enqueue_unsafe(self, value: T) -> None:
        """Enqueue without acquiring the lock or full-check (caller must hold lock)."""
        self._buffer[self._tail] = value
        self._tail = (self._tail + 1) % self._capacity
        self._size += 1

    def _next_index(self, index: int) -> int:
        """Return the next index modulo capacity."""
        return (index + 1) % self._capacity

    def _prev_index(self, index: int) -> int:
        """Return the previous index modulo capacity."""
        return (index - 1 + self._capacity) % self._capacity

    # ------------------------------------------------------------------ #
    #  Required operations                                                 #
    # ------------------------------------------------------------------ #

    def enqueue(self, value: T) -> None:
        """
        Add *value* to the rear of the queue.

        Parameters
        ----------
        value:
            The element to enqueue.

        Raises
        ------
        QueueFullError
            If the queue is at capacity.
        """
        with self._lock:
            if self._size == self._capacity:
                raise QueueFullError(self._capacity)
            self._enqueue_unsafe(value)

    def dequeue(self) -> T:
        """
        Remove and return the front element.

        Returns
        -------
        T

        Raises
        ------
        EmptyStructureError
            If the queue is empty.
        """
        with self._lock:
            if self._size == 0:
                raise EmptyStructureError("dequeue from an empty queue")
            value = self._buffer[self._head]
            self._buffer[self._head] = None
            self._head = self._next_index(self._head)
            self._size -= 1
            return value  # type: ignore[return-value]

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
            if self._size == 0:
                raise EmptyStructureError("front of an empty queue")
            return self._buffer[self._head]  # type: ignore[return-value]

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
            if self._size == 0:
                raise EmptyStructureError("rear of an empty queue")
            return self._buffer[self._prev_index(self._tail)]  # type: ignore[return-value]

    # ------------------------------------------------------------------ #
    #  Query operations                                                    #
    # ------------------------------------------------------------------ #

    def is_empty(self) -> bool:
        """Return ``True`` if the queue contains no elements."""
        return self._size == 0

    def is_full(self) -> bool:
        """Return ``True`` if the queue is at capacity."""
        return self._size == self._capacity

    def size(self) -> int:
        """Return the number of elements in the queue."""
        return self._size

    def capacity(self) -> int:
        """Return the maximum number of elements the queue can hold."""
        return self._capacity

    def clear(self) -> None:
        """Remove all elements from the queue."""
        with self._lock:
            self._buffer = [None] * self._capacity
            self._head = 0
            self._tail = 0
            self._size = 0

    def copy(self) -> CircularQueue[T]:
        """
        Return a shallow copy of this queue.

        Returns
        -------
        CircularQueue[T]
        """
        with self._lock:
            new = CircularQueue[T](self._capacity)
            new._buffer = list(self._buffer)
            new._head = self._head
            new._tail = self._tail
            new._size = self._size
            return new

    def to_list(self) -> list[T]:
        """
        Return a list of all elements, from front to rear.

        Returns
        -------
        list[T]
        """
        with self._lock:
            result: list[T] = []
            idx = self._head
            for _ in range(self._size):
                val = self._buffer[idx]
                if val is not None:
                    result.append(val)
                idx = self._next_index(idx)
            return result

    # ------------------------------------------------------------------ #
    #  Dunder methods                                                      #
    # ------------------------------------------------------------------ #

    def __iter__(self) -> Iterator[T]:
        with self._lock:
            snapshot = self.to_list()
        return iter(snapshot)

    def __len__(self) -> int:
        return self._size

    def __bool__(self) -> bool:
        return self._size > 0

    def __repr__(self) -> str:
        return f"CircularQueue(capacity={self._capacity}, items={self.to_list()!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CircularQueue):
            return NotImplemented
        return self.to_list() == other.to_list()
