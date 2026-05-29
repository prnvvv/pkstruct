"""
pkstruct.trees.bst
==================
Production-grade Binary Search Tree with a rich interview-utility API.

Architecture
------------
- Single class ``BinarySearchTree`` backed by ``TreeNode`` from ``node.py``.
- All recursive traversal variants are dispatched through ``_traverse()``,
  eliminating duplication.
- No external dependencies; Python 3.9+ only.

Public API
----------
Core CRUD
    insert, delete, search, contains, update, clear

Metrics
    size, height, is_empty, min, max, floor, ceil

Navigation
    predecessor, successor

Structural utilities
    validate, copy, invert, is_balanced, diameter, width

Traversals (via __iter__ and explicit helpers)
    inorder, preorder, postorder, level_order,
    zigzag_order, vertical_order, boundary_traversal

Interview utilities
    find_lca, kth_smallest, kth_largest, range_query,
    path_sum, root_to_leaf_paths, serialize, deserialize

Dunder
    __len__, __contains__, __iter__, __repr__

Complexity (h = tree height)
-----------------------------
Search  O(h)
Insert  O(h)
Delete  O(h)
Space   O(n)
"""

from __future__ import annotations

import collections
import json
from typing import Any, Generator, Iterator, Optional

from pkstruct.trees.node import TreeNode


