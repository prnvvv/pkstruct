from __future__ import annotations

from typing import Any, TypeVar

from pkstruct.linear.linked_lists._base import _LinkedListBase
from pkstruct.linear.linked_lists.nodes import SinglyNode

T = TypeVar("T")


class SinglyLinkedList(_LinkedListBase[T]):
    def __init__(self) -> None:
        super().__init__()

    def _append(self, value: T) -> None:
        node: SinglyNode[T] = SinglyNode(value)
        if self._head is None:
            self._head = node
            self._tail = node
        else:
            self._tail.next = node
            self._tail = node
        self._size += 1

    def _prepend(self, value: T) -> None:
        node: SinglyNode[T] = SinglyNode(value)
        node.next = self._head
        self._head = node
        if self._tail is None:
            self._tail = node
        self._size += 1

    def _node_at(self, index: int) -> SinglyNode[T]:
        cur: SinglyNode[T] | None = self._head
        for _ in range(index):
            if cur is None:
                raise RuntimeError("internal invariant violated: unexpected None in linked list chain")
            cur = cur.next
        if cur is None:
            raise RuntimeError("internal invariant violated: unexpected None in linked list chain")
        return cur

    def _find_node(self, value: object) -> SinglyNode[T] | None:
        cur: SinglyNode[T] | None = self._head
        while cur is not None:
            if cur.value == value:
                return cur
            cur = cur.next
        return None

    def _remove_node(self, node: SinglyNode[T]) -> T:
        if node is self._head:
            self._head = node.next
            if self._head is None:
                self._tail = None
        else:
            prev = self._head
            while prev is not None and prev.next is not node:
                prev = prev.next
            if prev is not None:
                prev.next = node.next
                if prev.next is None:
                    self._tail = prev
        node.next = None
        self._size -= 1
        return node.value

    def _insert_before_node(self, node: SinglyNode[T], value: T) -> None:
        new_node: SinglyNode[T] = SinglyNode(value)
        if node is self._head:
            new_node.next = self._head
            self._head = new_node
        else:
            prev = self._head
            while prev is not None and prev.next is not node:
                prev = prev.next
            if prev is not None:
                new_node.next = node
                prev.next = new_node
        self._size += 1

    def _insert_after_node(self, node: SinglyNode[T], value: T) -> None:
        new_node: SinglyNode[T] = SinglyNode(value)
        new_node.next = node.next
        node.next = new_node
        if node is self._tail:
            self._tail = new_node
        self._size += 1

    def _to_list_unsafe(self) -> list[T]:
        result: list[T] = []
        cur = self._head
        while cur is not None:
            result.append(cur.value)
            cur = cur.next
        return result

    def intersection_node(self, other: SinglyLinkedList[T]) -> T | None:
        with self._lock:
            len_a = self._size
            len_b = other._size
            cur_a: SinglyNode[T] | None = self._head
            cur_b: SinglyNode[T] | None = other._head
            while len_a > len_b:
                cur_a = cur_a.next if cur_a else None
                len_a -= 1
            while len_b > len_a:
                cur_b = cur_b.next if cur_b else None
                len_b -= 1
            while cur_a is not cur_b:
                cur_a = cur_a.next if cur_a else None
                cur_b = cur_b.next if cur_b else None
            return cur_a.value if cur_a is not None else None

    def visualize(self, style: str = "ascii") -> str:
        with self._lock:
            items = self._to_list_unsafe()
        if style != "ascii":
            from pkstruct.linear.exceptions import ValidationError
            raise ValidationError(f"Unknown style {style!r}. Only 'ascii' is supported.")
        if not items:
            return "NULL (empty)"
        parts = [f"[{v!r}]" for v in items]
        return " -> ".join(parts) + " -> NULL"

    def debug(self) -> dict[str, Any]:
        with self._lock:
            return {
                "type": "SinglyLinkedList",
                "length": self._size,
                "size": self._size,
                "head": repr(self._head),
                "tail": repr(self._node_at(self._size - 1)) if self._size > 0 else None,
                "values": self._to_list_unsafe(),
                "tracer": self._tracer.summary(),
            }
