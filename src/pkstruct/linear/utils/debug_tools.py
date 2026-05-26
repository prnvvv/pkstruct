"""Debug and integrity utilities for pkstruct linked lists."""
from __future__ import annotations
import sys
from typing import Any


def _get_list_types() -> tuple[type, type, type]:
    from pkstruct.linear.linked_lists.singly_linked_list import SinglyLinkedList
    from pkstruct.linear.linked_lists.doubly_linked_list import DoublyLinkedList
    from pkstruct.linear.linked_lists.circular_linked_list import CircularLinkedList
    return SinglyLinkedList, DoublyLinkedList, CircularLinkedList


# Base per-node overhead in bytes (measured experimentally on CPython 3.10)
_SINGLY_NODE_BYTES = 56
_DOUBLY_NODE_BYTES = 72
_CIRCULAR_NODE_BYTES = 56


def memory_usage(list_instance: Any) -> int:
    """Estimate memory used by *list_instance* in bytes.

    Uses fixed per-node overhead constants plus ``sys.getsizeof`` for the
    value stored in each node.

    Node overhead constants:
        - SinglyNode / CircularNode: 56 bytes
        - DoublyNode: 72 bytes

    Args:
        list_instance: Any pkstruct linked list instance.

    Returns:
        Estimated total bytes used by the list structure.

    Raises:
        TypeError: If *list_instance* is not a recognised list type.
    """
    SinglyLinkedList, DoublyLinkedList, CircularLinkedList = _get_list_types()

    if isinstance(list_instance, CircularLinkedList):
        per_node = _CIRCULAR_NODE_BYTES
        current = list_instance.head
        size = list_instance.size()
        steps = 0
        total = 0
        while current is not None and steps < size:
            try:
                value_bytes = sys.getsizeof(current.value)
            except Exception:
                value_bytes = 0
            total += per_node + value_bytes
            current = current.next
            steps += 1
        return total

    if isinstance(list_instance, DoublyLinkedList):
        per_node = _DOUBLY_NODE_BYTES
    elif isinstance(list_instance, SinglyLinkedList):
        per_node = _SINGLY_NODE_BYTES
    else:
        raise TypeError(
            f"memory_usage does not support {type(list_instance).__name__}."
        )

    total = 0
    current = list_instance.head
    visited: set[int] = set()
    while current is not None:
        if id(current) in visited:
            break
        visited.add(id(current))
        try:
            value_bytes = sys.getsizeof(current.value)
        except Exception:
            value_bytes = 0
        total += per_node + value_bytes
        current = current.next

    return total


def validate_integrity(list_instance: Any) -> dict[str, Any]:
    """Validate the structural integrity of *list_instance*.

    Checks performed:
        - **SinglyLinkedList**: no cycles (via Floyd's algorithm), size matches.
        - **DoublyLinkedList**: all ``prev``/``next`` pointers consistent,
          no cycles, size matches.
        - **CircularLinkedList**: ``tail.next is head``, no broken links,
          size matches.

    Args:
        list_instance: Any pkstruct linked list instance.

    Returns:
        Dictionary::

            {
                "valid": bool,
                "errors": list[str],
                "size_matches": bool,
            }

    Raises:
        TypeError: If *list_instance* is not a recognised list type.
    """
    SinglyLinkedList, DoublyLinkedList, CircularLinkedList = _get_list_types()

    errors: list[str] = []
    size_matches = True

    if isinstance(list_instance, CircularLinkedList):
        errors, size_matches = _validate_circular(list_instance)

    elif isinstance(list_instance, DoublyLinkedList):
        errors, size_matches = _validate_doubly(list_instance)

    elif isinstance(list_instance, SinglyLinkedList):
        errors, size_matches = _validate_singly(list_instance)

    else:
        raise TypeError(
            f"validate_integrity does not support {type(list_instance).__name__}."
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "size_matches": size_matches,
    }


def _validate_singly(lst: Any) -> tuple[list[str], bool]:
    errors: list[str] = []

    # Floyd's cycle detection
    slow = lst.head
    fast = lst.head
    has_cycle = False
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            has_cycle = True
            errors.append("Cycle detected in SinglyLinkedList.")
            break

    # Count nodes
    counted = 0
    current = lst.head
    visited: set[int] = set()
    while current is not None:
        if id(current) in visited:
            break
        visited.add(id(current))
        counted += 1
        current = current.next

    size_matches = counted == lst.size()
    if not size_matches:
        errors.append(
            f"Size mismatch: recorded={lst.size()}, counted={counted}."
        )

    return errors, size_matches


def _validate_doubly(lst: Any) -> tuple[list[str], bool]:
    errors: list[str] = []

    # Walk forward, check prev pointers
    prev_node = None
    current = lst.head
    counted = 0
    visited: set[int] = set()

    while current is not None:
        if id(current) in visited:
            errors.append(f"Cycle detected at node with data={current.value!r}.")
            break
        visited.add(id(current))

        if current.prev is not prev_node:
            errors.append(
                f"Broken prev pointer at node data={current.value!r}: "
                f"expected id={id(prev_node)}, got id={id(current.prev)}."
            )

        prev_node = current
        current = current.next
        counted += 1

    # Verify tail pointer
    if lst.tail is not None and lst.tail is not prev_node:
        errors.append(
            f"Tail pointer mismatch: tail.data={lst.tail.value!r}, "
            f"last traversed data={prev_node.value if prev_node else None!r}."
        )

    size_matches = counted == lst.size()
    if not size_matches:
        errors.append(
            f"Size mismatch: recorded={lst.size()}, counted={counted}."
        )

    return errors, size_matches


def _validate_circular(lst: Any) -> tuple[list[str], bool]:
    errors: list[str] = []

    # tail.next must be head
    if lst.head is not None and lst.tail is not None:
        if lst.tail.next is not lst.head:
            errors.append(
                "CircularLinkedList integrity error: tail.next is not head."
            )
    elif lst.head is None and lst.tail is not None:
        errors.append("head is None but tail is not None.")
    elif lst.tail is None and lst.head is not None:
        errors.append("tail is None but head is not None.")

    # Count nodes (bounded by reported size + 1 to detect over-count)
    counted = 0
    limit = lst.size() + 1
    current = lst.head
    while current is not None and counted < limit:
        counted += 1
        current = current.next
        if current is lst.head:
            break

    size_matches = counted == lst.size()
    if not size_matches:
        errors.append(
            f"Size mismatch: recorded={lst.size()}, counted={counted}."
        )

    return errors, size_matches