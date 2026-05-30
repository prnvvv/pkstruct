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

from pkstruct.graphs import (
    Graph,
    DirectedGraph,
    WeightedGraph,
    bfs,
    dfs,
    dijkstra,
    bellman_ford,
    floyd_warshall,
    kruskal,
    prim,
    connected_components,
    is_bipartite,
    has_cycle,
    topological_sort_kahn,
    topological_sort_dfs,
    kosaraju,
    tarjan,
    visualize,
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
    SerializationError,
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
    TreeBalanceError,
    TreeError,
)
from pkstruct.trees import (
    SerializationError as TreeSerializationError,
)

__all__ = [
    # Graphs
    "Graph",
    "DirectedGraph",
    "WeightedGraph",
    "bfs",
    "dfs",
    "dijkstra",
    "bellman_ford",
    "floyd_warshall",
    "kruskal",
    "prim",
    "connected_components",
    "is_bipartite",
    "has_cycle",
    "topological_sort_kahn",
    "topological_sort_dfs",
    "kosaraju",
    "tarjan",
    "visualize",
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
    "TreeSerializationError",
    "InvalidIntervalError",
    "IndexOutOfBoundsError",
]

__version__ = "0.1.0"
__author__ = "pkstruct contributors"
