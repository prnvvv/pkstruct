"""
pkstruct.trees.red_black
========================
Production-grade Red-Black Tree.

Architecture
------------
``RedBlackTree`` is a standalone class (not a subclass of BST) because the
RB delete fixup relies on a sentinel NIL node that would conflict with the
plain ``TreeNode`` infrastructure used by ``BinarySearchTree``.

Shared infrastructure used
--------------------------
  * ``RBNode``  from ``node.py``   – carries ``color``, ``parent``,
    ``left``, ``right`` attributes.
  * ``rotate``  from ``balancing.py`` – generic left/right rotation;
    called as ``rotate(node, "left")`` / ``rotate(node, "right")``.

Constants
---------
  RED   = 0
  BLACK = 1

Red-Black invariants maintained
---------------------------------
  1. Every node is RED or BLACK.
  2. The root is always BLACK.
  3. No RED node has a RED parent (no two consecutive red nodes).
  4. Every path from any node to its descendant NIL leaves passes through
     the same number of BLACK nodes (equal black-height).
  5. BST ordering: left.key < node.key < right.key.

Public API
----------
Core CRUD
    insert, delete, search, contains, update, clear

Metrics
    size, height, is_empty, min, max, black_height

Structural
    validate, is_red_black_valid, fix_insert, fix_delete, copy

Traversal / navigation
    predecessor, successor

Dunder
    __len__, __contains__, __iter__, __repr__

Complexity
----------
All major operations are O(log n) due to the RB height bound
  h ≤ 2 · log2(n + 1).
"""

from __future__ import annotations

from collections.abc import Generator, Iterator
from typing import Any

from pkstruct.trees.balancing import rotate
from pkstruct.trees.node import RBNode

RED: int = 0
BLACK: int = 1

# Sentinel NIL node – shared across the entire module, never modified.
_NIL: RBNode = RBNode(key=None, value=None)
_NIL.color = BLACK
_NIL.left = None  # type: ignore[assignment]
_NIL.right = None  # type: ignore[assignment]
_NIL.parent = None  # type: ignore[assignment]


def _is_nil(node: RBNode | None) -> bool:
    """Return *True* if *node* is the sentinel NIL or Python *None*."""
    return node is None or node is _NIL


