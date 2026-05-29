"""
pkstruct.linear.stacks.stack
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Abstract base class for all stack implementations.

Provides a formal interface contract. Every concrete stack in ``pkstruct``
derives from this class and implements all abstract methods.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Generic, TypeVar

T = TypeVar("T")


class Stack(ABC, Generic[T]):
    """
    Abstract base class for LIFO (last-in, first-out) stack structures.

    Subclasses must implement all abstract methods.  The interface is designed
    to be consistent across both array-backed and linked-list-backed stacks.

    Parameters
    ----------
    No parameters required at the abstract level.
    """

    __slots__ = ()

    # ------------------------------------------------------------------ #
    #  Required operations                                                 #
    # ------------------------------------------------------------------ #

    @abstractmethod
    def push(self, value: T) -> None:
        """
        Push *value* onto the top of the stack.

        Parameters
        ----------
        value:
            The element to push.
        """
        ...

    @abstractmethod
    def pop(self) -> T:
        """
        Remove and return the top element.

        Returns
        -------
        T
            The element at the top of the stack.

        Raises
        ------
        EmptyStructureError
            If the stack is empty.
        """
        ...

    @abstractmethod
    def peek(self) -> T:
        """
        Return the top element without removing it.

        Returns
        -------
        T
            The element at the top of the stack.

        Raises
        ------
        EmptyStructureError
            If the stack is empty.
        """
        ...

    # ------------------------------------------------------------------ #
    #  Query operations                                                    #
    # ------------------------------------------------------------------ #

    @abstractmethod
    def is_empty(self) -> bool:
        """
        Return ``True`` if the stack contains no elements.

        Returns
        -------
        bool
        """
        ...

    @abstractmethod
    def size(self) -> int:
        """
        Return the number of elements in the stack.

        Returns
        -------
        int
        """
        ...

    @abstractmethod
    def clear(self) -> None:
        """Remove all elements from the stack."""
        ...

    @abstractmethod
    def copy(self) -> Stack[T]:
        """
        Return a shallow copy of this stack.

        Returns
        -------
        Stack[T]
        """
        ...

    @abstractmethod
    def to_list(self) -> list[T]:
        """
        Return a list of all elements, from top to bottom.

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
