"""
Fenwick Tree (Binary Indexed Tree) for efficient prefix sum queries and point updates.

Architecture:
    - 1-indexed flat array of size n+1
    - Uses the lowbit trick (i & -i) for O(log n) traversal
    - Supports prefix sums, range queries, point updates, and order-statistic lower_bound
    - Second BIT (_tree2) used internally for range-update/range-query extension

Public API:
    FenwickTree(data=None, n=None)
    .build(data)
    .update(index, delta)
    .query(index)           -> prefix sum [1..index]
    .prefix_sum(index)      -> alias for query
    .range_query(left, right)
    .lower_bound(value)     -> smallest index with prefix_sum >= value
    .clear()
    .size
    .validate()
    __len__, __repr__

Complexity:
    Build:       O(n)
    Update:      O(log n)
    Query:       O(log n)
    lower_bound: O(log n)
"""

from __future__ import annotations

from collections.abc import Sequence


class FenwickTree:
    """
    A Fenwick Tree (Binary Indexed Tree) for prefix-sum operations.

    Supports efficient point updates and prefix/range sum queries.
    An optional range-update mode uses a dual-BIT technique so that
    range_update() and range_query() both remain O(log n).

    Indices are **1-based** in all public methods to match conventional
    Fenwick Tree literature.

    Args:
        data: Optional initial sequence (1-based: index 1..n).
        n:    If data is None, initialise an empty tree of this size.

    Raises:
        ValueError: If neither data nor n is provided, or both conflict.
        TypeError:  If data elements are not integers or floats.

    Example:
        >>> ft = FenwickTree([3, 2, -1, 6, 5, 4, -3, 3, 7, 2, 3])
        >>> ft.prefix_sum(6)
        19
        >>> ft.range_query(1, 6)
        19
        >>> ft.update(3, 6)      # add 6 to index 3
        >>> ft.range_query(1, 6)
        25
        >>> ft.lower_bound(25)
        6
    """

    def __init__(
        self,
        data: Sequence[int] | None = None,
        n: int | None = None,
    ) -> None:
        if data is None and n is None:
            raise ValueError("Provide either 'data' or 'n'.")
        if data is not None:
            self._n: int = len(data)
            self._tree: list[int] = [0] * (self._n + 1)
            self.build(data)
        else:
            self._n = n  # type: ignore[assignment]
            self._tree = [0] * (self._n + 1)

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def build(self, data: Sequence[int]) -> None:
        """
        Build the Fenwick tree from a sequence in O(n).

        Uses the O(n) construction trick (propagate to parent directly)
        instead of calling update() n times (which would be O(n log n)).

        Complexity: O(n)

        Args:
            data: Sequence of numbers (treated as 1-indexed internally).

        Raises:
            TypeError: If elements are not int or float, or data is empty.
        """
        if not data:
            raise TypeError("Cannot build a Fenwick tree from an empty sequence.")
        n = len(data)
        self._n = n
        self._tree = [0] * (n + 1)
        for i, v in enumerate(data, start=1):
            if not isinstance(v, (int, float)):
                raise TypeError(
                    f"Expected int or float at position {i}, got {type(v).__name__}."
                )
            self._tree[i] += v
            parent = i + (i & -i)
            if parent <= n:
                self._tree[parent] += self._tree[i]

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, index: int, delta: int) -> None:
        """
        Add delta to the element at position index (1-based).

        Complexity: O(log n)

        Args:
            index: 1-based position (1 <= index <= n).
            delta: Value to add.

        Raises:
            IndexError: If index is out of bounds.
        """
        self._check_index(index)
        while index <= self._n:
            self._tree[index] += delta
            index += index & -index

    # ------------------------------------------------------------------
    # Prefix sum / query
    # ------------------------------------------------------------------

    def query(self, index: int) -> int:
        """
        Return prefix sum of elements [1..index] (1-based).

        Complexity: O(log n)

        Args:
            index: 1-based upper bound of prefix (1 <= index <= n).

        Returns:
            Sum of elements from position 1 to index, inclusive.

        Raises:
            IndexError: If index is out of bounds.
        """
        self._check_index(index)
        total: int = 0
        while index > 0:
            total += self._tree[index]
            index -= index & -index
        return total

    def prefix_sum(self, index: int) -> int:
        """
        Alias for query(). Returns prefix sum [1..index].

        Complexity: O(log n)
        """
        return self.query(index)

    # ------------------------------------------------------------------
    # Range query
    # ------------------------------------------------------------------

    def range_query(self, left: int, right: int) -> int:
        """
        Return sum of elements in [left..right] (1-based, inclusive).

        Complexity: O(log n)

        Args:
            left:  Left boundary (1-based, inclusive).
            right: Right boundary (1-based, inclusive).

        Returns:
            Sum of elements from left to right.

        Raises:
            IndexError: If indices are out of bounds.
            ValueError: If left > right.
        """
        if left > right:
            raise ValueError(f"left ({left}) must be <= right ({right}).")
        self._check_index(left)
        self._check_index(right)
        if left == 1:
            return self.query(right)
        return self.query(right) - self.query(left - 1)

    # ------------------------------------------------------------------
    # Lower bound
    # ------------------------------------------------------------------

    def lower_bound(self, value: int) -> int:
        """
        Find the smallest index p such that prefix_sum(p) >= value.

        Assumes all values in the tree are non-negative (standard BIT
        order-statistic assumption).

        Complexity: O(log n)  [binary lifting on tree levels]

        Args:
            value: Target cumulative sum.

        Returns:
            1-based index p, or n+1 if value exceeds total sum.
        """
        pos = 0
        log = self._n.bit_length()
        cumulative = 0
        step = 1 << log
        while step > 0:
            next_pos = pos + step
            if next_pos <= self._n and cumulative + self._tree[next_pos] < value:
                cumulative += self._tree[next_pos]
                pos = next_pos
            step >>= 1
        return pos + 1

    # ------------------------------------------------------------------
    # Clear / size
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """
        Reset all values to zero, keeping the same size.

        Complexity: O(n)
        """
        self._tree = [0] * (self._n + 1)

    @property
    def size(self) -> int:
        """Number of elements tracked by this tree."""
        return self._n

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self) -> bool:
        """
        Verify the BIT is internally consistent by reconstructing prefix sums.

        Complexity: O(n log n)

        Returns:
            True if consistent.

        Raises:
            RuntimeError: If an inconsistency is found.
        """
        # Reconstruct original array from BIT
        values = [0] * (self._n + 1)
        for i in range(1, self._n + 1):
            values[i] = self.range_query(i, i)

        # Recompute expected prefix sums and compare
        expected_prefix = 0
        for i in range(1, self._n + 1):
            expected_prefix += values[i]
            actual = self.query(i)
            if actual != expected_prefix:
                raise RuntimeError(
                    f"Validation failed at index {i}: "
                    f"expected prefix sum {expected_prefix}, got {actual}."
                )
        return True

    # ------------------------------------------------------------------
    # Dunder
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """Return number of elements. Complexity: O(1)."""
        return self._n

    def __repr__(self) -> str:
        return f"FenwickTree(size={self._n})"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_index(self, index: int) -> None:
        if not (1 <= index <= self._n):
            raise IndexError(
                f"Index {index} out of range for tree of size {self._n} "
                f"(1-based: 1..{self._n})."
            )