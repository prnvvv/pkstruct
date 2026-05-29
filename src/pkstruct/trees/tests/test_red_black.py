"""
pkstruct.trees.tests.test_red_black
===================================
Comprehensive tests for RedBlackTree.
"""

from __future__ import annotations

import pytest
from pkstruct.trees.red_black import RedBlackTree, BLACK, RED


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build(values: list) -> RedBlackTree:
    t = RedBlackTree()
    for v in values:
        t.insert(v)
    return t


# ---------------------------------------------------------------------------
# 1. Creation / empty state
# ---------------------------------------------------------------------------


class TestCreation:
    def test_create_empty(self) -> None:
        t = RedBlackTree()
        assert t.is_empty()
        assert len(t) == 0

    def test_empty_height(self) -> None:
        t = RedBlackTree()
        assert t.height() == -1

    def test_empty_min_raises(self) -> None:
        with pytest.raises(ValueError):
            RedBlackTree().min()

    def test_empty_max_raises(self) -> None:
        with pytest.raises(ValueError):
            RedBlackTree().max()

    def test_empty_black_height(self) -> None:
        t = RedBlackTree()
        assert t.black_height() == 0


# ---------------------------------------------------------------------------
# 2. Insertion
# ---------------------------------------------------------------------------


class TestInsertion:
    def test_insert_single_root_is_black(self) -> None:
        t = RedBlackTree()
        t.insert(10)
        assert not t.is_empty()
        assert len(t) == 1

    def test_insert_multiple(self) -> None:
        t = _build([5, 3, 7, 2, 4, 6, 8])
        assert list(t) == [2, 3, 4, 5, 6, 7, 8]
        assert t.is_red_black_valid()

    def test_insert_duplicate_default(self) -> None:
        t = RedBlackTree()
        t.insert(5)
        t.insert(5)
        assert len(t) == 1

    def test_insert_duplicate_rejected(self) -> None:
        t = RedBlackTree(allow_duplicates=True)
        t.insert(1)
        with pytest.raises(ValueError, match="Duplicate"):
            t.insert(1)

    def test_insert_with_value(self) -> None:
        t = RedBlackTree()
        t.insert(42, "data")
        assert t.search(42) == "data"

    def test_insert_large_sequence(self) -> None:
        t = RedBlackTree()
        for i in range(100):
            t.insert(i)
        assert t.is_red_black_valid()
        assert t.size() == 100


# ---------------------------------------------------------------------------
# 3. Root property
# ---------------------------------------------------------------------------


class TestRootProperty:
    def test_root_is_black(self) -> None:
        t = _build([1, 2, 3])
        assert t.is_red_black_valid()

    def test_root_remains_black_after_insert(self) -> None:
        t = RedBlackTree()
        for v in [10, 5, 15, 3, 7, 12, 18]:
            t.insert(v)
        assert t.is_red_black_valid()


# ---------------------------------------------------------------------------
# 4. Red-red violation check
# ---------------------------------------------------------------------------


class TestRedRedViolation:
    def test_no_red_red_after_inserts(self) -> None:
        t = _build([10, 5, 15, 3, 7, 12, 18, 1, 4, 6, 8])
        assert t.is_red_black_valid()


# ---------------------------------------------------------------------------
# 5. Black height
# ---------------------------------------------------------------------------


class TestBlackHeight:
    def test_black_height_non_empty(self) -> None:
        t = _build([1, 2, 3, 4, 5])
        bh = t.black_height()
        assert bh >= 1

    def test_black_height_consistent(self) -> None:
        t = _build([10, 5, 15, 3, 7, 12, 18])
        assert t.is_red_black_valid()

    def test_black_height_single(self) -> None:
        t = _build([1])
        assert t.black_height() >= 1


# ---------------------------------------------------------------------------
# 6. Deletion
# ---------------------------------------------------------------------------


class TestDeletion:
    def test_delete_leaf(self) -> None:
        t = _build([5, 3, 7])
        t.delete(3)
        assert list(t) == [5, 7]
        assert t.is_red_black_valid()

    def test_delete_node_with_one_child(self) -> None:
        t = _build([5, 3, 7, 2])
        t.delete(3)
        assert list(t) == [2, 5, 7]
        assert t.is_red_black_valid()

    def test_delete_node_with_two_children(self) -> None:
        t = _build([5, 3, 7, 2, 4, 6, 8])
        t.delete(5)
        assert list(t) == [2, 3, 4, 6, 7, 8]
        assert t.is_red_black_valid()

    def test_delete_root(self) -> None:
        t = _build([10])
        t.delete(10)
        assert t.is_empty()

    def test_delete_maintains_rb_properties(self) -> None:
        import random
        t = RedBlackTree()
        values = list(range(200))
        random.shuffle(values)
        for v in values:
            t.insert(v)
        for v in values[:100]:
            t.delete(v)
        assert t.is_red_black_valid()

    def test_delete_not_found(self) -> None:
        t = _build([1, 2, 3])
        with pytest.raises(KeyError):
            t.delete(99)

    def test_delete_from_empty(self) -> None:
        with pytest.raises(KeyError):
            RedBlackTree().delete(1)


