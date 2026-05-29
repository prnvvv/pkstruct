"""
pkstruct - Production-grade modular data structures toolkit for Python.

This package provides industrial-strength implementations of fundamental
data structures with thread safety, serialization, visualization, and
comprehensive algorithmic helpers.

Modules
-------
trees
    BinarySearchTree, AVLTree, RedBlackTree, BTree, BPlusTree,
    SegmentTree, FenwickTree, IntervalTree
linear
    SinglyLinkedList, DoublyLinkedList, CircularLinkedList
shared
    Infrastructure components (exceptions, validators, serializers, etc.)

Example
-------
>>> from pkstruct import BinarySearchTree
>>> bst = BinarySearchTree()
>>> bst.insert(10)
>>> bst.insert(5)
>>> bst.insert(15)
>>> list(bst)
[5, 10, 15]
"""

from pkstruct.linear import (
    SinglyLinkedList,
    DoublyLinkedList,
    CircularLinkedList,
    PkstructError,
    ValidationError,
    IndexOutOfRangeError,
    ValueNotFoundError,
    EmptyStructureError,
    SerializationError,
    ConcurrencyError,
    InvalidRangeError,
)

from pkstruct.trees import (
    AVLTree,
    BinarySearchTree,
    BPlusTree,
    BTree,
    FenwickTree,
    IntervalTree,
    RedBlackTree,
    SegmentTree,
    TreeError,
    KeyNotFoundError,
    DuplicateKeyError,
    EmptyTreeError,
    InvalidOrderError,
    InvalidOperationError,
    TreeBalanceError,
    SerializationError as TreeSerializationError,
    InvalidIntervalError,
    IndexOutOfBoundsError,
)

__all__ = [
    # Linear
    "SinglyLinkedList",
    "DoublyLinkedList",
    "CircularLinkedList",
    "PkstructError",
    "ValidationError",
    "IndexOutOfRangeError",
    "ValueNotFoundError",
    "EmptyStructureError",
    "SerializationError",
    "ConcurrencyError",
    "InvalidRangeError",
    # Trees
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
    "TreeSerializationError",
    "InvalidIntervalError",
    "IndexOutOfBoundsError",
]

__version__ = "0.1.0"
__author__ = "pkstruct contributors"