# Changelog

All notable changes to pkstruct will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
