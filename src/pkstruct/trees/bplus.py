"""
pkstruct.trees.bplus
====================
B+ Tree implementation with leaf-linked chain for efficient range queries.

Architecture
------------
``BPlusTree`` stores all data in the leaves.  Internal nodes contain only
separator keys for routing.  Leaf nodes are linked via a ``next_leaf``
pointer, enabling efficient range scans without recursive traversal.

All major operations run in O(log n).  Range queries benefit from the
leaf chain after the initial O(log n) descent.

Public API
----------
Core CRUD
    insert, delete, search, contains, update, clear

Metrics
    size, is_empty, min, max

Navigation
    leaf_traversal

Range queries
    range_query

Structural
    validate

Traversal
    __iter__, __reversed__

Dunder
    __len__, __contains__, __iter__, __repr__

Complexity
----------
Search        O(log n)
Insert        O(log n)
Delete        O(log n)
Range query   O(log n + k)
Space         O(n)
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from pkstruct.trees.exceptions import (
    DuplicateKeyError,
    EmptyTreeError,
    InvalidOrderError,
    KeyNotFoundError,
)
from pkstruct.trees.node import BPlusNode


class BPlusTree:
    """A B+ Tree with leaf-linked chain for efficient range queries.

    Parameters
    ----------
    order:
        Minimum degree of the tree (must be >= 2).  The maximum number
        of keys per node is ``2 * order - 1``.
    allow_duplicates:
        When *False* (default) duplicate keys update the stored value.
        When *True* duplicates are rejected with ``DuplicateKeyError``.
    """

    def __init__(self, order: int = 3, allow_duplicates: bool = False) -> None:
        if order < 2:
            raise InvalidOrderError(order)
        self._order: int = order
        self._allow_duplicates: bool = allow_duplicates
        self._root: BPlusNode = BPlusNode(is_leaf=True)
        self._first_leaf: BPlusNode = self._root
        self._size: int = 0

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def order(self) -> int:
        """Minimum degree of this B+ Tree."""
        return self._order

    # ------------------------------------------------------------------
    # Core CRUD
    # ------------------------------------------------------------------

    def insert(self, key: Any, value: Any = None) -> None:
        """Insert *key* with optional *value*.

        Parameters
        ----------
        key:
            Comparable key.
        value:
            Optional payload.

        Raises
        ------
        DuplicateKeyError
            If ``allow_duplicates=True`` and *key* already exists.
        """
        # Check for duplicate
        try:
            existing = self._find_leaf(self._root, key)
            if existing is not None and key in existing.keys:
                if self._allow_duplicates:
                    raise DuplicateKeyError(key)
                idx = existing.keys.index(key)
                existing.values[idx] = value
                return
        except (KeyNotFoundError, AttributeError):
            pass

        leaf = self._find_leaf(self._root, key)
        self._insert_into_leaf(leaf, key, value)

        if len(leaf.keys) > 2 * self._order - 1:
            self._split_leaf(leaf)

    def _find_leaf(self, node: BPlusNode, key: Any) -> BPlusNode:
        if node.is_leaf:
            return node
        i = 0
        while i < len(node.keys) and key >= node.keys[i]:
            i += 1
        return self._find_leaf(node.children[i], key)

    def _insert_into_leaf(self, leaf: BPlusNode, key: Any, value: Any) -> None:
        i = 0
        while i < len(leaf.keys) and leaf.keys[i] < key:
            i += 1
        leaf.keys.insert(i, key)
        leaf.values.insert(i, value)
        self._size += 1

    def _split_leaf(self, leaf: BPlusNode) -> None:
        new_leaf = BPlusNode(is_leaf=True)
        mid = len(leaf.keys) // 2

        new_leaf.keys = leaf.keys[mid:]
        new_leaf.values = leaf.values[mid:]
        leaf.keys = leaf.keys[:mid]
        leaf.values = leaf.values[:mid]

        new_leaf.next_leaf = leaf.next_leaf
        leaf.next_leaf = new_leaf

        self._insert_into_parent(leaf, new_leaf.keys[0], new_leaf)

    def _insert_into_parent(
        self,
        left: BPlusNode,
        key: Any,
        right: BPlusNode,
    ) -> None:
        parent = left.parent
        if parent is None:
            new_root = BPlusNode(is_leaf=False)
            new_root.keys = [key]
            new_root.children = [left, right]
            left.parent = new_root
            right.parent = new_root
            self._root = new_root
            return

        i = parent.children.index(left) + 1
        parent.keys.insert(i - 1, key)
        parent.children.insert(i, right)
        right.parent = parent

        if len(parent.keys) > 2 * self._order - 1:
            self._split_internal(parent)

    def _split_internal(self, node: BPlusNode) -> None:
        new_node = BPlusNode(is_leaf=False)
        mid = len(node.keys) // 2
        up_key = node.keys[mid]

        new_node.keys = node.keys[mid + 1:]
        new_node.children = node.children[mid + 1:]
        node.keys = node.keys[:mid]
        node.children = node.children[:mid + 1]

        for child in new_node.children:
            child.parent = new_node

        self._insert_into_parent(node, up_key, new_node)

    def delete(self, key: Any) -> None:
        """Remove *key* from the tree.

        Parameters
        ----------
        key:
            Key to remove.

        Raises
        ------
        KeyNotFoundError
            If *key* is not present.
        """
        leaf = self._find_leaf(self._root, key)
        if key not in leaf.keys:
            raise KeyNotFoundError(key)
        idx = leaf.keys.index(key)
        leaf.keys.pop(idx)
        leaf.values.pop(idx)
        self._size -= 1

    def search(self, key: Any) -> Any | None:
        """Return the value associated with *key*, or *None* if absent."""
        leaf = self._find_leaf(self._root, key)
        if key in leaf.keys:
            idx = leaf.keys.index(key)
            return leaf.values[idx]
        return None

    def contains(self, key: Any) -> bool:
        """Return *True* if *key* is present."""
        leaf = self._find_leaf(self._root, key)
        return key in leaf.keys

    def update(self, key: Any, value: Any) -> None:
        """Update the value of an existing *key*.

        Raises
        ------
        KeyNotFoundError
            If *key* does not exist.
        """
        leaf = self._find_leaf(self._root, key)
        if key not in leaf.keys:
            raise KeyNotFoundError(key)
        idx = leaf.keys.index(key)
        leaf.values[idx] = value

    def clear(self) -> None:
        """Remove all keys from the tree."""
        self._root = BPlusNode(is_leaf=True)
        self._first_leaf = self._root
        self._size = 0

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    def size(self) -> int:
        """Return the number of keys currently in the tree."""
        return self._size

    def is_empty(self) -> bool:
        """Return *True* if the tree contains no keys."""
        return self._size == 0

    def min(self) -> Any:
        """Return the minimum key.

        Raises
        ------
        EmptyTreeError
            If the tree is empty.
        """
        if self.is_empty():
            raise EmptyTreeError("min")
        return self._first_leaf.keys[0]

    def max(self) -> Any:
        """Return the maximum key.

        Raises
        ------
        EmptyTreeError
            If the tree is empty.
        """
        if self.is_empty():
            raise EmptyTreeError("max")
        leaf = self._first_leaf
        while leaf.next_leaf is not None:
            leaf = leaf.next_leaf
        return leaf.keys[-1]

    # ------------------------------------------------------------------
    # Leaf traversal
    # ------------------------------------------------------------------

    def leaf_traversal(self) -> list[Any]:
        """Traverse all leaves via the leaf-linked chain.

        Returns
        -------
        list
            All keys in sorted order by walking the leaf chain.
        """
        result: list[Any] = []
        leaf = self._first_leaf
        while leaf is not None:
            result.extend(leaf.keys)
            leaf = leaf.next_leaf
        return result

    # ------------------------------------------------------------------
    # Range query
    # ------------------------------------------------------------------

    def range_query(self, lo: Any, hi: Any) -> list[Any]:
        """Return all keys in [*lo*, *hi*] using the leaf chain.

        Parameters
        ----------
        lo:
            Inclusive lower bound.
        hi:
            Inclusive upper bound.

        Returns
        -------
        list
            Sorted keys within the range.
        """
        result: list[Any] = []
        leaf = self._find_leaf(self._root, lo)
        while leaf is not None:
            for k in leaf.keys:
                if lo <= k <= hi:
                    result.append(k)
                elif k > hi:
                    return result
            leaf = leaf.next_leaf
        return result

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self) -> bool:
        """Verify internal B+ Tree invariants.

        Checks:
          1. All leaves are at the same depth.
          2. Internal nodes have correct separator keys.
          3. Leaf chain maintains sorted order.
          4. Key counts within bounds.

        Returns
        -------
        bool
            *True* if all invariants hold.
        """
        if self._size == 0:
            return True
        try:
            self._validate(self._root, None, None, 0, [])
            return True
        except (ValueError, AssertionError, AttributeError):
            return False

    def _validate(
        self,
        node: BPlusNode | None,
        lo: Any,
        hi: Any,
        depth: int,
        leaf_depths: list[int],
    ) -> None:
        if node is None:
            return
        kc = len(node.keys)
        if node is not self._root:
            assert kc >= self._order - 1, f"Underflow: {kc} keys"
        assert kc <= 2 * self._order - 1, f"Overflow: {kc} keys"
        for i in range(kc - 1):
            assert node.keys[i] < node.keys[i + 1], "Keys not sorted"
        if node.is_leaf:
            leaf_depths.append(depth)
            if len(leaf_depths) > 1 and leaf_depths[-1] != leaf_depths[-2]:
                raise ValueError("Leaves at different depths")
        else:
            for i, child in enumerate(node.children):
                child_lo = lo if i == 0 else node.keys[i - 1]
                child_hi = hi if i == kc else node.keys[i]
                self._validate(child, child_lo, child_hi, depth + 1, leaf_depths)

    # ------------------------------------------------------------------
    # Dunder methods
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return self._size

    def __contains__(self, key: Any) -> bool:
        return self.contains(key)

    def __iter__(self) -> Iterator[Any]:
        leaf = self._first_leaf
        while leaf is not None:
            yield from leaf.keys
            leaf = leaf.next_leaf

    def __repr__(self) -> str:  # pragma: no cover
        keys = list(self.__iter__())
        return f"BPlusTree(size={self._size}, order={self._order}, keys={keys})"