class BinarySearchTree:
    """An unbalanced Binary Search Tree.

    Parameters
    ----------
    allow_duplicates:
        When *False* (default) inserting an existing key updates the value.
        When *True* duplicate keys are rejected with ``ValueError``.
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def __init__(self, allow_duplicates: bool = False) -> None:
        self._root: Optional[TreeNode] = None
        self._size: int = 0
        self._allow_duplicates = allow_duplicates

    # ------------------------------------------------------------------
    # Core CRUD
    # ------------------------------------------------------------------

    def insert(self, key: Any, value: Any = None) -> None:
        """Insert *key* with an optional *value*.

        If *key* already exists and ``allow_duplicates`` is *False*, the
        stored value is updated in-place (O(h)).

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
        self._root, inserted = self._insert(self._root, key, value)
        if inserted:
            self._size += 1

    def _insert(
        self,
        node: Optional[TreeNode],
        key: Any,
        value: Any,
    ) -> tuple[Optional[TreeNode], bool]:
        if node is None:
            return TreeNode(key, value), True
        current = node
        parent: Optional[TreeNode] = None
        while current is not None:
            parent = current
            if key < current.key:
                current = current.left
            elif key > current.key:
                current = current.right
            else:
                if self._allow_duplicates:
                    raise ValueError(f"Duplicate key: {key!r}")
                current.value = value
                return node, False
        if key < parent.key:  # type: ignore[union-attr]
            parent.left = TreeNode(key, value)  # type: ignore[union-attr]
        else:
            parent.right = TreeNode(key, value)  # type: ignore[union-attr]
        return node, True

    def delete(self, key: Any) -> None:
        """Remove the node with *key*.

        Parameters
        ----------
        key:
            Key to delete.

        Raises
        ------
        KeyError
            If *key* is not found.
        """
        self._root, deleted = self._delete(self._root, key)
        if not deleted:
            raise KeyError(key)
        self._size -= 1

    def _delete(
        self,
        node: Optional[TreeNode],
        key: Any,
    ) -> tuple[Optional[TreeNode], bool]:
        if node is None:
            return None, False
        if key < node.key:
            node.left, deleted = self._delete(node.left, key)
        elif key > node.key:
            node.right, deleted = self._delete(node.right, key)
        else:
            deleted = True
            if node.left is None:
                return node.right, deleted
            if node.right is None:
                return node.left, deleted
            # Replace with in-order successor (min of right subtree)
            successor = self._min_node(node.right)
            node.key = successor.key
            node.value = successor.value
            node.right, _ = self._delete(node.right, successor.key)
        return node, deleted

    def search(self, key: Any) -> Optional[Any]:
        """Return the value associated with *key*, or *None* if absent.

        Parameters
        ----------
        key:
            Key to search.

        Returns
        -------
        Any or None
        """
        node = self._find(self._root, key)
        return node.value if node is not None else None

    def contains(self, key: Any) -> bool:
        """Return *True* if *key* is present in the tree."""
        return self._find(self._root, key) is not None

    def update(self, key: Any, value: Any) -> None:
        """Update the value of an existing *key*.

        Parameters
        ----------
        key:
            Key whose value should be updated.
        value:
            New value.

        Raises
        ------
        KeyError
            If *key* does not exist.
        """
        node = self._find(self._root, key)
        if node is None:
            raise KeyError(key)
        node.value = value

    def clear(self) -> None:
        """Remove all nodes from the tree."""
        self._root = None
        self._size = 0

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    def size(self) -> int:
        """Return the number of nodes currently in the tree."""
        return self._size

    def height(self) -> int:
        """Return the height of the tree (0 for a single-node tree, -1 if empty)."""
        return self._height(self._root)

    def is_empty(self) -> bool:
        """Return *True* if the tree contains no nodes."""
        return self._root is None

    def min(self) -> Any:
        """Return the minimum key.

        Raises
        ------
        ValueError
            If the tree is empty.
        """
        if self._root is None:
            raise ValueError("Tree is empty")
        return self._min_node(self._root).key

    def max(self) -> Any:
        """Return the maximum key.

        Raises
        ------
        ValueError
            If the tree is empty.
        """
        if self._root is None:
            raise ValueError("Tree is empty")
        return self._max_node(self._root).key

    def floor(self, key: Any) -> Optional[Any]:
        """Return the largest key less than or equal to *key*, or *None*."""
        node = self._floor(self._root, key)
        return node.key if node is not None else None

    def _floor(self, node: Optional[TreeNode], key: Any) -> Optional[TreeNode]:
        if node is None:
            return None
        if key == node.key:
            return node
        if key < node.key:
            return self._floor(node.left, key)
        right = self._floor(node.right, key)
        return right if right is not None else node

    def ceil(self, key: Any) -> Optional[Any]:
        """Return the smallest key greater than or equal to *key*, or *None*."""
        node = self._ceil(self._root, key)
        return node.key if node is not None else None

    def _ceil(self, node: Optional[TreeNode], key: Any) -> Optional[TreeNode]:
        if node is None:
            return None
        if key == node.key:
            return node
        if key > node.key:
            return self._ceil(node.right, key)
        left = self._ceil(node.left, key)
        return left if left is not None else node

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def predecessor(self, key: Any) -> Optional[Any]:
        """Return the in-order predecessor key of *key*, or *None*.

        Raises
        ------
        KeyError
            If *key* is not in the tree.
        """
        if not self.contains(key):
            raise KeyError(key)
        pred: Optional[TreeNode] = None
        node = self._root
        while node is not None:
            if key < node.key:
                node = node.left
            elif key > node.key:
                pred = node
                node = node.right
            else:
                if node.left is not None:
                    pred = self._max_node(node.left)
                break
        return pred.key if pred is not None else None

    def successor(self, key: Any) -> Optional[Any]:
        """Return the in-order successor key of *key*, or *None*.

        Raises
        ------
        KeyError
            If *key* is not in the tree.
        """
        if not self.contains(key):
            raise KeyError(key)
        succ: Optional[TreeNode] = None
        node = self._root
        while node is not None:
            if key > node.key:
                node = node.right
            elif key < node.key:
                succ = node
                node = node.left
            else:
                if node.right is not None:
                    succ = self._min_node(node.right)
                break
        return succ.key if succ is not None else None

    # ------------------------------------------------------------------
    # Structural utilities
    # ------------------------------------------------------------------

    def validate(self) -> bool:
        """Verify BST ordering invariant for every node.

        Returns
        -------
        bool
            *True* if all nodes satisfy the BST property.
        """
        return self._validate(self._root, None, None)

    def _validate(
        self,
        node: Optional[TreeNode],
        lo: Any,
        hi: Any,
    ) -> bool:
        if node is None:
            return True
        if lo is not None and node.key <= lo:
            return False
        if hi is not None and node.key >= hi:
            return False
        return self._validate(node.left, lo, node.key) and self._validate(
            node.right, node.key, hi
        )

    def copy(self) -> "BinarySearchTree":
        """Return a deep copy of this tree (new nodes, same key/value pairs)."""
        new_tree: BinarySearchTree = BinarySearchTree(
            allow_duplicates=self._allow_duplicates
        )
        new_tree._root = self._copy_node(self._root)
        new_tree._size = self._size
        return new_tree

    def _copy_node(self, node: Optional[TreeNode]) -> Optional[TreeNode]:
        if node is None:
            return None
        new_node = TreeNode(node.key, node.value)
        new_node.left = self._copy_node(node.left)
        new_node.right = self._copy_node(node.right)
        return new_node

    def invert(self) -> None:
        """Mirror the tree in-place (swap left/right children at every node)."""
        self._invert(self._root)

    def _invert(self, node: Optional[TreeNode]) -> None:
        if node is None:
            return
        node.left, node.right = node.right, node.left
        self._invert(node.left)
        self._invert(node.right)

    def is_balanced(self) -> bool:
        """Return *True* if the tree is height-balanced (|left_h - right_h| ≤ 1 for every node)."""
        return self._check_balanced(self._root) != -2

    def _check_balanced(self, node: Optional[TreeNode]) -> int:
        """Return height if balanced, -2 as sentinel for unbalanced."""
        if node is None:
            return -1
        lh = self._check_balanced(node.left)
        if lh == -2:
            return -2
        rh = self._check_balanced(node.right)
        if rh == -2:
            return -2
        if abs(lh - rh) > 1:
            return -2
        return max(lh, rh) + 1

    def diameter(self) -> int:
        """Return the diameter (longest path between any two nodes, in edges)."""
        self._diameter_max: int = 0
        self._diameter_helper(self._root)
        return self._diameter_max

    def _diameter_helper(self, node: Optional[TreeNode]) -> int:
        if node is None:
            return -1
        lh = self._diameter_helper(node.left) + 1
        rh = self._diameter_helper(node.right) + 1
        self._diameter_max = max(self._diameter_max, lh + rh)
        return max(lh, rh)

    def width(self) -> int:
        """Return the maximum width (number of nodes) across all levels."""
        if self._root is None:
            return 0
        max_w = 0
        queue: collections.deque[TreeNode] = collections.deque([self._root])
        while queue:
            level_size = len(queue)
            max_w = max(max_w, level_size)
            for _ in range(level_size):
                node = queue.popleft()
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
        return max_w

    # ------------------------------------------------------------------
    # Interview utilities
    # ------------------------------------------------------------------

    def find_lca(self, key1: Any, key2: Any) -> Optional[Any]:
        """Return the key of the Lowest Common Ancestor of *key1* and *key2*.

        Parameters
        ----------
        key1, key2:
            Both must exist in the tree.

        Raises
        ------
        KeyError
            If either key is absent.
        """
        for k in (key1, key2):
            if not self.contains(k):
                raise KeyError(k)
        node = self._lca(self._root, key1, key2)
        return node.key if node is not None else None

    def _lca(
        self,
        node: Optional[TreeNode],
        k1: Any,
        k2: Any,
    ) -> Optional[TreeNode]:
        if node is None:
            return None
        if k1 < node.key and k2 < node.key:
            return self._lca(node.left, k1, k2)
        if k1 > node.key and k2 > node.key:
            return self._lca(node.right, k1, k2)
        return node

    def kth_smallest(self, k: int) -> Any:
        """Return the k-th smallest key (1-indexed).

        Raises
        ------
        ValueError
            If *k* is out of range.
        """
        result: list[Any] = []
        self._inorder_collect(self._root, result, k)
        if k < 1 or k > len(result):
            raise ValueError(f"k={k} is out of range [1, {self._size}]")
        return result[k - 1]

    def kth_largest(self, k: int) -> Any:
        """Return the k-th largest key (1-indexed).

        Raises
        ------
        ValueError
            If *k* is out of range.
        """
        if k < 1 or k > self._size:
            raise ValueError(f"k={k} is out of range [1, {self._size}]")
        # Reverse in-order (right → root → left)
        result: list[Any] = []
        self._reverse_inorder_collect(self._root, result, k)
        return result[k - 1]

    def _reverse_inorder_collect(
        self,
        node: Optional[TreeNode],
        result: list,
        limit: int,
    ) -> None:
        if node is None or len(result) >= limit:
            return
        self._reverse_inorder_collect(node.right, result, limit)
        if len(result) < limit:
            result.append(node.key)
            self._reverse_inorder_collect(node.left, result, limit)

    def range_query(self, lo: Any, hi: Any) -> list[Any]:
        """Return all keys in [*lo*, *hi*] in sorted order.

        Parameters
        ----------
        lo, hi:
            Inclusive lower and upper bounds.
        """
        result: list[Any] = []
        self._range_collect(self._root, lo, hi, result)
        return result

    def _range_collect(
        self,
        node: Optional[TreeNode],
        lo: Any,
        hi: Any,
        result: list,
    ) -> None:
        if node is None:
            return
        if lo < node.key:
            self._range_collect(node.left, lo, hi, result)
        if lo <= node.key <= hi:
            result.append(node.key)
        if hi > node.key:
            self._range_collect(node.right, lo, hi, result)

    def path_sum(self, target: int | float) -> bool:
        """Return *True* if any root-to-leaf path sums to *target*.

        Assumes keys are numeric.
        """
        return self._path_sum(self._root, target, 0)

    def _path_sum(
        self,
        node: Optional[TreeNode],
        target: int | float,
        current: int | float,
    ) -> bool:
        if node is None:
            return False
        current += node.key
        if node.left is None and node.right is None:
            return current == target
        return self._path_sum(node.left, target, current) or self._path_sum(
            node.right, target, current
        )

    def root_to_leaf_paths(self) -> list[list[Any]]:
        """Return all root-to-leaf paths as lists of keys."""
        paths: list[list[Any]] = []
        self._collect_paths(self._root, [], paths)
        return paths

    def _collect_paths(
        self,
        node: Optional[TreeNode],
        current: list[Any],
        paths: list[list[Any]],
    ) -> None:
        if node is None:
            return
        current.append(node.key)
        if node.left is None and node.right is None:
            paths.append(list(current))
        else:
            self._collect_paths(node.left, current, paths)
            self._collect_paths(node.right, current, paths)
        current.pop()

    def serialize(self) -> str:
        """Serialize the tree to a JSON string (level-order with null sentinels).

        Returns
        -------
        str
            JSON representation that can be passed to :meth:`deserialize`.
        """
        if self._root is None:
            return "[]"
        result: list[Optional[Any]] = []
        queue: collections.deque[Optional[TreeNode]] = collections.deque([self._root])
        while queue:
            node = queue.popleft()
            if node is None:
                result.append(None)
            else:
                result.append(node.key)
                queue.append(node.left)
                queue.append(node.right)
        # Trim trailing nulls
        while result and result[-1] is None:
            result.pop()
        return json.dumps(result)

    def deserialize(self, data: str) -> None:
        """Rebuild the tree from a JSON string produced by :meth:`serialize`.

        Clears any existing content before loading.

        Parameters
        ----------
        data:
            JSON string as returned by :meth:`serialize`.
        """
        self.clear()
        keys: list[Optional[Any]] = json.loads(data)
        if not keys:
            return
        self._root = TreeNode(keys[0])
        self._size = 1
        queue: collections.deque[TreeNode] = collections.deque([self._root])
        i = 1
        while queue and i < len(keys):
            node = queue.popleft()
            if i < len(keys) and keys[i] is not None:
                node.left = TreeNode(keys[i])
                self._size += 1
                queue.append(node.left)
            i += 1
            if i < len(keys) and keys[i] is not None:
                node.right = TreeNode(keys[i])
                self._size += 1
                queue.append(node.right)
            i += 1

    def boundary_traversal(self) -> list[Any]:
        """Return keys in boundary order: left boundary + leaves + right boundary (reversed).

        The result traces the outer edge of the tree anti-clockwise starting
        from the root.
        """
        if self._root is None:
            return []
        result: list[Any] = [self._root.key]
        self._left_boundary(self._root.left, result)
        self._leaves(self._root.left, result)
        self._leaves(self._root.right, result)
        self._right_boundary(self._root.right, result)
        return result

    def _left_boundary(self, node: Optional[TreeNode], result: list) -> None:
        if node is None or (node.left is None and node.right is None):
            return
        result.append(node.key)
        if node.left:
            self._left_boundary(node.left, result)
        else:
            self._left_boundary(node.right, result)

    def _right_boundary(self, node: Optional[TreeNode], result: list) -> None:
        if node is None or (node.left is None and node.right is None):
            return
        if node.right:
            self._right_boundary(node.right, result)
        else:
            self._right_boundary(node.left, result)
        result.append(node.key)

    def _leaves(self, node: Optional[TreeNode], result: list) -> None:
        if node is None:
            return
        if node.left is None and node.right is None:
            result.append(node.key)
            return
        self._leaves(node.left, result)
        self._leaves(node.right, result)

    def vertical_order(self) -> list[list[Any]]:
        """Return keys grouped by vertical column, left to right.

        Each inner list contains the keys at the same horizontal distance
        from the root, sorted top-to-bottom within the column.
        """
        if self._root is None:
            return []
        col_map: dict[int, list[Any]] = collections.defaultdict(list)
        queue: collections.deque[tuple[TreeNode, int]] = collections.deque(
            [(self._root, 0)]
        )
        while queue:
            node, col = queue.popleft()
            col_map[col].append(node.key)
            if node.left:
                queue.append((node.left, col - 1))
            if node.right:
                queue.append((node.right, col + 1))
        return [col_map[c] for c in sorted(col_map)]

    def zigzag_order(self) -> list[list[Any]]:
        """Return keys level by level, alternating left-to-right and right-to-left."""
        if self._root is None:
            return []
        result: list[list[Any]] = []
        queue: collections.deque[TreeNode] = collections.deque([self._root])
        left_to_right = True
        while queue:
            level_size = len(queue)
            level: collections.deque[Any] = collections.deque()
            for _ in range(level_size):
                node = queue.popleft()
                if left_to_right:
                    level.append(node.key)
                else:
                    level.appendleft(node.key)
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
            result.append(list(level))
            left_to_right = not left_to_right
        return result

    # ------------------------------------------------------------------
    # Traversal helpers
    # ------------------------------------------------------------------

    def _traverse(
        self,
        order: str = "inorder",
    ) -> Generator[Any, None, None]:
        """Unified traversal generator.

        Parameters
        ----------
        order:
            One of ``"inorder"``, ``"preorder"``, ``"postorder"``,
            ``"levelorder"``.
        """
        if order == "inorder":
            yield from self._inorder(self._root)
        elif order == "preorder":
            yield from self._preorder(self._root)
        elif order == "postorder":
            yield from self._postorder(self._root)
        elif order == "levelorder":
            yield from self._levelorder()
        else:
            raise ValueError(f"Unknown traversal order: {order!r}")

    def _inorder(self, node: Optional[TreeNode]) -> Generator[Any, None, None]:
        stack: list[TreeNode] = []
        current = node
        while stack or current:
            while current:
                stack.append(current)
                current = current.left
            current = stack.pop()
            yield current.key
            current = current.right

    def _preorder(self, node: Optional[TreeNode]) -> Generator[Any, None, None]:
        if node is None:
            return
        stack: list[TreeNode] = [node]
        while stack:
            current = stack.pop()
            yield current.key
            if current.right:
                stack.append(current.right)
            if current.left:
                stack.append(current.left)

    def _postorder(self, node: Optional[TreeNode]) -> Generator[Any, None, None]:
        if node is None:
            return
        stack1: list[TreeNode] = [node]
        stack2: list[TreeNode] = []
        while stack1:
            current = stack1.pop()
            stack2.append(current)
            if current.left:
                stack1.append(current.left)
            if current.right:
                stack1.append(current.right)
        while stack2:
            yield stack2.pop().key

    def _levelorder(self) -> Generator[Any, None, None]:
        if self._root is None:
            return
        queue: collections.deque[TreeNode] = collections.deque([self._root])
        while queue:
            node = queue.popleft()
            yield node.key
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

    def _inorder_collect(
        self,
        node: Optional[TreeNode],
        result: list,
        limit: int,
    ) -> None:
        if node is None or len(result) >= limit:
            return
        self._inorder_collect(node.left, result, limit)
        if len(result) < limit:
            result.append(node.key)
            self._inorder_collect(node.right, result, limit)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _find(self, node: Optional[TreeNode], key: Any) -> Optional[TreeNode]:
        while node is not None:
            if key < node.key:
                node = node.left
            elif key > node.key:
                node = node.right
            else:
                return node
        return None

    def _height(self, node: Optional[TreeNode]) -> int:
        if node is None:
            return -1
        return 1 + max(self._height(node.left), self._height(node.right))

    def _min_node(self, node: TreeNode) -> TreeNode:
        while node.left is not None:
            node = node.left
        return node

    def _max_node(self, node: TreeNode) -> TreeNode:
        while node.right is not None:
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
        return self._traverse("inorder")

    def __repr__(self) -> str:  # pragma: no cover
        keys = list(self._traverse("inorder"))
        return f"BinarySearchTree(size={self._size}, keys={keys})"