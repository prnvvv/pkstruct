"""
pkstruct.trees.balancing
========================
Shared balancing utilities used by :class:`~pkstruct.trees.avl.AVLTree`
and :class:`~pkstruct.trees.red_black.RedBlackTree`.

Design goals
------------
* **Single** ``rotate`` function accepts a ``direction`` parameter instead
  of separate ``rotate_left`` / ``rotate_right`` methods.
* ``update_metadata`` is dispatched on node type so AVL and RB nodes each
  maintain their own invariants without branching inside tree classes.
* All functions operate on nodes directly and return the new sub-tree root
  when the root may change; callers are responsible for re-attaching.
"""

from __future__ import annotations

from typing import Optional, Union

from .node import AVLNode, RBNode, TreeNode

__all__ = [
    "rotate",
    "rebalance",
    "update_metadata",
    "get_balance_factor",
    "validate_balance",
]

_AnyNode = Union[AVLNode, RBNode, TreeNode]


# ---------------------------------------------------------------------------
# Height helpers (AVL)
# ---------------------------------------------------------------------------


def _height(node: Optional[AVLNode]) -> int:
    """Return the height of *node*, or 0 if *None*."""
    return node.height if node is not None else 0


def _update_height(node: AVLNode) -> None:
    """Recalculate ``node.height`` from its children."""
    node.height = 1 + max(_height(node.left), _height(node.right))  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Core rotation
# ---------------------------------------------------------------------------


def rotate(
    node: _AnyNode,
    direction: str,
    root: Optional[_AnyNode] = None,
) -> _AnyNode:
    """
    Perform a single rotation on *node* and return the new sub-tree root.

    Parameters
    ----------
    node:
        The node to rotate around (the "pivot's parent").
    direction:
        ``"left"`` or ``"right"``.
    root:
        The overall tree root.  When *node* **is** the tree root the
        caller must replace ``tree.root`` with the returned value.

    Returns
    -------
    _AnyNode
        The new sub-tree root after rotation.

    Raises
    ------
    ValueError
        If *direction* is not ``"left"`` or ``"right"``.
    ValueError
        If the required child is absent (cannot rotate).
    """
    if direction not in ("left", "right"):
        raise ValueError(f"direction must be 'left' or 'right', got {direction!r}.")

    if direction == "left":
        pivot = node.right
        if pivot is None:
            raise ValueError("Cannot rotate left: node has no right child.")
        node.right = pivot.left
        if pivot.left is not None and pivot.left.key is not None:
            pivot.left.parent = node
        pivot.parent = node.parent
        if node.parent is None:
            pass  # caller updates root
        elif node.parent.left is node:
            node.parent.left = pivot
        else:
            node.parent.right = pivot
        pivot.left = node
        node.parent = pivot
    else:  # right
        pivot = node.left
        if pivot is None:
            raise ValueError("Cannot rotate right: node has no left child.")
        node.left = pivot.right
        if pivot.right is not None and pivot.right.key is not None:
            pivot.right.parent = node
        pivot.parent = node.parent
        if node.parent is None:
            pass
        elif node.parent.left is node:
            node.parent.left = pivot
        else:
            node.parent.right = pivot
        pivot.right = node
        node.parent = pivot

    # Update heights for AVL nodes
    if isinstance(node, AVLNode):
        _update_height(node)
        _update_height(pivot)  # type: ignore[arg-type]

    return pivot  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Metadata update dispatch
# ---------------------------------------------------------------------------


def update_metadata(node: _AnyNode) -> None:
    """
    Recompute cached metadata stored on *node*.

    For :class:`~pkstruct.trees.node.AVLNode`: updates ``height``.
    For other node types: no-op (override as needed).

    Parameters
    ----------
    node:
        Node whose metadata should be refreshed.
    """
    if isinstance(node, AVLNode):
        _update_height(node)


# ---------------------------------------------------------------------------
# Balance factor
# ---------------------------------------------------------------------------


def get_balance_factor(node: Optional[AVLNode]) -> int:  # type: ignore[return]
    """
    Return the balance factor of *node* (left height − right height).

    Parameters
    ----------
    node:
        An :class:`~pkstruct.trees.node.AVLNode`, or *None*.

    Returns
    -------
    int
        Balance factor; **0** when *node* is *None*.
    """
    if node is None:
        return 0
    return _height(node.left) - _height(node.right)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# AVL rebalance
# ---------------------------------------------------------------------------


def rebalance(node: AVLNode, strategy: str = "avl") -> AVLNode:
    """
    Restore balance at *node* using the requested *strategy*.

    Currently the only supported strategy is ``"avl"``.

    Parameters
    ----------
    node:
        Node to rebalance.
    strategy:
        Balancing strategy identifier (currently only ``"avl"``).

    Returns
    -------
    AVLNode
        The new sub-tree root after rebalancing (may differ from *node*).

    Raises
    ------
    ValueError
        If *strategy* is not recognised.
    """
    if strategy != "avl":
        raise ValueError(f"Unknown rebalancing strategy: {strategy!r}.")

    _update_height(node)
    balance = get_balance_factor(node)

    # Left heavy
    if balance > 1:
        left_child: AVLNode = node.left  # type: ignore[assignment]
        if get_balance_factor(left_child) < 0:
            # Left-Right case
            node.left = rotate(left_child, "left")  # type: ignore[assignment]
            node.left.parent = node
        return rotate(node, "right")  # type: ignore[return-value]

    # Right heavy
    if balance < -1:
        right_child: AVLNode = node.right  # type: ignore[assignment]
        if get_balance_factor(right_child) > 0:
            # Right-Left case
            node.right = rotate(right_child, "right")  # type: ignore[assignment]
            node.right.parent = node
        return rotate(node, "left")  # type: ignore[return-value]

    return node


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_balance(root: Optional[AVLNode]) -> bool:
    """
    Recursively verify that every node satisfies the AVL balance property.

    Parameters
    ----------
    root:
        Root of the sub-tree to validate.

    Returns
    -------
    bool
        *True* when every node has ``|balance_factor| <= 1``.
    """

    def _check(node: Optional[AVLNode]) -> bool:
        if node is None:
            return True
        if abs(get_balance_factor(node)) > 1:
            return False
        return _check(node.left) and _check(node.right)  # type: ignore[arg-type]

    return _check(root)