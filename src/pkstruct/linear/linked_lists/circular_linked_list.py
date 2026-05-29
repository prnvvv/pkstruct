from __future__ import annotations

from typing import Any, TypeVar, cast

from pkstruct.linear.exceptions import (
    EmptyStructureError,
    ValidationError,
)
from pkstruct.linear.linked_lists._base import _LinkedListBase
from pkstruct.linear.linked_lists.nodes import CircularNode
from pkstruct.shared.validators import validate_index

T = TypeVar("T")


class CircularLinkedList(_LinkedListBase[T]):
    __slots__ = ()

    def __init__(self) -> None:
        super().__init__()

    def _append(self, value: T) -> None:
        new_node: CircularNode[T] = CircularNode(value)
        if self._tail is None:
            new_node.next = new_node
            self._head = new_node
            self._tail = new_node
        else:
            new_node.next = self._head
            self._tail.next = new_node
            self._tail = new_node
        self._size += 1

    def _prepend(self, value: T) -> None:
        new_node: CircularNode[T] = CircularNode(value)
        if self._tail is None:
            new_node.next = new_node
            self._head = new_node
            self._tail = new_node
        else:
            new_node.next = self._head
            self._tail.next = new_node
            self._head = new_node
        self._size += 1

    def _node_at(self, index: int) -> CircularNode[T]:
        validate_index(index, self._size)
        node: CircularNode[T] | None = self._head
        for _ in range(index):
            if node is None:
                raise RuntimeError("internal invariant violated: unexpected None in linked list chain")
            node = node.next
        if node is None:
            raise RuntimeError("internal invariant violated: unexpected None in linked list chain")
        return node

    def _node_before(self, target: CircularNode[T]) -> CircularNode[T]:
        node: CircularNode[T] | None = self._tail
        while node is not None and node.next is not target:
            node = node.next
        if node is None:
            raise RuntimeError("internal invariant violated: unexpected None in linked list chain")
        return node

    def _find_node(self, value: object) -> CircularNode[T] | None:
        if self._head is None:
            return None
        node: CircularNode[T] | None = self._head
        for _ in range(self._size):
            if node is None:
                return None
            if node.value == value:
                return node
            node = node.next
        return None

    def _remove_node(self, node: CircularNode[T]) -> T:
        if self._size == 1:
            self._head = None
            self._tail = None
            node.next = None
            self._size -= 1
            return node.value
        prev = self._node_before(node)
        prev.next = node.next
        if node is self._head:
            self._head = node.next
        if node is self._tail:
            self._tail = prev
        node.next = None
        self._size -= 1
        return node.value

    def _insert_before_node(self, node: CircularNode[T], value: T) -> None:
        if node is self._head:
            self._prepend(value)
        else:
            prev = self._node_before(node)
            new_node: CircularNode[T] = CircularNode(value)
            new_node.next = node
            prev.next = new_node
            self._size += 1

    def _insert_after_node(self, node: CircularNode[T], value: T) -> None:
        new_node: CircularNode[T] = CircularNode(value)
        new_node.next = node.next
        node.next = new_node
        if node is self._tail:
            self._tail = new_node
        self._size += 1

    def _to_list_unsafe(self) -> list[T]:
        if self._head is None:
            return []
        result: list[T] = []
        node = self._head
        for _ in range(self._size):
            result.append(node.value)
            node = node.next
        return result

    # ------------------------------------------------------------------ #
    #  Rotation overrides (pointer-based for full list)                     #
    # ------------------------------------------------------------------ #

    def _rotate_full_list(self, shift: int) -> None:
        if shift == 0 or self._size <= 1:
            return
        steps = (self._size - shift) % self._size
        for _ in range(steps):
            self._head = self._head.next
            self._tail = self._tail.next

    def rotate_head(self, steps: int = 1, direction: bool = True) -> None:
        with self._lock:
            if self._size == 0:
                raise EmptyStructureError("rotate_head on an empty list")
            self._tracer.record("rotate_head", steps=steps, direction=direction)
            steps = steps % self._size
            if steps == 0:
                return
            if not direction:
                steps = self._size - steps
            for _ in range(steps):
                self._tail = self._head
                self._head = self._head.next

    # ------------------------------------------------------------------ #
    #  Josephus problem (circular-unique)                                   #
    # ------------------------------------------------------------------ #

    def josephus(self, step: int) -> T:
        with self._lock:
            if self._size == 0:
                raise EmptyStructureError("josephus on an empty list")
            if step < 1:
                raise ValidationError("'step' must be >= 1.")
            self._tracer.record("josephus", step=step)
            current = self._head
            while self._size > 1:
                for _ in range(step - 1):
                    current = current.next
                next_node = current.next
                self._remove_node(current)
                current = next_node
            survivor = cast(T, self._head.value)
            self.clear()
            return survivor

    # ------------------------------------------------------------------ #
    #  Visualization & Debug                                                #
    # ------------------------------------------------------------------ #

    def visualize(self, style: str = "ascii") -> str:
        with self._lock:
            if self._size == 0:
                return "(empty circular list)"
            values = self._to_list_unsafe()
            if style == "simple":
                return ", ".join(str(v) for v in values)
            if style == "ring":
                nodes_str = " -> ".join(f"[{v}]" for v in values)
                return f"{nodes_str} -> \u21ba"
            inner = " -> ".join(str(v) for v in values)
            return f"{inner} -> (back to head)"

    def debug(self) -> dict[str, Any]:
        with self._lock:
            invariant = (
                (self._tail is not None and self._tail.next is self._head)
                if self._size > 0
                else True
            )
            return {
                "type": "CircularLinkedList",
                "length": self._size,
                "size": self._size,
                "head": self._head.value if self._head else None,
                "tail": self._tail.value if self._tail else None,
                "tail_next": (self._tail.next.value if self._tail and self._tail.next else None),
                "invariant_ok": invariant,
                "values": self._to_list_unsafe(),
                "events": self._tracer.get_events(),
            }

    def detect_cycle(self, return_start: bool = False) -> bool | tuple[bool, Any]:
        with self._lock:
            if self._head is None:
                return (False, None) if return_start else False
            slow = self._head
            fast = self._head
            has_cycle = False
            max_steps = self._size * 2
            for _ in range(max_steps):
                if fast.next is None or fast.next.next is None:
                    break
                slow = slow.next
                fast = fast.next.next
                if slow is fast:
                    has_cycle = True
                    break
            if not return_start:
                return has_cycle
            if not has_cycle:
                return False, None
            slow = self._head
            while slow is not fast:
                slow = slow.next
                fast = fast.next
            return True, slow.value
