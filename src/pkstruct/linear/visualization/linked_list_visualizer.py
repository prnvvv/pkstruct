"""High-level visualizer that dispatches to AsciiVisualizer based on list type."""
from __future__ import annotations

from typing import Any

from .ascii_visualizer import AsciiVisualizer


class LinkedListVisualizer:
    """Provides visualization and debug views for any pkstruct linked list."""

    # Lazy imports to avoid circular dependencies at module load time.
    @staticmethod
    def _list_types() -> tuple[type, type, type]:
        from pkstruct.linear.linked_lists.circular_linked_list import CircularLinkedList
        from pkstruct.linear.linked_lists.doubly_linked_list import DoublyLinkedList
        from pkstruct.linear.linked_lists.singly_linked_list import SinglyLinkedList
        return SinglyLinkedList, DoublyLinkedList, CircularLinkedList

    def visualize(self, list_instance: Any, style: str = "ascii") -> str:
        """Return a string representation of *list_instance*.

        Args:
            list_instance: A SinglyLinkedList, DoublyLinkedList, or
                CircularLinkedList instance.
            style: Rendering style. Currently only ``"ascii"`` is supported.

        Returns:
            ASCII art string describing the list.

        Raises:
            TypeError: If *list_instance* is not a recognised list type.
            ValueError: If *style* is not ``"ascii"``.
        """
        if style != "ascii":
            raise ValueError(f"Unsupported visualisation style: {style!r}. Use 'ascii'.")

        SinglyLinkedList, DoublyLinkedList, CircularLinkedList = self._list_types()

        if isinstance(list_instance, CircularLinkedList):
            return AsciiVisualizer.circular(
                list_instance.head,
                list_instance.size,
            )
        if isinstance(list_instance, DoublyLinkedList):
            return AsciiVisualizer.doubly(
                list_instance.head,
                list_instance.tail,
            )
        if isinstance(list_instance, SinglyLinkedList):
            return AsciiVisualizer.singly(list_instance.head)

        raise TypeError(
            f"Unsupported list type: {type(list_instance).__name__}. "
            "Expected SinglyLinkedList, DoublyLinkedList, or CircularLinkedList."
        )

    def debug_view(self, list_instance: Any) -> dict[str, Any]:
        """Return a diagnostic dictionary for *list_instance*.

        The returned dict always contains:
            - ``type``: class name string
            - ``size``: integer node count
            - ``head``: value of head node, or ``None``
            - ``tail``: value of tail node, or ``None``
            - ``values``: list of all values in forward order
            - ``node_ids``: list of ``id()`` for each node

        Args:
            list_instance: Any supported linked list instance.

        Returns:
            Dictionary with debugging information.

        Raises:
            TypeError: If *list_instance* is not a recognised list type.
        """
        SinglyLinkedList, DoublyLinkedList, CircularLinkedList = self._list_types()

        if not isinstance(list_instance, (SinglyLinkedList, DoublyLinkedList, CircularLinkedList)):
            raise TypeError(
                f"Unsupported list type: {type(list_instance).__name__}."
            )

        list_type = type(list_instance).__name__
        size = list_instance.size

        # Collect values and node ids safely
        values: list[Any] = []
        node_ids: list[int] = []

        if isinstance(list_instance, CircularLinkedList):
            current = list_instance.head
            steps = 0
            while current is not None and steps < size:
                values.append(current.value)
                node_ids.append(id(current))
                current = current.next
                steps += 1
        else:
            current = list_instance.head
            visited: set[int] = set()
            while current is not None:
                if id(current) in visited:
                    break
                visited.add(id(current))
                values.append(current.value)
                node_ids.append(id(current))
                current = current.next

        head_value = list_instance.head.value if list_instance.head is not None else None

        # Tail: DoublyLinkedList has .tail; others we derive
        if isinstance(list_instance, (DoublyLinkedList, CircularLinkedList)):
            tail_value = list_instance.tail.value if list_instance.tail is not None else None
        else:
            tail_value = values[-1] if values else None

        return {
            "type": list_type,
            "size": size,
            "head": head_value,
            "tail": tail_value,
            "values": values,
            "node_ids": node_ids,
        }