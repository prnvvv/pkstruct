# pkstruct - Agent Guide

## Test Suite
Run all tests:
```bash
python -m pytest
```
Tests are in `src/pkstruct/{linear,trees,graphs}/tests/` (898 tests).

## Architecture
- **src-layout**: `src/pkstruct/`
- **Build**: hatchling via `pyproject.toml`
- **Python**: >= 3.10
- **Python path**: `PYTHONPATH=src` (handled by pyproject.toml pytest config)

## Key Files
| File | Purpose |
|------|---------|
| `_str.py` | `StrMixin` - `__str__()`, `display(sep)`, `visualize()` |
| `_help.py` | `HelpMixin` - dynamic help system |
| `_linear_shortcuts.py` | `LinearShortcutsMixin` - `next()`, `prev()` |
| `_tree_shortcuts.py` | `TreeShortcutsMixin` - `root()`, `parent()`, `children()`, `left()`, `right()`, `sibling()`, `visualize()` |
| `linear/linked_lists/_base.py` | `_LinkedListBase` - shared LL logic |
| `linear/linked_lists/nodes.py` | `SinglyNode`, `DoublyNode`, `CircularNode` |
| `trees/node.py` | `TreeNode`, `AVLNode`, `RBNode`, `BTreeNode`, `BPlusNode` |
| `graphs/graph.py` | `Graph` class |

## Help System
- `pkstruct.help()` → lists all structures
- `pkstruct.help(ClassName)` → details + methods
- `pkstruct.help("method_name")` → method docs across all classes
- `instance.help()` / `instance.help("method")` / `instance.help(ClassName)`

## Validating Changes
Before/after editing, run: `python -m pytest --tb=short -q`

## Git
- No automated commits; use `git add -p` + `git commit` manually
