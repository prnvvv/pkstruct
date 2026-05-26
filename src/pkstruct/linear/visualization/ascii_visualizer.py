"""ASCII art visualization for linked list structures."""
from __future__ import annotations
from typing import Any, Callable, Optional


class AsciiVisualizer:
    """Static methods for rendering linked lists as ASCII strings."""

    @staticmethod
    def singly(
        head: Any,
        node_repr: Callable[[Any], str] = str,
    ) -> str:
        """Render a singly linked list.

        Args:
            head: Head node (must have .value and .next attributes).
            node_repr: Callable that converts a node's value to a string.

        Returns:
            String like ``"10 -> 20 -> 30 -> None"`` or ``"NULL (empty)"``
            when the list is empty.
        """
        if head is None:
            return "NULL (empty)"

        parts: list[str] = []
        current = head
        visited: set[int] = set()

        while current is not None:
            node_id = id(current)
            if node_id in visited:
                parts.append("(cycle detected)")
                break
            visited.add(node_id)
            parts.append(node_repr(current.value))
            current = current.next

        parts.append("None")
        return " -> ".join(parts)

    @staticmethod
    def doubly(
        head: Any,
        tail: Any,
        node_repr: Callable[[Any], str] = str,
    ) -> str:
        """Render a doubly linked list.

        Args:
            head: Head node (must have .value, .next, .prev attributes).
            tail: Tail node.
            node_repr: Callable that converts a node's value to a string.

        Returns:
            String like ``"None <- 10 <-> 20 <-> 30 -> None"`` or
            ``"NULL <-> NULL"`` when the list is empty.
        """
        if head is None:
            return "NULL <-> NULL"

        parts: list[str] = []
        current = head
        visited: set[int] = set()

        while current is not None:
            node_id = id(current)
            if node_id in visited:
                parts.append("(cycle detected)")
                break
            visited.add(node_id)
            parts.append(node_repr(current.value))
            current = current.next

        if not parts:
            return "NULL <-> NULL"

        inner = " <-> ".join(parts)
        return f"None <- {inner} -> None"

    @staticmethod
    def circular(
        head: Any,
        size: int,
        node_repr: Callable[[Any], str] = str,
    ) -> str:
        """Render a circular linked list.

        Args:
            head: Head node (must have .value and .next attributes).
            size: Number of nodes (used as iteration guard).
            node_repr: Callable that converts a node's value to a string.

        Returns:
            String like ``"10 -> 20 -> 30 -> (back to head)"`` or
            ``"empty circular list"`` when the list is empty.
        """
        if head is None or size == 0:
            return "empty circular list"

        parts: list[str] = []
        current = head
        steps = 0

        while steps < size:
            parts.append(node_repr(current.value))
            current = current.next
            steps += 1

        parts.append("(back to head)")
        return " -> ".join(parts)