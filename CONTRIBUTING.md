# Contributing to pkstruct

Thank you for your interest in contributing to pkstruct! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please report unacceptable behavior.

## How to Contribute

### Reporting Bugs

1. Search [existing issues](https://github.com/prnvvv/pkstruct/issues) to avoid duplicates.
2. Use the **Bug Report** issue template.
3. Include:
   - Python version and OS
   - Minimal reproduction code
   - Expected vs actual behavior
   - Full error output if applicable

### Suggesting Features

1. Search [existing issues](https://github.com/prnvvv/pkstruct/issues) first.
2. Use the **Feature Request** issue template.
3. Explain the use case and why it belongs in pkstruct.

### Questions

Use the **Question** issue template or start a [Discussion](https://github.com/prnvvv/pkstruct/discussions).

## Development Setup

```bash
git clone https://github.com/prnvvv/pkstruct.git
cd pkstruct
pip install -e ".[dev]"
```

## Coding Standards

- **Python**: >= 3.10
- **Type hints**: Required for all public APIs. Run `mypy src/pkstruct` — no errors allowed.
- **Style**: Run `ruff check src/pkstruct` — no violations allowed.
- **Line length**: 100 characters.
- **Imports**: Use Ruff's import ordering (`I` rule set).

### Rules

- No `eval()` or `exec()`.
- All mutable state must be protected by `threading.RLock`.
- Public API methods must have type annotations and docstrings.
- Internal/private methods prefixed with `_`.

## Testing

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src/pkstruct

# Run specific test file
python -m pytest src/pkstruct/linear/tests/test_linked_list.py
```

- All new code must include tests.
- Tests should cover normal paths, edge cases, and error conditions.
- Test files go in the corresponding `tests/` directory.

## Pull Request Process

1. **Create an issue** first for bugs or feature requests (unless trivial).
2. **Fork the repository** and create a branch from `main`:
   ```
   git checkout -b fix/issue-42-description
   ```
3. **Make your changes** following the coding standards.
4. **Run tests** locally to ensure nothing is broken.
5. **Run type checks** with `mypy src/pkstruct`.
6. **Run linter** with `ruff check src/pkstruct`.
7. **Commit** with a clear message:
   ```
   feat: add range_update to SegmentTree
   fix: handle empty list in SinglyLinkedList.sort
   docs: update README examples
   ```
8. **Push** and open a Pull Request.
9. **Address review feedback** promptly.

## Pull Request Checklist

- [ ] Code follows style guidelines
- [ ] Type hints added/updated
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] mypy passes with no errors
- [ ] ruff passes with no violations
- [ ] CHANGELOG.md updated (if user-facing change)
- [ ] Documentation updated (if API change)

## Review Expectations

- Maintainers review within 5 business days.
- Changes may be requested — this is normal.
- Two approving reviews required for significant changes.

## Project Structure

```
src/pkstruct/
├── __init__.py          # Package root, registry, help()
├── linear/             # Linked lists, stacks, queues, deques
│   ├── linked_lists/
│   ├── stacks/
│   ├── queues/
│   ├── deques/
│   ├── tests/
│   ├── utils/
│   └── visualization/
├── trees/              # BST, AVL, Red-Black, B-Tree, Fenwick, Segment, Interval
│   ├── tests/
│   └── visualization/
├── graphs/             # Graph, DirectedGraph, algorithms
│   └── tests/
└── shared/             # Validators, serializers, threading, benchmarking
```

## Getting Help

- Open a [Discussion](https://github.com/prnvvv/pkstruct/discussions)
- Ask in issue comments
- Tag `@prnvvv` for maintainer attention
