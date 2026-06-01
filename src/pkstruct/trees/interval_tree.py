"""
Interval Tree for efficient overlap queries and point containment.

Architecture:
    - Augmented BST (AVL-balanced) where each node stores an interval (start, end)
      and a subtree max_endpoint value for O(log n) overlap pruning.
    - AVL rotations keep height O(log n), giving O(log n) insert/delete/search.
    - merge_overlaps operates in O(n log n) by collecting + re-inserting.
    - No external dependencies; does not reuse balancing.py to stay self-contained
      (the interval augmentation requires custom metadata propagation incompatible
      with the generic rotate() signature in balancing.py).

Public API:
    IntervalTree()
    .insert(start, end)
    .delete(start, end)
    .search(start, end)       -> list of overlapping intervals
    .overlap(start, end)      -> bool
    .all_overlaps(start, end) -> list of all overlapping intervals
    .contains_point(point)    -> list of intervals containing point
    .merge_overlaps()         -> merges and rebuilds tree
    .validate()
    .clear()
    .size
    .height()
    __len__, __contains__, __iter__, __repr__

Complexity:
    Insert:        O(log n)
    Delete:        O(log n)
    Search:        O(log n + k)  where k = number of results
    overlap check: O(log n)
"""

from __future__ import annotations

from collections.abc import Iterator

from pkstruct._help import HelpMixin
from pkstruct._str import StrMixin
from pkstruct._tree_shortcuts import TreeShortcutsMixin
from pkstruct.shared.threading import StructureLock

Interval = tuple[int, int]


# ---------------------------------------------------------------------------
# Internal node
# ---------------------------------------------------------------------------


class _INode:
    """Internal node for the augmented AVL interval tree."""

    __slots__ = ("start", "end", "max_end", "height", "left", "right")

    def __init__(self, start: int, end: int) -> None:
        self.start: int = start
        self.end: int = end
        self.max_end: int = end  # max endpoint in subtree
        self.height: int = 1
        self.left: _INode | None = None
        self.right: _INode | None = None


# ---------------------------------------------------------------------------
# AVL helpers (interval-specific)
# ---------------------------------------------------------------------------


def _height(node: _INode | None) -> int:
    return node.height if node is not None else 0


def _max_end(node: _INode | None) -> int:
    return node.max_end if node is not None else -(2**62)


def _update(node: _INode) -> None:
    """Recompute height and max_end from children."""
    node.height = 1 + max(_height(node.left), _height(node.right))
    node.max_end = max(node.end, _max_end(node.left), _max_end(node.right))


def _balance_factor(node: _INode) -> int:
    return _height(node.left) - _height(node.right)


def _rotate_right(y: _INode) -> _INode:
    x = y.left
    assert x is not None
    t2 = x.right
    x.right = y
    y.left = t2
    _update(y)
    _update(x)
    return x


def _rotate_left(x: _INode) -> _INode:
    y = x.right
    assert y is not None
    t2 = y.left
    y.left = x
    x.right = t2
    _update(x)
    _update(y)
    return y


def _rebalance(node: _INode) -> _INode:
    _update(node)
    bf = _balance_factor(node)

    # Left heavy
    if bf > 1:
        assert node.left is not None
        if _balance_factor(node.left) < 0:
            node.left = _rotate_left(node.left)
        return _rotate_right(node)

    # Right heavy
    if bf < -1:
        assert node.right is not None
        if _balance_factor(node.right) > 0:
            node.right = _rotate_right(node.right)
        return _rotate_left(node)

    return node


# ---------------------------------------------------------------------------
# BST operations
# ---------------------------------------------------------------------------


def _insert(node: _INode | None, start: int, end: int) -> _INode:
    """Insert (start, end) into subtree rooted at node; return new root."""
    if node is None:
        return _INode(start, end)
    if (start, end) < (node.start, node.end):
        node.left = _insert(node.left, start, end)
    else:
        node.right = _insert(node.right, start, end)
    return _rebalance(node)


def _min_node(node: _INode) -> _INode:
    while node.left is not None:
        node = node.left
    return node


def _delete(node: _INode | None, start: int, end: int) -> _INode | None:
    """Delete first occurrence of (start, end); return new root."""
    if node is None:
        return None
    if (start, end) < (node.start, node.end):
        node.left = _delete(node.left, start, end)
    elif (start, end) > (node.start, node.end):
        node.right = _delete(node.right, start, end)
    else:
        # Found
        if node.left is None:
            return node.right
        if node.right is None:
            return node.left
        successor = _min_node(node.right)
        node.start, node.end = successor.start, successor.end
        node.right = _delete(node.right, successor.start, successor.end)

    return _rebalance(node)


