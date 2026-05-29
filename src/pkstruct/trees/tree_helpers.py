"""
Shared tree helper utilities for pkstruct.trees.

This module provides pure utility functions that are genuinely reusable across
multiple tree types (BST, AVL, Red-Black, B-Tree, Segment, Interval, etc.).

Design contract:
    - Functions operate on duck-typed node objects (Protocol-style).
    - No import from other pkstruct.trees sub-modules to prevent circular deps.
    - No balancing or traversal logic (those live in balancing.py / traversal.py).
    - All functions are stateless (no global state).

Reusable helpers:
    calculate_height(node)
    calculate_size(node)
    is_leaf(node)
    is_internal(node)
    clone_subtree(node, node_factory)
    tree_depth(node)             alias for calculate_height
    count_nodes(node)            alias for calculate_size
    count_leaves(node)
    validate_bst_order(node, key_fn, min_val, max_val)
"""

from __future__ import annotations

import math
from typing import Any, Callable, Generic, Iterable, List, Optional, Protocol, TypeVar


# ---------------------------------------------------------------------------
# Structural protocol
# ---------------------------------------------------------------------------

class _HasChildren(Protocol):
    """Minimal structural protocol for a binary tree node."""
    left: Optional[Any]
    right: Optional[Any]


class _HasKey(_HasChildren, Protocol):
    """Node with a comparable key (for BST validation)."""
    key: Any


N = TypeVar("N")


# ---------------------------------------------------------------------------
# Height / depth
# ---------------------------------------------------------------------------

def calculate_height(node: Optional[Any]) -> int:
    """
    Compute the height of the subtree rooted at node.

    Height of a single-node tree is 1; height of None is 0.

    Complexity: O(n)  — visits every node.

    Args:
        node: Root of a subtree. Must expose `.left` and `.right` attributes,
              or be None.

    Returns:
        Integer height of the subtree.

    Example:
        >>> calculate_height(None)
        0
        >>> calculate_height(leaf_node)
        1
    """
    if node is None:
        return 0
    return 1 + max(calculate_height(node.left), calculate_height(node.right))


def tree_depth(node: Optional[Any]) -> int:
    """
    Alias for calculate_height().

    Returns the depth (height) of the subtree rooted at node.

    Complexity: O(n)
    """
    return calculate_height(node)


# ---------------------------------------------------------------------------
# Size / count
# ---------------------------------------------------------------------------

def calculate_size(node: Optional[Any]) -> int:
    """
    Count all nodes in the subtree rooted at node.

    Complexity: O(n)

    Args:
        node: Root of a subtree (exposes `.left` and `.right`), or None.

    Returns:
        Total number of nodes in the subtree.
    """
    if node is None:
        return 0
    return 1 + calculate_size(node.left) + calculate_size(node.right)


def count_nodes(node: Optional[Any]) -> int:
    """
    Alias for calculate_size().

    Count all nodes in the subtree.

    Complexity: O(n)
    """
    return calculate_size(node)


def count_leaves(node: Optional[Any]) -> int:
    """
    Count leaf nodes (nodes with no children) in the subtree.

    Complexity: O(n)

    Args:
        node: Root of a subtree (exposes `.left` and `.right`), or None.

    Returns:
        Number of leaf nodes.
    """
    if node is None:
        return 0
    if node.left is None and node.right is None:
        return 1
    return count_leaves(node.left) + count_leaves(node.right)


# ---------------------------------------------------------------------------
# Leaf / internal classification
# ---------------------------------------------------------------------------

def is_leaf(node: Any) -> bool:
    """
    Return True if node has no children.

    Works for any node type that exposes `.left` and `.right` attributes.

    Complexity: O(1)

    Args:
        node: A tree node (not None).

    Returns:
        True if both children are None.

    Raises:
        AttributeError: If node does not expose `.left` / `.right`.
    """
    return node.left is None and node.right is None


def is_internal(node: Any) -> bool:
    """
    Return True if node has at least one child.

    Complement of is_leaf().

    Complexity: O(1)

    Args:
        node: A tree node (not None).

    Returns:
        True if node has at least one child.
    """
    return not is_leaf(node)


# ---------------------------------------------------------------------------
# Clone
# ---------------------------------------------------------------------------

