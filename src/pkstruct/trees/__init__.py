"""
pkstruct.trees
==============

Tree data structures module for the pkstruct ecosystem.

Provides production-grade implementations of BST, AVL, Red-Black, B-Tree,
B+Tree, Segment Tree, Fenwick Tree, and Interval Tree with full traversal,
balancing, serialization, and ASCII visualization support.

Classes
-------
BinarySearchTree
    Unbalanced binary search tree with full interview-utility API.
AVLTree
    Self-balancing AVL tree (extends BinarySearchTree).
RedBlackTree
    Self-balancing red-black tree.
BTree
    Balanced multi-way search tree (B-Tree).
BPlusTree
    B+ Tree with leaf-linked chain for efficient range queries.
SegmentTree
    Segment tree with lazy propagation (sum/min/max/gcd/xor).
FenwickTree
    Binary indexed tree for prefix-sum operations.
IntervalTree
    Augmented AVL interval tree for overlap queries.

Exceptions
----------
TreeError, KeyNotFoundError, DuplicateKeyError, EmptyTreeError,
InvalidOrderError, InvalidOperationError, TreeBalanceError,
SerializationError, InvalidIntervalError, IndexOutOfBoundsError

Example
-------
>>> from pkstruct.trees import BinarySearchTree
>>> bst = BinarySearchTree()
>>> bst.insert(10)
>>> bst.insert(5)
>>> bst.insert(15)
>>> len(bst)
3
>>> list(bst)
[5, 10, 15]
"""

from pkstruct.trees.avl import AVLTree
from pkstruct.trees.bplus import BPlusTree
from pkstruct.trees.bst import BinarySearchTree
from pkstruct.trees.btree import BTree
from pkstruct.trees.exceptions import (
    DuplicateKeyError,
    EmptyTreeError,
    IndexOutOfBoundsError,
    InvalidIntervalError,
    InvalidOperationError,
    InvalidOrderError,
    KeyNotFoundError,
    SerializationError,
    TreeBalanceError,
    TreeError,
)
from pkstruct.trees.fenwick_tree import FenwickTree
from pkstruct.trees.interval_tree import IntervalTree
from pkstruct.trees.red_black import RedBlackTree
from pkstruct.trees.segment_tree import SegmentTree

__all__ = [
    "BinarySearchTree",
    "AVLTree",
    "RedBlackTree",
    "BTree",
    "BPlusTree",
    "SegmentTree",
    "FenwickTree",
    "IntervalTree",
    "TreeError",
    "KeyNotFoundError",
    "DuplicateKeyError",
    "EmptyTreeError",
    "InvalidOrderError",
    "InvalidOperationError",
    "TreeBalanceError",
    "SerializationError",
    "InvalidIntervalError",
    "IndexOutOfBoundsError",
]

__version__ = "0.1.0"
__author__ = "pkstruct contributors"
