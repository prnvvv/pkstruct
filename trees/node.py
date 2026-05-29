"""
pkstruct.trees.node
===================
Reusable node classes for all tree implementations.

Inheritance hierarchy::

    TreeNode
    ├── AVLNode          (adds height)
    ├── RBNode           (adds color)
    ├── SegmentNode      (adds segment metadata)
    └── IntervalNode     (adds interval + max_endpoint)

    BTreeNode            (multi-key / multi-child; standalone)
    BPlusNode            (leaf-linked variant of BTreeNode)

Every node exposes only the fields it needs; fields not relevant to a
concrete subclass are never allocated.
"""

from __future__ import annotations

from typing import Any, Generic, List, Optional, TypeVar

__all__ = [
    "TreeNode",
    "AVLNode",
    "RBNode",
    "BTreeNode",
    "BPlusNode",
    "SegmentNode",
    "IntervalNode",
]

KT = TypeVar("KT")  # key type
VT = TypeVar("VT")  # value type

# ---------------------------------------------------------------------------
# Sentinel colours used by RBNode (module-level so they are importable)
# ---------------------------------------------------------------------------
RED: int = 0
BLACK: int = 1


class TreeNode(Generic[KT, VT]):
    """
    Base binary-tree node.

    Attributes
    ----------
    key:
        Comparable key used for ordering.
    value:
        Arbitrary payload; defaults to *None*.
    left:
        Left child or *None*.
    right:
        Right child or *None*.
    parent:
        Parent node or *None* (root).
    """

    __slots__ = ("key", "value", "left", "right", "parent")

    def __init__(
        self,
        key: KT,
        value: Optional[VT] = None,
        *,
        left: Optional["TreeNode[KT, VT]"] = None,
        right: Optional["TreeNode[KT, VT]"] = None,
        parent: Optional["TreeNode[KT, VT]"] = None,
    ) -> None:
        self.key: KT = key
        self.value: Optional[VT] = value
        self.left: Optional["TreeNode[KT, VT]"] = left
        self.right: Optional["TreeNode[KT, VT]"] = right
        self.parent: Optional["TreeNode[KT, VT]"] = parent

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def is_leaf(self) -> bool:
        """Return *True* when the node has no children."""
        return self.left is None and self.right is None

    def is_root(self) -> bool:
        """Return *True* when the node has no parent."""
        return self.parent is None

    def is_left_child(self) -> bool:
        """Return *True* when this node is the left child of its parent."""
        return self.parent is not None and self.parent.left is self

    def is_right_child(self) -> bool:
        """Return *True* when this node is the right child of its parent."""
        return self.parent is not None and self.parent.right is self

    def sibling(self) -> Optional["TreeNode[KT, VT]"]:
        """Return the sibling node, or *None* if no parent."""
        if self.parent is None:
            return None
        return self.parent.right if self.is_left_child() else self.parent.left

    def __repr__(self) -> str:  # pragma: no cover
        return f"{type(self).__name__}(key={self.key!r}, value={self.value!r})"


# ---------------------------------------------------------------------------
# AVL Node
# ---------------------------------------------------------------------------


class AVLNode(TreeNode[KT, VT]):
    """
    AVL-tree node with *height* field.

    The height of a leaf is **1**; *None* sentinel nodes have height **0**.

    Attributes
    ----------
    height:
        Height of the sub-tree rooted at this node.
    """

    __slots__ = ("height",)

    def __init__(
        self,
        key: KT,
        value: Optional[VT] = None,
        *,
        left: Optional["AVLNode[KT, VT]"] = None,
        right: Optional["AVLNode[KT, VT]"] = None,
        parent: Optional["AVLNode[KT, VT]"] = None,
    ) -> None:
        super().__init__(key, value, left=left, right=right, parent=parent)
        self.height: int = 1


# ---------------------------------------------------------------------------
# Red-Black Node
# ---------------------------------------------------------------------------


class RBNode(TreeNode[KT, VT]):
    """
    Red-black tree node with *color* field.

    Attributes
    ----------
    color:
        Either :data:`RED` (0) or :data:`BLACK` (1).
    """

    __slots__ = ("color",)

    def __init__(
        self,
        key: KT,
        value: Optional[VT] = None,
        *,
        color: int = RED,
        left: Optional["RBNode[KT, VT]"] = None,
        right: Optional["RBNode[KT, VT]"] = None,
        parent: Optional["RBNode[KT, VT]"] = None,
    ) -> None:
        super().__init__(key, value, left=left, right=right, parent=parent)
        self.color: int = color

    def is_red(self) -> bool:
        """Return *True* when the node is red."""
        return self.color == RED

    def is_black(self) -> bool:
        """Return *True* when the node is black."""
        return self.color == BLACK


# ---------------------------------------------------------------------------
# B-Tree Node
# ---------------------------------------------------------------------------


