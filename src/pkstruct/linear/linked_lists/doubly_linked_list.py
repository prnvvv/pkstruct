from __future__ import annotations

from typing import Any, TypeVar, cast

from pkstruct.linear.exceptions import EmptyStructureError
from pkstruct.linear.linked_lists._base import _LinkedListBase
from pkstruct.linear.linked_lists.nodes import DoublyNode
from pkstruct.shared.validators import validate_range

T = TypeVar("T")


class DoublyLinkedList(_LinkedListBase[T]):
    """A doubly-linked list. Each node points to both the next and previous node."""

    __slots__ = ()

    def __init__(self) -> None:
        super().__init__()

    def _append(self, value: T) -> None:
        new_node: DoublyNode[T] = DoublyNode(value)
        if self._tail is None:
            self._head = new_node
            self._tail = new_node
        else:
            new_node.prev = self._tail
            self._tail.next = new_node
            self._tail = new_node
        self._size += 1

    def _prepend(self, value: T) -> None:
        new_node: DoublyNode[T] = DoublyNode(value)
        if self._head is None:
            self._head = new_node
            self._tail = new_node
        else:
            new_node.next = self._head
            self._head.prev = new_node
            self._head = new_node
        self._size += 1

    def _node_at(self, index: int) -> DoublyNode[T]:
        if index <= self._size // 2:
            node: DoublyNode[T] | None = self._head
            for _ in range(index):
                if node is None:
                    raise RuntimeError(
                        "internal invariant violated: unexpected None in linked list chain"
                    )
                node = node.next
        else:
            node = self._tail
            for _ in range(self._size - 1 - index):
                if node is None:
                    raise RuntimeError(
                        "internal invariant violated: unexpected None in linked list chain"
                    )
                node = node.prev
        if node is None:
            raise RuntimeError("internal invariant violated: unexpected None in linked list chain")
        return node

    def _find_node(self, value: object) -> DoublyNode[T] | None:
        node: DoublyNode[T] | None = self._head
        while node is not None:
            if node.value == value:
                return node
            node = node.next
        return None

    def _remove_node(self, node: DoublyNode[T]) -> T:
        prev_node = node.prev
        next_node = node.next
        if prev_node is not None:
            prev_node.next = next_node
        else:
            self._head = next_node
        if next_node is not None:
            next_node.prev = prev_node
        else:
            self._tail = prev_node
        node.next = None
        node.prev = None
        self._size -= 1
        return node.value

    def _insert_before_node(self, node: DoublyNode[T], value: T) -> None:
        new_node: DoublyNode[T] = DoublyNode(value)
        prev_node = node.prev
        new_node.next = node
        new_node.prev = prev_node
        node.prev = new_node
        if prev_node is None:
            self._head = new_node
        else:
            prev_node.next = new_node
        self._size += 1

    def _insert_after_node(self, node: DoublyNode[T], value: T) -> None:
        new_node: DoublyNode[T] = DoublyNode(value)
        next_node = node.next
        new_node.prev = node
        new_node.next = next_node
        node.next = new_node
        if next_node is None:
            self._tail = new_node
        else:
            next_node.prev = new_node
        self._size += 1

    def _to_list_unsafe(self) -> list[T]:
        result: list[T] = []
        node = self._head
        while node is not None:
            result.append(node.value)
            node = node.next
        return result

    def reverse(self, start: int | None = None, end: int | None = None) -> None:
        with self._lock:
            if self._size == 0:
                raise EmptyStructureError("reverse an empty list")
            lo = 0 if start is None else start
            hi = self._size - 1 if end is None else end
            if lo >= hi:
                return
            validate_range(lo, hi, self._size)
            self._tracer.record("reverse", start=lo, end=hi)
            left = self._node_at(lo)
            right = self._node_at(hi)
            while left is not right and left is not cast(DoublyNode[T], right.next):
                left.value, right.value = right.value, left.value
                left = cast(DoublyNode[T], left.next)
                right = cast(DoublyNode[T], right.prev)

    def visualize(self, style: str = "ascii") -> str:
        with self._lock:
            if self._size == 0:
                return "None <- (empty) -> None"
            values = self._to_list_unsafe()
            if style == "simple":
                return ", ".join(str(v) for v in values)
            inner = " <-> ".join(str(v) for v in values)
            return f"None <- {inner} -> None"

    def debug(self) -> dict[str, Any]:
        with self._lock:
            return {
                "type": "DoublyLinkedList",
                "length": self._size,
                "size": self._size,
                "head": self._head.value if self._head else None,
                "tail": self._tail.value if self._tail else None,
                "values": self._to_list_unsafe(),
                "events": self._tracer.get_events(),
            }