def clone_subtree(
    node: Optional[N],
    node_factory: Callable[[N], N],
) -> Optional[N]:
    """
    Deep-clone a subtree using a caller-supplied node factory.

    The factory receives the original node and must return a *new* node whose
    key/value fields are copied but whose `.left`/`.right` are unset (they will
    be wired by this function).

    This design is node-type agnostic: each tree module supplies its own
    factory that knows what fields to copy.

    Complexity: O(n)

    Args:
        node:         Root of the subtree to clone (or None).
        node_factory: ``f(original) -> new_node`` — creates a shallow copy of
                      a single node (fields only, children ignored).

    Returns:
        Root of the cloned subtree, or None if node is None.

    Example:
        >>> def bst_factory(n):
        ...     clone = BSTNode(n.key, n.value)
        ...     return clone
        >>> new_root = clone_subtree(tree.root, bst_factory)
    """
    if node is None:
        return None
    new_node: N = node_factory(node)
    new_node.left = clone_subtree(node.left, node_factory)   # type: ignore[attr-defined]
    new_node.right = clone_subtree(node.right, node_factory)  # type: ignore[attr-defined]
    return new_node


# ---------------------------------------------------------------------------
# BST order validation
# ---------------------------------------------------------------------------

def validate_bst_order(
    node: Optional[Any],
    key_fn: Callable[[Any], Any] = lambda n: n.key,
    min_val: Any = -math.inf,
    max_val: Any = math.inf,
) -> bool:
    """
    Recursively verify BST ordering invariant for a binary subtree.

    Each node's key must satisfy min_val < key < max_val (strict).

    Compatible with any node type that exposes `.left`, `.right`, and a
    key attribute/property accessible via key_fn.

    Complexity: O(n)

    Args:
        node:    Root of subtree to validate (or None).
        key_fn:  Callable that extracts a comparable key from a node.
                 Defaults to ``lambda n: n.key``.
        min_val: Exclusive lower bound for all keys in this subtree.
        max_val: Exclusive upper bound for all keys in this subtree.

    Returns:
        True if the BST ordering invariant holds throughout.

    Raises:
        ValueError: If an ordering violation is detected.
    """
    if node is None:
        return True
    key = key_fn(node)
    if key <= min_val:
        raise ValueError(
            f"BST order violation: key {key!r} is not > lower bound {min_val!r}."
        )
    if key >= max_val:
        raise ValueError(
            f"BST order violation: key {key!r} is not < upper bound {max_val!r}."
        )
    validate_bst_order(node.left, key_fn, min_val, key)
    validate_bst_order(node.right, key_fn, key, max_val)
    return True


# ---------------------------------------------------------------------------
# Path / level utilities
# ---------------------------------------------------------------------------

def path_to_node(
    root: Optional[Any],
    key_fn: Callable[[Any], Any],
    target_key: Any,
) -> Optional[List[Any]]:
    """
    Return the path (list of nodes) from root to the node with target_key.

    Uses BST ordering (key_fn) for O(log n) traversal in a balanced BST, but
    falls back correctly for any binary tree if keys are unique.

    Complexity: O(log n) for balanced BST, O(n) worst-case.

    Args:
        root:        Root of the tree.
        key_fn:      Extracts a comparable key from a node.
        target_key:  The key to search for.

    Returns:
        List of nodes from root to target (inclusive), or None if not found.
    """
    path: List[Any] = []
    node = root
    while node is not None:
        path.append(node)
        k = key_fn(node)
        if target_key == k:
            return path
        elif target_key < k:
            node = node.left
        else:
            node = node.right
    return None


def level_of_node(
    root: Optional[Any],
    key_fn: Callable[[Any], Any],
    target_key: Any,
) -> Optional[int]:
    """
    Return the 0-based level (depth) of the node with target_key.

    Root is at level 0.

    Complexity: O(log n) for balanced BST, O(n) worst-case.

    Args:
        root:        Root of the tree.
        key_fn:      Extracts a comparable key from a node.
        target_key:  The key to locate.

    Returns:
        Integer level, or None if key is not found.
    """
    path = path_to_node(root, key_fn, target_key)
    return len(path) - 1 if path is not None else None


# ---------------------------------------------------------------------------
# Width utilities
# ---------------------------------------------------------------------------

def max_width(root: Optional[Any]) -> int:
    """
    Return the maximum number of nodes on any single level (BFS width).

    Complexity: O(n)

    Args:
        root: Root of the tree.

    Returns:
        Maximum level width, or 0 for an empty tree.
    """
    if root is None:
        return 0
    from collections import deque
    queue: deque = deque([root])
    max_w = 0
    while queue:
        width = len(queue)
        max_w = max(max_w, width)
        for _ in range(width):
            node = queue.popleft()
            if node.left is not None:
                queue.append(node.left)
            if node.right is not None:
                queue.append(node.right)
    return max_w