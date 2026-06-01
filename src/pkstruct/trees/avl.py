"""
pkstruct.trees.avl
==================
Production-grade AVL Tree (self-balancing BST).

Architecture
------------
``AVLTree`` *extends* ``BinarySearchTree``.  Only the mutation paths
(``insert`` / ``delete``) are overridden; every read-only method
(``search``, ``contains``, traversals, interview utilities) is inherited
directly from the BST base class.

Balancing is fully delegated to the shared infrastructure in
``balancing.py``:

  * ``rebalance(node, strategy="avl")``  – performs LL / RR / LR / RL
    rotations as needed.
  * ``update_metadata(node)``            – recalculates height & balance
    factor stored on ``AVLNode``.
  * ``get_balance_factor(node)``         – returns left_height - right_height.
  * ``rotate(node, direction, root)``    – generic left / right rotation.

Node type
---------
``AVLNode`` (from ``node.py``) carries ``height`` and ``balance_factor``
attributes that ``update_metadata`` keeps current.

Public API (additions over BST)
--------------------------------
  rebalance(node)      – internal; exposed for subclassing.
  is_avl_valid()       – structural assertion (balance + BST order).
  validate()           – overrides BST validate to include AVL checks.

Complexity
----------
All major operations are O(log n) due to the AVL height guarantee.
"""

from __future__ import annotations

import collections
import json
from typing import Any

from pkstruct.trees.balancing import (
    get_balance_factor,
    rebalance,
    update_metadata,
    validate_balance,
)
from pkstruct.trees.bst import BinarySearchTree
from pkstruct.trees.node import AVLNode


