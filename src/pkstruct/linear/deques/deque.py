"""
pkstruct.linear.deques.deque
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Abstract base class for all double-ended queue implementations.

Provides a formal interface contract. Every concrete deque in ``pkstruct``
derives from this class and implements all abstract methods.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Generic, Literal, TypeVar

T = TypeVar("T")

_Side = Literal["left", "right"]


class Deque(ABC, Generic[T]):
    """
    Abstract base class for double-ended queue (deque) structures.

    Subclasses must implement all abstract methods.  The interface supports
    O(1) append and pop at both ends, plus rotation and reversal.

    Parameters
    ----------
    No parameters required at the abstract level.
    """

    __slots__ = ()

    # ------------------------------------------------------------------ #
    #  Required operations                                                 #
    # ------------------------------------------------------------------ #

    @abstractmethod
    def append(self, value: T, side: _Side = "right") -> None:
        """
        Add *value* to one end of the deque.

        Parameters
        ----------
        value:
            The element to add.
        side:
            ``"left"`` to prepend (front), ``"right"`` to append (rear).
        """
        ...

    @abstractmethod
    def pop(self, side: _Side = "right") -> T:
        """
        Remove and return an element from one end.

        Parameters
        ----------
        side:
            ``"left"`` to remove from the front, ``"right"`` to remove from
            the rear.

        Returns
        -------
        T

        Raises
        ------
        EmptyStructureError
            If the deque is empty.
        """
        ...

    @abstractmethod
    def peek(self, side: _Side = "left") -> T:
        """
        Return an element from one end without removing it.

        Parameters
        ----------
        side:
            ``"left"`` to inspect the front, ``"right"`` to inspect the rear.

        Returns
        -------
        T

        Raises
        ------
        EmptyStructureError
            If the deque is empty.
        """
        ...

    # ------------------------------------------------------------------ #
    #  Bulk operations                                                     #
    # ------------------------------------------------------------------ #

    @abstractmethod
    def rotate(self, steps: int = 1) -> None:
        """
        Rotate the deque *steps* positions to the right.

        Negative *steps* rotates to the left.

        Parameters
        ----------
        steps:
            Number of positions to rotate (default 1).
        """
        ...

    @abstractmethod
    def reverse(self) -> None:
        """Reverse the order of all elements in the deque."""
        ...

    # ------------------------------------------------------------------ #
    #  Query operations                                                    #
    # ------------------------------------------------------------------ #

    @abstractmethod
    def is_empty(self) -> bool:
        """
        Return ``True`` if the deque contains no elements.

        Returns
        -------
        bool
        """
        ...

    @abstractmethod
    def size(self) -> int:
        """
        Return the number of elements in the deque.

        Returns
        -------
        int
        """
        ...

    @abstractmethod
    def clear(self) -> None:
        """Remove all elements from the deque."""
        ...

    @abstractmethod
    def copy(self) -> Deque[T]:
        """
        Return a shallow copy of this deque.

        Returns
        -------
        Deque[T]
        """
        ...

    @abstractmethod
    def to_list(self) -> list[T]:
        """
        Return a list of all elements, from left to right.

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
