# Changelog

All notable changes to pkstruct will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-06-02

### Added
- `__bool__` to all tree types (BST, RedBlack, BTree, BPlus, Interval, Segment, Fenwick) and Graph
- `__iter__` to SegmentTree, FenwickTree
- `__contains__` to all 6 linear adapters (ArrayStack, LinkedStack, LinkedQueue, CircularQueue, PriorityQueue, LinkedDeque), SegmentTree, FenwickTree
- `copy()` to BTree, BPlusTree, IntervalTree, SegmentTree, FenwickTree
- `validate()`, `to_list()`, `from_list()` to Graph (inherited by DirectedGraph, WeightedGraph)
- `HelpMixin` to all 6 linear adapters
- Side validation in `LinkedDeque.append()`, `LinkedDeque.pop()`, `LinkedDeque.peek()`

### Changed
- BST/AVL `serialize()` now encodes each node as a `[key, value]` pair to prevent data loss on round-trip
- BST/AVL `deserialize()` handles both new `[key, value]` and legacy bare-key formats
- BTree/BPlusTree use `InvalidOrderError` instead of `ValueError` in `__init__`
- `module_help()` raises `ValueError` for invalid targets instead of silently returning `""`

### Fixed
- BST/AVL serialization no longer silently drops values during round-trip
- README `str(sll)` example corrected from `"1 2 3"` to `"[1, 2, 3]"`

## [0.1.0] - 2026-06-01

### Added
- `pkstruct.linear` module with `SinglyLinkedList`, `DoublyLinkedList`, `CircularLinkedList`
- Full CRUD operations: `insert`, `delete`, `get`, `replace`, `extend`, `clear`
- Algorithmic operations: `sort`, `merge`, `partition`, `reverse`, `rotate`, `swap`
- Interview problems: `detect_cycle`, `intersection_node`, `palindrome`, `reorder`, `segregate_even_odd`
- Serialization: `from_list`, `from_json`, `to_list`, `copy`
- ASCII visualization with `visualize()` and `debug()` introspection
- Thread-safe operations via `RLock`
- Custom exception hierarchy via `pkstruct.linear.exceptions`
- Shared subsystem (`pkstruct.shared`) for validators, serializers, threading, benchmarking
- Full pytest suite with edge cases, randomization, and threading tests
- Benchmark suite comparing against `list` and `collections.deque`
- Type annotations, mypy strict compliance
- PyPI-ready packaging with `hatchling`