class AVLTree(BinarySearchTree):
    """Self-balancing AVL Tree.

    Inherits the full BST API.  Insert and delete automatically maintain
    the AVL invariant (|balance_factor| ≤ 1 at every node) via LL, RR,
    LR, and RL rotations supplied by ``balancing.rebalance``.

    Parameters
    ----------
    allow_duplicates:
        Forwarded to the BST base class.
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def __init__(self, allow_duplicates: bool = False) -> None:
        super().__init__(allow_duplicates=allow_duplicates)

    # ------------------------------------------------------------------
    # Override: use AVLNode and rebalance after mutations
    # ------------------------------------------------------------------

    def insert(self, key: Any, value: Any = None) -> None:
        """Insert *key* into the AVL tree, rebalancing as required.

        If *key* already exists and ``allow_duplicates`` is *False*, the
        stored value is updated.  All rotations are delegated to
        ``balancing.rebalance``.

        Parameters
        ----------
        key:
            Comparable key.
        value:
            Optional payload.

        Raises
        ------
        ValueError
            If ``allow_duplicates=True`` and the key already exists.
        """
        with self._lock:
            self._root, inserted = self._avl_insert(self._root, key, value)
            if inserted:
                self._size += 1

    def _avl_insert(
        self,
        node: AVLNode | None,
        key: Any,
        value: Any,
    ) -> tuple[AVLNode | None, bool]:
        """Recursive AVL insert; returns (new_subtree_root, was_inserted)."""
        if node is None:
            return AVLNode(key, value), True

        if key < node.key:
            node.left, inserted = self._avl_insert(node.left, key, value)
        elif key > node.key:
            node.right, inserted = self._avl_insert(node.right, key, value)
        else:
            if self._allow_duplicates:
                raise ValueError(f"Duplicate key: {key!r}")
            node.value = value
            return node, False

        update_metadata(node)
        node = rebalance(node, strategy="avl")
        return node, inserted

    def delete(self, key: Any) -> None:
        """Remove *key* from the AVL tree, rebalancing as required.

        Parameters
        ----------
        key:
            Key to remove.

        Raises
        ------
        KeyError
            If *key* is not present.
        """
        with self._lock:
            self._root, deleted = self._avl_delete(self._root, key)
            if not deleted:
                raise KeyError(f"Key not found: {key!r}")
            self._size -= 1

    def _avl_delete(
        self,
        node: AVLNode | None,
        key: Any,
    ) -> tuple[AVLNode | None, bool]:
        """Recursive AVL delete; returns (new_subtree_root, was_deleted)."""
        if node is None:
            return None, False

        if key < node.key:
            node.left, deleted = self._avl_delete(node.left, key)
        elif key > node.key:
            node.right, deleted = self._avl_delete(node.right, key)
        else:
            deleted = True
            if node.left is None:
                return node.right, deleted
            if node.right is None:
                return node.left, deleted
            # Replace with in-order successor
            successor = self._min_node(node.right)
            node.key = successor.key
            node.value = successor.value
            node.right, _ = self._avl_delete(node.right, successor.key)

        update_metadata(node)
        node = rebalance(node, strategy="avl")
        return node, deleted

    # ------------------------------------------------------------------
    # AVL-specific API
    # ------------------------------------------------------------------

    def rebalance_node(self, node: AVLNode) -> AVLNode:
        """Manually trigger a rebalance on *node* and return the new root.

        Intended for subclassing or advanced use cases.  Normal usage
        should not require calling this directly.

        Parameters
        ----------
        node:
            The ``AVLNode`` to rebalance.

        Returns
        -------
        AVLNode
            The new subtree root after rotations.
        """
        with self._lock:
            update_metadata(node)
            return rebalance(node, strategy="avl")

    def is_avl_valid(self) -> bool:
        """Return *True* if the tree satisfies both the BST and AVL properties.

        Checks:
          1. BST ordering invariant (via inherited ``_validate``).
          2. Balance factor ≤ 1 at every node (via ``balancing.validate_balance``).
          3. Stored height metadata is consistent.
        """
        with self._lock:
            if not self._validate(self._root, None, None):
                return False
            if self._root is None:
                return True
            return validate_balance(self._root) and self._check_heights(self._root)

    def _check_heights(self, node: AVLNode | None) -> bool:
        """Verify stored height values are consistent with tree structure."""
        if node is None:
            return True
        lh = node.left.height if (node.left and hasattr(node.left, "height")) else 0
        rh = node.right.height if (node.right and hasattr(node.right, "height")) else 0
        expected_height = 1 + max(lh, rh)
        stored_height = getattr(node, "height", None)
        if stored_height != expected_height:
            return False
        return self._check_heights(node.left) and self._check_heights(node.right)

    def validate(self) -> bool:
        """Verify both BST order and AVL balance properties.

        Returns
        -------
        bool
            *True* if the tree is a valid AVL tree.
        """
        return self.is_avl_valid()

    # is_avl_valid already wraps with lock

    def balance_factor(self, key: Any) -> int:
        """Return the balance factor (left_height - right_height) for *key*'s node.

        Parameters
        ----------
        key:
            The key whose balance factor is requested.

        Raises
        ------
        KeyError
            If *key* is not in the tree.
        """
        with self._lock:
            node = self._find(self._root, key)
            if node is None:
                raise KeyError(f"Key not found: {key!r}")
            return get_balance_factor(node)

    # ------------------------------------------------------------------
    # Serialization override: create AVLNodes instead of plain TreeNodes
    # ------------------------------------------------------------------

    def serialize(self) -> str:
        """Serialize the tree to a JSON string (level-order with null sentinels).

        Each node is encoded as a ``[key, value]`` pair so values are
        preserved across round-trips.
        """
        with self._lock:
            if self._root is None:
                return "[]"
            result: list[Any | None] = []
            q: collections.deque[AVLNode | None] = collections.deque([self._root])
            while q:
                node = q.popleft()
                if node is None:
                    result.append(None)
                else:
                    result.append([node.key, node.value])
                    q.append(node.left)
                    q.append(node.right)
            while result and result[-1] is None:
                result.pop()
            return json.dumps(result)

    def deserialize(self, data: str) -> None:
        """Rebuild the tree from a JSON string, creating AVLNodes."""
        with self._lock:
            self.clear()
            raw: list[Any | None] = json.loads(data)
            if not raw:
                return
            def _kv(entry: Any | None) -> tuple[Any, Any] | tuple[None, None]:
                if entry is None:
                    return None, None
                if isinstance(entry, list) and len(entry) == 2:
                    return entry[0], entry[1]
                return entry, None

            key0, val0 = _kv(raw[0])
            self._root = AVLNode(key0, val0)
            self._size = 1
            q: collections.deque[AVLNode] = collections.deque([self._root])
            i = 1
            while q and i < len(raw):
                node = q.popleft()
                if i < len(raw) and raw[i] is not None:
                    k, v = _kv(raw[i])
                    node.left = AVLNode(k, v)
                    self._size += 1
                    q.append(node.left)
                i += 1
                if i < len(raw) and raw[i] is not None:
                    k, v = _kv(raw[i])
                    node.right = AVLNode(k, v)
                    self._size += 1
                    q.append(node.right)
                i += 1
            self._fix_heights(self._root)

    def _fix_heights(self, node: AVLNode | None) -> None:
        """Post-order traversal to recalculate heights after deserialization."""
        if node is None:
            return
        self._fix_heights(node.left)
        self._fix_heights(node.right)
        update_metadata(node)

    # ------------------------------------------------------------------
    # Dunder
    # ------------------------------------------------------------------

    def __repr__(self) -> str:  # pragma: no cover
        with self._lock:
            keys = list(self._traverse("inorder"))
            h = self.height()
            return f"AVLTree(size={self._size}, height={h}, keys={keys})"