# ---------------------------------------------------------------------------
# Overlap search helpers
# ---------------------------------------------------------------------------


def _overlaps(a_start: int, a_end: int, b_start: int, b_end: int) -> bool:
    """True if intervals [a_start, a_end] and [b_start, b_end] overlap."""
    return a_start <= b_end and b_start <= a_end


def _search_overlaps(
    node: _INode | None,
    start: int,
    end: int,
    results: list[Interval],
) -> None:
    """Collect all intervals overlapping [start, end] into results."""
    if node is None:
        return
    # Prune: if max_end of left subtree < start, no overlap in left subtree
    if _overlaps(node.start, node.end, start, end):
        results.append((node.start, node.end))
    if node.left is not None and node.left.max_end >= start:
        _search_overlaps(node.left, start, end, results)
    _search_overlaps(node.right, start, end, results)


def _contains_point(
    node: _INode | None,
    point: int,
    results: list[Interval],
) -> None:
    """Collect all intervals containing point."""
    if node is None:
        return
    if node.max_end < point:
        return
    if node.start <= point <= node.end:
        results.append((node.start, node.end))
    _contains_point(node.left, point, results)
    _contains_point(node.right, point, results)


def _inorder(node: _INode | None, out: list[Interval]) -> None:
    if node is None:
        return
    _inorder(node.left, out)
    out.append((node.start, node.end))
    _inorder(node.right, out)


# ---------------------------------------------------------------------------
# IntervalTree
# ---------------------------------------------------------------------------


