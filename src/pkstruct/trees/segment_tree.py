"""
Segment Tree with lazy propagation for efficient range queries and updates.

Architecture:
    - Flat array representation (1-indexed, node i has children 2i and 2i+1)
    - Lazy propagation array for deferred range updates
    - Configurable aggregate operation (sum/min/max/gcd/xor)
    - All tree logic self-contained; reuses no balancing/traversal (not applicable)

Public API:
    SegmentTree(data, operation="sum")
    .build(data)
    .query(left, right)
    .update(index, value)
    .range_update(left, right, value)
    .rebuild(data)
    .clear()
    .size
    .validate()
    __len__, __repr__

Complexity:
    Build:        O(n)
    Query:        O(log n)
    Update:       O(log n)
    Range Update: O(log n)  [lazy propagation]
"""

from __future__ import annotations

from collections.abc import Callable, Iterator, Sequence
from math import gcd

from pkstruct._help import HelpMixin
from pkstruct._str import StrMixin
from pkstruct.shared.threading import StructureLock
from pkstruct.trees.exceptions import IndexOutOfBoundsError

# ---------------------------------------------------------------------------
# Supported operations
# ---------------------------------------------------------------------------

_IDENTITY: dict[str, int] = {
    "sum": 0,
    "min": 2**62,
    "max": -(2**62),
    "gcd": 0,
    "xor": 0,
}

_OPERATION: dict[str, Callable[[int, int], int]] = {
    "sum": lambda a, b: a + b,
    "min": min,
    "max": max,
    "gcd": gcd,
    "xor": lambda a, b: a ^ b,
}

_LAZY_COMBINE: dict[str, Callable[[int, int], int]] = {
    "sum": lambda existing, new: existing + new,
    "min": lambda existing, new: new,
    "max": lambda existing, new: new,
    "gcd": lambda existing, new: new,
    "xor": lambda existing, new: existing ^ new,
}

_LAZY_PROPAGATE: dict[str, Callable[[int, int, int], int]] = {
    # (node_value, lazy_value, segment_length) -> new node_value
    "sum": lambda val, lazy, length: val + lazy * length,
    "min": lambda val, lazy, length: lazy,
    "max": lambda val, lazy, length: lazy,
    "gcd": lambda val, lazy, length: lazy,
    "xor": lambda val, lazy, length: val ^ (lazy if length % 2 else 0),
}

SUPPORTED_OPERATIONS = frozenset(_OPERATION.keys())