class RedBlackTree:
    """Self-balancing Red-Black Tree.

    All major operations run in O(log n) time.  The four Red-Black
    invariants are enforced automatically on every insert and delete.

    Parameters
    ----------
    allow_duplicates:
        When *False* (default) duplicate keys update the stored value.
        When *True* duplicates raise ``ValueError``.
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def __init__(self, allow_duplicates: bool = False) -> None:
        self._root: RBNode = _NIL
        self._size: int = 0
        self._allow_duplicates = allow_duplicates

    # ------------------------------------------------------------------
    # Core CRUD
    # ------------------------------------------------------------------

    def insert(self, key: Any, value: Any = None) -> None:
        """Insert *key* with optional *value*, fixing RB invariants afterwards.

        Parameters
        ----------
        key:
            Comparable key used for BST ordering.
        value:
            Arbitrary payload stored alongside the key.

        Raises
        ------
        ValueError
            If ``allow_duplicates=True`` and *key* already exists.
        """
        existing = self._find(self._root, key)
        if not _is_nil(existing):
            if self._allow_duplicates:
                raise ValueError(f"Duplicate key: {key!r}")
            existing.value = value
            return

        new_node = RBNode(key, value)
        new_node.color = RED
        new_node.left = _NIL
        new_node.right = _NIL
        new_node.parent = _NIL

        # Standard BST insert
        parent: RBNode = _NIL
        current: RBNode = self._root
        while not _is_nil(current):
            parent = current
            current = current.left if key < current.key else current.right

        new_node.parent = parent
        if _is_nil(parent):
            self._root = new_node
        elif key < parent.key:
            parent.left = new_node
        else:
            parent.right = new_node

        self._size += 1
        self.fix_insert(new_node)

    def fix_insert(self, node: RBNode) -> None:
        """Restore Red-Black properties after a standard BST insert.

        Handles the three canonical cases:
          - Uncle is RED → recolor.
          - Uncle is BLACK, triangle → rotate to line case.
          - Uncle is BLACK, line → rotate and recolor.

        Parameters
        ----------
        node:
            The newly inserted RED node.
        """
        while not _is_nil(node.parent) and node.parent.color == RED:
            parent = node.parent
            grandparent = parent.parent
            if _is_nil(grandparent):
                break

            if parent is grandparent.left:
                uncle = grandparent.right
                if not _is_nil(uncle) and uncle.color == RED:
                    # Case 1: recolor
                    parent.color = BLACK
                    uncle.color = BLACK
                    grandparent.color = RED
                    node = grandparent
                else:
                    if node is parent.right:
                        # Case 2: triangle → convert to line
                        node = parent
                        new_root = rotate(node, "left", self._root)
                        if _is_nil(new_root.parent):
                            self._root = new_root
                        parent = node.parent
                        grandparent = parent.parent if not _is_nil(parent) else _NIL
                    # Case 3: line
                    if not _is_nil(parent):
                        parent.color = BLACK
                    if not _is_nil(grandparent):
                        grandparent.color = RED
                        new_root = rotate(grandparent, "right", self._root)
                        if _is_nil(new_root.parent):
                            self._root = new_root
            else:
                uncle = grandparent.left
                if not _is_nil(uncle) and uncle.color == RED:
                    # Case 1 (mirror)
                    parent.color = BLACK
                    uncle.color = BLACK
                    grandparent.color = RED
                    node = grandparent
                else:
                    if node is parent.left:
                        # Case 2 (mirror)
                        node = parent
                        new_root = rotate(node, "right", self._root)
                        if _is_nil(new_root.parent):
                            self._root = new_root
                        parent = node.parent
                        grandparent = parent.parent if not _is_nil(parent) else _NIL
                    # Case 3 (mirror)
                    if not _is_nil(parent):
                        parent.color = BLACK
                    if not _is_nil(grandparent):
                        grandparent.color = RED
                        new_root = rotate(grandparent, "left", self._root)
                        if _is_nil(new_root.parent):
                            self._root = new_root

        self._root.color = BLACK

    def delete(self, key: Any) -> None:
        """Remove *key* from the tree, fixing RB invariants afterwards.

        Parameters
        ----------
        key:
            Key to delete.

        Raises
        ------
        KeyError
            If *key* is not present.
        """
        target = self._find(self._root, key)
        if _is_nil(target):
            raise KeyError(key)
        self._rb_delete(target)
        self._size -= 1

    def _rb_delete(self, z: RBNode) -> None:
        """Standard Cormen RB-delete on node *z*."""
        y = z
        y_original_color = y.color
        x: RBNode

        if _is_nil(z.left):
            x = z.right
            self._transplant(z, z.right)
        elif _is_nil(z.right):
            x = z.left
            self._transplant(z, z.left)
        else:
            # y = minimum of z.right
            y = self._min_node(z.right)
            y_original_color = y.color
            x = y.right
            if y.parent is z:
                x.parent = y
            else:
                self._transplant(y, y.right)
                y.right = z.right
                y.right.parent = y
            self._transplant(z, y)
            y.left = z.left
            y.left.parent = y
            y.color = z.color

        if y_original_color == BLACK:
            self.fix_delete(x)

    def _transplant(self, u: RBNode, v: RBNode) -> None:
        """Replace subtree rooted at *u* with subtree rooted at *v*."""
        if _is_nil(u.parent):
            self._root = v
        elif u is u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        v.parent = u.parent

    def fix_delete(self, x: RBNode) -> None:
        """Restore Red-Black properties after a standard BST delete.

        Handles the four canonical cases for a doubly-black node *x*.

        Parameters
        ----------
        x:
            The node that may be doubly-black after deletion.
        """
        while x is not self._root and x.color == BLACK:
            parent = x.parent
            if _is_nil(parent):
                break
            if x is parent.left:
                w = parent.right
                if not _is_nil(w) and w.color == RED:
                    # Case 1
                    w.color = BLACK
                    parent.color = RED
                    new_root = rotate(parent, "left", self._root)
                    if _is_nil(new_root.parent):
                        self._root = new_root
                    w = x.parent.right

                w_left_black = _is_nil(w.left) or w.left.color == BLACK
                w_right_black = _is_nil(w.right) or w.right.color == BLACK

                if w_left_black and w_right_black:
                    # Case 2
                    if not _is_nil(w):
                        w.color = RED
                    x = x.parent
                else:
                    if w_right_black:
                        # Case 3
                        if not _is_nil(w.left):
                            w.left.color = BLACK
                        if not _is_nil(w):
                            w.color = RED
                        new_root = rotate(w, "right", self._root)
                        if _is_nil(new_root.parent):
                            self._root = new_root
                        w = x.parent.right

                    # Case 4
                    if not _is_nil(w):
                        w.color = x.parent.color
                    x.parent.color = BLACK
                    if not _is_nil(w) and not _is_nil(w.right):
                        w.right.color = BLACK
                    new_root = rotate(x.parent, "left", self._root)
                    if _is_nil(new_root.parent):
                        self._root = new_root
                    x = self._root
            else:
                w = parent.left
                if not _is_nil(w) and w.color == RED:
                    # Case 1 (mirror)
                    w.color = BLACK
                    parent.color = RED
                    new_root = rotate(parent, "right", self._root)
                    if _is_nil(new_root.parent):
                        self._root = new_root
                    w = x.parent.left

                w_left_black = _is_nil(w.left) or w.left.color == BLACK
                w_right_black = _is_nil(w.right) or w.right.color == BLACK

                if w_right_black and w_left_black:
                    # Case 2 (mirror)
                    if not _is_nil(w):
                        w.color = RED
                    x = x.parent
                else:
                    if w_left_black:
                        # Case 3 (mirror)
                        if not _is_nil(w.right):
                            w.right.color = BLACK
                        if not _is_nil(w):
                            w.color = RED
                        new_root = rotate(w, "left", self._root)
                        if _is_nil(new_root.parent):
                            self._root = new_root
                        w = x.parent.left

                    # Case 4 (mirror)
                    if not _is_nil(w):
                        w.color = x.parent.color
                    x.parent.color = BLACK
                    if not _is_nil(w) and not _is_nil(w.left):
                        w.left.color = BLACK
                    new_root = rotate(x.parent, "right", self._root)
                    if _is_nil(new_root.parent):
                        self._root = new_root
                    x = self._root

        x.color = BLACK

    def search(self, key: Any) -> Any | None:
        """Return the value for *key*, or *None* if absent.

        Parameters
        ----------
        key:
            Key to look up.
        """
        node = self._find(self._root, key)
        return node.value if not _is_nil(node) else None

    def contains(self, key: Any) -> bool:
        """Return *True* if *key* is present."""
        return not _is_nil(self._find(self._root, key))

    def update(self, key: Any, value: Any) -> None:
        """Update the value of an existing *key*.

        Parameters
        ----------
        key:
            Key to update.
        value:
            New value.

        Raises
        ------
        KeyError
            If *key* does not exist.
        """
        node = self._find(self._root, key)
        if _is_nil(node):
            raise KeyError(key)
        node.value = value

    def clear(self) -> None:
        """Remove all nodes from the tree."""
        self._root = _NIL
        self._size = 0

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    def size(self) -> int:
        """Return the number of stored nodes."""
        return self._size

    def is_empty(self) -> bool:
        """Return *True* if the tree is empty."""
        return _is_nil(self._root)

    def height(self) -> int:
        """Return the tree height (-1 for empty, 0 for a single node)."""
        return self._height(self._root)

    def _height(self, node: RBNode | None) -> int:
        if _is_nil(node):
            return -1
        return 1 + max(self._height(node.left), self._height(node.right))

    def min(self) -> Any:
        """Return the minimum key.

        Raises
        ------
        ValueError
            If the tree is empty.
        """
        if _is_nil(self._root):
            raise ValueError("Tree is empty")
        return self._min_node(self._root).key

    def max(self) -> Any:
        """Return the maximum key.

        Raises
        ------
        ValueError
            If the tree is empty.
        """
        if _is_nil(self._root):
            raise ValueError("Tree is empty")
        return self._max_node(self._root).key

    def black_height(self) -> int:
        """Return the black-height of the tree.

        Black-height is the number of BLACK nodes on any path from the
        root to a NIL leaf (not counting the root itself if it is RED,
        but the root is always BLACK in a valid RB tree).

        Returns
        -------
        int
            Black-height ≥ 0.  Returns 0 for an empty tree.
        """
        return self._black_height(self._root)

    def _black_height(self, node: RBNode | None) -> int:
        if _is_nil(node):
            return 0
        left_bh = self._black_height(node.left)
        add = 1 if node.color == BLACK else 0
        return add + left_bh

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def predecessor(self, key: Any) -> Any | None:
        """Return the in-order predecessor key, or *None*.

        Raises
        ------
        KeyError
            If *key* is not in the tree.
        """
        if not self.contains(key):
            raise KeyError(key)
        pred: RBNode | None = None
        node: RBNode = self._root
        while not _is_nil(node):
            if key < node.key:
                node = node.left
            elif key > node.key:
                pred = node
                node = node.right
            else:
                if not _is_nil(node.left):
                    pred = self._max_node(node.left)
                break
        return pred.key if pred is not None and not _is_nil(pred) else None

    def successor(self, key: Any) -> Any | None:
        """Return the in-order successor key, or *None*.

        Raises
        ------
        KeyError
            If *key* is not in the tree.
        """
        if not self.contains(key):
            raise KeyError(key)
        succ: RBNode | None = None
        node: RBNode = self._root
        while not _is_nil(node):
            if key > node.key:
                node = node.right
            elif key < node.key:
                succ = node
                node = node.left
            else:
                if not _is_nil(node.right):
                    succ = self._min_node(node.right)
                break
        return succ.key if succ is not None and not _is_nil(succ) else None

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def is_red_black_valid(self) -> bool:
        """Return *True* if all four Red-Black invariants hold.

        Checks:
          1. Root is BLACK.
          2. No RED node has a RED child.
          3. All root-to-NIL paths have the same black-height.
          4. BST ordering is correct.
        """
        if _is_nil(self._root):
            return True
        if self._root.color != BLACK:
            return False
        if not self._check_no_red_red(self._root):
            return False
        bh = [None]
        if not self._check_black_height(self._root, 0, bh):
            return False
        return self._check_bst_order(self._root, None, None)

    def validate(self) -> bool:
        """Alias for :meth:`is_red_black_valid`."""
        return self.is_red_black_valid()

    def _check_no_red_red(self, node: RBNode | None) -> bool:
        if _is_nil(node):
            return True
        if node.color == RED and ((not _is_nil(node.left) and node.left.color == RED) or (
            not _is_nil(node.right) and node.right.color == RED
        )):
            return False
        return self._check_no_red_red(node.left) and self._check_no_red_red(node.right)

    def _check_black_height(
        self,
        node: RBNode | None,
        current_bh: int,
        expected: list,
    ) -> bool:
        if _is_nil(node):
            if expected[0] is None:
                expected[0] = current_bh
            return expected[0] == current_bh
        add = 1 if node.color == BLACK else 0
        return self._check_black_height(
            node.left, current_bh + add, expected
        ) and self._check_black_height(node.right, current_bh + add, expected)

    def _check_bst_order(
        self,
        node: RBNode | None,
        lo: Any,
        hi: Any,
    ) -> bool:
        if _is_nil(node):
            return True
        if lo is not None and node.key <= lo:
            return False
        if hi is not None and node.key >= hi:
            return False
        return self._check_bst_order(node.left, lo, node.key) and self._check_bst_order(
            node.right, node.key, hi
        )

    # ------------------------------------------------------------------
    # Copy
    # ------------------------------------------------------------------

    def copy(self) -> RedBlackTree:
        """Return a deep copy of this tree (new nodes, same key/value/color)."""
        new_tree = RedBlackTree(allow_duplicates=self._allow_duplicates)
        new_tree._root = self._copy_node(self._root, _NIL)
        new_tree._size = self._size
        return new_tree

    def _copy_node(
        self,
        node: RBNode | None,
        parent: RBNode,
    ) -> RBNode:
        if _is_nil(node):
            return _NIL
        new_node = RBNode(node.key, node.value)
        new_node.color = node.color
        new_node.parent = parent
        new_node.left = self._copy_node(node.left, new_node)
        new_node.right = self._copy_node(node.right, new_node)
        return new_node

    # ------------------------------------------------------------------
    # Traversal helpers (private)
    # ------------------------------------------------------------------

    def _inorder(self, node: RBNode | None) -> Generator[Any, None, None]:
        if _is_nil(node):
            return
        yield from self._inorder(node.left)
        yield node.key
        yield from self._inorder(node.right)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _find(self, node: RBNode | None, key: Any) -> RBNode:
        while not _is_nil(node):
            if key < node.key:
                node = node.left
            elif key > node.key:
                node = node.right
            else:
                return node
        return _NIL

    def _min_node(self, node: RBNode) -> RBNode:
        while not _is_nil(node.left):
            node = node.left
        return node

    def _max_node(self, node: RBNode) -> RBNode:
        while not _is_nil(node.right):
            node = node.right
        return node

    # ------------------------------------------------------------------
    # Dunder methods
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """Return the number of nodes in the tree."""
        return self._size

    def __contains__(self, key: Any) -> bool:
        """Support ``key in tree`` syntax."""
        return self.contains(key)

    def __iter__(self) -> Iterator[Any]:
        """Iterate over keys in ascending (in-order) order."""
        return self._inorder(self._root)

    def __repr__(self) -> str:  # pragma: no cover
        keys = list(self._inorder(self._root))
        bh = self.black_height()
        return f"RedBlackTree(size={self._size}, black_height={bh}, keys={keys})"