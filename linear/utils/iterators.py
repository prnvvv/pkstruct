"""Iterator utilities for pkstruct linked lists."""
from __future__ import annotations
from typing import Any, Generator, Iterator, Optional


def _get_list_types() -> tuple[type, type, type]:
    from pkstruct.linear.linked_lists.singly_linked_list import SinglyLinkedList
    from pkstruct.linear.linked_lists.doubly_linked_list import DoublyLinkedList
    from pkstruct.linear.linked_lists.circular_linked_list import CircularLinkedList
    return SinglyLinkedList, DoublyLinkedList, CircularLinkedList


class ForwardIterator:
    """Iterate over all node values in forward order.

    Works with SinglyLinkedList, DoublyLinkedList, and CircularLinkedList.

    Args:
        list_instance: Any supported linked list instance.

    Yields:
        Node data values from head to tail.
    """

    def __init__(self, list_instance: Any) -> None:
        self._list = list_instance

    def __iter__(self) -> Iterator[Any]:
        SinglyLinkedList, DoublyLinkedList, CircularLinkedList = _get_list_types()
        lst = self._list

        if isinstance(lst, CircularLinkedList):
            size = lst.size
            current = lst.head
            steps = 0
            while current is not None and steps < size:
                yield current.value
                current = current.next
                steps += 1
        elif isinstance(lst, (SinglyLinkedList, DoublyLinkedList)):
            current = lst.head
            visited: set[int] = set()
            while current is not None:
                if id(current) in visited:
                    break
                visited.add(id(current))
                yield current.value
                current = current.next
        else:
            raise TypeError(
                f"ForwardIterator does not support {type(lst).__name__}. "
                "Use SinglyLinkedList, DoublyLinkedList, or CircularLinkedList."
            )


class BackwardIterator:
    """Iterate over all node values in reverse order.

    Only supported for DoublyLinkedList (which has .prev pointers).

    Args:
        list_instance: A DoublyLinkedList instance.

    Yields:
        Node data values from tail to head.

    Raises:
        TypeError: If *list_instance* is not a DoublyLinkedList.
    """

    def __init__(self, list_instance: Any) -> None:
        self._list = list_instance

    def __iter__(self) -> Iterator[Any]:
        SinglyLinkedList, DoublyLinkedList, CircularLinkedList = _get_list_types()
        lst = self._list

        if isinstance(lst, DoublyLinkedList):
            current = lst.tail
            visited: set[int] = set()
            while current is not None:
                if id(current) in visited:
                    break
                visited.add(id(current))
                yield current.value
                current = current.prev
        elif isinstance(lst, (SinglyLinkedList, CircularLinkedList)):
            raise TypeError(
                f"BackwardIterator is not supported for {type(lst).__name__}. "
                "Only DoublyLinkedList supports backward iteration via .prev pointers."
            )
        else:
            raise TypeError(
                f"BackwardIterator does not support {type(lst).__name__}."
            )


class CircularIterator:
    """Infinite (or bounded) circular iterator over a CircularLinkedList.

    Args:
        list_instance: A CircularLinkedList instance.
        max_cycles: Maximum full cycles to iterate before stopping.
            ``None`` means infinite (caller is responsible for breaking).

    Yields:
        Node data values, wrapping around indefinitely (or until *max_cycles*
        full circuits have been completed).

    Raises:
        TypeError: If *list_instance* is not a CircularLinkedList.
    """

    def __init__(self, list_instance: Any, max_cycles: Optional[int] = None, max_steps: Optional[int] = None) -> None:
        self._list = list_instance
        self._max_cycles = max_cycles
        self._max_steps = max_steps

    def __iter__(self) -> Iterator[Any]:
        _, _, CircularLinkedList = _get_list_types()
        lst = self._list

        if not isinstance(lst, CircularLinkedList):
            raise TypeError(
                f"CircularIterator requires a CircularLinkedList, got {type(lst).__name__}."
            )

        if lst.head is None or lst.size == 0:
            return

        size = lst.size
        if self._max_steps is not None:
            limit = self._max_steps
        elif self._max_cycles is not None:
            limit = self._max_cycles * size
        else:
            limit = None

        current = lst.head
        steps = 0
        while limit is None or steps < limit:
            yield current.value
            current = current.next
            steps += 1
            if current is None:
                break