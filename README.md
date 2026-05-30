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
from pkstruct.linear import SinglyLinkedList, DoublyLinkedList, CircularLinkedList

# Singly Linked List
sll = SinglyLinkedList.from_list([1, 2, 3, 4, 5])
sll.insert(99, position=2)       # [1, 2, 99, 3, 4, 5]
sll.sort()                       # [1, 2, 3, 4, 5, 99]
print(sll.visualize())
# [1] -> [2] -> [3] -> [4] -> [5] -> [99] -> NULL

# Doubly Linked List
dll = DoublyLinkedList.from_list([10, 20, 30])
dll.reverse()
print(dll.visualize())
# None <- 30 <-> 20 <-> 10 -> None

# Circular Linked List
cll = CircularLinkedList.from_list(["a", "b", "c"])
cll.rotate(shift=1)
print(cll.visualize())
# c -> a -> b -> (back to head)
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

# AVL Tree (self-balancing)
avl = AVLTree.from_list([1, 2, 3, 4, 5])
avl.height()       # 2 (logarithmic, not linear)

# Segment Tree with lazy propagation
st = SegmentTree([1, 2, 3, 4, 5], func="sum")
st.query(1, 3)     # 9 (2 + 3 + 4)
st.update(2, 10)   # point update
st.range_update(1, 3, 5)  # range add
st.query(1, 3)     # 24
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
st = SegmentTree([1, 2, 3, 4, 5], func="sum")
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

## String Protocol

```python
sll = SinglyLinkedList.from_list([1, 2, 3])
list(sll)          # [1, 2, 3]
len(sll)           # 3
bool(sll)          # True (False when empty)
repr(sll)          # SinglyLinkedList([1, 2, 3])
str(sll)           # SinglyLinkedList([1, 2, 3])
42 in sll          # True / False
sll == other       # value equality
```

## Development

```bash
pip install -e ".[dev]"
pytest src/pkstruct/linear/tests src/pkstruct/trees/tests -v
python run_all_tests.py
```

## Publishing

```bash
python -m build
twine check dist/*
twine upload dist/*
```

## License

MIT © pkstruct Contributors
