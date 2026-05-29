"""
pkstruct.trees.traversal
========================
Unified traversal engine for binary trees.

A single :func:`traverse` entry-point supports eight traversal orders,
both recursive and iterative implementations, and an option to yield
raw :class:`~pkstruct.trees.node.TreeNode` objects instead of
``(key, value)`` tuples.

Supported orders
----------------
``inorder``
    Left → Root → Right  (produces sorted output for BSTs).
``preorder``
    Root → Left → Right.
``postorder``
    Left → Right → Root.
``levelorder``
    Breadth-first, level by level.
``reverse_inorder``
    Right → Root → Left  (produces descending output for BSTs).
``zigzag``
    Level-order with alternating left-right / right-left direction.
``boundary``
    Left boundary + leaves + right boundary (anti-clockwise).
``vertical``
    Nodes grouped by horizontal distance from the root.

All public functions are generator-based for memory efficiency.
"""

from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Generator
from typing import (
    Any,
)

from .node import TreeNode

__all__ = [
    "traverse",
    "inorder",
    "preorder",
    "postorder",
    "levelorder",
    "reverse_inorder",
    "zigzag",
    "boundary",
    "vertical",
]

# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

_Node = TreeNode | None
_Yield = TreeNode | tuple[Any, Any]

_ORDER_DISPATCH: dict[str, str] = {
    "inorder": "_inorder",
    "preorder": "_preorder",
    "postorder": "_postorder",
    "levelorder": "_levelorder",
    "reverse_inorder": "_reverse_inorder",
    "zigzag": "_zigzag",
    "boundary": "_boundary",
    "vertical": "_vertical",
}


# ---------------------------------------------------------------------------
# Public entry-point
# ---------------------------------------------------------------------------


def traverse(
    root: _Node,
    order: str = "inorder",
    *,
    recursive: bool = False,
    yield_nodes: bool = False,
) -> Generator[_Yield, None, None]:
    """
    Unified traversal generator.

    Parameters
    ----------
    root:
        Root node of the tree (or sub-tree).
    order:
        One of ``"inorder"``, ``"preorder"``, ``"postorder"``,
        ``"levelorder"``, ``"reverse_inorder"``, ``"zigzag"``,
        ``"boundary"``, ``"vertical"``.
    recursive:
        If *True* use the recursive implementation (may hit Python's
        default recursion limit for very deep trees).  Ignored for orders
        that are inherently iterative (``levelorder``, ``zigzag``,
        ``boundary``, ``vertical``).
    yield_nodes:
        If *True* yield raw :class:`~pkstruct.trees.node.TreeNode`
        objects; otherwise yield ``(key, value)`` tuples.

    Yields
    ------
    :class:`~pkstruct.trees.node.TreeNode` | tuple
        Nodes or ``(key, value)`` pairs in the requested order.

    Raises
    ------
    ValueError
        If *order* is not one of the supported strings.
    """
    if order not in _ORDER_DISPATCH:
        raise ValueError(
            f"Unknown traversal order {order!r}. "
            f"Choose from: {sorted(_ORDER_DISPATCH)}"
        )

    gen_func_name = _ORDER_DISPATCH[order]
    # Select recursive vs iterative variant
    rec_orders = {"inorder", "preorder", "postorder", "reverse_inorder"}
    use_recursive = recursive and order in rec_orders
    suffix = "_rec" if use_recursive else "_iter"
    func_name = gen_func_name + suffix
    # Fallback: some orders are iterative-only
    gen_func = globals().get(func_name) or globals()[gen_func_name + "_iter"]

    for node in gen_func(root):  # type: ignore[operator]
        if node is None:
            continue
        yield node if yield_nodes else (node.key, node.value)


# ---------------------------------------------------------------------------
# Public convenience wrappers
# ---------------------------------------------------------------------------


def inorder(
    root: _Node, *, recursive: bool = False, yield_nodes: bool = False
) -> Generator[_Yield, None, None]:
    """Inorder (Left → Root → Right) traversal."""
    yield from traverse(root, "inorder", recursive=recursive, yield_nodes=yield_nodes)