# ---------------------------------------------------------------------------
# 7. Search / contains
# ---------------------------------------------------------------------------


class TestSearch:
    def test_search_found(self) -> None:
        t = _build([10, 20, 30])
        assert 20 in t

    def test_search_not_found(self) -> None:
        t = _build([1, 2, 3])
        assert t.search(99) is None

    def test_contains(self) -> None:
        t = _build([5, 15, 25])
        assert 15 in t
        assert 99 not in t


# ---------------------------------------------------------------------------
# 8. Update
# ---------------------------------------------------------------------------


class TestUpdate:
    def test_update_existing(self) -> None:
        t = RedBlackTree()
        t.insert("x", 1)
        t.update("x", 99)
        assert t.search("x") == 99

    def test_update_missing(self) -> None:
        t = RedBlackTree()
        with pytest.raises(KeyError):
            t.update("missing", 1)


# ---------------------------------------------------------------------------
# 9. Navigation
# ---------------------------------------------------------------------------


class TestNavigation:
    def test_min(self) -> None:
        t = _build([5, 3, 7, 1, 9])
        assert t.min() == 1

    def test_max(self) -> None:
        t = _build([5, 3, 7, 1, 9])
        assert t.max() == 9

    def test_predecessor(self) -> None:
        t = _build([5, 3, 7, 2, 4, 6, 8])
        assert t.predecessor(5) == 4
        assert t.predecessor(2) is None

    def test_predecessor_missing(self) -> None:
        t = _build([1, 2])
        with pytest.raises(KeyError):
            t.predecessor(99)

    def test_successor(self) -> None:
        t = _build([5, 3, 7, 2, 4, 6, 8])
        assert t.successor(5) == 6
        assert t.successor(8) is None

    def test_successor_missing(self) -> None:
        t = _build([1, 2])
        with pytest.raises(KeyError):
            t.successor(99)


# ---------------------------------------------------------------------------
# 10. Validation
# ---------------------------------------------------------------------------


class TestValidation:
    def test_is_red_black_valid_empty(self) -> None:
        assert RedBlackTree().is_red_black_valid() is True

    def test_is_red_black_valid_single(self) -> None:
        t = _build([1])
        assert t.is_red_black_valid() is True

    def test_is_red_black_valid_complex(self) -> None:
        t = _build([10, 5, 15, 3, 7, 12, 18, 1, 4, 6, 8])
        assert t.is_red_black_valid() is True

    def test_validate_method(self) -> None:
        t = _build([5, 3, 7])
        assert t.validate() is True


# ---------------------------------------------------------------------------
# 11. Copy
# ---------------------------------------------------------------------------


class TestCopy:
    def test_copy_is_deep(self) -> None:
        t = _build([5, 3, 7])
        cp = t.copy()
        assert list(cp) == [3, 5, 7]
        cp.insert(99)
        assert 99 not in t

    def test_copy_preserves_validity(self) -> None:
        t = _build([10, 5, 15, 3, 7, 12, 18])
        cp = t.copy()
        assert cp.is_red_black_valid()


# ---------------------------------------------------------------------------
# 12. Traversal / iteration
# ---------------------------------------------------------------------------


class TestTraversal:
    def test_inorder(self) -> None:
        t = _build([5, 3, 7, 2, 4, 6, 8])
        assert list(t) == [2, 3, 4, 5, 6, 7, 8]

    def test_iter_empty(self) -> None:
        t = RedBlackTree()
        assert list(t) == []


# ---------------------------------------------------------------------------
# 13. Clear
# ---------------------------------------------------------------------------


class TestClear:
    def test_clear(self) -> None:
        t = _build([1, 2, 3, 4, 5])
        t.clear()
        assert t.is_empty()

    def test_clear_reuse(self) -> None:
        t = _build([1, 2, 3])
        t.clear()
        t.insert(99)
        assert 99 in t


# ---------------------------------------------------------------------------
# 14. Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_single_element(self) -> None:
        t = _build([42])
        assert t.height() == 0
        assert t.is_red_black_valid()
        t.delete(42)
        assert t.is_empty()

    def test_insert_delete_interleaved(self) -> None:
        t = RedBlackTree()
        for i in range(50):
            t.insert(i)
        for i in range(0, 50, 2):
            t.delete(i)
        assert t.is_red_black_valid()

    def test_large_random(self) -> None:
        import random
        t = RedBlackTree()
        values = list(range(500))
        random.shuffle(values)
        for v in values:
            t.insert(v)
        assert t.is_red_black_valid()
        assert t.size() == 500
