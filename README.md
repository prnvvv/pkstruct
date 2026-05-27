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

## Features

| Feature                | SLL | DLL | CLL |
|------------------------|-----|-----|-----|
| Insert / Delete        | ✅  | ✅  | ✅  |
| Sort (merge sort)      | ✅  | ✅  | ✅  |
| Reverse (partial)      | ✅  | ✅  | ✅  |
| Rotate (sub-range)     | ✅  | ✅  | ✅  |
| Swap elements          | ✅  | ✅  | ✅  |
| Cycle detection        | ✅  | ✅  | —   |
| Palindrome check       | ✅  | ✅  | —   |
| Even-odd segregation   | ✅  | ✅  | —   |
| JSON serialization     | ✅  | ✅  | ✅  |
| ASCII visualization    | ✅  | ✅  | ✅  |
| Thread-safe (RLock)    | ✅  | ✅  | ✅  |
| `__slots__` nodes      | ✅  | ✅  | ✅  |

## API Overview

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
ll.replace(position=0, new_value=99)
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

## String protocol

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

## Modules Roadmap

- `pkstruct.linear` — Singly, doubly & circular linked lists
- `pkstruct.trees` — BST, AVL, Red-Black, Trie *(planned)*
- `pkstruct.graphs` — Adjacency list/matrix, weighted *(planned)*
- `pkstruct.spatial` — k-d tree, segment tree *(planned)*
- `pkstruct.cache` — LRU, LFU, TTL caches *(planned)*
- `pkstruct.prob` — Bloom filter, Count-Min sketch *(planned)*

## Development

```bash
pip install -e ".[dev]"
pytest src/pkstruct/linear/tests/ -v
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
