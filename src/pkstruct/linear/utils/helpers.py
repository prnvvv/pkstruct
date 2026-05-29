"""Helper utilities for pkstruct linked lists."""
from __future__ import annotations

from typing import Any


def _get_list_types() -> tuple[type, type, type]:
    from pkstruct.linear.linked_lists.circular_linked_list import CircularLinkedList
    from pkstruct.linear.linked_lists.doubly_linked_list import DoublyLinkedList
    from pkstruct.linear.linked_lists.singly_linked_list import SinglyLinkedList
    return SinglyLinkedList, DoublyLinkedList, CircularLinkedList


def _to_values(lst: Any) -> list[Any]:
    """Extract all values from a linked list into a Python list."""
    SinglyLinkedList, DoublyLinkedList, CircularLinkedList = _get_list_types()

    if isinstance(lst, CircularLinkedList):
        result = []
        current = lst.head
        size = lst.size
        steps = 0
        while current is not None and steps < size:
            result.append(current.value)  # FIXED: .data → .value
            current = current.next
            steps += 1
        return result

    result = []
    current = lst.head
    visited: set[int] = set()
    while current is not None:
        if id(current) in visited:
            break
        visited.add(id(current))
        result.append(current.value)  # FIXED: .data → .value
        current = current.next
    return result


def merge_sorted_lists(*lists: Any) -> Any:
    """Merge pre-sorted linked lists into a new sorted SinglyLinkedList.

    All input lists must already be sorted in ascending order.

    Args:
        *lists: Any number of pkstruct linked list instances, each sorted.

    Returns:
        A new SinglyLinkedList containing all elements from *lists* in
        sorted (ascending) order.

    Raises:
        ValueError: If no lists are provided.
    """
    if not lists:
        raise ValueError("merge_sorted_lists requires at least one list argument.")

    SinglyLinkedList, _, _ = _get_list_types()

    # Collect all values, sort, build new list
    all_values: list[Any] = []
    for lst in lists:
        all_values.extend(_to_values(lst))

    all_values.sort()
    return SinglyLinkedList.from_list(all_values)


def detect_intersection(list_a: Any, list_b: Any) -> Any | None:
    """Detect whether two linked lists share a common node by identity.

    Uses a hash-set approach on node ids to find the first node that
    appears in both *list_a* and *list_b*.

    Args:
        list_a: First linked list instance.
        list_b: Second linked list instance.

    Returns:
        The data value of the first intersecting node, or ``None`` if the
        lists do not intersect.
    """
    SinglyLinkedList, DoublyLinkedList, CircularLinkedList = _get_list_types()

    def node_ids(lst: Any) -> dict[int, Any]:
        """Return mapping of node id → data for *lst*."""
        mapping: dict[int, Any] = {}
        if isinstance(lst, CircularLinkedList):
            current = lst.head
            size = lst.size
            steps = 0
            while current is not None and steps < size:
                mapping[id(current)] = current.value  # FIXED: .data → .value
                current = current.next
                steps += 1
        else:
            current = lst.head
            visited: set[int] = set()
            while current is not None:
                nid = id(current)
                if nid in visited:
                    break
                visited.add(nid)
                mapping[nid] = current.value  # FIXED: .data → .value
                current = current.next
        return mapping

    ids_a = node_ids(list_a)
    ids_b = node_ids(list_b)

    for nid in ids_b:
        if nid in ids_a:
            return ids_b[nid]

    return None


def list_equal(list_a: Any, list_b: Any) -> bool:
    """Return True if *list_a* and *list_b* contain the same values in order.

    Args:
        list_a: First linked list instance.
        list_b: Second linked list instance.

    Returns:
        ``True`` if the value sequences are identical, ``False`` otherwise.
    """
    return _to_values(list_a) == _to_values(list_b)


def to_array(list_instance: Any) -> list[Any]:
    """Alias for converting a linked list to a Python list via ``to_list()``.

    Args:
        list_instance: Any pkstruct linked list instance.

    Returns:
        A plain Python list of node values in forward order.
    """
    if hasattr(list_instance, "to_list"):
        return list_instance.to_list()
    return _to_values(list_instance)