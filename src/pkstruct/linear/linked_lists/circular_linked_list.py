"""
pkstruct.linear.linked_lists.circular_linked_list

Thread-safe circular linked list where the tail node's ``next`` pointer
always points back to the head, forming a closed ring.  A sentinel
``CircularNode`` is used (see nodes.py).

Structural invariant
--------------------
* Empty  : ``_head is None``, ``_tail is None``, ``_size == 0``
* Size 1 : ``_head is _tail``, ``_head.next is _head``
* Size n : ``_tail.next is _head`` at all times

All mutating operations acquire ``self._lock`` (a ``StructureLock``).
Debug events are recorded via ``DebugTracer``.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any, Generic, TypeVar

from pkstruct.linear.linked_lists.nodes import CircularNode
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


class CircularLinkedList(Generic[T]):
    """
    Thread-safe singly-circular linked list.

    The list is stored as a ring: ``tail.next`` always references
    ``head``.  Maintaining a ``_tail`` pointer gives O(1) append *and*
    O(1) prepend (head is just ``_tail.next``).

    Type parameter
    --------------
    T : any type stored as node values.

    Examples
    --------
    >>> cll = CircularLinkedList.from_list([1, 2, 3])
    >>> cll.insert(0, position=0)
    >>> list(cll)
    [0, 1, 2, 3]
    >>> cll.delete(position=1)
    1
    >>> cll.visualize()
    '0 -> 2 -> 3 -> (back to 0)'
    """

    __slots__ = ("_head", "_tail", "_size", "_lock", "_tracer")

    # ------------------------------------------------------------------ #
    #  Initialisation                                                      #
    # ------------------------------------------------------------------ #

    def __init__(self) -> None:
        self._head: CircularNode[T] | None = None
        self._tail: CircularNode[T] | None = None
        self._size: int = 0
        self._lock: StructureLock = StructureLock()
        self._tracer: DebugTracer = DebugTracer()

    # ------------------------------------------------------------------ #
    #  Creation (class methods)                                            #
    # ------------------------------------------------------------------ #

    @classmethod
    def create(cls) -> CircularLinkedList[T]:
        """Return a new, empty ``CircularLinkedList``."""
        return cls()

    @classmethod
    def from_list(cls, items: list[T]) -> CircularLinkedList[T]:
        """
        Build a ``CircularLinkedList`` from a Python list.

        Parameters
        ----------
        items:
            Sequence of values inserted left-to-right (first item
            becomes the head).

        Returns
        -------
        CircularLinkedList[T]
        """
        cll: CircularLinkedList[T] = cls()
        for item in items:
            cll._append(item)
        return cll

    @classmethod
    def from_json(cls, json_str: str) -> CircularLinkedList[T]:
        """
        Deserialise a ``CircularLinkedList`` from a JSON string produced
        by :py:meth:`to_json`.

        Raises
        ------
        SerializationError
        """
        items: list[T] = deserialize_from_json(json_str)
        return cls.from_list(items)

    def copy(self) -> CircularLinkedList[T]:
        """Return a shallow copy (values are not deep-copied)."""
        with self._lock:
            return CircularLinkedList.from_list(self._to_list_unsafe())

    # ------------------------------------------------------------------ #
    #  Private helpers                                                     #
    # ------------------------------------------------------------------ #

    def _append(self, value: T) -> None:
        """O(1) tail-append.  Does NOT acquire the lock."""
        new_node: CircularNode[T] = CircularNode(value)
        if self._tail is None:
            # First node: points to itself
            new_node.next = new_node
            self._head = new_node
            self._tail = new_node
        else:
            new_node.next = self._head  # close the ring
            self._tail.next = new_node  # old tail → new node
            self._tail = new_node  # advance tail
        self._size += 1

    def _prepend(self, value: T) -> None:
        """O(1) head-prepend.  Does NOT acquire the lock."""
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
        """
        Return the node at *index* (0-based), traversing from head.

        Raises
        ------
        IndexOutOfRangeError
        """
        validate_index(index, self._size)
        node = self._head
        for _ in range(index):
            node = node.next  # type: ignore[union-attr]
        return node  # type: ignore[return-value]

    def _node_before(self, target: CircularNode[T]) -> CircularNode[T]:
        """Return the node immediately preceding *target* in the ring."""
        node = self._tail
        while node.next is not target:  # type: ignore[union-attr]
            node = node.next  # type: ignore[union-attr]
        return node  # type: ignore[return-value]

    def _find_node(self, value: object) -> CircularNode[T] | None:
        """Linear scan; returns the first node whose value equals *value*."""
        if self._head is None:
            return None
        node = self._head
        for _ in range(self._size):
            if node.value == value:
                return node
            node = node.next  # type: ignore[union-attr]
        return None

    def _remove_node(self, node: CircularNode[T]) -> T:
        """
        Unlink *node* from the ring and return its value.
        Updates ``_head`` / ``_tail`` as required.
        """
        if self._size == 1:
            # Only node
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

    def _to_list_unsafe(self) -> list[T]:
        """Snapshot to a plain list without acquiring the lock."""
        if self._head is None:
            return []
        result: list[T] = []
        node = self._head
        for _ in range(self._size):  # KEY: bounded by size
            result.append(node.value)
            node = node.next  # type: ignore[union-attr]
        return result

    # ------------------------------------------------------------------ #
    #  Insertion                                                           #
    # ------------------------------------------------------------------ #

    def _insert_original(
        self,
        value: T,
        position: int | None = None,
        before: T | None = None,
        after: T | None = None,
    ) -> None:
        """
        Insert *value* into the ring.

        Provide **at most one** of *position*, *before*, or *after*.
        With no keyword argument the value is appended to the tail.

        Parameters
        ----------
        value:
            The value to insert.
        position:
            Zero-based index at which the new node should appear.
            Supports negative indices (``-1`` → before the last node).
        before:
            Insert immediately before the first node matching this value.
        after:
            Insert immediately after the first node matching this value.

        Raises
        ------
        ValidationError
            More than one keyword argument supplied.
        ValueNotFoundError
            *before* / *after* value not present.
        IndexOutOfRangeError
            *position* out of ``[0, size]``.
        """
        provided = sum(x is not None for x in (position, before, after))
        if provided > 1:
            raise ValidationError("Provide at most one of 'position', 'before', or 'after'.")

        with self._lock:
            self._tracer.record(
                "insert", value=value, position=position, before=before, after=after
            )

            # --- before / after shortcuts ---
            if before is not None:
                target = self._find_node(before)
                if target is None:
                    raise ValueNotFoundError(before)
                # insert before target == insert after target's predecessor
                if target is self._head:
                    self._prepend(value)
                else:
                    prev = self._node_before(target)
                    new_node: CircularNode[T] = CircularNode(value)
                    new_node.next = target
                    prev.next = new_node
                    self._size += 1
                return

            if after is not None:
                target = self._find_node(after)
                if target is None:
                    raise ValueNotFoundError(after)
                new_node = CircularNode(value)
                new_node.next = target.next
                target.next = new_node
                if target is self._tail:
                    self._tail = new_node
                self._size += 1
                return

            # --- positional insert ---
            if position is None:
                self._append(value)
                return

            # Normalise negative index: -1 → size (append), -2 → size-1, …
            if position < 0:
                raise IndexOutOfRangeError(position, self._size)

            if position <= 0:
                self._prepend(value)
                return

            if position > self._size:
                raise IndexOutOfRangeError(position, self._size)
            if position == self._size:
                self._append(value)
                return

            # General case: insert before node at `position`
            pred = self._node_at(position - 1)
            new_node = CircularNode(value)
            new_node.next = pred.next
            pred.next = new_node
            self._size += 1

    def insert(self, *args, **kwargs):
        if kwargs:
            if len(args) == 1:
                kwargs.setdefault("value", args[0])
            elif len(args) == 2:
                kwargs.setdefault("position", args[0])
                kwargs.setdefault("value", args[1])
            self._insert_original(**kwargs)
        elif len(args) == 1:
            self._insert_original(value=args[0])
        elif len(args) == 2 and isinstance(args[0], int):
            pos, val = args
            self._insert_original(value=val, position=pos)
        else:
            self._insert_original(*args)

    def extend(self, values: list[T] | CircularLinkedList[T]) -> None:
        """
        Append every item in *values* to the tail.

        Parameters
        ----------
        values:
            A Python list or another ``CircularLinkedList``.
        """
        with self._lock:
            self._tracer.record("extend")
            items: list[T] = (
                values._to_list_unsafe() if isinstance(values, CircularLinkedList) else list(values)
            )
            for item in items:
                self._append(item)

    # ------------------------------------------------------------------ #
    #  Deletion                                                            #
    # ------------------------------------------------------------------ #

    def _delete_original(
        self,
        value: T | None = None,
        position: int | None = None,
        rng: tuple[int, int] | None = None,
    ) -> T | list[T] | None:
        """
        Remove and return node(s) from the ring.

        Provide **exactly one** of *value*, *position*, or *rng*.

        Parameters
        ----------
        value:
            Remove the first node whose value equals this.
        position:
            Remove the node at this zero-based index.
        rng:
            ``(start, end)`` inclusive index range.  Returns a list.

        Returns
        -------
        T
            When *value* or *position* is used.
        list[T]
            When *rng* is used.

        Raises
        ------
        EmptyStructureError, ValueNotFoundError,
        IndexOutOfRangeError, InvalidRangeError, ValidationError
        """
        provided = sum(x is not None for x in (value, position, rng))
        if provided == 0:
            raise ValidationError("Provide one of 'value', 'position', or 'range'.")
        if provided > 1:
            raise ValidationError("Provide only one of 'value', 'position', or 'range'.")

        with self._lock:
            if self._size == 0:
                raise EmptyStructureError("delete from an empty list")

            self._tracer.record("delete", value=value, position=position, rng=rng)

            if value is not None:
                node = self._find_node(value)
                if node is None:
                    raise ValueNotFoundError(value)
                return self._remove_node(node)

            if position is not None:
                node = self._node_at(position)
                return self._remove_node(node)

            # range deletion
            start, end = rng
            validate_range(start, end, self._size)
            removed: list[T] = []
            # collect nodes first to avoid pointer confusion during removal
            nodes_to_remove = []
            node = self._node_at(start)
            for _ in range(end - start + 1):
                nodes_to_remove.append(node)
                node = node.next  # type: ignore[union-attr]
            for n in nodes_to_remove:
                removed.append(self._remove_node(n))
            return removed

    def delete(self, *args, **kwargs):
        if kwargs:
            return self._delete_original(**kwargs)
        if len(args) == 1:
            arg = args[0]
            if isinstance(arg, int):
                return self._delete_original(position=arg)
            else:
                return self._delete_original(value=arg)
        elif len(args) == 2:
            start, end = args
            return self._delete_original(rng=(start, end))
        else:
            return self._delete_original(*args)

    def clear(self) -> None:
        """Remove all nodes and reset the ring to an empty state."""
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
            Zero-based index.  When *from_end* is ``True`` counts from
            the tail (``0`` → last element).

        Raises
        ------
        EmptyStructureError, IndexOutOfRangeError
        """
        with self._lock:
            if self._size == 0:
                raise EmptyStructureError("get from an empty list")
            if from_end:
                if position < 0:
                    raise IndexOutOfRangeError(position, self._size)
                validate_index(position, self._size)
                # walk backward by (size - 1 - position) steps from head
                actual = self._size - 1 - position
                return self._node_at(actual).value
            if position < 0:
                raise IndexOutOfRangeError(position, self._size)
            return self._node_at(position).value

    def to_list(self) -> list[T]:
        """Return a Python list of all values (head → … → tail)."""
        with self._lock:
            return self._to_list_unsafe()

    def size(self) -> int:
        """Return the number of nodes."""
        with self._lock:
            return self._size

    def is_empty(self) -> bool:
        """Return ``True`` if the ring has no nodes."""
        with self._lock:
            return self._size == 0

    def count(self, value: T) -> int:
        """Count occurrences of *value* in the ring."""
        with self._lock:
            total = 0
            if self._head is None:
                return total
            node = self._head
            for _ in range(self._size):
                if node.value == value:
                    total += 1
                node = node.next  # type: ignore[union-attr]
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
            for i in range(self._size):
                if node.value == value:  # type: ignore[union-attr]
                    return i
                node = node.next  # type: ignore[union-attr]
            raise ValueNotFoundError(value)

    # ------------------------------------------------------------------ #
    #  Replacement                                                         #
    # ------------------------------------------------------------------ #

    def _replace_original(
        self,
        old_value: T | None = None,
        new_value: T | None = None,
        position: int | None = None,
        replace_all: bool = False,
    ) -> int:
        if new_value is None:
            raise ValidationError("'new_value' must be provided.")
        with self._lock:
            self._tracer.record(
                "replace", old_value=old_value, new_value=new_value, position=position
            )
            if position is not None:
                self._node_at(position).value = new_value
                return 1
            if old_value is None:
                raise ValidationError("Provide either 'position' or 'old_value'.")
            count = 0
            node = self._head
            for _ in range(self._size):
                if node.value == old_value:  # type: ignore[union-attr]
                    node.value = new_value  # type: ignore[union-attr]
                    count += 1
                    if not replace_all:
                        break
                node = node.next  # type: ignore[union-attr]
            if count == 0:
                raise ValueNotFoundError(old_value)
            return count

    def replace(self, *args, **kwargs):
        if kwargs:
            return self._replace_original(**kwargs)
        if len(args) == 2:
            a, b = args
            if isinstance(a, int):
                return self._replace_original(position=a, new_value=b)
            else:
                return self._replace_original(old_value=a, new_value=b)
        return self._replace_original(*args)

    # ------------------------------------------------------------------ #
    #  Reverse & Rotation                                                  #
    # ------------------------------------------------------------------ #

    def reverse(
        self,
        start: int | None = None,
        end: int | None = None,
    ) -> None:
        """
        Reverse the ring in-place, or reverse a sub-range [start, end].

        For a full reverse the ``_head`` / ``_tail`` pointers are
        swapped and all ``next`` links are re-wired.

        Parameters
        ----------
        start:
            Inclusive start index (default ``0``).
        end:
            Inclusive end index (default ``self._size - 1``).

        Raises
        ------
        EmptyStructureError, InvalidRangeError
        """
        with self._lock:
            if self._size == 0:
                raise EmptyStructureError("reverse an empty list")

            lo = 0 if start is None else start
            hi = self._size - 1 if end is None else end
            validate_range(lo, hi, self._size)
            self._tracer.record("reverse", start=lo, end=hi)

            if lo == hi:
                return

            # Collect only the values in range and swap in-place
            # (avoids full pointer re-wiring complexity for sub-ranges)
            nodes: list[CircularNode[T]] = []
            node = self._node_at(lo)
            for _ in range(hi - lo + 1):
                nodes.append(node)
                node = node.next  # type: ignore[union-attr]

            left, right = 0, len(nodes) - 1
            while left < right:
                nodes[left].value, nodes[right].value = (
                    nodes[right].value,
                    nodes[left].value,
                )
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

            self._tracer.record(
                "rotate", start=start, end=end, direction=direction, shift=effective_shift
            )

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

            self._tracer.record(
                "rotate",
                shift=actual_shift,
                start=actual_start,
                end=actual_end,
                direction=direction,
            )

            # For full list rotation, we can use a more efficient approach
            if actual_start == 0 and actual_end == self._size - 1:
                self._rotate_full_list(effective_shift)
            else:
                self._rotate_subrange(actual_start, actual_end, effective_shift)

    def _rotate_full_list(self, shift: int) -> None:
        if shift == 0 or self._size <= 1:
            return
        steps = (self._size - shift) % self._size
        for _ in range(steps):
            self._head = self._head.next
            self._tail = self._tail.next

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
    #  Circular-specific: rotate head                                      #
    # ------------------------------------------------------------------ #

    def rotate_head(self, steps: int = 1, direction: bool = True) -> None:
        """
        Advance (or retreat) the head pointer by *steps* positions **in
        O(steps)** without copying any values — a uniquely circular
        operation.

        Parameters
        ----------
        steps:
            How many positions to move the head pointer.
        direction:
            ``True`` → move head forward (clockwise).
            ``False`` → move head backward (counter-clockwise, i.e.
            advance by ``size - steps``).

        Raises
        ------
        EmptyStructureError
        """
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
                self._tail = self._head  # type: ignore[assignment]
                self._head = self._head.next  # type: ignore[union-attr]

    # ------------------------------------------------------------------ #
    #  Swapping                                                            #
    # ------------------------------------------------------------------ #

    def _swap_original(
        self,
        value1: T | None = None,
        value2: T | None = None,
        pos1: int | None = None,
        pos2: int | None = None,
        pairwise: bool = False,
    ) -> None:
        """
        Swap nodes by value, by position, or pairwise across the ring.

        Modes (mutually exclusive):

        * **value swap** – supply *value1* and *value2*.
        * **position swap** – supply *pos1* and *pos2*.
        * **pairwise** – set ``pairwise=True`` to swap adjacent pairs
        (index 0↔1, 2↔3, …).

        Raises
        ------
        EmptyStructureError, ValueNotFoundError,
        IndexOutOfRangeError, ValidationError
        """
        with self._lock:
            if self._size == 0:
                raise EmptyStructureError("swap in an empty list")

            self._tracer.record(
                "swap", value1=value1, value2=value2, pos1=pos1, pos2=pos2, pairwise=pairwise
            )

            if pairwise:
                node = self._head
                for _ in range(self._size // 2):
                    node.value, node.next.value = (  # type: ignore[union-attr]
                        node.next.value,  # type: ignore[union-attr]
                        node.value,
                    )
                    node = node.next.next  # type: ignore[union-attr]
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

            raise ValidationError("Provide (value1, value2), (pos1, pos2), or pairwise=True.")

    def swap(self, *args, **kwargs):
        if kwargs:
            self._swap_original(**kwargs)
            return
        if len(args) == 1:
            self._swap_original(pairwise=True)
        elif len(args) == 2:
            a, b = args
            if isinstance(a, int) and isinstance(b, int):
                self._swap_original(pos1=a, pos2=b)
            else:
                self._swap_original(value1=a, value2=b)

    # ------------------------------------------------------------------ #
    #  Merge & Sort                                                        #
    # ------------------------------------------------------------------ #

    def merge(self, *others):
        with self._lock:
            for other in others:
                with other._lock:
                    values = other._to_list_unsafe()
                    for v in values:
                        self._append(v)

    def sort(
        self,
        reverse: bool = False,
        key: Callable[[T], Any] | None = None,
    ) -> None:
        """
        Sort the ring in-place (values reassigned; node structure
        unchanged).

        Parameters
        ----------
        reverse:
            Descending order when ``True``.
        key:
            Single-argument comparison-key extractor.
        """
        with self._lock:
            if self._size <= 1:
                return
            self._tracer.record("sort", reverse=reverse)
            values = self._to_list_unsafe()
            values.sort(key=key, reverse=reverse)  # type: ignore[type-var]
            node = self._head
            for v in values:
                node.value = v  # type: ignore[union-attr]
                node = node.next  # type: ignore[assignment]

    def partition(self, predicate_or_pivot):
        with self._lock:
            if self._size <= 1:
                return
            if callable(predicate_or_pivot):
                pred = predicate_or_pivot
            else:
                pivot = predicate_or_pivot
                pred = lambda x: x < pivot
            values = self._to_list_unsafe()
            left = [v for v in values if pred(v)]
            right = [v for v in values if not pred(v)]
            new_values = left + right
            node = self._head
            for v in new_values:
                node.value = v
                node = node.next

    # ------------------------------------------------------------------ #
    #  Interview Problems                                                  #
    # ------------------------------------------------------------------ #

    def detect_cycle(self, return_start: bool = False) -> bool | tuple[bool, Any]:
        """
        Verify that the circular invariant holds and, optionally, return
        the entry node value.

        A well-formed ``CircularLinkedList`` always has a cycle
        (``tail.next is head``).  This method confirms the invariant
        using Floyd's algorithm — useful for spotting corruption where
        a ``next`` pointer was accidentally set to ``None``.

        Parameters
        ----------
        return_start:
            When ``True`` return ``(has_cycle, entry_value)``.

        Returns
        -------
        bool | tuple[bool, Any]
        """
        with self._lock:
            if self._head is None:
                return (False, None) if return_start else False

            slow = self._head
            fast = self._head
            has_cycle = False
            # Use size as a bound to avoid infinite loop on a valid ring
            max_steps = self._size * 2
            for _ in range(max_steps):
                if fast.next is None or fast.next.next is None:
                    break
                slow = slow.next  # type: ignore[union-attr]
                fast = fast.next.next  # type: ignore[union-attr]
                if slow is fast:
                    has_cycle = True
                    break

            if not return_start:
                return has_cycle

            if not has_cycle:
                return False, None

            slow = self._head
            while slow is not fast:
                slow = slow.next  # type: ignore[union-attr]
                fast = fast.next  # type: ignore[union-attr]
            return True, slow.value  # type: ignore[union-attr]

    def palindrome(self) -> bool:
        with self._lock:
            if self._size == 0:
                raise EmptyStructureError("palindrome on empty list")
            if self._size <= 1:
                return True
            values = self._to_list_unsafe()
            return values == values[::-1]

    def reorder(self, mode: str = "odd_even") -> None:
        """
        Reorder nodes in-place according to *mode*.

        Modes
        -----
        ``"odd_even"``
            Odd-indexed nodes first, then even-indexed (0-based indexing,
            so indices 1, 3, 5, … precede 0, 2, 4, …).

        Raises
        ------
        ValidationError
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
                raise ValidationError(f"Unknown reorder mode: '{mode}'. Supported: 'odd_even'.")

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

            # Collect values in order - MUST use size bound, not None check
            evens: list[T] = []
            odds: list[T] = []

            node = self._head
            for _ in range(self._size):  # KEY FIX: use size bound, not while node is not None
                try:
                    # Check if value is integer and even
                    if isinstance(node.value, int) and node.value % 2 == 0:
                        evens.append(node.value)
                    else:
                        odds.append(node.value)
                except (TypeError, ValueError):
                    # If can't check parity, treat as odd
                    odds.append(node.value)
                node = node.next  # type: ignore[union-attr]

            # Combine: evens first, then odds
            all_values = evens + odds

            # Write back to list - also use size bound
            node = self._head
            for v in all_values:
                node.value = v  # type: ignore[union-attr]
                node = node.next  # type: ignore[assignment]

    # ------------------------------------------------------------------ #
    #  Josephus problem (circular-unique)                                  #
    # ------------------------------------------------------------------ #

    def josephus(self, step: int) -> T:
        """
        Simulate the Josephus elimination problem on the ring and return
        the value of the last surviving node.

        Starting from the head, every *step*-th node is eliminated until
        one remains.  The original list is **consumed** (all nodes
        removed).

        Parameters
        ----------
        step:
            Counting interval (must be >= 1).

        Returns
        -------
        T
            Value of the surviving node.

        Raises
        ------
        EmptyStructureError
        ValidationError
            If *step* < 1.
        """
        with self._lock:
            if self._size == 0:
                raise EmptyStructureError("josephus on an empty list")
            if step < 1:
                raise ValidationError("'step' must be >= 1.")

            self._tracer.record("josephus", step=step)

            current = self._head
            while self._size > 1:
                # Advance step-1 more nodes
                for _ in range(step - 1):
                    current = current.next  # type: ignore[union-attr]
                next_node = current.next  # type: ignore[union-attr]
                self._remove_node(current)  # type: ignore[arg-type]
                current = next_node

            survivor = self._head.value  # type: ignore[union-attr]
            self.clear()
            return survivor

    # ------------------------------------------------------------------ #
    #  Serialisation                                                       #
    # ------------------------------------------------------------------ #

    def to_json(self) -> str:
        """Serialise the ring to a JSON string (head → tail order)."""
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
        Return a human-readable string representation.

        Parameters
        ----------
        style:
            ``"ascii"`` (default) –
                ``v1 -> v2 -> v3 -> (back to v1)``
            ``"simple"`` – comma-separated values.
            ``"ring"`` – closes the ring explicitly with an arrow back:
                ``[v1] -> [v2] -> [v3] -> ↺``

        Returns
        -------
        str
        """
        with self._lock:
            if self._size == 0:
                return "(empty circular list)"

            values = self._to_list_unsafe()

            if style == "simple":
                return ", ".join(str(v) for v in values)

            if style == "ring":
                nodes_str = " -> ".join(f"[{v}]" for v in values)
                return f"{nodes_str} -> ↺"

            # default "ascii"
            inner = " -> ".join(str(v) for v in values)
            return f"{inner} -> (back to head)"

    def debug(self) -> dict[str, Any]:
        """
        Return a snapshot of internal state for debugging.

        Returns
        -------
        dict[str, Any]
            Keys: ``size``, ``head``, ``tail``, ``tail_next``,
            ``invariant_ok``, ``values``, ``events``.
        """
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

    # ------------------------------------------------------------------ #
    #  Public properties for testing compatibility                        #
    # ------------------------------------------------------------------ #

    @property
    def head(self):
        """Return the head node (for testing compatibility)."""
        with self._lock:
            return self._head

    @property
    def tail(self):
        """Return the tail node (for testing compatibility)."""
        with self._lock:
            return self._tail

    # ------------------------------------------------------------------ #
    #  Dunder methods                                                      #
    # ------------------------------------------------------------------ #

    def __iter__(self) -> Iterator[T]:
        """Yield values from head around the ring, stopping after size steps."""
        with self._lock:
            if self._head is None:
                return
            node = self._head
            for _ in range(self._size):  # KEY: bounded by size
                yield node.value
                node = node.next  # type: ignore[union-attr]

    def __len__(self) -> int:
        with self._lock:
            return self._size

    def __bool__(self) -> bool:
        with self._lock:
            return self._size > 0

    def __repr__(self) -> str:
        with self._lock:
            values = self._to_list_unsafe()
        return f"CircularLinkedList({values!r})"

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
        if not isinstance(other, CircularLinkedList):
            return NotImplemented
        with self._lock:
            self_vals = self._to_list_unsafe()
        with other._lock:
            other_vals = other._to_list_unsafe()
        return self_vals == other_vals
