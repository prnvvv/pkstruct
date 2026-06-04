"""
pkstruct.linear.stacks.array_stack
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A LIFO stack backed by a dynamic Python ``list``.

``ArrayStack`` offers compact memory (no per-node overhead) and excellent
cache locality.  All operations are O(1) amortised.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import TypeVar

from pkstruct._help import HelpMixin
from pkstruct._linear_shortcuts import LinearShortcutsMixin
from pkstruct._str import StrMixin
from pkstruct.linear.exceptions import EmptyStructureError
from pkstruct.linear.stacks.stack import Stack
from pkstruct.shared.threading import StructureLock

T = TypeVar("T")


class ArrayStack(Stack[T], StrMixin, LinearShortcutsMixin, HelpMixin):
    """
    A thread-safe stack backed by a Python ``list``.

    The underlying list grows and shrinks dynamically.  Push and pop at the
    end of the list are O(1) amortised.

    Parameters
    ----------
    items:
        Optional iterable of initial values (bottom-to-top order).
        If omitted the stack starts empty.

    Examples
    --------
    >>> s = ArrayStack([1, 2, 3])
    >>> s.push(4)
    >>> s.pop()
    4
    >>> s.peek()
    3
    """

    __slots__ = ("_data", "_lock", "_min_data")

    def __init__(self, items: list[T] | None = None) -> None:
        self._data: list[T] = list(items) if items is not None else []
        self._lock: StructureLock = StructureLock()
        self._min_data: list[T] = []
        for item in self._data:
            if not self._min_data or item <= self._min_data[-1]:
                self._min_data.append(item)

    @classmethod
    def from_list(cls, items: list[T]) -> ArrayStack[T]:
        """Create an ArrayStack from a list.

        Args:
            items: Initial elements (bottom-to-top order).

        Returns:
            A new ArrayStack populated with *items*.
        """
        return cls(items)

    # ------------------------------------------------------------------ #
    #  Required operations                                                 #
    # ------------------------------------------------------------------ #

    def push(self, value: T) -> None:
        """
        Push *value* onto the top of the stack.

        Parameters
        ----------
        value:
            The element to push.
        """
        with self._lock:
            self._data.append(value)
            if not self._min_data or value <= self._min_data[-1]:
                self._min_data.append(value)

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
            if not self._data:
                raise EmptyStructureError("pop from an empty stack")
            value = self._data.pop()
            if self._min_data and value == self._min_data[-1]:
                self._min_data.pop()
            return value

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
            if not self._data:
                raise EmptyStructureError("peek at an empty stack")
            return self._data[-1]

    # ------------------------------------------------------------------ #
    #  Query operations                                                    #
    # ------------------------------------------------------------------ #

    def is_empty(self) -> bool:
        """Return ``True`` if the stack contains no elements."""
        return len(self._data) == 0

    def size(self) -> int:
        """Return the number of elements in the stack."""
        return len(self._data)

    def clear(self) -> None:
        """Remove all elements from the stack."""
        with self._lock:
            self._data.clear()

    def copy(self) -> ArrayStack[T]:
        """
        Return a shallow copy of this stack.

        Returns
        -------
        ArrayStack[T]
        """
        with self._lock:
            new = ArrayStack[T]()
            new._data = self._data.copy()
            new._min_data = list(self._min_data)
            return new

    def validate(self) -> bool:
        """Verify internal consistency. Always True for array-backed stacks.

        Returns:
            True if the stack is in a valid state.
        """
        return True

    def debug(self) -> dict[str, object]:
        """Return internal state for debugging purposes."""
        with self._lock:
            return {
                "type": "ArrayStack",
                "size": len(self._data),
                "data": list(self._data),
            }

    def to_list(self) -> list[T]:
        """
        Return a list of all elements, from top to bottom.

        Returns
        -------
        list[T]
        """
        with self._lock:
            return list(reversed(self._data))

    # ------------------------------------------------------------------ #
    #  LeetCode-style methods                                              #
    # ------------------------------------------------------------------ #

    def min_stack(self) -> T | None:
        with self._lock:
            return self._min_data[-1] if self._min_data else None

    @classmethod
    def is_valid_parentheses(cls, s: str) -> bool:
        mapping = {')': '(', '}': '{', ']': '['}
        stack: list[str] = []
        for char in s:
            if char in mapping:
                top = stack.pop() if stack else '#'
                if top != mapping[char]:
                    return False
            else:
                stack.append(char)
        return not stack

    @classmethod
    def evaluate_rpn(cls, tokens: list[str]) -> int:
        stack: list[int] = []
        for token in tokens:
            if token in {'+', '-', '*', '/'}:
                b = stack.pop()
                a = stack.pop()
                if token == '+':
                    stack.append(a + b)
                elif token == '-':
                    stack.append(a - b)
                elif token == '*':
                    stack.append(a * b)
                else:
                    stack.append(int(a / b))
            else:
                stack.append(int(token))
        return stack[0]

    @classmethod
    def daily_temperatures(cls, temperatures: list[int]) -> list[int]:
        n = len(temperatures)
        result = [0] * n
        stack: list[int] = []
        for i, t in enumerate(temperatures):
            while stack and t > temperatures[stack[-1]]:
                idx = stack.pop()
                result[idx] = i - idx
            stack.append(i)
        return result

    # ------------------------------------------------------------------ #
    #  Dunder methods                                                      #
    # ------------------------------------------------------------------ #

    def __contains__(self, item: object) -> bool:
        """Return True if item is in the stack."""
        with self._lock:
            return item in self._data

    def __iter__(self) -> Iterator[T]:
        with self._lock:
            snapshot = self.to_list()
        return iter(snapshot)

    def __len__(self) -> int:
        return self.size()

    def __bool__(self) -> bool:
        return not self.is_empty()

    def __repr__(self) -> str:
        return f"ArrayStack({self.to_list()!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ArrayStack):
            return NotImplemented
        return self.to_list() == other.to_list()
