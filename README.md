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
sll.insert(99, position=2)
sll.sort()
print(sll.visualize())
# [1] -> [2] -> [3] -> [4] -> [5] -> [99] -> NULL

# Doubly Linked List
dll = DoublyLinkedList.from_list([10, 20, 30])
dll.reverse()
print(dll.visualize())
# NULL <-> [30] <-> [20] <-> [10] <-> NULL

# Circular Linked List
cll = CircularLinkedList.from_list(["a", "b", "c"])
cll.rotate(0, 2, direction=True, shift=1)
print(cll.visualize())
# [b] -> [c] -> [a] -> (back to head)
```

## Features

| Feature                | SLL | DLL | CLL |
|------------------------|-----|-----|-----|
| Insert / Delete        | ✅  | ✅  | ✅  |
| Sort (merge sort)      | ✅  | ✅  | ✅  |
| Reverse (partial)      | ✅  | ✅  | ✅  |
| Rotate (range)         | ✅  | ✅  | ✅  |
| Cycle detection        | ✅  | ✅  | —   |
| Palindrome check       | ✅  | ✅  | —   |
| Odd-even reorder       | ✅  | ✅  | —   |
| JSON serialization     | ✅  | ✅  | ✅  |
| ASCII visualization    | ✅  | ✅  | ✅  |
| Thread-safe            | ✅  | ✅  | ✅  |
| `__slots__` nodes      | ✅  | ✅  | ✅  |

## Modules Roadmap

- `pkstruct.linear` — linked lists, stacks, queues ✅
- `pkstruct.trees` — BST, AVL, Red-Black, Trie *(planned)*
- `pkstruct.graphs` — adjacency list/matrix, weighted *(planned)*
- `pkstruct.spatial` — k-d tree, segment tree *(planned)*
- `pkstruct.cache` — LRU, LFU, TTL caches *(planned)*
- `pkstruct.prob` — Bloom filter, Count-Min sketch *(planned)*

## Development

```bash
pip install -e ".[dev]"
pytest pkstruct/linear/tests/ -v --cov=pkstruct
black pkstruct/ && ruff check pkstruct/ && mypy pkstruct/
```

## Publishing

```bash
python -m build
twine check dist/*
twine upload dist/*
```

## License

MIT © pkstruct Contributors