def preorder(
    root: _Node, *, recursive: bool = False, yield_nodes: bool = False
) -> Generator[_Yield, None, None]:
    """Preorder (Root → Left → Right) traversal."""
    yield from traverse(root, "preorder", recursive=recursive, yield_nodes=yield_nodes)


def postorder(
    root: _Node, *, recursive: bool = False, yield_nodes: bool = False
) -> Generator[_Yield, None, None]:
    """Postorder (Left → Right → Root) traversal."""
    yield from traverse(
        root, "postorder", recursive=recursive, yield_nodes=yield_nodes
    )


def levelorder(
    root: _Node, *, yield_nodes: bool = False
) -> Generator[_Yield, None, None]:
    """Breadth-first (level-order) traversal."""
    yield from traverse(root, "levelorder", yield_nodes=yield_nodes)


def reverse_inorder(
    root: _Node, *, recursive: bool = False, yield_nodes: bool = False
) -> Generator[_Yield, None, None]:
    """Reverse-inorder (Right → Root → Left) traversal."""
    yield from traverse(
        root, "reverse_inorder", recursive=recursive, yield_nodes=yield_nodes
    )


def zigzag(root: _Node, *, yield_nodes: bool = False) -> Generator[_Yield, None, None]:
    """Zigzag level-order traversal."""
    yield from traverse(root, "zigzag", yield_nodes=yield_nodes)


def boundary(root: _Node, *, yield_nodes: bool = False) -> Generator[_Yield, None, None]:
    """Boundary traversal (anti-clockwise)."""
    yield from traverse(root, "boundary", yield_nodes=yield_nodes)


def vertical(root: _Node, *, yield_nodes: bool = False) -> Generator[_Yield, None, None]:
    """Vertical-order traversal."""
    yield from traverse(root, "vertical", yield_nodes=yield_nodes)


# ---------------------------------------------------------------------------
# Internal: Inorder
# ---------------------------------------------------------------------------


def _inorder_rec(root: _Node) -> Generator[_Node, None, None]:
    if root is None:
        return
    yield from _inorder_rec(root.left)
    yield root
    yield from _inorder_rec(root.right)


def _inorder_iter(root: _Node) -> Generator[_Node, None, None]:
    stack: list[_Node] = []
    current: _Node = root
    while current or stack:
        while current:
            stack.append(current)
            current = current.left
        current = stack.pop()
        yield current
        current = current.right


# ---------------------------------------------------------------------------
# Internal: Preorder
# ---------------------------------------------------------------------------


def _preorder_rec(root: _Node) -> Generator[_Node, None, None]:
    if root is None:
        return
    yield root
    yield from _preorder_rec(root.left)
    yield from _preorder_rec(root.right)


def _preorder_iter(root: _Node) -> Generator[_Node, None, None]:
    if root is None:
        return
    stack: list[_Node] = [root]
    while stack:
        node = stack.pop()
        yield node
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)


# ---------------------------------------------------------------------------
# Internal: Postorder
# ---------------------------------------------------------------------------


def _postorder_rec(root: _Node) -> Generator[_Node, None, None]:
    if root is None:
        return
    yield from _postorder_rec(root.left)
    yield from _postorder_rec(root.right)
    yield root


def _postorder_iter(root: _Node) -> Generator[_Node, None, None]:
    if root is None:
        return
    stack: list[_Node] = [root]
    result: list[_Node] = []
    while stack:
        node = stack.pop()
        result.append(node)
        if node.left:
            stack.append(node.left)
        if node.right:
            stack.append(node.right)
    yield from reversed(result)


# ---------------------------------------------------------------------------
# Internal: Level-order
# ---------------------------------------------------------------------------


def _levelorder_iter(root: _Node) -> Generator[_Node, None, None]:
    if root is None:
        return
    queue: deque[_Node] = deque([root])
    while queue:
        node = queue.popleft()
        yield node
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)


# ---------------------------------------------------------------------------
# Internal: Reverse inorder
# ---------------------------------------------------------------------------