class IntervalTree(HelpMixin, StrMixin, TreeShortcutsMixin):
    """
    An augmented AVL interval tree supporting efficient overlap queries.

    Each node stores an interval (start, end) and the maximum endpoint
    in its subtree (max_end), enabling O(log n) overlap pruning.

    Intervals are inclusive: [start, end].

    Args:
        None

    Example:
        >>> it = IntervalTree()
        >>> it.insert(15, 20)
        >>> it.insert(10, 30)
        >>> it.insert(17, 19)
        >>> it.search(14, 16)
        [(15, 20), (10, 30)]
        >>> (17, 19) in it
        True
        >>> it.contains_point(18)
        [(15, 20), (10, 30), (17, 19)]
    """

    def __init__(self) -> None:
        self._root: _INode | None = None
        self._size: int = 0
        self._lock: StructureLock = StructureLock()

    # ------------------------------------------------------------------
    # Insert / delete
    # ------------------------------------------------------------------

    def insert(self, start: int, end: int) -> None:
        """
        Insert interval [start, end] into the tree.

        Complexity: O(log n)

        Args:
            start: Interval start (inclusive).
            end:   Interval end (inclusive).

        Raises:
            ValueError: If start > end.
        """
        with self._lock:
            if start > end:
                raise ValueError(f"Invalid interval: start ({start}) must be <= end ({end}).")
            self._root = _insert(self._root, start, end)
            self._size += 1

    def delete(self, start: int, end: int) -> None:
        """
        Delete one occurrence of interval [start, end] from the tree.

        Complexity: O(log n)

        Args:
            start: Interval start.
            end:   Interval end.

        Raises:
            KeyError: If the interval is not present.
        """
        with self._lock:
            if not self.__contains__((start, end)):
                raise KeyError(f"Interval ({start}, {end}) not found in tree.")
            self._root = _delete(self._root, start, end)
            self._size -= 1

    # ------------------------------------------------------------------
    # Search / overlap
    # ------------------------------------------------------------------

    def search(self, start: int, end: int) -> list[Interval]:
        """
        Return a list of intervals that overlap with [start, end].

        Two intervals overlap if they share at least one point.

        Complexity: O(log n + k) where k is the number of results.

        Args:
            start: Query interval start.
            end:   Query interval end.

        Returns:
            List of overlapping (start, end) tuples.
        """
        with self._lock:
            results: list[Interval] = []
            _search_overlaps(self._root, start, end, results)
            return results

    def overlap(self, start: int, end: int) -> bool:
        """
        Return True if any interval in the tree overlaps [start, end].

        Complexity: O(log n)

        Args:
            start: Query interval start.
            end:   Query interval end.

        Returns:
            True if at least one overlap exists.
        """
        with self._lock:
            return self._overlap_exists(self._root, start, end)

    def _overlap_exists(self, node: _INode | None, start: int, end: int) -> bool:
        if node is None:
            return False
        if _overlaps(node.start, node.end, start, end):
            return True
        if (
            node.left is not None
            and node.left.max_end >= start
            and self._overlap_exists(node.left, start, end)
        ):
            return True
        return self._overlap_exists(node.right, start, end)

    def all_overlaps(self, start: int, end: int) -> list[Interval]:
        """
        Return ALL intervals overlapping [start, end].

        Alias for search() with semantically clearer name.

        Complexity: O(log n + k)
        """
        return self.search(start, end)

    # all_overlaps delegates to search which wraps with lock

    def contains_point(self, point: int) -> list[Interval]:
        """
        Return all intervals that contain the given point.

        Complexity: O(log n + k)

        Args:
            point: Query point.

        Returns:
            List of intervals [start, end] where start <= point <= end.
        """
        with self._lock:
            results: list[Interval] = []
            _contains_point(self._root, point, results)
            return results

    # ------------------------------------------------------------------
    # Merge overlaps
    # ------------------------------------------------------------------

    def merge_overlaps(self) -> None:
        """
        Merge all overlapping/touching intervals in-place.

        The tree is rebuilt from the merged set of intervals.

        Complexity: O(n log n)  [sort + linear merge + rebuild]
        """
        with self._lock:
            intervals: list[Interval] = []
            _inorder(self._root, intervals)
            if not intervals:
                return
            intervals.sort()
            merged: list[Interval] = [intervals[0]]
            for start, end in intervals[1:]:
                prev_start, prev_end = merged[-1]
                if start <= prev_end + 1:  # overlapping or touching
                    merged[-1] = (prev_start, max(prev_end, end))
                else:
                    merged.append((start, end))
            self.clear()
            for s, e in merged:
                self.insert(s, e)

    # ------------------------------------------------------------------
    # Validate
    # ------------------------------------------------------------------
    # Validate
    # ------------------------------------------------------------------

    def validate(self) -> bool:
        """
        Verify AVL balance property and max_end invariant throughout the tree.

        Complexity: O(n)

        Returns:
            True if tree is valid.

        Raises:
            RuntimeError: If any invariant is violated.
        """
        with self._lock:
            self._validate_node(self._root)
            return True

    def _validate_node(self, node: _INode | None) -> tuple[int, int]:
        """Returns (height, max_end) of subtree; raises on violation."""
        if node is None:
            return 0, -(2**62)
        lh, lmax = self._validate_node(node.left)
        rh, rmax = self._validate_node(node.right)
        expected_height = 1 + max(lh, rh)
        if node.height != expected_height:
            raise RuntimeError(
                f"Height mismatch at ({node.start},{node.end}): "
                f"stored {node.height}, expected {expected_height}."
            )
        expected_max = max(node.end, lmax, rmax)
        if node.max_end != expected_max:
            raise RuntimeError(
                f"max_end mismatch at ({node.start},{node.end}): "
                f"stored {node.max_end}, expected {expected_max}."
            )
        bf = lh - rh
        if abs(bf) > 1:
            raise RuntimeError(
                f"AVL balance violation at ({node.start},{node.end}): balance factor {bf}."
            )
        return expected_height, expected_max

    # ------------------------------------------------------------------
    # Clear / size / height
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """Remove all intervals from the tree. Complexity: O(1)."""
        with self._lock:
            self._root = None
            self._size = 0

    @property
    def size(self) -> int:
        """Number of intervals stored in the tree."""
        return self._size

    def height(self) -> int:
        """
        Return the height of the tree.

        Complexity: O(1)  [stored in root node]
        """
        with self._lock:
            return _height(self._root)

    @property
    def max_endpoint(self) -> int | None:
        """
        Maximum endpoint across all intervals in the tree.

        Returns None for an empty tree.

        Complexity: O(1)
        """
        with self._lock:
            return self._root.max_end if self._root is not None else None

    # ------------------------------------------------------------------
    # Dunder
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """Return number of intervals. Complexity: O(1)."""
        return self.size

    def __contains__(self, interval: object) -> bool:
        """
        Return True if interval (start, end) is in the tree.

        Complexity: O(log n)
        """
        with self._lock:
            if not (isinstance(interval, tuple) and len(interval) == 2):
                return False
            start, end = interval  # type: ignore[misc]
            return self._find(self._root, start, end)

    def _find(self, node: _INode | None, start: int, end: int) -> bool:
        if node is None:
            return False
        if node.start == start and node.end == end:
            return True
        if (start, end) < (node.start, node.end):
            return self._find(node.left, start, end)
        return self._find(node.right, start, end)

    def __iter__(self) -> Iterator[Interval]:
        """
        Iterate over all intervals in sorted (start, end) order.

        Complexity: O(n)
        """
        with self._lock:
            intervals: list[Interval] = []
            _inorder(self._root, intervals)
            result = list(intervals)
        return iter(result)

    def __repr__(self) -> str:
        with self._lock:
            return (
                f"IntervalTree(size={self._size}, "
                f"height={self.height()}, "
                f"max_endpoint={self.max_endpoint})"
            )
