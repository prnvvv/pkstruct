"""
pkstruct.linear.linked_lists.singly_linked_list
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Production-grade singly linked list with full API, thread safety,
serialization, visualization, and interview-problem helpers.
"""
from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any, Generic, TypeVar

from pkstruct.linear.linked_lists.nodes import SinglyNode
from pkstruct.shared.debugging import DebugTracer
from pkstruct.shared.threading import StructureLock
from pkstruct.shared.serializers import deserialize_from_json, serialize_to_json
from pkstruct.shared.validators import validate_index, validate_range
from pkstruct.shared.debugging import DebugTracer
from pkstruct.shared.exceptions import (
    EmptyStructureError,
    IndexOutOfRangeError,
    ValidationError,
    ValueNotFoundError,
)
from pkstruct.shared.serializers import deserialize_from_json, serialize_to_json
from pkstruct.shared.threading import StructureLock
from pkstruct.shared.validators import validate_index, validate_range

T = TypeVar("T")


class SinglyLinkedList(Generic[T]):
    """A thread-safe, generic singly-linked list.

    All mutation methods acquire the internal ``RLock`` so concurrent
    modifications from multiple threads do not corrupt internal state.

    Type parameter *T* is covariant at the usage site but stored with
    ``Generic[T]`` for full mypy compatibility.
    """

    # ------------------------------------------------------------------ #
    # Construction helpers                                                 #
    # ------------------------------------------------------------------ #

    def __init__(self) -> None:
        self._head: SinglyNode[T] | None = None
        self._size: int = 0
        self._lock: StructureLock = StructureLock()
        self._tracer: DebugTracer = DebugTracer()

    @classmethod
    def create(cls) -> "SinglyLinkedList[T]":
        """Return a new empty SinglyLinkedList."""
        return cls()

    @classmethod
    def from_list(cls, items: list[T]) -> "SinglyLinkedList[T]":
        """Build a SinglyLinkedList from a Python list.

        Args:
            items: Source list (may be empty).

        Returns:
            A new SinglyLinkedList containing *items* in order.

        Raises:
            ValidationError: If *items* is not a list.
        """
        if not isinstance(items, list):
            raise ValidationError(
                f"'items' must be a list, got {type(items).__name__!r}."
            )
        sll: SinglyLinkedList[T] = cls()
        for item in items:
            sll._append(item)
        return sll

    @classmethod
    def from_json(cls, json_str: str) -> "SinglyLinkedList[T]":
        """Build a SinglyLinkedList from a JSON string.

        The JSON must have the shape ``{"items": [...]}``.

        Args:
            json_str: A JSON string produced by :meth:`to_list` + serialization
                      or :func:`pkstruct.shared.serializers.serialize_to_json`.

        Returns:
            A new SinglyLinkedList.

        Raises:
            SerializationError: On malformed JSON.
        """
        items: list[T] = deserialize_from_json(json_str)  # type: ignore[assignment]
        return cls.from_list(items)
    def to_json(self) -> str:
        """Serialize the list to a JSON string (list of items)."""
        return serialize_to_json(self.to_list())

    def serialize(self) -> str:
        """Alias for to_json() for test compatibility."""
        return self.to_json()

    def deserialize(self, json_str: str) -> None:
        """Alias for from_json() for test compatibility."""
        new_list = self.from_json(json_str)
        self.clear()
        for v in new_list.to_list():
            self.insert(v)

    def copy(self) -> "SinglyLinkedList[T]":
        """Return a shallow copy of this list."""
        with self._lock:
            return SinglyLinkedList.from_list(self.to_list())

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _append(self, value: T) -> None:
        """Append *value* to the tail without acquiring the lock (internal use)."""
        node: SinglyNode[T] = SinglyNode(value)
        if self._head is None:
            self._head = node
        else:
            cur = self._head
            while cur.next is not None:
                cur = cur.next
            cur.next = node
        self._size += 1

    def _node_at(self, index: int) -> SinglyNode[T]:
        """Return the node at *index* (0-based, no bounds check)."""
        cur = self._head
        for _ in range(index):
            assert cur is not None
            cur = cur.next
        assert cur is not None
        return cur

    def _node_before(self, index: int) -> SinglyNode[T] | None:
        """Return the node immediately before *index*, or None if index==0."""
        if index == 0:
            return None
        return self._node_at(index - 1)

    # ------------------------------------------------------------------ #
    # Insertion                                                            #
    # ------------------------------------------------------------------ #

    def insert(
        self,
        value: T,
        position: int | None = None,
        before: T | None = None,
        after: T | None = None,
    ) -> None:
        """Insert *value* into the list.

        Exactly one of *position*, *before*, or *after* should be supplied
        (or none, to append at the tail).

        Args:
            value:    The value to insert.
            position: 0-based index at which to insert.  Negative indices are
                      supported (``-1`` inserts before the current last element).
                      If equal to ``self.size()``, appends at tail.
            before:   Insert immediately before the first occurrence of this value.
            after:    Insert immediately after the first occurrence of this value.

        Raises:
            ValidationError:      If multiple targeting arguments are given.
            IndexOutOfRangeError: If *position* is out of range.
            ValueNotFoundError:   If *before* / *after* target is absent.
        """
        _count = sum(x is not None for x in (position, before, after))
        if _count > 1:
            raise ValidationError(
                "Provide at most one of 'position', 'before', or 'after'."
            )
        with self._lock:
            self._tracer.record("insert", value=value, position=position)

            if before is not None:
                self._insert_before_value(value, before)
                return
            if after is not None:
                self._insert_after_value(value, after)
                return
            if position is None:
                # default: append at tail
                self._append(value)
                return
            # normalise negative index; allow == size for append-at-end
            normalised = position if position >= 0 else position + self._size
            if not (0 <= normalised <= self._size):
                raise IndexOutOfRangeError(position, self._size)

            node: SinglyNode[T] = SinglyNode(value)
            if normalised == 0:
                node.next = self._head
                self._head = node
            else:
                prev = self._node_at(normalised - 1)
                node.next = prev.next
                prev.next = node
            self._size += 1

    def _insert_before_value(self, value: T, target: T) -> None:
        prev: SinglyNode[T] | None = None
        cur = self._head
        while cur is not None:
            if cur.value == target:
                node: SinglyNode[T] = SinglyNode(value)
                node.next = cur
                if prev is None:
                    self._head = node
                else:
                    prev.next = node
                self._size += 1
                return
            prev = cur
            cur = cur.next
        raise ValueNotFoundError(target)

    def _insert_after_value(self, value: T, target: T) -> None:
        cur = self._head
        while cur is not None:
            if cur.value == target:
                node: SinglyNode[T] = SinglyNode(value)
                node.next = cur.next
                cur.next = node
                self._size += 1
                return
            cur = cur.next
        raise ValueNotFoundError(target)

    def extend(self, values: "list[T] | SinglyLinkedList[T]") -> None:
        """Append all elements from *values* to the tail.

        Args:
            values: A Python list or another SinglyLinkedList.

        Raises:
            ValidationError: If *values* is neither a list nor a SinglyLinkedList.
        """
        if isinstance(values, SinglyLinkedList):
            items: list[T] = values.to_list()
        elif isinstance(values, list):
            items = values
        else:
            raise ValidationError(
                f"'values' must be a list or SinglyLinkedList, got {type(values).__name__!r}."
            )
        with self._lock:
            for item in items:
                self._append(item)

    # ------------------------------------------------------------------ #
    # Deletion                                                             #
    # ------------------------------------------------------------------ #

    def delete(
        self,
        value: T | None = None,
        position: int | None = None,
        range: tuple[int, int] | None = None,
    ) -> "T | list[T] | None":
        """Remove element(s) and return the removed value(s).

        Exactly one argument should be supplied.

        Args:
            value:    Remove first occurrence of *value*.
            position: Remove element at 0-based *position*.
            range:    Remove elements in the inclusive range ``(start, end)``.

        Returns:
            Removed value (scalar) or list of removed values (range).
            Returns ``None`` if *value* is not found (soft delete).

        Raises:
            ValidationError:      If multiple or zero targeting arguments given.
            IndexOutOfRangeError: If *position* is out of range.
            InvalidRangeError:    If range bounds are invalid.
            EmptyStructureError:  If the list is empty.
        """
        _given = sum(x is not None for x in (value, position, range))
        if _given == 0:
            raise ValidationError(
                "Provide exactly one of 'value', 'position', or 'range'."
            )
        if _given > 1:
            raise ValidationError(
                "Provide exactly one of 'value', 'position', or 'range'."
            )
        with self._lock:
            if self._size == 0:
                raise EmptyStructureError("delete")
            if value is not None:
                return self._delete_by_value(value)
            if position is not None:
                return self._delete_by_position(position)
            assert range is not None
            return self._delete_range(range[0], range[1])

    def _delete_by_value(self, target: T) -> T | None:
        prev: SinglyNode[T] | None = None
        cur = self._head
        while cur is not None:
            if cur.value == target:
                if prev is None:
                    self._head = cur.next
                else:
                    prev.next = cur.next
                self._size -= 1
                self._tracer.record("delete_by_value", value=target)
                return cur.value
            prev = cur
            cur = cur.next
        return None

    def _delete_by_position(self, position: int) -> T:
        normalised = position if position >= 0 else position + self._size
        if not (0 <= normalised < self._size):
            raise IndexOutOfRangeError(position, self._size)
        if normalised == 0:
            assert self._head is not None
            removed = self._head.value
            self._head = self._head.next
        else:
            prev = self._node_at(normalised - 1)
            assert prev.next is not None
            removed = prev.next.value
            prev.next = prev.next.next
        self._size -= 1
        self._tracer.record("delete_by_position", position=normalised)
        return removed

    def _delete_range(self, start: int, end: int) -> list[T]:
        ns, ne = validate_range(start, end, self._size)
        removed: list[T] = []
        for _ in range(ne - ns + 1):
            removed.append(self._delete_by_position(ns))
        return removed

    def clear(self) -> None:
        """Remove all elements from the list."""
        with self._lock:
            self._head = None
            self._size = 0
            self._tracer.record("clear")

    # ------------------------------------------------------------------ #
    # Access                                                               #
    # ------------------------------------------------------------------ #

    def get(self, position: int, from_end: bool = False) -> T:
        """Return the value at *position*.

        Args:
            position: 0-based index.  Negative indices count from the tail.
            from_end: If True, *position* counts from the tail (0 = last element).

        Returns:
            The value at *position*.

        Raises:
            IndexOutOfRangeError: If *position* is out of range.
            EmptyStructureError:  If the list is empty.
        """
        with self._lock:
            if self._size == 0:
                raise EmptyStructureError("get")
            if from_end:
                idx = self._size - 1 - position
            else:
                idx = position if position >= 0 else position + self._size
            if not (0 <= idx < self._size):
                raise IndexOutOfRangeError(position, self._size)
            return self._node_at(idx).value

    def to_list(self) -> list[T]:
        """Return a Python list of all values in order."""
        with self._lock:
            result: list[T] = []
            cur = self._head
            while cur is not None:
                result.append(cur.value)
                cur = cur.next
            return result

    def size(self) -> int:
        """Return the number of elements."""
        with self._lock:
            return self._size

    def is_empty(self) -> bool:
        """Return True if the list has no elements."""
        with self._lock:
            return self._size == 0

    def count(self, value: T) -> int:
        """Return the number of occurrences of *value*."""
        with self._lock:
            n = 0
            cur = self._head
            while cur is not None:
                if cur.value == value:
                    n += 1
                cur = cur.next
            return n

    # ------------------------------------------------------------------ #
    # Search                                                               #
    # ------------------------------------------------------------------ #

    def index(self, value: T) -> int:
        """Return the 0-based index of the first occurrence of *value*.

        Raises:
            ValueNotFoundError: If *value* is not in the list.
        """
        with self._lock:
            cur = self._head
            idx = 0
            while cur is not None:
                if cur.value == value:
                    return idx
                cur = cur.next
                idx += 1
            raise ValueNotFoundError(value)

    # ------------------------------------------------------------------ #
    # Replacement                                                          #
    # ------------------------------------------------------------------ #

    def replace(
        self,
        old_value: T | None = None,
        new_value: T | None = None,
        position: int | None = None,
        replace_all: bool = False,
    ) -> int:
        """Replace value(s) in-place.

        Supply *old_value* + *new_value* to replace by value, or *position* +
        *new_value* to replace at a specific index.

        Args:
            old_value:   Value to search for and replace.
            new_value:   Replacement value.
            position:    If given, replaces the element at this position.
            replace_all: If True and using value replacement, replace every
                         occurrence.  Defaults to replacing only the first.

        Returns:
            Number of replacements made.

        Raises:
            ValidationError:      On invalid argument combinations.
            IndexOutOfRangeError: If *position* is out of range.
            ValueNotFoundError:   If *old_value* is not found (value mode).
        """
        if new_value is None:
            raise ValidationError("'new_value' is required.")
        with self._lock:
            if position is not None:
                idx = position if position >= 0 else position + self._size
                validate_index(idx, self._size)
                self._node_at(idx).value = new_value
                return 1
            if old_value is None:
                raise ValidationError("Provide 'old_value' or 'position'.")
            count = 0
            cur = self._head
            while cur is not None:
                if cur.value == old_value:
                    cur.value = new_value
                    count += 1
                    if not replace_all:
                        break
                cur = cur.next
            if count == 0:
                raise ValueNotFoundError(old_value)
            return count

    # ------------------------------------------------------------------ #
    # Reverse & Rotation                                                   #
    # ------------------------------------------------------------------ #

    def reverse(self, start: int | None = None, end: int | None = None) -> None:
        """Reverse the list (or a sub-range) in place.

        Args:
            start: Inclusive start index (default: 0).
            end:   Inclusive end index (default: size - 1).
        """
        with self._lock:
            if self._size <= 1:
                return
            s = 0 if start is None else (start if start >= 0 else start + self._size)
            e = self._size - 1 if end is None else (end if end >= 0 else end + self._size)
            if s >= e:
                return
            validate_range(s, e, self._size)
            self._reverse_segment(s, e)

    def _reverse_segment(self, s: int, e: int) -> None:
        """Reverse the sub-list [s, e] (both inclusive, 0-based)."""
        # Collect node references in the range
        nodes: list[SinglyNode[T]] = []
        cur = self._head
        for i in range(self._size):
            assert cur is not None
            if s <= i <= e:
                nodes.append(cur)
            cur = cur.next
        # Swap values in-place (avoids pointer manipulation complexity)
        left, right = 0, len(nodes) - 1
        while left < right:
            nodes[left].value, nodes[right].value = nodes[right].value, nodes[left].value
            left += 1
            right -= 1

    def rotate_full(self, start: int, end: int, direction: bool = True, shift: int = 1) -> None:
        """
        Rotate a sub-range of the list (full interface).
        
        Args:
            start: Inclusive start index
            end: Inclusive end index
            direction: True = rotate right, False = rotate left
            shift: Number of positions to rotate
        """
        with self._lock:
            if self._size == 0:
                raise EmptyStructureError("rotate an empty list")
            
            # Normalize indices
            if start < 0:
                start = self._size + start
            if end < 0:
                end = self._size + end
            
            validate_range(start, end, self._size)
            
            length = end - start + 1
            if length <= 1:
                return
            
            effective_shift = shift % length
            if effective_shift == 0:
                return
            
            if not direction:
                effective_shift = length - effective_shift
            
            self._tracer.record("rotate", start=start, end=end, 
                                direction=direction, shift=effective_shift)
            
            # Get values in range
            values = []
            node = self._node_at(start)
            for _ in range(length):
                values.append(node.value)
                node = node.next  # type: ignore[union-attr]
            
            # Rotate values
            rotated = values[-effective_shift:] + values[:-effective_shift]
            
            # Write back
            node = self._node_at(start)
            for v in rotated:
                node.value = v
                node = node.next  # type: ignore[union-attr]

    def rotate(
        self,
        shift: int = 1,
        start: int | None = None,
        end: int | None = None,
        direction: bool = True,
    ) -> None:
        """
        Rotate the list or a sub-range by `shift` positions.
        
        This method supports two calling patterns:
        
        1. Simple rotation (entire list):
            >>> ll.rotate(2)  # Rotate entire list right by 2
            >>> ll.rotate(-2) # Rotate entire list left by 2
        
        2. Advanced rotation (sub-range):
            >>> ll.rotate(shift=2, start=1, end=5, direction=True)  # Rotate right by 2
        
        Args:
            shift: Number of positions to rotate. Positive = right, negative = left.
            start: Inclusive start index (None = 0, entire list start)
            end: Inclusive end index (None = size-1, entire list end)
            direction: True = rotate right, False = rotate left (ignored if shift negative)
        
        Raises:
            EmptyStructureError: If list is empty
            InvalidRangeError: If start/end indices are invalid
        """
        with self._lock:
            if self._size == 0:
                raise EmptyStructureError("rotate an empty list")
            
            # Handle negative shift as left rotation
            actual_shift = shift
            if shift < 0:
                actual_shift = abs(shift)
                direction = False
            
            # Set default range to entire list
            actual_start = 0 if start is None else start
            actual_end = self._size - 1 if end is None else end
            
            # Normalize negative indices
            if actual_start < 0:
                actual_start = self._size + actual_start
            if actual_end < 0:
                actual_end = self._size + actual_end
            
            # Validate range
            validate_range(actual_start, actual_end, self._size)
            
            length = actual_end - actual_start + 1
            if length <= 1:
                return
            
            # Calculate effective shift
            effective_shift = actual_shift % length
            if effective_shift == 0:
                return
            
            # Convert left rotation to right rotation
            if not direction:
                effective_shift = length - effective_shift
            
            self._tracer.record("rotate", shift=actual_shift, start=actual_start, 
                                end=actual_end, direction=direction)
            
            # For full list rotation, we can use a more efficient approach
            if actual_start == 0 and actual_end == self._size - 1:
                self._rotate_full_list(effective_shift)
            else:
                self._rotate_subrange(actual_start, actual_end, effective_shift)


    def _rotate_full_list(self, shift: int) -> None:
        """
        Efficiently rotate the entire list by `shift` positions right.
        
        This is O(n) but uses value rotation rather than pointer manipulation
        to maintain consistency across all list types.
        """
        if shift == 0 or self._size <= 1:
            return
        
        # Get all values
        values = self._to_list_unsafe()
        
        # Rotate values
        rotated = values[-shift:] + values[:-shift]
        
        # Write back
        node = self._head
        for v in rotated:
            node.value = v  # type: ignore[union-attr]
            node = node.next  # type: ignore[assignment]


    def _rotate_subrange(self, start: int, end: int, shift: int) -> None:
        """
        Rotate a sub-range [start, end] by `shift` positions right.
        Uses value reassignment for simplicity and correctness.
        """
        # Collect nodes in range
        nodes: list = []
        node = self._node_at(start)
        for _ in range(end - start + 1):
            nodes.append(node)
            node = node.next  # type: ignore[union-attr]
        
        # Get values and rotate
        values = [n.value for n in nodes]
        rotated = values[-shift:] + values[:-shift]
        
        # Write back rotated values
        for n, v in zip(nodes, rotated):
            n.value = v

    def rotate_entire(self, shift: int) -> None:
        """Rotate entire list by shift (test compatibility wrapper)."""
        if self._size > 0:
            self.rotate(start=0, end=self._size - 1, direction=True, shift=shift)

    # ------------------------------------------------------------------ #
    # Swapping                                                             #
    # ------------------------------------------------------------------ #

    def swap(
        self,
        value1: T | None = None,
        value2: T | None = None,
        pos1: int | None = None,
        pos2: int | None = None,
        pairwise: bool = False,
    ) -> None:
        """Swap two elements or perform pairwise swapping.

        Args:
            value1, value2: Swap the first occurrences of these values.
            pos1, pos2:     Swap elements at these positions.
            pairwise:       If True, swap (0,1), (2,3), … in the whole list,
                            ignoring other arguments.

        Raises:
            ValidationError:      On invalid argument combinations.
            ValueNotFoundError:   If a value target is absent.
            IndexOutOfRangeError: If a position target is out of range.
        """
        with self._lock:
            if pairwise:
                self._pairwise_swap()
                return
            if pos1 is not None and pos2 is not None:
                i1 = pos1 if pos1 >= 0 else pos1 + self._size
                i2 = pos2 if pos2 >= 0 else pos2 + self._size
                validate_index(i1, self._size)
                validate_index(i2, self._size)
                n1, n2 = self._node_at(i1), self._node_at(i2)
                n1.value, n2.value = n2.value, n1.value
                return
            if value1 is not None and value2 is not None:
                i1 = self.index(value1)  # raises ValueNotFoundError if absent
                i2 = self.index(value2)
                n1, n2 = self._node_at(i1), self._node_at(i2)
                n1.value, n2.value = n2.value, n1.value
                return
            raise ValidationError(
                "Provide (value1, value2), (pos1, pos2), or pairwise=True."
            )

    def _pairwise_swap(self) -> None:
        cur = self._head
        while cur is not None and cur.next is not None:
            cur.value, cur.next.value = cur.next.value, cur.value
            cur = cur.next.next

    # ------------------------------------------------------------------ #
    # Merge & Sort                                                         #
    # ------------------------------------------------------------------ #

    def merge(
        self, *lists: "SinglyLinkedList[T]", sorted_merge: bool = False
    ) -> "SinglyLinkedList[T]":
        """Merge this list with one or more other lists.

        Args:
            *lists:       Other SinglyLinkedLists to merge in.
            sorted_merge: If True, the result is sorted (all inputs must be
                          pre-sorted for a correct merge-sort).

        Returns:
            A new SinglyLinkedList containing all elements.
        """
        with self._lock:
            combined: list[T] = self.to_list()
            for lst in lists:
                combined.extend(lst.to_list())
        result: SinglyLinkedList[T] = SinglyLinkedList.from_list(combined)
        if sorted_merge:
            result.sort()
        return result

    def sort(
        self,
        reverse: bool = False,
        key: Callable[[T], Any] | None = None,
    ) -> None:
        """Sort the list in place using an O(n log n) merge sort.

        Args:
            reverse: If True, sort in descending order.
            key:     Optional key function (like :func:`sorted`).
        """
        with self._lock:
            if self._size <= 1:
                return
            self._head = self._merge_sort(self._head, reverse=reverse, key=key)

    def _merge_sort(
        self,
        head: SinglyNode[T] | None,
        *,
        reverse: bool,
        key: Callable[[T], Any] | None,
    ) -> SinglyNode[T] | None:
        if head is None or head.next is None:
            return head
        mid = self._split_midpoint(head)
        assert mid is not None
        right_head = mid.next
        mid.next = None
        left = self._merge_sort(head, reverse=reverse, key=key)
        right = self._merge_sort(right_head, reverse=reverse, key=key)
        return self._merge_sorted(left, right, reverse=reverse, key=key)

    @staticmethod
    def _split_midpoint(head: SinglyNode[T]) -> SinglyNode[T]:
        slow: SinglyNode[T] = head
        fast: SinglyNode[T] | None = head.next
        while fast is not None and fast.next is not None:
            slow = slow.next  # type: ignore[assignment]
            fast = fast.next.next
        return slow

    @staticmethod
    def _merge_sorted(
        left: SinglyNode[T] | None,
        right: SinglyNode[T] | None,
        *,
        reverse: bool,
        key: Callable[[T], Any] | None,
    ) -> SinglyNode[T] | None:
        dummy: SinglyNode[Any] = SinglyNode(None)
        cur: SinglyNode[Any] = dummy

        def _key(node: SinglyNode[T]) -> Any:
            return key(node.value) if key else node.value

        while left is not None and right is not None:
            lk, rk = _key(left), _key(right)
            take_left = (lk <= rk) if not reverse else (lk >= rk)
            if take_left:
                cur.next = left
                left = left.next
            else:
                cur.next = right
                right = right.next
            cur = cur.next

        cur.next = left if left is not None else right
        return dummy.next

    def partition(
        self, predicate: Callable[[T], bool]
    ) -> "tuple[SinglyLinkedList[T], SinglyLinkedList[T]]":
        """Split into two lists based on *predicate*.

        Args:
            predicate: Callable that returns True / False for each element.

        Returns:
            ``(true_list, false_list)`` — elements for which predicate holds,
            and those for which it does not.
        """
        with self._lock:
            true_items: list[T] = []
            false_items: list[T] = []
            cur = self._head
            while cur is not None:
                if predicate(cur.value):
                    true_items.append(cur.value)
                else:
                    false_items.append(cur.value)
                cur = cur.next
        return (
            SinglyLinkedList.from_list(true_items),
            SinglyLinkedList.from_list(false_items),
        )

    # ------------------------------------------------------------------ #
    # Interview problems                                                   #
    # ------------------------------------------------------------------ #

    def detect_cycle(
        self, return_start: bool = False
    ) -> "bool | tuple[bool, Any]":
        """Detect a cycle using Floyd's tortoise-and-hare algorithm.

        This method is safe to call even if the internal structure has
        somehow been corrupted to contain a cycle.

        Args:
            return_start: If True, also returns the value at the cycle
                          entry node (or None if no cycle).

        Returns:
            ``True`` / ``False``, or ``(bool, start_value_or_None)``.
        """
        with self._lock:
            slow: SinglyNode[T] | None = self._head
            fast: SinglyNode[T] | None = self._head
            while fast is not None and fast.next is not None:
                slow = slow.next  # type: ignore[union-attr]
                fast = fast.next.next
                if slow is fast:
                    if not return_start:
                        return True
                    # Find cycle start
                    slow = self._head
                    while slow is not fast:
                        slow = slow.next  # type: ignore[union-attr]
                        fast = fast.next  # type: ignore[union-attr]
                    return True, slow.value  # type: ignore[union-attr]
            if return_start:
                return False, None
            return False

    def intersection_node(self, other: "SinglyLinkedList[T]") -> T | None:
        """Find the value at the intersection node of two lists.

        Uses length-difference technique for O(n+m) time, O(1) space.

        Args:
            other: Another SinglyLinkedList.

        Returns:
            The value at the intersection, or None if there is none.
        """
        with self._lock:
            len_a = self._size
            len_b = other._size
            cur_a: SinglyNode[T] | None = self._head
            cur_b: SinglyNode[T] | None = other._head
            # Advance the pointer of the longer list
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

    def palindrome(self) -> bool:
        """Return True if the list reads the same forwards and backwards."""
        with self._lock:
            values: list[T] = []
            cur = self._head
            while cur is not None:
                values.append(cur.value)
                cur = cur.next
            return values == values[::-1]

    def reorder(self, mode: str = "odd_even") -> None:
        """Reorder elements according to *mode*.

        Modes:
            ``"odd_even"``  — All nodes at odd indices (1, 3, 5 …) followed by
                              nodes at even indices (0, 2, 4 …).  LeetCode #328.
            ``"zigzag"``    — Elements rearranged as a₀ < a₁ > a₂ < a₃ …

        Args:
            mode: Reordering strategy.

        Raises:
            ValidationError: If *mode* is not recognised.
        """
        with self._lock:
            if mode == "odd_even":
                self._reorder_odd_even()
            elif mode == "zigzag":
                self._reorder_zigzag()
            else:
                raise ValidationError(
                    f"Unknown reorder mode {mode!r}. Choose 'odd_even' or 'zigzag'."
                )

    def _reorder_odd_even(self) -> None:
        if self._size < 3:
            return
        odd_dummy: SinglyNode[Any] = SinglyNode(None)
        even_dummy: SinglyNode[Any] = SinglyNode(None)
        odd_cur: SinglyNode[Any] = odd_dummy
        even_cur: SinglyNode[Any] = even_dummy
        cur = self._head
        idx = 0
        while cur is not None:
            nxt = cur.next
            cur.next = None
            if idx % 2 == 0:
                even_cur.next = cur
                even_cur = cur
            else:
                odd_cur.next = cur
                odd_cur = cur
            cur = nxt
            idx += 1
        even_cur.next = odd_dummy.next
        self._head = even_dummy.next

    def _reorder_zigzag(self) -> None:
        nodes: list[SinglyNode[T]] = []
        cur = self._head
        while cur is not None:
            nodes.append(cur)
            cur = cur.next
        for i in range(len(nodes) - 1):
            a, b = nodes[i].value, nodes[i + 1].value
            if i % 2 == 0:
                if a > b:  # type: ignore[operator]
                    nodes[i].value, nodes[i + 1].value = b, a
            else:
                if a < b:  # type: ignore[operator]
                    nodes[i].value, nodes[i + 1].value = b, a

    def segregate_even_odd(self) -> None:
        """
        Move all even-valued elements before odd-valued elements.
        
        Works only for integer-valued lists. Order within each group is
        preserved (stable). Non-integer values are treated as odd.
        """
        with self._lock:
            if self._size <= 1:
                return
            
            self._tracer.record("segregate_even_odd")
            
            # Collect values in order
            evens: list[T] = []
            odds: list[T] = []
            
            node = self._head
            while node is not None:
                try:
                    # Check if value is integer and even
                    if isinstance(node.value, int) and node.value % 2 == 0:
                        evens.append(node.value)
                    else:
                        odds.append(node.value)
                except (TypeError, ValueError):
                    # If can't check parity, treat as odd
                    odds.append(node.value)
                node = node.next
            
            # Combine: evens first, then odds
            all_values = evens + odds
            
            # Write back to list
            node = self._head
            for v in all_values:
                node.value = v  # type: ignore[union-attr]
                node = node.next  # type: ignore[assignment]

    # ------------------------------------------------------------------ #
    # Visualization                                                        #
    # ------------------------------------------------------------------ #

    def visualize(self, style: str = "ascii") -> str:
        """Return a string visualisation of the list.

        Args:
            style: Currently only ``"ascii"`` is supported.

        Returns:
            A human-readable string representation.
        """
        with self._lock:
            items = self.to_list()
        if style != "ascii":
            raise ValidationError(f"Unknown style {style!r}. Only 'ascii' is supported.")
        if not items:
            return "NULL (empty)"
        parts = [f"[{v!r}]" for v in items]
        return " -> ".join(parts) + " -> NULL"

    def debug(self) -> dict[str, Any]:
        """Return internal metadata for debugging."""
        with self._lock:
            return {
                "type": "SinglyLinkedList",
                "size": self._size,
                "head": repr(self._head),
                "tail": repr(self._node_at(self._size - 1)) if self._size > 0 else None,
                "values": self.to_list(),
                "tracer": self._tracer.summary(),
            }

    # ------------------------------------------------------------------ #
    # Dunder methods                                                       #
    # ------------------------------------------------------------------ #

    def __iter__(self) -> Iterator[T]:
        with self._lock:
            snapshot = self.to_list()
        return iter(snapshot)

    def __len__(self) -> int:
        return self.size()

    def __repr__(self) -> str:
        return f"SinglyLinkedList({self.to_list()!r})"

    def __contains__(self, item: object) -> bool:
        with self._lock:
            cur = self._head
            while cur is not None:
                if cur.value == item:
                    return True
                cur = cur.next
            return False

    def __getitem__(self, index: int) -> T:
        return self.get(index)

    def __setitem__(self, index: int, value: T) -> None:
        self.replace(position=index, new_value=value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SinglyLinkedList):
            return NotImplemented
        return self.to_list() == other.to_list()