def _reverse_inorder_rec(root: _Node) -> Generator[_Node, None, None]:
    if root is None:
        return
    yield from _reverse_inorder_rec(root.right)
    yield root
    yield from _reverse_inorder_rec(root.left)


def _reverse_inorder_iter(root: _Node) -> Generator[_Node, None, None]:
    stack: list[_Node] = []
    current: _Node = root
    while current or stack:
        while current:
            stack.append(current)
            current = current.right
        current = stack.pop()
        yield current
        current = current.left


# ---------------------------------------------------------------------------
# Internal: Zigzag
# ---------------------------------------------------------------------------


def _zigzag_iter(root: _Node) -> Generator[_Node, None, None]:
    if root is None:
        return
    current_level: list[_Node] = [root]
    left_to_right = True
    while current_level:
        next_level: list[_Node] = []
        if left_to_right:
            for node in current_level:
                yield node
                if node.left:
                    next_level.append(node.left)
                if node.right:
                    next_level.append(node.right)
        else:
            for node in reversed(current_level):
                yield node
            # children still appended L→R for next reversal
            for node in current_level:
                if node.left:
                    next_level.append(node.left)
                if node.right:
                    next_level.append(node.right)
        current_level = next_level
        left_to_right = not left_to_right


# ---------------------------------------------------------------------------
# Internal: Boundary
# ---------------------------------------------------------------------------


def _boundary_iter(root: _Node) -> Generator[_Node, None, None]:
    """Anti-clockwise boundary: root → left boundary → leaves → right boundary."""
    if root is None:
        return
    yield root
    if root.left is None and root.right is None:
        return

    # Left boundary (top-down, excluding leaf)
    node: _Node = root.left
    while node:
        if not (node.left is None and node.right is None):
            yield node
        node = node.left if node.left else node.right

    # Leaves (left to right)
    yield from _leaves_iter(root.left)
    yield from _leaves_iter(root.right)

    # Right boundary (bottom-up, excluding leaf)
    right_boundary: list[_Node] = []
    node = root.right
    while node:
        if not (node.left is None and node.right is None):
            right_boundary.append(node)
        node = node.right if node.right else node.left
    yield from reversed(right_boundary)


def _leaves_iter(root: _Node) -> Generator[_Node, None, None]:
    if root is None:
        return
    if root.left is None and root.right is None:
        yield root
        return
    yield from _leaves_iter(root.left)
    yield from _leaves_iter(root.right)


# ---------------------------------------------------------------------------
# Internal: Vertical
# ---------------------------------------------------------------------------


def _vertical_iter(root: _Node) -> Generator[_Node, None, None]:
    """
    Yield nodes grouped by horizontal distance (HD) from the root.

    Nodes at the same HD are ordered top-down, left-before-right within
    the same level.
    """
    if root is None:
        return
    # BFS tracking horizontal distance
    hd_map: dict[int, list[_Node]] = defaultdict(list)
    queue: deque[tuple[_Node, int]] = deque([(root, 0)])
    while queue:
        node, hd = queue.popleft()
        hd_map[hd].append(node)
        if node.left:
            queue.append((node.left, hd - 1))
        if node.right:
            queue.append((node.right, hd + 1))
    for hd in sorted(hd_map):
        yield from hd_map[hd]


# ---------------------------------------------------------------------------
# Iterator helpers (public)
# ---------------------------------------------------------------------------


def iter_levels(
    root: _Node,
) -> Generator[list[tuple[Any, Any]], None, None]:
    """
    Yield one list of ``(key, value)`` pairs per level (BFS).

    Useful for pretty-printing or level-wise analysis.

    Parameters
    ----------
    root:
        Root of the tree.

    Yields
    ------
    list of (key, value)
        One list per level, left to right.
    """
    if root is None:
        return
    current_level: list[_Node] = [root]
    while current_level:
        yield [(n.key, n.value) for n in current_level]
        next_level: list[_Node] = []
        for node in current_level:
            if node.left:
                next_level.append(node.left)
            if node.right:
                next_level.append(node.right)
        current_level = next_level