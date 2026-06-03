"""
pkstruct - Production-grade modular data structures toolkit for Python.

This package provides industrial-strength implementations of fundamental
data structures with thread safety, serialization, visualization, and
comprehensive algorithmic helpers.

Modules
-------
graphs
    Graph, DirectedGraph, WeightedGraph, traversal, shortest path, MST, SCC
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

from pkstruct._display import display as _display_fn
from pkstruct._help import _register, module_help
from pkstruct.graphs import (
    Graph,
    DirectedGraph,
    WeightedGraph,
    bfs,
    dfs,
    bfs_paths,
    dfs_paths,
    dijkstra,
    bellman_ford,
    floyd_warshall,
    reconstruct_path,
    reconstruct_path_fw,
    kruskal,
    prim,
    connected_components,
    is_bipartite,
    is_connected,
    has_cycle,
    has_cycle_directed,
    topological_sort_kahn,
    topological_sort_dfs,
    kosaraju,
    tarjan,
    visualize,
    adjacency_matrix,
    GraphError,
    VertexNotFoundError,
    EdgeNotFoundError,
    InvalidGraphOperationError,
    NegativeCycleError,
    NoPathError,
)
from pkstruct.linear import (
    ArrayStack,
    CircularLinkedList,
    CircularQueue,
    ConcurrencyError,
    DoublyLinkedList,
    EmptyStructureError,
    IndexOutOfRangeError,
    InvalidRangeError,
    LinkedDeque,
    LinkedQueue,
    LinkedStack,
    PkstructError,
    PriorityQueue,
    QueueFullError,
    SinglyLinkedList,
    ValidationError,
    ValueNotFoundError,
)
from pkstruct.trees import (
    AVLTree,
    BinarySearchTree,
    BPlusTree,
    BTree,
    DuplicateKeyError,
    EmptyTreeError,
    FenwickTree,
    IndexOutOfBoundsError,
    IntervalTree,
    InvalidIntervalError,
    InvalidOperationError,
    InvalidOrderError,
    KeyNotFoundError,
    RedBlackTree,
    SegmentTree,
    SerializationError,
    TreeBalanceError,
    TreeError,
)


_STRUCTURES = [
    SinglyLinkedList,
    DoublyLinkedList,
    CircularLinkedList,
    ArrayStack,
    LinkedStack,
    LinkedQueue,
    CircularQueue,
    PriorityQueue,
    LinkedDeque,
    BinarySearchTree,
    AVLTree,
    RedBlackTree,
    BTree,
    BPlusTree,
    SegmentTree,
    FenwickTree,
    IntervalTree,
    Graph,
    DirectedGraph,
    WeightedGraph,
]

for _cls in _STRUCTURES:
    _register(_cls)


def help(target: object = None) -> str:  # noqa: A001
    """Display help for pkstruct structures and methods.

    Usage:
        pkstruct.help()            -> list all structures
        pkstruct.help(bst)         -> describe a structure
        pkstruct.help("insert")    -> describe a method

    Parameters
    ----------
    target:
        A structure class, a method name (str), or None to list all.
    """
    return module_help(target)


def display(ds: object, sep: str = " ") -> None:
    """Print the elements of a data structure separated by *sep*.

    Parameters
    ----------
    ds:
        Any pkstruct data structure.
    sep:
        Separator between elements (default: space).
    """
    _display_fn(ds, sep)


__all__ = [
    "help",
    "display",
    # Graphs
    "Graph",
    "DirectedGraph",
    "WeightedGraph",
    "bfs",
    "dfs",
    "bfs_paths",
    "dfs_paths",
    "dijkstra",
    "bellman_ford",
    "floyd_warshall",
    "reconstruct_path",
    "reconstruct_path_fw",
    "kruskal",
    "prim",
    "connected_components",
    "is_bipartite",
    "is_connected",
    "has_cycle",
    "has_cycle_directed",
    "topological_sort_kahn",
    "topological_sort_dfs",
    "kosaraju",
    "tarjan",
    "visualize",
    "adjacency_matrix",
    "GraphError",
    "VertexNotFoundError",
    "EdgeNotFoundError",
    "InvalidGraphOperationError",
    "NegativeCycleError",
    "NoPathError",
    # Linear
    "SinglyLinkedList",
    "DoublyLinkedList",
    "CircularLinkedList",
    "ArrayStack",
    "LinkedStack",
    "LinkedQueue",
    "CircularQueue",
    "PriorityQueue",
    "LinkedDeque",
    "QueueFullError",
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
    "InvalidIntervalError",
    "IndexOutOfBoundsError",
]

__version__ = "0.1.1"
__author__ = "pkstruct contributors"
