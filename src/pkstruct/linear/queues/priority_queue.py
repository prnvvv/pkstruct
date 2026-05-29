"""
pkstruct.linear.queues.priority_queue
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A priority queue backed by a binary heap (``heapq``).

``PriorityQueue`` wraps the standard library ``heapq`` module, adding thread
safety and the full pkstruct queue interface.  The minimum element is always
at the front.  Complexity is O(log n) for ``enqueue`` and ``dequeue``.
"""

from __future__ import annotations

import heapq
from collections.abc import Iterator
from typing import TypeVar

from pkstruct.linear.exceptions import EmptyStructureError
from pkstruct.linear.queues.queue import Queue
from pkstruct.shared.threading import StructureLock

T = TypeVar("T")


class PriorityQueue(Queue[T]):
    """
    A thread-safe min-heap priority queue.

    The element with the smallest priority (or smallest value when no explicit
    priority is given) is always at the front.  If two elements share the same
    priority, the one enqueued first is served first (stable via insertion
    counter).

    Parameters
    ----------
    items:
        Optional iterable of initial values.  All elements are heapified at
        construction (O(n)).

    Examples
    --------
    >>> pq = PriorityQueue([3, 1, 2])
    >>> pq.dequeue()
    1
    >>> pq.enqueue(0)
    >>> pq.dequeue()
    0
    """

    __slots__ = ("_heap", "_lock", "_counter")

    def __init__(self, items: list[T] | None = None) -> None:
        self._heap: list[tuple[object, int, T]] = []
        self._lock: StructureLock = StructureLock()
        self._counter: int = 0
        if items is not None:
            for item in items:
                self.enqueue(item)

    # ------------------------------------------------------------------ #
    #  Required operations                                                 #
    # ------------------------------------------------------------------ #

    def enqueue(self, value: T, priority: object = None) -> None:
        """
        Add *value* to the priority queue.

        Parameters
        ----------
        value:
            The element to enqueue.
        priority:
            Optional sort key.  If ``None``, *value* itself is used for
            ordering (requires comparable elements).
        """
        with self._lock:
            key: object = priority if priority is not None else value
            heapq.heappush(self._heap, (key, self._counter, value))
            self._counter += 1

    def dequeue(self) -> T:
        """
        Remove and return the element with the smallest priority.

        Returns
        -------
        T

        Raises
        ------
        EmptyStructureError
            If the priority queue is empty.
        """
        with self._lock:
            if not self._heap:
                raise EmptyStructureError("dequeue from an empty priority queue")
            _, _, value = heapq.heappop(self._heap)
            return value

    def front(self) -> T:
        """
        Return the smallest-priority element without removing it.

        Returns
        -------
        T

        Raises
        ------
        EmptyStructureError
            If the priority queue is empty.
        """
        with self._lock:
            if not self._heap:
                raise EmptyStructureError("front of an empty priority queue")
            return self._heap[0][2]

    def rear(self) -> T:
        """
        Return the largest-priority element without removing it.

        This operation is O(n) because heap order does not directly expose
        the maximum element.

        Returns
        -------
        T

        Raises
        ------
        EmptyStructureError
            If the priority queue is empty.
        """
        with self._lock:
            if not self._heap:
                raise EmptyStructureError("rear of an empty priority queue")
            return max(self._heap, key=lambda x: x[0])[2]  # type: ignore[arg-type, return-value]

    # ------------------------------------------------------------------ #
    #  Query operations                                                    #
    # ------------------------------------------------------------------ #

    def is_empty(self) -> bool:
        """Return ``True`` if the priority queue contains no elements."""
        return len(self._heap) == 0

    def size(self) -> int:
        """Return the number of elements in the priority queue."""
        return len(self._heap)

    def clear(self) -> None:
        """Remove all elements from the priority queue."""
        with self._lock:
            self._heap.clear()
            self._counter = 0

    def copy(self) -> PriorityQueue[T]:
        """
        Return a shallow copy of this priority queue.

        Returns
        -------
        PriorityQueue[T]
        """
        with self._lock:
            new: PriorityQueue[T] = PriorityQueue()
            new._heap = list(self._heap)
            new._counter = self._counter
            return new

    def to_list(self) -> list[T]:
        """
        Return a list of all elements in priority order (smallest first).

        Returns
        -------
        list[T]
        """
        with self._lock:
            return [v for _, _, v in sorted(self._heap)]

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
        return f"PriorityQueue({self.to_list()!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PriorityQueue):
            return NotImplemented
        return self.to_list() == other.to_list()
