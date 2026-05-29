"""
pkstruct.linear.queues.queue
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Abstract base class for all queue implementations.

Provides a formal interface contract. Every concrete queue in ``pkstruct``
derives from this class and implements all abstract methods.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Generic, TypeVar

T = TypeVar("T")


class Queue(ABC, Generic[T]):
    """
    Abstract base class for FIFO (first-in, first-out) queue structures.

    Subclasses must implement all abstract methods.  The interface is
    consistent across array-backed, linked-list-backed, and heap-backed
    implementations.

    Parameters
    ----------
    No parameters required at the abstract level.
    """

    __slots__ = ()

    # ------------------------------------------------------------------ #
    #  Required operations                                                 #
    # ------------------------------------------------------------------ #

    @abstractmethod
    def enqueue(self, value: T) -> None:
        """
        Add *value* to the rear of the queue.

        Parameters
        ----------
        value:
            The element to enqueue.
        """
        ...

    @abstractmethod
    def dequeue(self) -> T:
        """
        Remove and return the front element.

        Returns
        -------
        T
            The element at the front of the queue.

        Raises
        ------
        EmptyStructureError
            If the queue is empty.
        """
        ...

    @abstractmethod
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
        ...

    @abstractmethod
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
        ...

    # ------------------------------------------------------------------ #
    #  Query operations                                                    #
    # ------------------------------------------------------------------ #

    @abstractmethod
    def is_empty(self) -> bool:
        """
        Return ``True`` if the queue contains no elements.

        Returns
        -------
        bool
        """
        ...

    @abstractmethod
    def size(self) -> int:
        """
        Return the number of elements in the queue.

        Returns
        -------
        int
        """
        ...

    @abstractmethod
    def clear(self) -> None:
        """Remove all elements from the queue."""
        ...

    @abstractmethod
    def copy(self) -> Queue[T]:
        """
        Return a shallow copy of this queue.

        Returns
        -------
        Queue[T]
        """
        ...

    @abstractmethod
    def to_list(self) -> list[T]:
        """
        Return a list of all elements, from front to rear.

        Returns
        -------
        list[T]
        """
        ...

    # ------------------------------------------------------------------ #
    #  Dunder methods                                                      #
    # ------------------------------------------------------------------ #

    @abstractmethod
    def __iter__(self) -> Iterator[T]:
        ...

    @abstractmethod
    def __len__(self) -> int:
        ...

    @abstractmethod
    def __bool__(self) -> bool:
        ...

    @abstractmethod
    def __repr__(self) -> str:
        ...

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        ...