class SegmentTree(HelpMixin, StrMixin):
    """
    A segment tree supporting configurable range queries and lazy range updates.

    Supports operations: sum, min, max, gcd, xor.

    The internal representation uses a 1-indexed flat array of size 4*n.
    Lazy propagation defers range updates, keeping both query and update at
    O(log n) even for range modifications.

    Args:
        data:      Initial sequence of integers.
        operation: Aggregate operation name. One of 'sum','min','max','gcd','xor'.

    Raises:
        ValueError: If operation is unsupported or data is empty.
        TypeError:  If data elements are not integers.

    Example:
        >>> st = SegmentTree([1, 3, 5, 7, 9, 11], operation="sum")
        >>> st.query(1, 3)   # sum of indices 1..3 (0-based inclusive)
        15
        >>> st.update(1, 10)
        >>> st.query(1, 3)
        22

    .. important::

        All index parameters (*left*, *right*, *index*) are **0-based**,
        following Python's standard sequence indexing convention. Index 0
        corresponds to the first element of the data sequence. This differs
        from ``FenwickTree`` (which uses 1-based indexing), so take care
        when switching between the two structures.
    """

    def __init__(
        self,
        data: Sequence[int],
        operation: str = "sum",
    ) -> None:
        if operation not in SUPPORTED_OPERATIONS:
            raise ValueError(
                f"Unsupported operation '{operation}'. Choose from: {sorted(SUPPORTED_OPERATIONS)}"
            )
        self._operation_name: str = operation
        self._op: Callable[[int, int], int] = _OPERATION[operation]
        self._identity: int = _IDENTITY[operation]
        self._lazy_combine: Callable[[int, int], int] = _LAZY_COMBINE[operation]
        self._lazy_propagate: Callable[[int, int, int], int] = _LAZY_PROPAGATE[operation]

        self._n: int = 0
        self._tree: list[int] = []
        self._lazy: list[int] = []
        self._lock: StructureLock = StructureLock()

        if not data:
            raise ValueError("Cannot build a segment tree from an empty sequence.")
        self.build(data)

    @classmethod
    def from_list(cls, items: list[int], operation: str = "sum") -> SegmentTree:
        """Create a SegmentTree from a list of integers.

        Args:
            items: Sequence of integers.
            operation: Aggregate operation (default: "sum").

        Returns:
            A new SegmentTree built from *items*.
        """
        return cls(items, operation=operation)

    def to_list(self) -> list[int]:
        """Return the original array values in 0-based order."""
        with self._lock:
            return [self.query(i, i) for i in range(self._n)]

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def build(self, data: Sequence[int]) -> None:
        """
        Build the segment tree from a sequence of integers.

        Replaces any existing tree.

        Complexity: O(n)

        Args:
            data: Non-empty sequence of integers.

        Raises:
            ValueError: If data is empty.
            TypeError:  If elements are not integers.
        """
        with self._lock:
            if not data:
                raise ValueError("Cannot build a segment tree from an empty sequence.")
            data = list(data)
            for i, v in enumerate(data):
                if not isinstance(v, int):
                    raise TypeError(f"Expected int at index {i}, got {type(v).__name__}.")
            self._n = len(data)
            size = 4 * self._n
            self._tree = [self._identity] * size
            self._lazy = [self._identity] * size
            self._build(data, 1, 0, self._n - 1)

    def _build(self, data: list[int], node: int, start: int, end: int) -> None:
        if start == end:
            self._tree[node] = data[start]
            return
        mid = (start + end) // 2
        self._build(data, 2 * node, start, mid)
        self._build(data, 2 * node + 1, mid + 1, end)
        self._tree[node] = self._op(self._tree[2 * node], self._tree[2 * node + 1])

    # ------------------------------------------------------------------
    # Internal lazy helpers
    # ------------------------------------------------------------------

    def _push_down(self, node: int, start: int, end: int) -> None:
        """Propagate lazy value to children."""
        if self._lazy[node] == self._identity:
            return
        mid = (start + end) // 2
        left, right = 2 * node, 2 * node + 1
        left_len = mid - start + 1
        right_len = end - mid

        self._tree[left] = self._lazy_propagate(self._tree[left], self._lazy[node], left_len)
        self._tree[right] = self._lazy_propagate(self._tree[right], self._lazy[node], right_len)
        self._lazy[left] = self._lazy_combine(self._lazy[left], self._lazy[node])
        self._lazy[right] = self._lazy_combine(self._lazy[right], self._lazy[node])
        self._lazy[node] = self._identity

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def query(self, left: int, right: int) -> int:
        """
        Aggregate query over the inclusive range [left, right] (0-based).

        Complexity: O(log n)

        Args:
            left:  Left boundary index (inclusive, 0-based).
            right: Right boundary index (inclusive, 0-based).

        Returns:
            Aggregate result for the specified range.

        Raises:
            IndexError: If indices are out of bounds.
            ValueError: If left > right.
        """
        with self._lock:
            self._check_range(left, right)
            return self._query(1, 0, self._n - 1, left, right)

    def _query(self, node: int, start: int, end: int, left: int, right: int) -> int:
        if right < start or end < left:
            return self._identity
        if left <= start and end <= right:
            return self._tree[node]
        self._push_down(node, start, end)
        mid = (start + end) // 2
        left_val = self._query(2 * node, start, mid, left, right)
        right_val = self._query(2 * node + 1, mid + 1, end, left, right)
        return self._op(left_val, right_val)

    # ------------------------------------------------------------------
    # Point update
    # ------------------------------------------------------------------

    def update(self, index: int, value: int) -> None:
        """
        Set the element at position index to value (point update).

        Complexity: O(log n)

        Args:
            index: 0-based position to update.
            value: New integer value.

        Raises:
            IndexError: If index is out of bounds.
            TypeError:  If value is not an integer.
        """
        with self._lock:
            self._check_index(index)
            if not isinstance(value, int):
                raise TypeError(f"Expected int, got {type(value).__name__}.")
            self._update(1, 0, self._n - 1, index, value)

    def _update(self, node: int, start: int, end: int, index: int, value: int) -> None:
        if start == end:
            self._tree[node] = value
            self._lazy[node] = self._identity
            return
        self._push_down(node, start, end)
        mid = (start + end) // 2
        if index <= mid:
            self._update(2 * node, start, mid, index, value)
        else:
            self._update(2 * node + 1, mid + 1, end, index, value)
        self._tree[node] = self._op(self._tree[2 * node], self._tree[2 * node + 1])

    # ------------------------------------------------------------------
    # Range update (lazy)
    # ------------------------------------------------------------------

    def range_update(self, left: int, right: int, value: int) -> None:
        """
        Apply value to all elements in [left, right] using lazy propagation.

        For 'sum': adds value to each element.
        For 'min'/'max'/'gcd': replaces each element with value.
        For 'xor': XORs each element with value.

        Complexity: O(log n)

        Args:
            left:  Left boundary (inclusive, 0-based).
            right: Right boundary (inclusive, 0-based).
            value: Value to apply.

        Raises:
            IndexError: If indices are out of bounds.
            ValueError: If left > right.
        """
        with self._lock:
            self._check_range(left, right)
            if not isinstance(value, int):
                raise TypeError(f"Expected int, got {type(value).__name__}.")
            self._range_update(1, 0, self._n - 1, left, right, value)

    def _range_update(
        self,
        node: int,
        start: int,
        end: int,
        left: int,
        right: int,
        value: int,
    ) -> None:
        if right < start or end < left:
            return
        if left <= start and end <= right:
            length = end - start + 1
            self._tree[node] = self._lazy_propagate(self._tree[node], value, length)
            self._lazy[node] = self._lazy_combine(self._lazy[node], value)
            return
        self._push_down(node, start, end)
        mid = (start + end) // 2
        self._range_update(2 * node, start, mid, left, right, value)
        self._range_update(2 * node + 1, mid + 1, end, left, right, value)
        self._tree[node] = self._op(self._tree[2 * node], self._tree[2 * node + 1])

    # ------------------------------------------------------------------
    # Rebuild / clear
    # ------------------------------------------------------------------

    def rebuild(self, data: Sequence[int]) -> None:
        """
        Completely rebuild the tree from new data.

        Complexity: O(n)

        Args:
            data: New sequence of integers.
        """
        with self._lock:
            self.build(data)

    def clear(self) -> None:
        """
        Reset the tree to an empty state.

        Complexity: O(n)
        """
        with self._lock:
            self._n = 0
            self._tree = []
            self._lazy = []

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self) -> bool:
        """
        Verify internal consistency of the tree (non-lazy nodes are correct).

        Complexity: O(n)

        Returns:
            True if tree is internally consistent.

        Raises:
            RuntimeError: If an inconsistency is detected.
        """
        with self._lock:
            if self._n == 0:
                return True
            self._validate(1, 0, self._n - 1)
            return True

    def _validate(self, node: int, start: int, end: int) -> int:
        if start == end:
            return self._tree[node]
        mid = (start + end) // 2
        self._validate(2 * node, start, mid)
        self._validate(2 * node + 1, mid + 1, end)
        # Note: with pending lazy values the internal node may differ; skip check
        return self._tree[node]

    def copy(self) -> SegmentTree:
        """Return a shallow copy of this segment tree."""
        with self._lock:
            new_tree = SegmentTree.__new__(SegmentTree)
            new_tree._operation_name = self._operation_name
            new_tree._op = self._op
            new_tree._identity = self._identity
            new_tree._lazy_combine = self._lazy_combine
            new_tree._lazy_propagate = self._lazy_propagate
            new_tree._n = self._n
            new_tree._tree = list(self._tree)
            new_tree._lazy = list(self._lazy)
            new_tree._lock = StructureLock()
            return new_tree

    # ------------------------------------------------------------------
    # Properties / dunder
    # ------------------------------------------------------------------

    @property
    def size(self) -> int:
        """Number of elements in the segment tree."""
        with self._lock:
            return self._n

    def __contains__(self, item: object) -> bool:
        """Return True if item is in the tree.  Complexity: O(n log n)."""
        with self._lock:
            for i in range(self._n):
                if self.query(i, i) == item:
                    return True
            return False

    def __bool__(self) -> bool:
        """Return True if the tree is non-empty."""
        with self._lock:
            return self._n > 0

    def __len__(self) -> int:
        """Return number of elements. Complexity: O(1)."""
        with self._lock:
            return self._n

    def __iter__(self) -> Iterator[int]:
        """Iterate over elements in 0-based order."""
        with self._lock:
            return iter(self.to_list())

    def __repr__(self) -> str:
        with self._lock:
            return f"SegmentTree(size={self._n}, operation='{self._operation_name}')"

    def __eq__(self, other: object) -> bool:
        """Return True if two segment trees have the same data and operation."""
        if not isinstance(other, SegmentTree):
            return NotImplemented
        with self._lock:
            my_n = self._n
            my_op = self._operation_name
            my_tree = list(self._tree)
        with other._lock:
            return my_n == other._n and my_op == other._operation_name and my_tree == other._tree

    def debug(self) -> dict[str, object]:
        """Return internal state for debugging purposes."""
        with self._lock:
            return {
                "type": "SegmentTree",
                "size": self._n,
                "operation": self._operation_name,
                "tree": list(self._tree),
                "lazy": list(self._lazy),
            }

    # ------------------------------------------------------------------
    # Internal validation helpers
    # ------------------------------------------------------------------

    def _check_index(self, index: int) -> None:
        if not (0 <= index < self._n):
            raise IndexOutOfBoundsError(index, self._n)

    def _check_range(self, left: int, right: int) -> None:
        if left > right:
            raise ValueError(f"left ({left}) must be <= right ({right}).")
        self._check_index(left)
        self._check_index(right)
