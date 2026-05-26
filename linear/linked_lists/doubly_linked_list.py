"""
pkstruct/linear/linked_lists/doubly_linked_list.py

Thread-safe doubly linked list with bidirectional traversal,
tail-pointer optimization, and full pkstruct ecosystem integration.
"""
from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any, Generic, TypeVar

from pkstruct.linear.linked_lists.nodes import DoublyNode
from pkstruct.shared.debugging import DebugTracer
from pkstruct.shared.threading import StructureLock
from pkstruct.shared.serializers import deserialize_from_json, serialize_to_json
from pkstruct.shared.validators import validate_index, validate_range
from pkstruct.linear.exceptions import (
    EmptyStructureError,
    IndexOutOfRangeError,
    InvalidRangeError,
    ValidationError,
    ValueNotFoundError,
)

T = TypeVar("T")


class DoublyLinkedList(Generic[T]):
    """
    Thread-safe doubly linked list with bidirectional traversal.

    Maintains both head and tail pointers for O(1) append and efficient
    reverse-direction traversal. All mutating operations are protected by
    an internal ``StructureLock``; debug events are recorded via
    ``DebugTracer``.

    Type parameter
    --------------
    T : any hashable or comparable type stored as node values.

    Examples
    --------
    >>> dll = DoublyLinkedList.from_list([1, 2, 3])
    >>> dll.insert(0, position=0)
    >>> list(dll)
    [0, 1, 2, 3]
    >>> dll.delete(position=2)
    2
    """

    __slots__ = ("_head", "_tail", "_size", "_lock", "_tracer")

    # ------------------------------------------------------------------ #
    #  Construction helpers                                                #
    # ------------------------------------------------------------------ #

    def __init__(self) -> None:
        self._head: DoublyNode[T] | None = None
        self._tail: DoublyNode[T] | None = None
        self._size: int = 0
        self._lock: StructureLock = StructureLock()
        self._tracer: DebugTracer = DebugTracer()

    # ---------- Creation (class methods) -------------------------------- #

    @classmethod
    def create(cls) -> DoublyLinkedList[T]:
        """Return a new, empty ``DoublyLinkedList``."""
        return cls()

    @classmethod
    def from_list(cls, items: list[T]) -> DoublyLinkedList[T]:
        """
        Build a ``DoublyLinkedList`` from a Python list.

        Parameters
        ----------
        items:
            Sequence of values to insert (left to right).

        Returns
        -------
        DoublyLinkedList[T]
        """
        dll: DoublyLinkedList[T] = cls()
        for item in items:
            dll._append(item)
        return dll

    @classmethod
    def from_json(cls, json_str: str) -> DoublyLinkedList[T]:
        """
        Deserialize a ``DoublyLinkedList`` from a JSON string.

        Parameters
        ----------
        json_str:
            JSON string produced by :py:meth:`serialize_to_json`.

        Returns
        -------
        DoublyLinkedList[T]

        Raises
        ------
        SerializationError
            If the JSON string is malformed or incompatible.
        """
        items: list[T] = deserialize_from_json(json_str)
        return cls.from_list(items)

    def copy(self) -> DoublyLinkedList[T]:
        """
        Return a shallow copy of this list (values are not deep-copied).

        Returns
        -------
        DoublyLinkedList[T]
        """
        with self._lock:
            return DoublyLinkedList.from_list(self._to_list_unsafe())

    # ------------------------------------------------------------------ #
    #  Private helpers                                                     #
    # ------------------------------------------------------------------ #

    def _append(self, value: T) -> None:
        """O(1) tail append — does NOT acquire the lock."""
        new_node: DoublyNode[T] = DoublyNode(value)
        if self._tail is None:
            self._head = new_node
            self._tail = new_node
        else:
            new_node.prev = self._tail
            self._tail.next = new_node
            self._tail = new_node
        self._size += 1

    def _node_at(self, index: int) -> DoublyNode[T]:
        """
        Return the node at *index*, traversing from the nearest end.

        Raises
        ------
        IndexOutOfRangeError
        """
        validate_index(index, self._size)
        if index <= self._size // 2:
            node = self._head
            for _ in range(index):
                node = node.next  # type: ignore[union-attr]
        else:
            node = self._tail
            for _ in range(self._size - 1 - index):
                node = node.prev  # type: ignore[union-attr]
        return node  # type: ignore[return-value]

    def _insert_before_node(self, node: DoublyNode[T], value: T) -> None:
        """Insert a new node with *value* immediately before *node*."""
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
        """Insert a new node with *value* immediately after *node*."""
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

    def _remove_node(self, node: DoublyNode[T]) -> T:
        """Unlink *node* and return its value."""
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

    def _find_node(self, value: T) -> DoublyNode[T] | None:
        """Linear scan for the first node whose value equals *value*."""
        node = self._head
        while node is not None:
            if node.value == value:
                return node
            node = node.next
        return None

    def _to_list_unsafe(self) -> list[T]:
        """Build a Python list without acquiring the lock."""
        result: list[T] = []
        node = self._head
        while node is not None:
            result.append(node.value)
            node = node.next
        return result

    # ------------------------------------------------------------------ #
    #  Insertion                                                           #
    # ------------------------------------------------------------------ #

    def insert(
        self,
        value: T,
        position: int | None = None,
        before: T | None = None,
        after: T | None = None,
    ) -> None:
        """
        Insert *value* into the list.

        Exactly one of *position*, *before*, or *after* should be given.
        If none is provided the value is appended to the tail.

        Parameters
        ----------
        value:
            The value to insert.
        position:
            Zero-based index at which the new node should appear.
            Negative indices are supported (``-1`` inserts before the
            last element).
        before:
            Insert *value* immediately before the first node whose value
            equals this argument.
        after:
            Insert *value* immediately after the first node whose value
            equals this argument.

        Raises
        ------
        IndexOutOfRangeError
            When *position* is out of bounds.
        ValueNotFoundError
            When *before* or *after* refers to a value not in the list.
        ValidationError
            When more than one keyword argument is supplied.
        """
        provided = sum(x is not None for x in (position, before, after))
        if provided > 1:
            raise ValidationError(
                "Provide at most one of 'position', 'before', or 'after'."
            )

        with self._lock:
            self._tracer.record("insert", value=value, position=position,
                                before=before, after=after)

            if before is not None:
                target = self._find_node(before)
                if target is None:
                    raise ValueNotFoundError(before)
                self._insert_before_node(target, value)
                return

            if after is not None:
                target = self._find_node(after)
                if target is None:
                    raise ValueNotFoundError(after)
                self._insert_after_node(target, value)
                return

            if position is None or position == self._size or position == -1 and self._size == 0:
                # default: append
                if position is None:
                    self._append(value)
                    return

            # Normalise negative index
            if position is not None and position < 0:
                position = self._size + 1 + position  # e.g. -1 → self._size

            if position == 0:
                new_node: DoublyNode[T] = DoublyNode(value)
                new_node.next = self._head
                if self._head is not None:
                    self._head.prev = new_node
                else:
                    self._tail = new_node
                self._head = new_node
                self._size += 1
                return

            if position == self._size:
                self._append(value)
                return

            target_node = self._node_at(position)
            self._insert_before_node(target_node, value)

    def extend(self, values: list[T] | DoublyLinkedList[T]) -> None:
        """
        Append all items in *values* to the tail of this list.

        Parameters
        ----------
        values:
            A Python list or another ``DoublyLinkedList``.
        """
        with self._lock:
            self._tracer.record("extend")
            items: list[T] = (
                values._to_list_unsafe()
                if isinstance(values, DoublyLinkedList)
                else list(values)
            )
            for item in items:
                self._append(item)

    # ------------------------------------------------------------------ #
    #  Deletion                                                            #
    # ------------------------------------------------------------------ #

    def delete(
        self,
        value: T | None = None,
        position: int | None = None,
        range: tuple[int, int] | None = None,
    ) -> T | list[T] | None:
        """
        Remove and return node(s) from the list.

        Provide exactly one of *value*, *position*, or *range*.

        Parameters
        ----------
        value:
            Remove the first node whose value equals this.
        position:
            Remove the node at this zero-based index.
        range:
            A ``(start, end)`` tuple (both inclusive) of indices to
            remove.  Returns a list of removed values.

        Returns
        -------
        T
            The removed value when *value* or *position* is used.
        list[T]
            When *range* is used.

        Raises
        ------
        EmptyStructureError
        ValueNotFoundError
        IndexOutOfRangeError
        InvalidRangeError
        ValidationError
        """
        provided = sum(x is not None for x in (value, position, range))
        if provided == 0:
            raise ValidationError(
                "Provide one of 'value', 'position', or 'range'."
            )
        if provided > 1:
            raise ValidationError(
                "Provide only one of 'value', 'position', or 'range'."
            )

        with self._lock:
            if self._size == 0:
                raise EmptyStructureError("delete from an empty list")

            self._tracer.record("delete", value=value, position=position,
                                range=range)

            if value is not None:
                node = self._find_node(value)
                if node is None:
                    raise ValueNotFoundError(value)
                return self._remove_node(node)

            if position is not None:
                node = self._node_at(position)
                return self._remove_node(node)

            # range deletion
            start, end = range  # type: ignore[misc]
            validate_range(start, end, self._size)
            removed: list[T] = []
            node = self._node_at(start)
            for _ in range(end - start + 1):
                next_node = node.next
                removed.append(self._remove_node(node))
                node = next_node  # type: ignore[assignment]
            return removed

    def clear(self) -> None:
        """Remove all nodes, resetting the list to an empty state."""
        with self._lock:
            self._tracer.record("clear")
            self._head = None
            self._tail = None
            self._size = 0

    # ------------------------------------------------------------------ #
    #  Access                                                              #
    # ------------------------------------------------------------------ #

    def get(self, position: int, from_end: bool = False) -> T:
        """
        Return the value at *position* without removing it.

        Parameters
        ----------
        position:
            Zero-based index.  When *from_end* is ``True``, counts from
            the tail (``0`` → last element).
        from_end:
            Traverse from the tail instead of the head.

        Returns
        -------
        T

        Raises
        ------
        EmptyStructureError
        IndexOutOfRangeError
        """
        with self._lock:
            if self._size == 0:
                raise EmptyStructureError("get from an empty list")
            if from_end:
                validate_index(position, self._size)
                node = self._tail
                for _ in range(position):
                    node = node.prev  # type: ignore[union-attr]
                return node.value  # type: ignore[union-attr]
            return self._node_at(position).value

    def to_list(self) -> list[T]:
        """Return a Python list of all values (head → tail)."""
        with self._lock:
            return self._to_list_unsafe()

    def size(self) -> int:
        """Return the number of nodes in the list."""
        with self._lock:
            return self._size

    def is_empty(self) -> bool:
        """Return ``True`` if the list has no nodes."""
        with self._lock:
            return self._size == 0

    def count(self, value: T) -> int:
        """
        Count occurrences of *value* in the list.

        Returns
        -------
        int
        """
        with self._lock:
            total = 0
            node = self._head
            while node is not None:
                if node.value == value:
                    total += 1
                node = node.next
            return total

    # ------------------------------------------------------------------ #
    #  Search                                                              #
    # ------------------------------------------------------------------ #

    def index(self, value: T) -> int:
        """
        Return the zero-based index of the first occurrence of *value*.

        Raises
        ------
        ValueNotFoundError
        """
        with self._lock:
            node = self._head
            idx = 0
            while node is not None:
                if node.value == value:
                    return idx
                node = node.next
                idx += 1
            raise ValueNotFoundError(value)

    # ------------------------------------------------------------------ #
    #  Replacement                                                         #
    # ------------------------------------------------------------------ #

    def replace(
        self,
        old_value: T | None = None,
        new_value: T | None = None,
        position: int | None = None,
        replace_all: bool = False,
    ) -> int:
        """
        Replace node value(s) and return the count of substitutions made.

        Parameters
        ----------
        old_value:
            Value to search for (required when *position* is ``None``).
        new_value:
            Replacement value.
        position:
            When given, replace the node at this index regardless of its
            current value (*old_value* is ignored).
        replace_all:
            When ``True``, replace every occurrence of *old_value*;
            otherwise only the first.

        Returns
        -------
        int
            Number of replacements performed.

        Raises
        ------
        ValidationError
        ValueNotFoundError
        IndexOutOfRangeError
        """
        if new_value is None:
            raise ValidationError("'new_value' must be provided.")

        with self._lock:
            self._tracer.record("replace", old_value=old_value,
                                new_value=new_value, position=position)

            if position is not None:
                self._node_at(position).value = new_value
                return 1

            if old_value is None:
                raise ValidationError(
                    "Provide either 'position' or 'old_value'."
                )

            count = 0
            node = self._head
            while node is not None:
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
    #  Reverse & Rotation                                                  #
    # ------------------------------------------------------------------ #

    def reverse(
        self,
        start: int | None = None,
        end: int | None = None,
    ) -> None:
        """
        Reverse the list in-place, or reverse a sub-range [start, end].

        A full reverse also swaps ``_head`` and ``_tail``.

        Parameters
        ----------
        start:
            Inclusive start index (default ``0``).
        end:
            Inclusive end index (default ``self._size - 1``).

        Raises
        ------
        EmptyStructureError
        InvalidRangeError
        """
        with self._lock:
            if self._size == 0:
                raise EmptyStructureError("reverse an empty list")

            lo = 0 if start is None else start
            hi = self._size - 1 if end is None else end
            validate_range(lo, hi, self._size)

            self._tracer.record("reverse", start=lo, end=hi)

            left = self._node_at(lo)
            right = self._node_at(hi)

            while left is not right and left is not right.next:
                left.value, right.value = right.value, left.value
                left = left.next   # type: ignore[assignment]
                right = right.prev  # type: ignore[assignment]

    def rotate(self, shift: int) -> None:
        """
        Rotate entire list by shift positions (simple interface for tests).
        
        Args:
            shift: Number of positions to rotate right (positive) or left (negative)
        """
        if self._size == 0:
            raise EmptyStructureError("rotate an empty list")
        
        if shift == 0:
            return
        
        # Convert negative shift to left rotation
        direction = True  # True = right rotation
        actual_shift = shift
        if shift < 0:
            actual_shift = abs(shift)
            direction = False
        
        # Call the full rotate method
        self.rotate_full(start=0, end=self._size - 1, direction=direction, shift=actual_shift)


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
    #  Swapping                                                            #
    # ------------------------------------------------------------------ #

    def swap(
        self,
        value1: T | None = None,
        value2: T | None = None,
        pos1: int | None = None,
        pos2: int | None = None,
        pairwise: bool = False,
    ) -> None:
        """
        Swap nodes by value, position, or pairwise across the whole list.

        Modes (mutually exclusive):

        * **value swap** – supply *value1* and *value2*.
        * **position swap** – supply *pos1* and *pos2*.
        * **pairwise** – set ``pairwise=True`` to swap adjacent pairs
          (index 0↔1, 2↔3, …).

        Raises
        ------
        EmptyStructureError
        ValueNotFoundError
        IndexOutOfRangeError
        ValidationError
        """
        with self._lock:
            if self._size == 0:
                raise EmptyStructureError("swap in an empty list")

            self._tracer.record("swap", value1=value1, value2=value2,
                                pos1=pos1, pos2=pos2, pairwise=pairwise)

            if pairwise:
                node = self._head
                while node is not None and node.next is not None:
                    node.value, node.next.value = node.next.value, node.value
                    node = node.next.next
                return

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
                n1 = self._node_at(pos1)
                n2 = self._node_at(pos2)
                n1.value, n2.value = n2.value, n1.value
                return

            raise ValidationError(
                "Provide (value1, value2), (pos1, pos2), or pairwise=True."
            )

    # ------------------------------------------------------------------ #
    #  Merge & Sort                                                        #
    # ------------------------------------------------------------------ #

    def merge(
        self,
        *lists: DoublyLinkedList[T],
        sorted_merge: bool = False,
    ) -> DoublyLinkedList[T]:
        """
        Return a new ``DoublyLinkedList`` that concatenates *self* and
        every list in *lists*.

        Parameters
        ----------
        *lists:
            One or more ``DoublyLinkedList`` instances to merge in.
        sorted_merge:
            When ``True``, assume all input lists are already sorted and
            perform a k-way merge (values must be comparable).

        Returns
        -------
        DoublyLinkedList[T]
        """
        with self._lock:
            self._tracer.record("merge", count=len(lists))
            all_values: list[T] = self._to_list_unsafe()

        for other in lists:
            with other._lock:
                all_values.extend(other._to_list_unsafe())

        if sorted_merge:
            all_values.sort()  # type: ignore[type-var]

        return DoublyLinkedList.from_list(all_values)

    def sort(
        self,
        reverse: bool = False,
        key: Callable[[T], Any] | None = None,
    ) -> None:
        """
        Sort the list in-place using an adaptive merge sort.

        Parameters
        ----------
        reverse:
            Descending order when ``True``.
        key:
            Single-argument function used to extract a comparison key.
        """
        with self._lock:
            if self._size <= 1:
                return
            self._tracer.record("sort", reverse=reverse)
            values = self._to_list_unsafe()
            values.sort(key=key, reverse=reverse)  # type: ignore[type-var]
            node = self._head
            for v in values:
                node.value = v   # type: ignore[union-attr]
                node = node.next  # type: ignore[assignment]

    def partition(
        self,
        predicate: Callable[[T], bool],
    ) -> tuple[DoublyLinkedList[T], DoublyLinkedList[T]]:
        """
        Split the list into two new lists based on *predicate*.

        Returns
        -------
        tuple[DoublyLinkedList[T], DoublyLinkedList[T]]
            ``(true_list, false_list)`` — nodes that satisfy the
            predicate and nodes that do not.
        """
        with self._lock:
            self._tracer.record("partition")
            true_list: DoublyLinkedList[T] = DoublyLinkedList()
            false_list: DoublyLinkedList[T] = DoublyLinkedList()
            node = self._head
            while node is not None:
                if predicate(node.value):
                    true_list._append(node.value)
                else:
                    false_list._append(node.value)
                node = node.next
            return true_list, false_list

    # ------------------------------------------------------------------ #
    #  Interview Problems                                                  #
    # ------------------------------------------------------------------ #

    def detect_cycle(
        self, return_start: bool = False
    ) -> bool | tuple[bool, Any]:
        """
        Floyd's cycle-detection algorithm.

        DoublyLinkedList by construction cannot have a cycle (every
        ``_append`` sets a fresh node), but this method detects any
        manually-introduced cycle and optionally returns the cycle entry
        node value.

        Parameters
        ----------
        return_start:
            When ``True``, return ``(has_cycle, entry_value)`` where
            *entry_value* is the value of the node at the cycle start, or
            ``None`` if there is no cycle.

        Returns
        -------
        bool | tuple[bool, Any]
        """
        with self._lock:
            slow = self._head
            fast = self._head
            has_cycle = False
            while fast is not None and fast.next is not None:
                slow = slow.next        # type: ignore[union-attr]
                fast = fast.next.next
                if slow is fast:
                    has_cycle = True
                    break

            if not return_start:
                return has_cycle

            if not has_cycle:
                return False, None

            # Find cycle entry
            slow = self._head
            while slow is not fast:
                slow = slow.next  # type: ignore[union-attr]
                fast = fast.next  # type: ignore[union-attr]
            return True, slow.value  # type: ignore[union-attr]

    def palindrome(self) -> bool:
        """
        Return ``True`` if the list reads the same forwards and backwards.

        Uses the bidirectional pointers for an O(n) comparison without
        extra memory (beyond two traversal pointers).
        """
        with self._lock:
            if self._size <= 1:
                return True
            left = self._head
            right = self._tail
            steps = self._size // 2
            for _ in range(steps):
                if left.value != right.value:  # type: ignore[union-attr]
                    return False
                left = left.next    # type: ignore[union-attr]
                right = right.prev  # type: ignore[union-attr]
            return True

    def reorder(self, mode: str = "odd_even") -> None:
        """
        Reorder nodes in-place according to *mode*.

        Modes
        -----
        ``"odd_even"``
            All odd-indexed nodes first, then even-indexed nodes
            (0-based: indices 1, 3, 5, … then 0, 2, 4, …).

        Raises
        ------
        ValidationError
            If *mode* is unrecognised.
        """
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
                    node.value = v  # type: ignore[union-attr]
                    node = node.next  # type: ignore[assignment]
            else:
                raise ValidationError(
                    f"Unknown reorder mode: '{mode}'. Supported: 'odd_even'."
                )

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
    #  Serialization                                                       #
    # ------------------------------------------------------------------ #

    def to_json(self) -> str:
        """
        Serialize the list to a JSON string.

        Returns
        -------
        str
        """
        with self._lock:
            return serialize_to_json(self._to_list_unsafe())
    def serialize(self) -> str:
        """Alias for to_json() for test compatibility."""
        return self.to_json()

    def deserialize(self, json_str: str) -> None:
        """Alias for from_json() for test compatibility."""
        new_list = self.from_json(json_str)
        self.clear()
        for v in new_list.to_list():
            self.insert(v)

    # ------------------------------------------------------------------ #
    #  Visualization                                                       #
    # ------------------------------------------------------------------ #

    def visualize(self, style: str = "ascii") -> str:
        """
        Return a human-readable string representation of the list.

        Parameters
        ----------
        style:
            ``"ascii"`` (default) – ``None <- v1 <-> v2 -> None``.
            ``"simple"`` – comma-separated values.

        Returns
        -------
        str
        """
        with self._lock:
            if self._size == 0:
                return "None <- (empty) -> None"

            values = self._to_list_unsafe()

            if style == "simple":
                return ", ".join(str(v) for v in values)

            inner = " <-> ".join(str(v) for v in values)
            return f"None <- {inner} -> None"

    def debug(self) -> dict[str, Any]:
        """
        Return a snapshot of internal state for debugging.

        Returns
        -------
        dict[str, Any]
            Keys: ``size``, ``head``, ``tail``, ``values``, ``events``.
        """
        with self._lock:
            return {
                "size": self._size,
                "head": self._head.value if self._head else None,
                "tail": self._tail.value if self._tail else None,
                "values": self._to_list_unsafe(),
                "events": self._tracer.get_events(),
            }

    # ------------------------------------------------------------------ #
    #  Dunder methods                                                      #
    # ------------------------------------------------------------------ #

    def __iter__(self) -> Iterator[T]:
        """Yield values from head to tail."""
        with self._lock:
            node = self._head
            values: list[T] = []
            while node is not None:
                values.append(node.value)
                node = node.next
        yield from values

    def __len__(self) -> int:
        """Return the number of nodes."""
        with self._lock:
            return self._size

    def __repr__(self) -> str:
        with self._lock:
            values = self._to_list_unsafe()
        return f"DoublyLinkedList({values!r})"

    def __contains__(self, item: object) -> bool:
        with self._lock:
            return self._find_node(item) is not None  # type: ignore[arg-type]

    def __getitem__(self, index: int) -> T:
        with self._lock:
            if self._size == 0:
                raise EmptyStructureError("__getitem__ on an empty list")
            return self._node_at(index).value

    def __setitem__(self, index: int, value: T) -> None:
        with self._lock:
            if self._size == 0:
                raise EmptyStructureError("__setitem__ on an empty list")
            self._node_at(index).value = value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DoublyLinkedList):
            return NotImplemented
        with self._lock:
            self_vals = self._to_list_unsafe()
        with other._lock:
            other_vals = other._to_list_unsafe()
        return self_vals == other_vals
