"""
pkstruct.trees.btree
====================
B-Tree implementation.

Architecture
------------
``BTree`` stores keys and values in multi-key nodes.  Internal nodes have
children between every pair of keys.  Insert triggers node splits when a
node overflows (exceeds ``2 * order - 1`` keys).  Delete triggers merges or
borrowing when a node underflows (drops below ``order - 1`` keys).

All major operations run in O(log n) due to the tree's self-balancing
property (every leaf is at the same depth).

Public API
----------
Core CRUD
    insert, delete, search, contains, update, clear

Metrics
    size, is_empty, min, max

Structural
    validate

Traversal
    __iter__, __reversed__ (in-order)

Dunder
    __len__, __contains__, __iter__, __repr__

Complexity
----------
Search  O(log n)
Insert  O(log n)
Delete  O(log n)
Space   O(n)
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from pkstruct._help import HelpMixin
from pkstruct._str import StrMixin
from pkstruct._tree_shortcuts import TreeShortcutsMixin
from pkstruct.shared.threading import StructureLock
from pkstruct.trees.exceptions import (
    DuplicateKeyError,
    EmptyTreeError,
    InvalidOrderError,
    KeyNotFoundError,
)
from pkstruct.trees.node import BTreeNode


class BTree(HelpMixin, StrMixin, TreeShortcutsMixin):
    """A balanced multi-way search tree (B-Tree).

    Parameters
    ----------
    order:
        Minimum degree of the tree (must be >= 2).  Each node (except root)
        must contain at least ``order - 1`` keys and at most
        ``2 * order - 1`` keys.
    allow_duplicates:
        When *False* (default) duplicate keys update the stored value.
        When *True* duplicates are rejected with ``DuplicateKeyError``.
    """

    def __init__(self, order: int = 3, allow_duplicates: bool = False) -> None:
        if order < 2:
            raise InvalidOrderError(order)
        self._order: int = order
        self._allow_duplicates: bool = allow_duplicates
        self._root: BTreeNode = BTreeNode()
        self._size: int = 0
        self._lock: StructureLock = StructureLock()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def order(self) -> int:
        """Minimum degree of this B-Tree."""
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
        with self._lock:
            # Check for duplicate
            try:
                existing = self._find(self._root, key)
                if existing is not None:
                    if self._allow_duplicates:
                        raise DuplicateKeyError(key)
                    # Update value in-place
                    self._update_value(self._root, key, value)
                    return
            except KeyNotFoundError:
                pass

            root = self._root
            if len(root.keys) == 2 * self._order - 1:
                new_root = BTreeNode()
                new_root.children.append(root)
                root.parent = new_root
                self._split_child(new_root, 0)
                self._root = new_root
            self._insert_non_full(self._root, key, value)
            self._size += 1

    def _insert_non_full(self, node: BTreeNode, key: Any, value: Any) -> None:
        i = len(node.keys) - 1
        if node.is_leaf():
            node.keys.append(None)
            node.values.append(None)
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                node.values[i + 1] = node.values[i]
                i -= 1
            node.keys[i + 1] = key
            node.values[i + 1] = value
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            if len(node.children[i].keys) == 2 * self._order - 1:
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            self._insert_non_full(node.children[i], key, value)

    def _split_child(self, parent: BTreeNode, index: int) -> None:
        order = self._order
        child = parent.children[index]
        new_child = BTreeNode()
        new_child.parent = parent
        mid = order - 1

        # Save the key/value to promote before truncating
        mid_key = child.keys[mid]
        mid_value = child.values[mid]

        # Copy second half of keys/values
        new_child.keys = child.keys[mid + 1 :]
        new_child.values = child.values[mid + 1 :]
        child.keys = child.keys[:mid]
        child.values = child.values[:mid]

        if not child.is_leaf():
            new_child.children = child.children[mid + 1 :]
            child.children = child.children[: mid + 1]

        # Promote middle key to parent
        parent.keys.insert(index, mid_key)
        parent.values.insert(index, mid_value)
        parent.children.insert(index + 1, new_child)

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
        with self._lock:
            if not self._find(self._root, key):
                raise KeyNotFoundError(key)
            self._delete(self._root, key)
            self._size -= 1
            if len(self._root.keys) == 0 and not self._root.is_leaf():
                self._root = self._root.children[0]
                self._root.parent = None

    def _delete(self, node: BTreeNode, key: Any) -> None:
        if node.is_leaf():
            if key in node.keys:
                idx = node.keys.index(key)
                node.keys.pop(idx)
                node.values.pop(idx)
            return

        if key in node.keys:
            idx = node.keys.index(key)
            if len(node.children[idx].keys) >= self._order:
                pred = self._get_predecessor(node.children[idx])
                node.keys[idx], node.values[idx] = pred
                self._delete(node.children[idx], pred[0])
            elif len(node.children[idx + 1].keys) >= self._order:
                succ = self._get_successor(node.children[idx + 1])
                node.keys[idx], node.values[idx] = succ
                self._delete(node.children[idx + 1], succ[0])
            else:
                self._merge(node, idx)
                self._delete(node.children[idx], key)
        else:
            idx = 0
            while idx < len(node.keys) and key > node.keys[idx]:
                idx += 1
            if len(node.children[idx].keys) < self._order:
                self._fix_child(node, idx)
                if idx > 0 and node.children[idx - 1] is self._get_sibling(node, idx):
                    idx -= 1
            self._delete(node.children[idx], key)

    def _get_predecessor(self, node: BTreeNode) -> tuple[Any, Any]:
        while not node.is_leaf():
            node = node.children[-1]
        return (node.keys[-1], node.values[-1])

    def _get_successor(self, node: BTreeNode) -> tuple[Any, Any]:
        while not node.is_leaf():
            node = node.children[0]
        return (node.keys[0], node.values[0])

    def _merge(self, parent: BTreeNode, idx: int) -> None:
        left = parent.children[idx]
        right = parent.children[idx + 1]
        left.keys.append(parent.keys.pop(idx))
        left.values.append(parent.values.pop(idx))
        left.keys.extend(right.keys)
        left.values.extend(right.values)
        if not right.is_leaf():
            left.children.extend(right.children)
        parent.children.pop(idx + 1)

    def _fix_child(self, parent: BTreeNode, idx: int) -> None:
        if idx > 0 and len(parent.children[idx - 1].keys) >= self._order:
            self._borrow_from_left(parent, idx)
        elif idx < len(parent.children) - 1 and len(parent.children[idx + 1].keys) >= self._order:
            self._borrow_from_right(parent, idx)
        else:
            if idx < len(parent.children) - 1:
                self._merge(parent, idx)
            else:
                self._merge(parent, idx - 1)

    def _borrow_from_left(self, parent: BTreeNode, idx: int) -> None:
        child = parent.children[idx]
        left = parent.children[idx - 1]
        child.keys.insert(0, parent.keys[idx - 1])
        child.values.insert(0, parent.values[idx - 1])
        parent.keys[idx - 1] = left.keys.pop()
        parent.values[idx - 1] = left.values.pop()
        if not left.is_leaf():
            child.children.insert(0, left.children.pop())

    def _borrow_from_right(self, parent: BTreeNode, idx: int) -> None:
        child = parent.children[idx]
        right = parent.children[idx + 1]
        child.keys.append(parent.keys[idx])
        child.values.append(parent.values[idx])
        parent.keys[idx] = right.keys.pop(0)
        parent.values[idx] = right.values.pop(0)
        if not right.is_leaf():
            child.children.append(right.children.pop(0))

    def _get_sibling(self, node: BTreeNode, idx: int) -> BTreeNode:
        if idx < len(node.children) - 1:
            return node.children[idx + 1]
        return node.children[idx - 1]

    def search(self, key: Any) -> Any | None:
        """Return the value associated with *key*, or *None* if absent."""
        with self._lock:
            try:
                node, idx = self._search(self._root, key)
                return node.values[idx]
            except (KeyNotFoundError, TypeError):
                return None

    def _search(self, node: BTreeNode | None, key: Any) -> tuple[BTreeNode, int]:
        if node is None:
            raise KeyNotFoundError(key)
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        if i < len(node.keys) and key == node.keys[i]:
            return node, i
        if node.is_leaf():
            raise KeyNotFoundError(key)
        return self._search(node.children[i], key)

    def contains(self, key: Any) -> bool:
        """Return *True* if *key* is present."""
        with self._lock:
            try:
                self._search(self._root, key)
                return True
            except KeyNotFoundError:
                return False

    def update(self, key: Any, value: Any) -> None:
        """Update the value of an existing *key*.

        Raises
        ------
        KeyNotFoundError
            If *key* does not exist.
        """
        with self._lock:
            node, idx = self._search(self._root, key)
            node.values[idx] = value

    def _update_value(self, node: BTreeNode, key: Any, value: Any) -> None:
        try:
            n, idx = self._search(node, key)
            n.values[idx] = value
        except KeyNotFoundError:
            pass

    def _find(self, node: BTreeNode | None, key: Any) -> BTreeNode | None:
        try:
            n, _ = self._search(node, key)
            return n
        except KeyNotFoundError:
            return None

    def clear(self) -> None:
        """Remove all keys from the tree."""
        with self._lock:
            self._root = BTreeNode()
            self._size = 0

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    def size(self) -> int:
        """Return the number of keys currently in the tree."""
        with self._lock:
            return self._size

    def is_empty(self) -> bool:
        """Return *True* if the tree contains no keys."""
        with self._lock:
            return self._size == 0

    def min(self) -> Any:
        """Return the minimum key.

        Raises
        ------
        EmptyTreeError
            If the tree is empty.
        """
        with self._lock:
            if self.is_empty():
                raise EmptyTreeError("min")
            node = self._root
            while not node.is_leaf():
                node = node.children[0]
            return node.keys[0]

    def max(self) -> Any:
        """Return the maximum key.

        Raises
        ------
        EmptyTreeError
            If the tree is empty.
        """
        with self._lock:
            if self.is_empty():
                raise EmptyTreeError("max")
            node = self._root
            while not node.is_leaf():
                node = node.children[-1]
            return node.keys[-1]

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self) -> bool:
        """Verify internal B-Tree invariants.

        Checks:
          1. Every node (except root) has at least ``order - 1`` keys.
          2. Every node has at most ``2 * order - 1`` keys.
          3. All leaves are at the same depth.
          4. Keys within each node are sorted.
          5. BST ordering is maintained across children.

        Returns
        -------
        bool
            *True* if all invariants hold.
        """
        with self._lock:
            if self._size == 0:
                return True
            try:
                self._validate(self._root, None, None)
                return True
            except (ValueError, AssertionError):
                return False

    def _validate(
        self,
        node: BTreeNode | None,
        lo: Any,
        hi: Any,
        depth: int | None = None,
        leaf_depth: list | None = None,
    ) -> None:
        if node is None:
            return
        if leaf_depth is None:
            leaf_depth = []
        if depth is None:
            depth = 0

        # Key count invariants
        kc = len(node.keys)
        assert kc >= self._order - 1 or node.parent is None, (
            f"Underflow: node has {kc} keys, need at least {self._order - 1}"
        )
        assert kc <= 2 * self._order - 1, (
            f"Overflow: node has {kc} keys, max is {2 * self._order - 1}"
        )

        # Keys sorted
        for i in range(kc - 1):
            assert node.keys[i] < node.keys[i + 1], "Keys not sorted"

        # BST ordering
        for _, k in enumerate(node.keys):
            if lo is not None and k <= lo:
                raise ValueError(f"Key {k} <= lower bound {lo}")
            if hi is not None and k >= hi:
                raise ValueError(f"Key {k} >= upper bound {hi}")

        if node.is_leaf():
            leaf_depth.append(depth)
            if len(leaf_depth) > 1 and leaf_depth[-1] != leaf_depth[-2]:
                raise ValueError("Leaves at different depths")
            return

        # Children
        assert len(node.children) == kc + 1, "Wrong child count"

        for i, child in enumerate(node.children):
            child_lo = lo if i == 0 else node.keys[i - 1]
            child_hi = hi if i == kc else node.keys[i]
            self._validate(child, child_lo, child_hi, depth + 1, leaf_depth)

    # ------------------------------------------------------------------
    # Dunder methods
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """Return the number of keys in the tree."""
        return self.size()

    def __contains__(self, key: Any) -> bool:
        """Support ``key in tree`` syntax."""
        return self.contains(key)

    def __iter__(self) -> Iterator[Any]:
        """Iterate over keys in ascending order."""
        with self._lock:
            keys = list(self._inorder(self._root))
        return iter(keys)

    def _inorder(self, node: BTreeNode | None) -> Iterator[Any]:
        if node is None:
            return
        if node.is_leaf():
            yield from node.keys
            return
        for i in range(len(node.keys)):
            yield from self._inorder(node.children[i])
            yield node.keys[i]
        yield from self._inorder(node.children[-1])

    def __repr__(self) -> str:  # pragma: no cover
        with self._lock:
            keys = list(self._inorder(self._root))
            return f"BTree(size={self._size}, order={self._order}, keys={keys})"
