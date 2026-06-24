<div align="center">

# pkstruct

**A production-grade Python library providing comprehensive data structures and algorithms with type hints, thread safety, and extensive testing.**

[![PyPI]([https://img.shields.io/pypi/v/pkstruct)](https://pypi.org/project/pkstruct/](https://pypi.org/project/pkstruct/))
[![Python](https://img.shields.io/pypi/pyversions/pkstruct)](https://pypi.org/project/pkstruct/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-899_✔️-success)](https://github.com/prnvvv/pkstruct)
[![Type Checked](https://img.shields.io/badge/mypy-strict-blue)](https://github.com/python/mypy)
[![Code Style](https://img.shields.io/badge/code%20style-ruff-000000)](https://github.com/astral-sh/ruff)

</div>

---

## Why pkstruct?

| Need | pkstruct gives you |
|------|-------------------|
| **Interview prep** | Linked lists, trees, graphs with LeetCode-style helpers (palindrome, cycle detection, LCA, topological sort, etc.) |
| **Production code** | Thread-safe structures (`threading.RLock`), strict type hints, 899+ tests |
| **Learning DSA** | Consistent API across all structures, built-in ASCII visualization, runtime help system |
| **Competitive programming** | Drop-in collection of trees (BST, AVL, Red-Black, Fenwick, Segment, Interval) and graph algorithms (Dijkstra, Kruskal, Tarjan, etc.) |

## 📦 Installation

```bash
pip install pkstruct
```

## 🚀 Quick Start

```python
import pkstruct
from pkstruct.linear import SinglyLinkedList, DoublyLinkedList, LinkedStack, LinkedQueue
from pkstruct.trees import BinarySearchTree, AVLTree, RedBlackTree, SegmentTree
from pkstruct.graphs import Graph, DirectedGraph, bfs, dfs, dijkstra, kruskal

# ── Linked Lists ────────────────────────────────────
sll = SinglyLinkedList.from_list([1, 2, 3, 4, 5])
sll.insert(99, position=2)   # [1, 2, 99, 3, 4, 5]
sll.sort()                    # [1, 2, 3, 4, 5, 99]
print(sll.visualize())
# [1] -> [2] -> [3] -> [4] -> [5] -> [99] -> NULL

# ── Trees ───────────────────────────────────────────
bst = BinarySearchTree()
bst.insert(10, value="ten")
bst.insert(5, value="five")
bst.insert(15, value="fifteen")
list(bst)                     # [5, 10, 15]

avl = AVLTree.from_list([1, 2, 3, 4, 5])
avl.height()                  # 2 (logarithmic)

st = SegmentTree([1, 2, 3, 4, 5], operation="sum")
st.query(1, 3)                # 9 (2 + 3 + 4)

# ── Graphs ──────────────────────────────────────────
g = Graph()
g.add_edge("A", "B", weight=4.0)
g.add_edge("B", "C", weight=2.0)
g.add_edge("A", "C", weight=1.0)

bfs(g, "A")                   # ['A', 'B', 'C']

dist, _ = dijkstra(g, "A")
dist["C"]                     # 1.0

kruskal(g)                    # [('A', 'C', 1.0), ('B', 'C', 2.0)]
```

## 🧭 Help System

Every structure is automatically registered — inspect anything at runtime:

```python
import pkstruct

pkstruct.help()                    # list all 20 structures
pkstruct.help(BinarySearchTree)    # class description + all methods
pkstruct.help("insert")            # insert signatures across all classes

sll = SinglyLinkedList()
sll.help()                         # instance-level help for this type
```

The registry is dynamic — new classes are picked up on first call.

---

## 📚 Data Structures

### `pkstruct.linear` — Linked Lists, Stacks, Queues, Deques

| Class | Description |
|-------|-------------|
| `SinglyLinkedList` | Forward-only linked list — merge sort, cycle detection, palindrome |
| `DoublyLinkedList` | Bidirectional linked list — backward traversal, two-pointer reverse |
| `CircularLinkedList` | Circular linked list — Josephus problem, head rotation |
| `ArrayStack` | LIFO stack backed by a dynamic array |
| `LinkedStack` | LIFO stack backed by `SinglyLinkedList` |
| `LinkedQueue` | FIFO queue backed by `SinglyLinkedList` |
| `CircularQueue` | Fixed-capacity FIFO queue backed by a ring buffer |
| `PriorityQueue` | Min-heap priority queue (heapq) |
| `LinkedDeque` | Double-ended queue backed by `DoublyLinkedList` |

### `pkstruct.trees` — Binary, Balanced, Multi-way, Range-Query Trees

| Class | Description |
|-------|-------------|
| `BinarySearchTree` | Unbalanced BST — full interview-utility API |
| `AVLTree` | Self-balancing AVL tree — strict O(log n) height |
| `RedBlackTree` | Self-balancing red-black tree — 5-color invariants |
| `BTree` | Balanced multi-way search tree — configurable order |
| `BPlusTree` | B+ Tree with leaf-linked chain for efficient range queries |
| `SegmentTree` | Segment tree with lazy propagation — sum/min/max/gcd/xor |
| `FenwickTree` | Binary indexed tree — prefix sums, range queries, lower bound |
| `IntervalTree` | Augmented interval tree — overlap queries, point stabbing |

### `pkstruct.graphs` — Graphs & Algorithms

| Class / Function | Description |
|------------------|-------------|
| `Graph` | Adjacency-list graph — directed/undirected, weighted |
| `DirectedGraph` | Directed graph — in-degree, out-degree, reverse, sources/sinks |
| `WeightedGraph` | Convenience class for weighted undirected graphs |
| `bfs` / `dfs` | Breadth-first and depth-first search |
| `bfs_paths` / `dfs_paths` | Find all paths between two vertices |
| `dijkstra` | Shortest paths — non-negative weights |
| `bellman_ford` | Shortest paths — negative weights allowed |
| `floyd_warshall` | All-pairs shortest paths |
| `reconstruct_path` / `reconstruct_path_fw` | Path reconstruction |
| `kruskal` / `prim` | Minimum spanning tree |
| `connected_components` | Find all connected components |
| `is_connected` / `is_bipartite` | Connectivity checks |
| `has_cycle` / `has_cycle_directed` | Cycle detection |
| `topological_sort_kahn` / `topological_sort_dfs` | Topological sort |
| `kosaraju` / `tarjan` | Strongly connected components |
| `visualize` / `adjacency_matrix` | ASCII visualization |

### Exceptions

| Module | Exceptions |
|--------|------------|
| **shared** | `PkstructError`, `ValidationError`, `IndexOutOfRangeError`, `ValueNotFoundError`, `EmptyStructureError`, `SerializationError`, `ConcurrencyError`, `InvalidRangeError` |
| **trees** | `TreeError`, `KeyNotFoundError`, `DuplicateKeyError`, `EmptyTreeError`, `InvalidOrderError`, `InvalidOperationError`, `TreeBalanceError`, `SerializationError`, `InvalidIntervalError`, `IndexOutOfBoundsError` |
| **graphs** | `GraphError`, `VertexNotFoundError`, `EdgeNotFoundError`, `InvalidGraphOperationError`, `NegativeCycleError`, `NoPathError` |

---

## 🎯 API Reference

### Linear — Linked Lists

```python
# ── Construction ──
ll = SinglyLinkedList()                     # empty
ll = SinglyLinkedList.from_list([1, 2, 3])  # from iterable
ll = SinglyLinkedList.from_json('{"items": [1, 2, 3]}')

# ── Insertion ──
ll.insert(99)                                # append at tail
ll.insert(99, position=0)                    # insert at head
ll.insert(99, before=50)                     # insert before value
ll.insert(99, after=50)                      # insert after value
ll.extend([1, 2, 3])                         # extend with iterable

# ── Deletion ──
ll.delete(position=2)                        # delete by index
ll.delete(value=42)                          # delete by value (first match)
ll.delete(rng=(1, 3))                        # delete sub-range
ll.clear()                                   # remove all

# ── Access ──
ll.get(0)                                    # by index
ll[0]                                        # via __getitem__
ll.index(42)                                 # find first occurrence
ll.count(42)                                 # count occurrences
ll.next(42)                                  # element after 42
ll.prev(42)                                  # element before 42
ll.head                                      # first element
ll.tail                                      # last element

# ── Mutation ──
ll[0] = 99                                   # via __setitem__
ll.swap(0, 2)                                # swap two positions
ll.reverse()                                 # full reverse
ll.reverse(start=1, end=3)                   # sub-range reverse
ll.rotate(shift=2)                           # rotate whole list right
ll.rotate(shift=2, start=1, end=4)           # rotate sub-range
ll.sort()                                    # ascending
ll.sort(reverse=True)                        # descending
ll.merge(other_list)                         # merge in-place

# ── Interview Helpers ──
ll.palindrome()                              # palindrome check
ll.detect_cycle()                            # Floyd's algorithm
ll.segregate_even_odd()                      # reorder
ll.partition(5)                              # pivot partition
ll.find_middle()                             # middle node (SLL)
ll.intersection_node(other)                  # intersecting node (SLL)
ll.remove_nth_from_end(2)                    # remove nth from end (SLL)
ll.delete_duplicates()                       # remove consecutive dupes (SLL)
ll.add_numbers(other)                        # add two numbers as lists (SLL)
ll.swap_pairs()                              # pairwise swap (SLL)

# ── Circular List Specifics ──
cll.rotate_head(steps=3, direction="right")  # rotate head pointer
cll.josephus(step=3)                         # Josephus survivor

# ── Serialization ──
json_str = ll.to_json()
ll = SinglyLinkedList.from_json(json_str)

# ── Visualization ──
print(ll.visualize())                        # ASCII art
print(ll.visualize(style="compact"))         # bracket format
info = ll.debug()                            # diagnostic dict
```

### Linear — Stacks, Queues, Deques

```python
# ── Stack ──
s = LinkedStack([1, 2, 3])
s.push(4)
s.pop()          # 4
s.peek()         # 3
len(s)           # 3

# LeetCode extras (ArrayStack)
ArrayStack().is_valid_parentheses("()[]{}")   # True
ArrayStack().evaluate_rpn(["2", "1", "+", "3", "*"])  # 9
ArrayStack().daily_temperatures([73, 74, 75]) # [1, 1, 0]

# ── Queue ──
q = LinkedQueue([1, 2, 3])
q.enqueue(4)
q.dequeue()      # 1
q.front()        # 2

# LeetCode extras
LinkedQueue().sliding_window_maximum([1,3,-1,-3,5,3,6,7], 3)  # [3,3,5,5,6,7]

# ── Circular Queue (fixed capacity) ──
cq = CircularQueue(capacity=3)
cq.enqueue(1); cq.enqueue(2); cq.enqueue(3)
cq.is_full()     # True
cq.dequeue()     # 1

# ── Priority Queue (min-heap) ──
pq = PriorityQueue()
pq.enqueue("task1", priority=3)
pq.enqueue("task2", priority=1)
pq.dequeue()     # "task2"

# LeetCode extras
PriorityQueue().kth_largest([3,2,1,5,6,4], 2)  # 5
PriorityQueue().top_k_frequent([1,1,1,2,2,3], 2)  # [1, 2]

# ── Deque ──
d = LinkedDeque([1, 2, 3])
d.append(4)
d.append(0, side="left")   # append to left side
d.pop()                    # 4 (from right)
d.pop(side="left")         # 0 (from left)
d.rotate(2)                # rotate right by 2
```

### Linear — Utilities

```python
from pkstruct.linear.utils import (
    merge_sorted_lists, detect_intersection, list_equal, to_array,
    ForwardIterator, BackwardIterator, CircularIterator,
    memory_usage, validate_integrity,
    benchmark_operations, compare_with_builtins, run_full_benchmark,
)

# Merge multiple sorted linked lists
merged = merge_sorted_lists(sll1, sll2)        # [1, 2, 3, 4, 5, 6]

# Detect node sharing
node_data = detect_intersection(sll1, sll2)    # by identity

# Compare equality
list_equal(sll1, sll2)                         # False

# Convert to plain list
to_array(sll1)                                 # [1, 3, 5]

# Specialized iterators
list(ForwardIterator(sll))                     # forward over SLL/DLL/CLL
list(BackwardIterator(dll))                    # backward over DLL only
circ = CircularIterator(cll, max_cycles=2)     # bounded circular iteration

# Diagnostics
memory_usage(sll)                              # estimated bytes
validate_integrity(sll)                        # {"valid": True, "errors": [], ...}

# Benchmarks
benchmark_operations(SinglyLinkedList)         # time insert/delete/get/search
compare_with_builtins()                        # pkstruct vs list vs deque
run_full_benchmark()                            # full suite
```

### Trees — Binary Search & Self-Balancing

```python
# ── Binary Search Tree ──
bst = BinarySearchTree()
bst.insert(10, value="ten")
bst.insert(5, value="five")
bst.search(10)               # ("ten", Node)
bst.delete(5)
len(bst)                     # 1

# Traversals (via standalone functions)
from pkstruct.trees.traversal import inorder, preorder, postorder, levelorder
list(inorder(bst.root))          # [5, 10, 15]
list(preorder(bst.root))         # [10, 5, 15]
list(postorder(bst.root))        # [5, 15, 10]
list(levelorder(bst.root))       # [10, 5, 15]
list(bst.zigzag_order())          # [10, 15, 5]

# Navigation Shortcuts
bst.root                     # root node
bst.parent(5)                # parent node
bst.children(10)             # [node(5), node(15)]
bst.left(10)                 # left child node
bst.right(10)                # right child node
bst.sibling(15)              # sibling node (node(5))

# Metrics & Queries
bst.find_lca(5, 15)          # 10 (lowest common ancestor)
bst.kth_smallest(1)          # 5
bst.kth_largest(1)           # 15
bst.range_query(5, 15)       # [5, 10, 15]
bst.path_sum(20)             # True
bst.root_to_leaf_paths()     # [[10, 5], [10, 15]]
bst.diameter()               # 2
bst.is_balanced()            # True
bst.invert()                 # mirror tree
bst.floor(12)                # 10
bst.ceil(12)                 # 15
bst.predecessor(15)          # 10
bst.successor(5)             # 10
bst.serialize() / bst.deserialize(data)
bst.from_sorted_list([1, 2, 3, 4, 5])
bst.boundary_traversal()     # anti-clockwise boundary
bst.vertical_order()         # grouped by horizontal distance

# ── AVL Tree (self-balancing) ──
avl = AVLTree()
avl.insert(3); avl.insert(2); avl.insert(1)    # triggers LL rotation
avl.is_avl_valid()           # True
avl.height()                 # 1
avl.balance_factor(3)        # 0 (balanced)
avl.rebalance_node(node)     # manual rebalance

# ── Red-Black Tree ──
rbt = RedBlackTree()
rbt.insert(10); rbt.insert(20); rbt.insert(30)
rbt.validate()               # checks 5 red-black invariants
rbt.black_height()           # black-height of tree
```

### Trees — B-Tree & B+ Tree

```python
# ── B-Tree ──
bt = BTree(order=4)
bt.insert(10); bt.insert(20); bt.insert(5)
bt.search(10)                # True
bt.delete(10)                # rebalancing triggered

# ── B+ Tree ──
bpt = BPlusTree(order=4)
bpt.insert(10); bpt.insert(20); bpt.insert(5)
bpt.range_query(5, 15)       # efficient via leaf chain
for key, value in bpt.leaf_traversal():
    print(key, value)        # iterate leaf chain
```

### Trees — Segment, Fenwick, Interval

```python
# ── Segment Tree (lazy propagation) ──
st = SegmentTree([1, 2, 3, 4, 5], operation="sum")
st.query(0, 2)               # 6
st.range_update(0, 2, 3)     # range add
st.query(0, 2)               # 15
st.rebuild([5, 6, 7, 8])    # replace underlying data

# Operations: "sum", "min", "max", "gcd", "xor"
st_min = SegmentTree([3, 1, 4, 1, 5], operation="min")
st_min.query(0, 2)           # 1

# ── Fenwick Tree (Binary Indexed Tree) ──
ft = FenwickTree(5)
ft.add(1, 10); ft.add(2, 20)
ft.prefix_sum(2)             # 30
ft.range_query(1, 2)         # 30
ft.lower_bound(25)           # smallest index with prefix sum ≥ 25
ft.build([1, 2, 3, 4, 5])   # rebuild from array

# ── Interval Tree (augmented AVL) ──
it = IntervalTree()
it.insert(5, 10, "A")
it.insert(15, 20, "B")
it.overlap(8, 12)            # [(5, 10, "A")]
it.overlap_all(8, 12)        # all overlapping intervals
it.contains_point(7)         # [(5, 10, "A")]
it.merge_overlaps()          # merge all overlapping intervals
```

### Trees — Traversals & Utilities

```python
from pkstruct.trees.traversal import (
    traverse, inorder, preorder, postorder,
    levelorder, reverse_inorder, zigzag,
    boundary, vertical, iter_levels,
)
from pkstruct.trees.balancing import (
    rotate, rebalance, update_metadata,
    get_balance_factor, validate_balance,
)
from pkstruct.trees.tree_helpers import (
    calculate_height, calculate_size, count_leaves,
    is_leaf, is_internal, clone_subtree,
    validate_bst_order, path_to_node,
    level_of_node, max_width,
)
from pkstruct.trees.node import TreeNode

# Traversal functions (work on any binary tree root)
bst = BinarySearchTree()
for k in [10, 5, 15, 3, 7, 12, 20]: bst.insert(k)
root = bst.root

list(inorder(root))              # [(3,None), (5,None), ...]
list(preorder(root))             # [(10,None), (5,None), ...]
list(postorder(root))            # [(3,None), (7,None), ...]
list(levelorder(root))           # BFS order
list(reverse_inorder(root))      # descending order
list(zigzag(root))               # alternating direction
list(boundary(root))             # anti-clockwise boundary
list(vertical(root))             # grouped by horizontal distance

# Level-wise iteration
for level_nodes in iter_levels(root):
    print(level_nodes)           # one list per level

# Unified dispatcher
traverse(root, order="zigzag", yield_nodes=True)

# Balancing utilities
rotate(node, direction="left")       # single rotation
rebalance(node, strategy="avl")      # restore AVL balance
update_metadata(node)                # refresh cached height
get_balance_factor(node)             # left - right height
validate_balance(root)               # check entire tree

# Tree helpers
calculate_height(root)               # height of tree
calculate_size(root)                 # total node count
count_leaves(root)                   # leaf node count
is_leaf(node)                        # True if no children
is_internal(node)                    # True if has children
clone_subtree(root, lambda n: TreeNode(n.key, n.value))
validate_bst_order(root)             # strict BST invariant
path_to_node(root, lambda n: n.key, 7)    # [10, 5, 7]
level_of_node(root, lambda n: n.key, 12)  # 2
max_width(root)                      # maximum nodes on any level
```

### Graphs

```python
from pkstruct.graphs import (
    Graph, DirectedGraph, WeightedGraph,
    bfs, dfs, bfs_paths, dfs_paths,
    dijkstra, bellman_ford, floyd_warshall,
    reconstruct_path, reconstruct_path_fw,
    kruskal, prim,
    connected_components, is_connected, is_bipartite,
    has_cycle, has_cycle_directed,
    topological_sort_kahn, topological_sort_dfs,
    kosaraju, tarjan,
    visualize, adjacency_matrix,
)

# ── Graph Construction ──
g = Graph()
g.add_vertex("A")
g.add_edge("A", "B", weight=4.0)
g.add_edge("B", "C", weight=2.0)
g.add_edge("A", "C", weight=1.0)

# ── Access ──
g.has_vertex("A")                    # True
g.has_edge("A", "B")                 # True
g.get_weight("A", "B")               # 4.0
g.get_neighbors("A")                 # {'B': 4.0, 'C': 1.0}
g.degree("A")                        # 2
g.order()                            # 3
g.edge_count()                       # 3
g.is_directed()                      # False

# ── Traversal ──
bfs(g, "A")                          # ['A', 'B', 'C']
dfs(g, "A")                          # ['A', 'B', 'C']
bfs_paths(g, "A", "C")               # all shortest paths
dfs_paths(g, "A", "C")               # all paths

# ── Shortest Paths ──
dist, pred = dijkstra(g, "A")
dist["C"]                            # 1.0
reconstruct_path(pred, "A", "C")     # ['A', 'C']

dist, pred = bellman_ford(g, "A")
dist_all, next_nodes = floyd_warshall(g)
reconstruct_path_fw(next_nodes, "A", "C")  # ['A', 'C']

# ── Minimum Spanning Tree ──
kruskal(g)                           # [('A', 'C', 1.0), ('B', 'C', 2.0)]
prim(g)                              # [('A', 'C', 1.0), ('B', 'C', 2.0)]

# ── Connectivity ──
connected_components(g)              # [['A', 'B', 'C']]
is_connected(g)                      # True
is_bipartite(g)                      # True
has_cycle(g)                         # True (triangle)
has_cycle_directed(dg)               # True

# ── Directed Graph ──
dg = DirectedGraph()
dg.add_edge("A", "B")
dg.add_edge("B", "C")
dg.add_edge("A", "C")
dg.in_degree("A")                    # 0
dg.out_degree("A")                   # 2
dg.sources()                         # ['A']
dg.sinks()                           # ['C']
dg.reverse()                         # reversed directed graph

topological_sort_kahn(dg)            # ['A', 'B', 'C']
topological_sort_dfs(dg)             # ['A', 'B', 'C']

# Strongly connected components
dg.add_edge("C", "A")
kosaraju(dg)                         # [['A', 'B', 'C']]
tarjan(dg)                           # [['A', 'B', 'C']]

# ── Weighted Graph ──
wg = WeightedGraph()
wg.add_edge("X", "Y", 3.5)
wg.add_edge("Y", "Z", 1.5)

# ── Visualization ──
print(visualize(g))
# Graph (directed=False, vertices=3, edges=3)
#   'A' -> 'B' [4.0] <-> 'C' [1.0]
#   'B' -> 'A' [4.0] <-> 'C' [2.0]
#   'C' -> 'A' [1.0] <-> 'B' [2.0]

adjacency_matrix(g)                  # numpy-style 2D list

# ── Exception Handling ──
from pkstruct.graphs.exceptions import VertexNotFoundError, NegativeCycleError

try:
    g.get_weight("X", "Y")
except VertexNotFoundError:
    print("Vertex does not exist")

# ── LeetCode-Style Extras ──
Graph().number_of_islands(grid)      # count islands (2D grid)
Graph().course_schedule(2, [[1,0]])  # True (can finish)
Graph().alien_order(["wrt","wrf","er","ett","rftt"])  # "wertf"
Graph().network_delay_time([[2,1,1],[2,3,1],[3,4,1]], 4, 2)  # 2
Graph().clone_graph(node)            # deep copy of graph
```

---

## ✨ Features

### Linked Lists Feature Matrix

| Feature | SLL | DLL | CLL |
|---------|:---:|:---:|:---:|
| Insert / Delete | ✅ | ✅ | ✅ |
| Sort (merge sort) | ✅ | ✅ | ✅ |
| Reverse (full/sub-range) | ✅ | ✅ | ✅ |
| Rotate (full/sub-range) | ✅ | ✅ | ✅ |
| Swap elements | ✅ | ✅ | ✅ |
| Cycle detection (Floyd's) | ✅ | ✅ | — |
| Palindrome check | ✅ | ✅ | — |
| Even-odd segregation | ✅ | ✅ | — |
| Intersection node | ✅ | — | — |
| Find middle | ✅ | — | — |
| Merge sorted | ✅ | — | — |
| Remove nth from end | ✅ | — | — |
| Add numbers (list as number) | ✅ | — | — |
| Swap pairs | ✅ | — | — |
| Josephus problem | — | — | ✅ |
| Head rotation | — | — | ✅ |
| JSON serialization | ✅ | ✅ | ✅ |
| ASCII visualization | ✅ | ✅ | ✅ |
| Thread-safe (RLock) | ✅ | ✅ | ✅ |
| `__slots__` nodes | ✅ | ✅ | ✅ |
| `next()` / `prev()` navigation | ✅ | ✅ | ✅ |
| `head` / `tail` properties | ✅ | ✅ | ✅ |

### Thread Safety

Every data structure embeds a `threading.RLock` — all mutating operations are atomic and re-entrant safe:

```python
sll = SinglyLinkedList.from_list([1, 2, 3])

# All mutating ops acquire self._lock automatically
sll.insert(99)
sll.sort()
sll.reverse()
```

### Serialization

```python
# JSON (linked lists)
json_str = sll.to_json()
restored = SinglyLinkedList.from_json(json_str)

# Custom serialize/deserialize (BST, AVL)
data = bst.serialize()
bst2 = BinarySearchTree()
bst2.deserialize(data)
```

### Visualization

```python
# Linked lists
print(sll.visualize())                  # [1] -> [2] -> [3] -> NULL
print(sll.visualize(style="compact"))   # [1, 2, 3]

# Trees
print(bst.visualize())                  # ASCII tree layout

# Graphs
print(visualize(g))                     # vertex -> neighbor(s) with weights
```

### Debug & Validation

```python
info = sll.debug()      # {"type": "SinglyLinkedList", "length": 3, "head": ...}
report = sll.validate() # {"valid": True, "errors": [], ...}
```

### Benchmarking

```python
from pkstruct.shared.benchmarking import timeit, compare

# Time a function
stats = timeit(sll.sort, iterations=1000)
# {"min": ..., "max": ..., "mean": ..., "median": ..., "stdev": ..., "total": ...}

# Compare two approaches
result = compare("list", list.sort, "pkstruct", sll.sort)
# {"winner": ..., "speedup": ...}

# Full suite
from pkstruct.linear.utils import benchmark_operations, compare_with_builtins, run_full_benchmark
benchmark_operations(SinglyLinkedList)
compare_with_builtins()
run_full_benchmark()
```

---

## 🔧 Development

```bash
# Clone and install
git clone https://github.com/prnvvv/pkstruct.git
cd pkstruct
pip install -e ".[dev]"

# Run tests (899 tests)
pytest -v

# Type check
mypy src/pkstruct

# Lint
ruff check src/pkstruct
```

---

## 📄 License

MIT © Prannavakhanth & Priyanka Kaliraj

## 🙌 Credits

pkstruct is created and maintained by:

- **Prannavakhanth** ([@prnvvv](https://github.com/prnvvv)) — Founder & Lead Maintainer
- **Priyanka Kaliraj** ([@pri-23-k](https://github.com/pri-23-k)) — Co-Founder & Maintainer
