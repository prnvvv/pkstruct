from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from typing import Any, Generic, TypeVar, cast

from pkstruct.linear.exceptions import (
    EmptyStructureError,
    IndexOutOfRangeError,
    ValidationError,
    ValueNotFoundError,
)
from pkstruct._help import HelpMixin
from pkstruct._linear_shortcuts import LinearShortcutsMixin
from pkstruct._str import StrMixin
from pkstruct.shared.debugging import DebugTracer
from pkstruct.shared.serializers import deserialize_from_json, serialize_to_json
from pkstruct.shared.threading import StructureLock
from pkstruct.shared.validators import validate_index, validate_range

T = TypeVar("T")


class _LinkedListBase(Generic[T], ABC, StrMixin, LinearShortcutsMixin, HelpMixin):
    __slots__ = ("_head", "_tail", "_size", "_lock", "_tracer")

    def __init__(self) -> None:
        self._head: Any = None
        self._tail: Any = None
        self._size: int = 0
        self._lock: StructureLock = StructureLock()
        self._tracer: DebugTracer = DebugTracer()

    # ------------------------------------------------------------------ #
    #  Abstract node operations                                           #
    # ------------------------------------------------------------------ #

    @abstractmethod
    def _append(self, value: T) -> None: ...

    @abstractmethod
    def _prepend(self, value: T) -> None: ...

    @abstractmethod
    def _node_at(self, index: int) -> Any: ...

    @abstractmethod
    def _find_node(self, value: object) -> Any | None: ...

    @abstractmethod
    def _remove_node(self, node: Any) -> T: ...

    @abstractmethod
    def _insert_before_node(self, node: Any, value: T) -> None: ...

    @abstractmethod
    def _insert_after_node(self, node: Any, value: T) -> None: ...

    @abstractmethod
    def _to_list_unsafe(self) -> list[T]: ...

    # ------------------------------------------------------------------ #
    #  Construction helpers                                                 #
    # ------------------------------------------------------------------ #

    @classmethod
    def create(cls) -> _LinkedListBase[T]:
        return cls()

    @classmethod
    def from_list(cls, items: list[T]) -> _LinkedListBase[T]:
        if not isinstance(items, list):
            raise ValidationError(f"'items' must be a list, got {type(items).__name__!r}.")
        obj: _LinkedListBase[T] = cls()
        for item in items:
            obj._append(item)
        return obj

    @classmethod
    def from_json(cls, json_str: str) -> _LinkedListBase[T]:
        items: list[T] = deserialize_from_json(json_str)
        return cls.from_list(items)

    def to_json(self) -> str:
        return serialize_to_json(self._to_list_unsafe())

    def copy(self) -> _LinkedListBase[T]:
        with self._lock:
            return self.from_list(self._to_list_unsafe())

    # ------------------------------------------------------------------ #
    #  Insertion                                                            #
    # ------------------------------------------------------------------ #

    def insert(
        self,
        value: T,
        position: int | None = None,
        before: T | None = None,
        after: T | None = None,
    ) -> None:
        provided = sum(x is not None for x in (position, before, after))
        if provided > 1:
            raise ValidationError("Provide at most one of 'position', 'before', or 'after'.")
        with self._lock:
            self._tracer.record(
                "insert", value=value, position=position, before=before, after=after
            )

            if before is not None:
                target = self._find_node(before)
                if target is None:
                    raise ValueNotFoundError(before)
                if target is self._head:
                    self._prepend(value)
                else:
                    self._insert_before_node(target, value)
                return

            if after is not None:
                target = self._find_node(after)
                if target is None:
                    raise ValueNotFoundError(after)
                self._insert_after_node(target, value)
                return

            if position is None:
                self._append(value)
                return

            if position < 0:
                raise IndexOutOfRangeError(position, self._size)
            if position == 0:
                self._prepend(value)
                return
            if position > self._size:
                raise IndexOutOfRangeError(position, self._size)
            if position == self._size:
                self._append(value)
                return

            target = self._node_at(position)
            self._insert_before_node(target, value)

    def extend(self, values: list[T] | _LinkedListBase[T]) -> None:
        if isinstance(values, _LinkedListBase):
            items: list[T] = values._to_list_unsafe()
        elif isinstance(values, list):
            items = values
        else:
            raise ValidationError(
                f"'values' must be a list or linked list, got {type(values).__name__!r}."
            )
        with self._lock:
            for item in items:
                self._append(item)

    def merge(self, *others: _LinkedListBase[T]) -> None:
        with self._lock:
            for other in others:
                with other._lock:
                    values = other._to_list_unsafe()
                    for v in values:
                        self._append(v)

    # ------------------------------------------------------------------ #
    #  Deletion                                                             #
    # ------------------------------------------------------------------ #

    def delete(
        self,
        value: T | None = None,
        position: int | None = None,
        rng: tuple[int, int] | None = None,
    ) -> T | list[T] | None:
        provided = sum(x is not None for x in (value, position, rng))
        if provided == 0:
            raise ValidationError("Provide one of 'value', 'position', or 'rng'.")
        if provided > 1:
            raise ValidationError("Provide only one of 'value', 'position', or 'rng'.")
        with self._lock:
            if self._size == 0:
                raise EmptyStructureError("delete")
            self._tracer.record("delete", value=value, position=position, rng=rng)

            if value is not None:
                node = self._find_node(value)
                if node is None:
                    raise ValueNotFoundError(value)
                return self._remove_node(node)

            if position is not None:
                normalised = position if position >= 0 else position + self._size
                if not (0 <= normalised < self._size):
                    raise IndexOutOfRangeError(position, self._size)
                node = self._node_at(normalised)
                return self._remove_node(node)

            if rng is None:
                raise RuntimeError(
                    "internal invariant violated: rng should not be None in the range-delete branch"
                )
            start, end = rng
            validate_range(start, end, self._size)
            removed: list[T] = []
            for _ in range(end - start + 1):
                node = self._node_at(start)
                removed.append(self._remove_node(node))
            return removed

    def clear(self) -> None:
        with self._lock:
            self._head = None
            self._tail = None
            self._size = 0
            self._tracer.record("clear")

    # ------------------------------------------------------------------ #
    #  Access                                                               #
    # ------------------------------------------------------------------ #

    def get(self, position: int, from_end: bool = False) -> T:
        with self._lock:
            if self._size == 0:
                raise EmptyStructureError("get")
            if from_end:
                if position < 0:
                    raise IndexOutOfRangeError(position, self._size)
                validate_index(position, self._size)
                idx = self._size - 1 - position
                return cast(T, self._node_at(idx).value)
            if position < 0:
                raise IndexOutOfRangeError(position, self._size)
            validate_index(position, self._size)
            return cast(T, self._node_at(position).value)

    def to_list(self) -> list[T]:
        with self._lock:
            return self._to_list_unsafe()

    def size(self) -> int:
        with self._lock:
            return self._size

    def is_empty(self) -> bool:
        with self._lock:
            return self._size == 0

    def count(self, value: T) -> int:
        with self._lock:
            n = 0
            node = self._head
            for _ in range(self._size):
                if node.value == value:
                    n += 1
                node = node.next
            return n

    # ------------------------------------------------------------------ #
    #  Search                                                               #
    # ------------------------------------------------------------------ #

    def index(self, value: T) -> int:
        with self._lock:
            node = self._head
            for i in range(self._size):
                if node.value == value:
                    return i
                node = node.next
            raise ValueNotFoundError(value)

    # ------------------------------------------------------------------ #
    #  Replacement                                                          #
    # ------------------------------------------------------------------ #

    def replace(
        self,
        new_value: T,
        old_value: T | None = None,
        position: int | None = None,
        replace_all: bool = False,
    ) -> int:
        if new_value is None:
            raise ValidationError("'new_value' is required.")
        with self._lock:
            self._tracer.record(
                "replace", old_value=old_value, new_value=new_value, position=position
            )
            if position is not None:
                idx = position if position >= 0 else position + self._size
                validate_index(idx, self._size)
                self._node_at(idx).value = new_value
                return 1
            if old_value is None:
                raise ValidationError("Provide 'old_value' or 'position'.")
            count = 0
            node = self._head
            for _ in range(self._size):
                if node.value == old_value:
                    node.value = new_value
                    count += 1
                    if not replace_all:
                        break
                node = node.next
            if count == 0:
                raise ValueNotFoundError(old_value)
            return count

    # ------------------------------------------------------------------ #
    #  Reverse & Rotation                                                   #
    # ------------------------------------------------------------------ #

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
            nodes: list[Any] = []
            node = self._node_at(lo)
            for _ in range(hi - lo + 1):
                nodes.append(node)
                node = node.next
            left, right = 0, len(nodes) - 1
            while left < right:
                nodes[left].value, nodes[right].value = nodes[right].value, nodes[left].value
                left += 1
                right -= 1

    def rotate(
        self,
        shift: int = 1,
        start: int | None = None,
        end: int | None = None,
        direction: bool = True,
    ) -> None:
        with self._lock:
            if self._size == 0:
                raise EmptyStructureError("rotate an empty list")

            actual_shift = shift
            if shift < 0:
                actual_shift = abs(shift)
                direction = False

            actual_start = 0 if start is None else start
            actual_end = self._size - 1 if end is None else end

            if actual_start < 0:
                actual_start = self._size + actual_start
            if actual_end < 0:
                actual_end = self._size + actual_end

            validate_range(actual_start, actual_end, self._size)

            length = actual_end - actual_start + 1
            if length <= 1:
                return

            effective_shift = actual_shift % length
            if effective_shift == 0:
                return

            if not direction:
                effective_shift = length - effective_shift

            self._tracer.record(
                "rotate",
                shift=actual_shift,
                start=actual_start,
                end=actual_end,
                direction=direction,
            )

            if actual_start == 0 and actual_end == self._size - 1:
                self._rotate_full_list(effective_shift)
            else:
                self._rotate_subrange(actual_start, actual_end, effective_shift)

    def _rotate_full_list(self, shift: int) -> None:
        if shift == 0 or self._size <= 1:
            return
        values = self._to_list_unsafe()
        rotated = values[-shift:] + values[:-shift]
        node = self._head
        for v in rotated:
            node.value = v
            node = node.next

    def _rotate_subrange(self, start: int, end: int, shift: int) -> None:
        nodes: list[Any] = []
        node = self._node_at(start)
        for _ in range(end - start + 1):
            nodes.append(node)
            node = node.next
        values = [n.value for n in nodes]
        rotated = values[-shift:] + values[:-shift]
        for n, v in zip(nodes, rotated, strict=True):
            n.value = v

    # ------------------------------------------------------------------ #
    #  Swapping                                                             #
    # ------------------------------------------------------------------ #

    def swap(
        self,
        value1: T | None = None,
        value2: T | None = None,
        pos1: int | None = None,
        pos2: int | None = None,
        pairwise: bool = False,
    ) -> None:
        with self._lock:
            self._tracer.record(
                "swap", value1=value1, value2=value2, pos1=pos1, pos2=pos2, pairwise=pairwise
            )
            if pairwise:
                node = self._head
                for _ in range(self._size // 2):
                    node.value, node.next.value = node.next.value, node.value
                    node = node.next.next
                return
            if self._size == 0:
                raise EmptyStructureError("swap")
            if value1 is not None and value2 is not None:
                n1 = self._find_node(value1)
                n2 = self._find_node(value2)
                if n1 is None:
                    raise ValueNotFoundError(value1)
                if n2 is None:
                    raise ValueNotFoundError(value2)
                n1.value, n2.value = n2.value, n1.value
                return
            if pos1 is not None and pos2 is not None:
                i1 = pos1 if pos1 >= 0 else pos1 + self._size
                i2 = pos2 if pos2 >= 0 else pos2 + self._size
                validate_index(i1, self._size)
                validate_index(i2, self._size)
                n1 = self._node_at(i1)
                n2 = self._node_at(i2)
                n1.value, n2.value = n2.value, n1.value
                return
            raise ValidationError("Provide (value1, value2), (pos1, pos2), or pairwise=True.")

    # ------------------------------------------------------------------ #
    #  Sort & Partition                                                     #
    # ------------------------------------------------------------------ #

    def sort(
        self,
        reverse: bool = False,
        key: Callable[[T], Any] | None = None,
    ) -> None:
        with self._lock:
            if self._size <= 1:
                return
            self._tracer.record("sort", reverse=reverse)
            values = self._to_list_unsafe()
            values.sort(key=key, reverse=reverse)
            node = self._head
            for v in values:
                node.value = v
                node = node.next

    def partition(self, predicate_or_pivot: Callable[[T], bool] | T) -> None:
        with self._lock:
            if self._size <= 1:
                return
            if callable(predicate_or_pivot):
                pred = predicate_or_pivot
            else:
                pivot = predicate_or_pivot

                def pred(x: T) -> bool:
                    return cast(bool, x < pivot)  # type: ignore[operator]

            values = self._to_list_unsafe()
            left = [v for v in values if pred(v)]
            right = [v for v in values if not pred(v)]
            new_values = left + right
            node = self._head
            for v in new_values:
                node.value = v
                node = node.next

    # ------------------------------------------------------------------ #
    #  Interview problems                                                   #
    # ------------------------------------------------------------------ #

    def detect_cycle(self, return_start: bool = False) -> bool | tuple[bool, Any]:
        with self._lock:
            slow = self._head
            fast = self._head
            while fast is not None and fast.next is not None:
                slow = slow.next
                fast = fast.next.next
                if slow is fast:
                    if not return_start:
                        return True
                    slow = self._head
                    while slow is not fast:
                        slow = slow.next
                        fast = fast.next
                    return True, slow.value
            if return_start:
                return False, None
            return False

    def palindrome(self) -> bool:
        with self._lock:
            if self._size == 0:
                raise EmptyStructureError("palindrome on empty list")
            values = self._to_list_unsafe()
            return values == values[::-1]

    def reorder(self, mode: str = "odd_even") -> None:
        with self._lock:
            if self._size <= 1:
                return
            self._tracer.record("reorder", mode=mode)
            if mode == "odd_even":
                values = self._to_list_unsafe()
                odd_vals = [v for i, v in enumerate(values) if i % 2 == 1]
                even_vals = [v for i, v in enumerate(values) if i % 2 == 0]
                reordered = odd_vals + even_vals
                node = self._head
                for v in reordered:
                    node.value = v
                    node = node.next
            elif mode == "zigzag":
                nodes: list[Any] = []
                cur = self._head
                while cur is not None:
                    nodes.append(cur)
                    cur = cur.next
                for i in range(len(nodes) - 1):
                    a, b = nodes[i].value, nodes[i + 1].value
                    if i % 2 == 0:
                        if a > b:
                            nodes[i].value, nodes[i + 1].value = b, a
                    else:
                        if a < b:
                            nodes[i].value, nodes[i + 1].value = b, a
            else:
                raise ValidationError(
                    f"Unknown reorder mode {mode!r}. Choose 'odd_even' or 'zigzag'."
                )

    def segregate_even_odd(self) -> None:
        with self._lock:
            if self._size <= 1:
                return
            self._tracer.record("segregate_even_odd")
            evens: list[Any] = []
            odds: list[Any] = []
            node = self._head
            for _ in range(self._size):
                try:
                    if isinstance(node.value, int) and node.value % 2 == 0:
                        evens.append(node.value)
                    else:
                        odds.append(node.value)
                except (TypeError, ValueError):
                    odds.append(node.value)
                node = node.next
            all_values = evens + odds
            node = self._head
            for v in all_values:
                node.value = v
                node = node.next

    # ------------------------------------------------------------------ #
    #  Public properties                                                    #
    # ------------------------------------------------------------------ #

    @property
    def head(self) -> Any:
        with self._lock:
            return self._head

    @property
    def tail(self) -> Any:
        with self._lock:
            return self._tail

    # ------------------------------------------------------------------ #
    #  Dunder methods                                                       #
    # ------------------------------------------------------------------ #

    def __iter__(self) -> Iterator[T]:
        with self._lock:
            snapshot = self._to_list_unsafe()
        return iter(snapshot)

    def __len__(self) -> int:
        return self.size()

    def __bool__(self) -> bool:
        return self._size > 0

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._to_list_unsafe()!r})"

    def __contains__(self, item: object) -> bool:
        with self._lock:
            return self._find_node(item) is not None

    def __getitem__(self, index: int) -> T:
        return self.get(index)

    def __setitem__(self, index: int, value: T) -> None:
        self.replace(new_value=value, position=index)

    def __eq__(self, other: object) -> bool:
        if type(other) is not type(self):
            return NotImplemented
        return self._to_list_unsafe() == other._to_list_unsafe()