class BTreeNode(Generic[KT, VT]):
    """
    Multi-key / multi-child node used by :class:`~pkstruct.trees.btree.BTree`.

    Attributes
    ----------
    keys:
        Ordered list of keys stored in this node.
    values:
        Parallel list of values; ``values[i]`` corresponds to ``keys[i]``.
    children:
        Child nodes; an internal node with *k* keys has *k+1* children.
        Leaf nodes have an empty children list.
    parent:
        Parent node or *None* (root).
    """

    __slots__ = ("keys", "values", "children", "parent")

    def __init__(self) -> None:
        self.keys: List[KT] = []
        self.values: List[Optional[VT]] = []
        self.children: List["BTreeNode[KT, VT]"] = []
        self.parent: Optional["BTreeNode[KT, VT]"] = None

    def is_leaf(self) -> bool:
        """Return *True* when this node has no children."""
        return len(self.children) == 0

    def __repr__(self) -> str:  # pragma: no cover
        return f"BTreeNode(keys={self.keys!r})"


# ---------------------------------------------------------------------------
# B+ Tree Node
# ---------------------------------------------------------------------------


class BPlusNode(Generic[KT, VT]):
    """
    Node for :class:`~pkstruct.trees.bplus.BPlusTree`.

    Leaf nodes carry ``(key, value)`` pairs and a ``next_leaf`` pointer.
    Internal nodes carry separator keys and child pointers.

    Attributes
    ----------
    keys:
        Ordered list of keys.
    values:
        Values stored only in leaf nodes.
    children:
        Child pointers (internal nodes only).
    parent:
        Parent node or *None*.
    next_leaf:
        Pointer to the next leaf (leaf nodes only); forms a linked list.
    is_leaf:
        *True* when this is a leaf node.
    """

    __slots__ = ("keys", "values", "children", "parent", "next_leaf", "is_leaf")

    def __init__(self, *, is_leaf: bool = False) -> None:
        self.keys: List[KT] = []
        self.values: List[Optional[VT]] = []           # leaf only
        self.children: List["BPlusNode[KT, VT]"] = []  # internal only
        self.parent: Optional["BPlusNode[KT, VT]"] = None
        self.next_leaf: Optional["BPlusNode[KT, VT]"] = None  # leaf only
        self.is_leaf: bool = is_leaf

    def __repr__(self) -> str:  # pragma: no cover
        return f"BPlusNode(keys={self.keys!r}, leaf={self.is_leaf})"


# ---------------------------------------------------------------------------
# Segment Tree Node
# ---------------------------------------------------------------------------


class SegmentNode:
    """
    Node for :class:`~pkstruct.trees.segment_tree.SegmentTree`.

    The tree is stored as a flat array (1-indexed), so this class is used
    only when a pointer-based implementation is preferred.

    Attributes
    ----------
    start:
        Left boundary of the segment (inclusive).
    end:
        Right boundary of the segment (inclusive).
    value:
        Aggregated value (sum / min / max / …) of the segment.
    lazy:
        Pending lazy-propagation value; *None* means no pending update.
    left:
        Left child segment node.
    right:
        Right child segment node.
    """

    __slots__ = ("start", "end", "value", "lazy", "left", "right")

    def __init__(
        self,
        start: int,
        end: int,
        value: Any = 0,
        lazy: Optional[Any] = None,
    ) -> None:
        self.start: int = start
        self.end: int = end
        self.value: Any = value
        self.lazy: Optional[Any] = lazy
        self.left: Optional["SegmentNode"] = None
        self.right: Optional["SegmentNode"] = None

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"SegmentNode([{self.start},{self.end}], "
            f"value={self.value!r}, lazy={self.lazy!r})"
        )


# ---------------------------------------------------------------------------
# Interval Tree Node
# ---------------------------------------------------------------------------


class IntervalNode(TreeNode[KT, VT]):
    """
    Augmented BST node used by :class:`~pkstruct.trees.interval_tree.IntervalTree`.

    Each node represents a half-open or closed interval ``[lo, hi]``.
    The ``max_endpoint`` field stores the maximum ``hi`` value in the
    sub-tree rooted at this node, enabling O(log n) overlap queries.

    Attributes
    ----------
    lo:
        Left endpoint of the interval (used as the BST key).
    hi:
        Right endpoint of the interval.
    max_endpoint:
        Maximum ``hi`` value in the sub-tree rooted here.
    """

    __slots__ = ("lo", "hi", "max_endpoint")

    def __init__(
        self,
        lo: KT,
        hi: KT,
        value: Optional[VT] = None,
        *,
        left: Optional["IntervalNode[KT, VT]"] = None,
        right: Optional["IntervalNode[KT, VT]"] = None,
        parent: Optional["IntervalNode[KT, VT]"] = None,
    ) -> None:
        super().__init__(lo, value, left=left, right=right, parent=parent)
        self.lo: KT = lo
        self.hi: KT = hi
        self.max_endpoint: KT = hi

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"IntervalNode([{self.lo!r}, {self.hi!r}], "
            f"max={self.max_endpoint!r})"
        )