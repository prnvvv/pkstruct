# pkstruct

**Industrial-grade data structures and algorithms for Python ≥ 3.10**

[![PyPI](https://img.shields.io/pypi/v/pkstruct)](https://pypi.org/project/pkstruct/)
[![Python](https://img.shields.io/pypi/pyversions/pkstruct)](https://pypi.org/project/pkstruct/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Installation

```bash
pip install pkstruct
```

## Quick Start

```python
import pkstruct
from pkstruct.linear import SinglyLinkedList, DoublyLinkedList

# Singly Linked List
sll = SinglyLinkedList.from_list([1, 2, 3, 4, 5])
sll.insert(99, position=2)       # [1, 2, 99, 3, 4, 5]
sll.sort()                       # [1, 2, 3, 4, 5, 99]
print(sll.visualize())
# [1] -> [2] -> [3] -> [4] -> [5] -> [99] -> NULL

# Node navigation on linear structures
dll = DoublyLinkedList.from_list([10, 20, 30])
dll.next(10)    # 20
dll.prev(30)    # 20

# Built-in help system
pkstruct.help()                # list all structures
pkstruct.help(SinglyLinkedList)  # describe a structure + its methods
pkstruct.help("insert")        # show all insert signatures + docs
sll.help()                     # instance-level help
```

```python
from pkstruct.trees import BinarySearchTree, AVLTree, RedBlackTree, SegmentTree

# Binary Search Tree
bst = BinarySearchTree()
bst.insert(10)
bst.insert(5)
bst.insert(15)
list(bst)          # [5, 10, 15]
10 in bst          # True

# Node navigation on trees
bst.root()         # root node
bst.left(10)       # left child node
bst.right(10)      # right child node
bst.parent(5)      # parent node (if maintained by tree)

# AVL Tree (self-balancing)
avl = AVLTree.from_list([1, 2, 3, 4, 5])
avl.height()       # 2 (logarithmic, not linear)

# Segment Tree with lazy propagation
st = SegmentTree([1, 2, 3, 4, 5], operation="sum")
st.query(1, 3)     # 9 (2 + 3 + 4)
st.update(2, 10)   # point update
st.range_update(1, 3, 5)  # range add
st.query(1, 3)     # 24
```

```python
from pkstruct.graphs import Graph, DirectedGraph, bfs, dfs, dijkstra, kruskal

# Create a weighted graph
g = Graph()
g.add_edge("A", "B", weight=4.0)
g.add_edge("B", "C", weight=2.0)
g.add_edge("A", "C", weight=1.0)

# Traversal
bfs(g, "A")              # ['A', 'B', 'C']

# Shortest paths
dist, _ = dijkstra(g, "A")
dist["C"]                # 1.0

# Minimum spanning tree
kruskal(g)               # [('A', 'C', 1.0), ('B', 'C', 2.0)]
```

## Modules

### `pkstruct.linear`

| Data Structure | Description |
|---|---|
| `SinglyLinkedList` | Forward-only linked list with merge sort, cycle detection, palindrome check |
| `DoublyLinkedList` | Bidirectional linked list with backward traversal |
| `CircularLinkedList` | Circular linked list maintaining circular invariant |
| `ArrayStack` | LIFO stack backed by a dynamic array |
| `LinkedStack` | LIFO stack backed by `SinglyLinkedList` |
| `LinkedQueue` | FIFO queue backed by `SinglyLinkedList` |
| `CircularQueue` | Fixed-capacity FIFO queue backed by a ring buffer |
| `PriorityQueue` | Min-heap priority queue |
| `LinkedDeque` | Double-ended queue backed by `DoublyLinkedList` |

### `pkstruct.trees`

| Data Structure | Description |
|---|---|
| `BinarySearchTree` | Unbalanced BST with full interview-utility API |
| `AVLTree` | Self-balancing AVL tree (extends BST) |
| `RedBlackTree` | Self-balancing red-black tree |
| `BTree` | Balanced multi-way search tree |
| `BPlusTree` | B+ Tree with leaf-linked chain for efficient range queries |
| `SegmentTree` | Segment tree with lazy propagation (sum/min/max/gcd/xor) |
| `FenwickTree` | Binary indexed tree for prefix-sum operations |
| `IntervalTree` | Augmented interval tree for overlap queries |

### `pkstruct.graphs`

| Class / Function | Description |
|---|---|
| `Graph` | Adjacency-list graph (directed/undirected, weighted) |
| `DirectedGraph` | Directed graph with in-degree, out-degree, reverse |
| `WeightedGraph` | Convenience class for weighted undirected graphs |
| `bfs` / `dfs` | Breadth-first and depth-first search |
| `bfs_paths` / `dfs_paths` | Find all paths between two vertices |
| `dijkstra` | Shortest paths (non-negative weights) |
| `bellman_ford` | Shortest paths (negative weights allowed) |
| `floyd_warshall` | All-pairs shortest paths |
| `reconstruct_path` | Path reconstruction from Dijkstra / Bellman-Ford |
| `reconstruct_path_fw` | Path reconstruction from Floyd-Warshall |
| `kruskal` / `prim` | Minimum spanning tree |
| `connected_components` | Find all connected components |
| `is_connected` / `is_bipartite` | Connectivity checks |
| `has_cycle` / `has_cycle_directed` | Cycle detection |
| `topological_sort_kahn` / `topological_sort_dfs` | Topological sort |
| `kosaraju` / `tarjan` | Strongly connected components |
| `visualize` / `adjacency_matrix` | ASCII visualization |

**Exceptions:** `GraphError`, `VertexNotFoundError`, `EdgeNotFoundError`,
`InvalidGraphOperationError`, `NegativeCycleError`, `NoPathError`

## Features

### Linked Lists

| Feature | SLL | DLL | CLL |
|---|---|---|---|
| Insert / Delete | ✅ | ✅ | ✅ |
| Sort (merge sort) | ✅ | ✅ | ✅ |
| Reverse (partial) | ✅ | ✅ | ✅ |
| Rotate (sub-range) | ✅ | ✅ | ✅ |
| Swap elements | ✅ | ✅ | ✅ |
| Cycle detection | ✅ | ✅ | — |
| Palindrome check | ✅ | ✅ | — |
| Even-odd segregation | ✅ | ✅ | — |
| JSON serialization | ✅ | ✅ | ✅ |
| ASCII visualization | ✅ | ✅ | ✅ |
| Thread-safe (RLock) | ✅ | ✅ | ✅ |
| `__slots__` nodes | ✅ | ✅ | ✅ |
| `next()` / `prev()` navigation | ✅ | ✅ | ✅ |

## API Overview

### Linear — Linked Lists

```python
# Construction
ll = SinglyLinkedList()               # empty
ll = SinglyLinkedList.from_list([1, 2, 3])
ll = SinglyLinkedList.from_json('{"items": [1, 2, 3]}')

# Insertion
ll.insert(99)                          # append at tail
ll.insert(99, position=0)              # insert at head
ll.insert(99, before=50)               # insert before value
ll.insert(99, after=50)                # insert after value

# Deletion
ll.delete(position=2)                  # delete by index
ll.delete(value=42)                    # delete by value (first match)
ll.delete(rng=(1, 3))                 # delete sub-range [1..3]
ll.clear()                             # remove all

# Access
ll.get(0)                              # by index
ll[0]                                   # via __getitem__
ll.index(42)                           # find first occurrence
ll.count(42)                           # count occurrences
ll.next(42)                            # element after 42
ll.prev(42)                            # element before 42

# Mutation
ll[0] = 99                             # via __setitem__
ll.swap(0, 2)                          # swap two positions
ll.reverse()                           # full reverse
ll.reverse(start=1, end=3)             # sub-range reverse
ll.rotate(shift=2)                     # rotate whole list right
ll.rotate(shift=2, start=1, end=4)     # rotate sub-range
ll.sort()                              # ascending
ll.sort(reverse=True)                  # descending
ll.merge(other_list)                   # merge in-place

# Interview helpers
ll.palindrome()                        # palindrome check
ll.detect_cycle()                      # Floyd's algorithm
ll.segregate_even_odd()                # reorder
ll.partition(5)                        # pivot partition

# Serialization
json_str = ll.to_json()
ll = SinglyLinkedList.from_json(json_str)

# Visualization
print(ll.visualize())                  # ASCII art
info = ll.debug()                      # diagnostic dict
```

### Linear — Stacks, Queues, Deques

```python
from pkstruct.linear import ArrayStack, LinkedStack, LinkedQueue, CircularQueue, PriorityQueue, LinkedDeque

# Stack
s = LinkedStack([1, 2, 3])
s.push(4)
s.pop()         # 4
s.peek()        # 3
len(s)          # 3

# Queue
q = LinkedQueue([1, 2, 3])
q.enqueue(4)
q.dequeue()     # 1
q.peek()        # 2

# Circular Queue (fixed capacity)
cq = CircularQueue(capacity=3)
cq.enqueue(1)
cq.enqueue(2)
cq.enqueue(3)
cq.is_full()    # True
cq.dequeue()    # 1

# Priority Queue (min-heap)
pq = PriorityQueue()
pq.push("task1", priority=3)
pq.push("task2", priority=1)
pq.pop()        # "task2"

# Deque
d = LinkedDeque([1, 2, 3])
d.append(4)
d.appendleft(0)
d.pop()         # 4
d.popleft()     # 0
```

### Linear — Utilities

```python
from pkstruct.linear.utils import merge_sorted_lists, detect_intersection, list_equal, to_array
from pkstruct.linear.utils import ForwardIterator, BackwardIterator, CircularIterator
from pkstruct.linear.utils import memory_usage, validate_integrity
from pkstruct.linear.utils import benchmark_operations, compare_with_builtins, run_full_benchmark

# Merge multiple sorted linked lists
sll1 = SinglyLinkedList.from_list([1, 3, 5])
sll2 = SinglyLinkedList.from_list([2, 4, 6])
merged = merge_sorted_lists(sll1, sll2)   # [1, 2, 3, 4, 5, 6]

# Detect if two lists share a node (by identity)
node_data = detect_intersection(sll1, sll2)

# Compare list equality
list_equal(sll1, sll2)                     # False

# Convert to plain list
to_array(sll1)                             # [1, 3, 5]

# Specialized iterators
list(ForwardIterator(sll))                 # forward over SLL/DLL/CLL
list(BackwardIterator(dll))                # backward over DLL only
circ = CircularIterator(cll, max_cycles=2) # bounded circular iteration

# Diagnostics
memory_usage(sll)                          # estimated bytes
validate_integrity(sll)                    # {"valid": True, "errors": [], ...}

# Benchmarks
benchmark_operations(SinglyLinkedList)     # time insert/delete/get/search
compare_with_builtins()                    # pkstruct vs list vs deque
run_full_benchmark()                       # full suite
```

### Trees

```python
# Binary Search Tree
bst = BinarySearchTree()
bst.insert(10, value="ten")
bst.insert(5, value="five")
bst[5]               # "five"
bst.search(10)       # ("ten", Node)
bst.delete(5)
len(bst)             # 1

# Traversals
list(bst.inorder())      # [5, 10, 15]
list(bst.preorder())     # [10, 5, 15]
list(bst.postorder())    # [5, 15, 10]
list(bst.level_order())  # [10, 5, 15]
list(bst.zigzag())       # [10, 15, 5]

# Navigation shortcuts
bst.root()               # root node
bst.parent(5)            # parent node (if maintained by tree)
bst.children(10)         # [node(5), node(15)]
bst.left(10)             # left child node
bst.right(10)            # right child node
bst.sibling(15)          # sibling node (node(5))

# Utilities
bst.find_lca(5, 15)      # 10 (lowest common ancestor)
bst.kth_smallest(1)      # 5
bst.kth_largest(1)       # 15
bst.range_query(5, 15)   # [5, 10, 15]
bst.path_sum(20)         # True
bst.root_to_leaf_paths() # [[10, 5], [10, 15]]
bst.diameter()           # 2
bst.is_balanced()        # True
bst.invert()

# AVL Tree (self-balancing)
avl = AVLTree()
avl.insert(3)
avl.insert(2)
avl.insert(1)            # triggers LL rotation
avl.is_avl_valid()       # True
avl.height()             # 1

# Red-Black Tree
rbt = RedBlackTree()
rbt.insert(10)
rbt.insert(20)
rbt.insert(30)           # triggers recoloring / rotation
rbt.validate()           # checks red-black invariants

# B-Tree & B+ Tree
bt = BTree(order=4)
bt.insert(10)
bt.insert(20)
bt.insert(5)
bt.search(10)            # True

bpt = BPlusTree(order=4)
bpt.insert(10)
bpt.insert(20)
bpt.range_query(5, 15)   # efficient via leaf chain

# Segment Tree
st = SegmentTree([1, 2, 3, 4, 5], operation="sum")
st.query(0, 2)           # 6
st.range_update(0, 2, 3) # range add
st.query(0, 2)           # 15
st.rebuild([5, 6, 7, 8])

# Fenwick Tree
ft = FenwickTree(5)
ft.add(1, 10)
ft.add(2, 20)
ft.prefix_sum(2)         # 30
ft.range_sum(1, 2)       # 30

# Interval Tree
it = IntervalTree()
it.insert(5, 10, "A")
it.insert(15, 20, "B")
it.overlap(8, 12)        # [(5, 10, "A")]
it.overlap_all(8, 12)    # all overlapping intervals
```

### Trees — Utilities

```python
from pkstruct.trees.traversal import traverse, inorder, preorder, postorder
from pkstruct.trees.traversal import levelorder, reverse_inorder, zigzag
from pkstruct.trees.traversal import boundary, vertical, iter_levels
from pkstruct.trees.balancing import rotate, rebalance, update_metadata
from pkstruct.trees.balancing import get_balance_factor, validate_balance
from pkstruct.trees.tree_helpers import (calculate_height, calculate_size,
    count_nodes, count_leaves, is_leaf, is_internal, clone_subtree,
    validate_bst_order, path_to_node, level_of_node, max_width)

# Traversal functions (work on any binary tree root)
bst = BinarySearchTree()
for k in [10, 5, 15, 3, 7, 12, 20]: bst.insert(k)
root = bst.root()

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
path_to_node(root, lambda n: n.key, 7)   # [10, 5, 7]
level_of_node(root, lambda n: n.key, 12) # 2
max_width(root)                      # max nodes on any level
```

### Graphs

```python
from pkstruct.graphs import Graph, DirectedGraph, WeightedGraph
from pkstruct.graphs import bfs, dfs, dijkstra, bellman_ford, floyd_warshall
from pkstruct.graphs import reconstruct_path, kruskal, kosaraju

# Create a graph
g = Graph()
g.add_edge("A", "B", weight=4.0)
g.add_edge("B", "C", weight=2.0)
g.add_edge("A", "C", weight=1.0)

# Traversal
bfs(g, "A")              # ['A', 'B', 'C']
dfs(g, "A")              # ['A', 'B', 'C']

# Shortest path (Dijkstra)
dist, pred = dijkstra(g, "A")
dist["C"]                # 1.0
reconstruct_path(pred, "A", "C")  # ['A', 'C']

# Minimum spanning tree
mst = kruskal(g)         # [('A', 'C', 1.0), ('B', 'C', 2.0)]

# Bellman-Ford (supports negative weights)
dist, pred = bellman_ford(g, "A")
dist["C"]                # 1.0

# All-pairs shortest paths
dist_all, _ = floyd_warshall(g)
dist_all["A"]["C"]       # 1.0

# Directed graph
dg = DirectedGraph()
dg.add_edge("A", "B")
dg.add_edge("B", "C")
dg.add_edge("A", "C")
topological_sort_kahn(dg)  # ['A', 'B', 'C']

# Strongly connected components
dg.add_edge("C", "A")
kosaraju(dg)             # [['A', 'B', 'C']] (one SCC)

# Weighted graph
wg = WeightedGraph()
wg.add_edge("X", "Y", 3.5)
wg.add_edge("Y", "Z", 1.5)
wg.get_weight("X", "Y")  # 3.5

# Visualization
from pkstruct.graphs import visualize
print(visualize(g))
# Graph (directed=False, vertices=3, edges=3)
#   'A' -> 'B' [4.0] <-> 'C' [1.0]
#   'B' -> 'A' [4.0] <-> 'C' [2.0]
#   'C' -> 'A' [1.0] <-> 'B' [2.0]

# Exception handling
from pkstruct.graphs.exceptions import VertexNotFoundError, NegativeCycleError

try:
    g.get_weight("X", "Y")
except VertexNotFoundError:
    print("Vertex does not exist")
```

## Help System

Every public structure is automatically registered.  Access help at the module or instance level:

```python
import pkstruct

pkstruct.help()                   # list all 20 structures
pkstruct.help(BinarySearchTree)   # class description + all methods
pkstruct.help("insert")           # insert from every class, grouped

sll = SinglyLinkedList()
sll.help()                        # instance-level help for this type
```

The registry is dynamic — any new structure class is picked up automatically on first call.

## Display Utility

```python
import pkstruct

pkstruct.display(sll)             # "1 2 3 4 5"  (space-separated)
pkstruct.display(sll, sep=",")    # "1,2,3,4,5"
```

## Node Navigation

Linear structures expose positional neighbor lookups:

```python
sll = SinglyLinkedList.from_list([1, 2, 3])
sll.next(1)   # 2
sll.next(3)   # None
sll.prev(2)   # 1
```

Trees expose parent/child relationships:

```python
bst = BinarySearchTree()
for k in [5, 3, 7, 2, 4]: bst.insert(k)

bst.root()            # node with key=5
bst.parent(2)         # parent node (key=3, if maintained)
bst.children(3)       # [node(2), node(4)]
bst.left(5)           # node(3)
bst.right(5)          # node(7)
bst.sibling(4)        # node(2)
```

Linear structures also provide `head` and `tail` properties; `from_list` and `to_list` for bulk conversion.

## String Protocol

```python
sll = SinglyLinkedList.from_list([1, 2, 3])
list(sll)          # [1, 2, 3]
len(sll)           # 3
bool(sll)          # True (False when empty)
repr(sll)          # SinglyLinkedList([1, 2, 3])
str(sll)           # "[1, 2, 3]"
42 in sll          # True / False
sll == other       # value equality
```

## Development

```bash
pip install -e ".[dev]"
pytest -v
```

## Publishing

```bash
python -m build
twine check dist/*
twine upload dist/*
```

## License

MIT © pkstruct Contributors
