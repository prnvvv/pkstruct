"""
pkstruct.trees.tests.test_btree
================================
Comprehensive tests for BTree.
"""

from __future__ import annotations

import pytest
from pkstruct.trees.btree import BTree
from pkstruct.trees.exceptions import EmptyTreeError, InvalidOrderError, KeyNotFoundError


# ---------------------------------------------------------------------------
# 1. Creation
# ---------------------------------------------------------------------------


class TestCreation:
    def test_create_default(self) -> None:
        t = BTree()
        assert t.is_empty()
        assert len(t) == 0

    def test_create_with_order(self) -> None:
        t = BTree(order=3)
        assert t.is_empty()

    def test_create_invalid_order(self) -> None:
        with pytest.raises(InvalidOrderError):
            BTree(order=1)

    def test_create_order_two(self) -> None:
        t = BTree(order=2)
        assert t.order >= 2


# ---------------------------------------------------------------------------
# 2. Insertion
# ---------------------------------------------------------------------------


class TestInsertion:
    def test_insert_single(self) -> None:
        t = BTree(order=3)
        t.insert(10)
        assert len(t) == 1
        assert 10 in t

    def test_insert_multiple(self) -> None:
        t = BTree(order=3)
        for v in [10, 20, 30, 40, 50]:
            t.insert(v)
        assert len(t) == 5

    def test_insert_causes_split(self) -> None:
        t = BTree(order=3)
        for v in [10, 20, 30, 40, 50]:
            t.insert(v)
        assert t.validate()

    def test_insert_duplicate_default(self) -> None:
        t = BTree(order=3)
        t.insert(10)
        t.insert(10)
        assert len(t) == 1

    def test_insert_with_value(self) -> None:
        t = BTree(order=3)
        t.insert(42, "payload")
        assert t.search(42) == "payload"

    def test_insert_large_sequence(self) -> None:
        t = BTree(order=4)
        for i in range(100):
            t.insert(i)
        assert t.size() == 100
        assert t.validate()


# ---------------------------------------------------------------------------
# 3. Search / contains
# ---------------------------------------------------------------------------


class TestSearch:
    def test_search_found(self) -> None:
        t = BTree(order=3)
        for v in [10, 20, 30, 40, 50]:
            t.insert(v)
        assert t.contains(30)
        assert t.search(99) is None

    def test_search_not_found(self) -> None:
        t = BTree(order=3)
        t.insert(10)
        t.insert(20)
        assert t.search(99) is None

    def test_search_empty(self) -> None:
        t = BTree(order=3)
        assert t.search(1) is None

    def test_contains(self) -> None:
        t = BTree(order=3)
        t.insert(25)
        assert 25 in t
        assert 99 not in t


# ---------------------------------------------------------------------------
# 4. Deletion
# ---------------------------------------------------------------------------


class TestDeletion:
    def test_delete_leaf(self) -> None:
        t = BTree(order=3)
        t.insert(10)
        t.insert(20)
        t.delete(10)
        assert 10 not in t
        assert len(t) == 1

    def test_delete_internal(self) -> None:
        t = BTree(order=3)
        for v in [10, 20, 30, 40, 50]:
            t.insert(v)
        t.delete(30)
        assert 30 not in t
        assert t.validate()

    def test_delete_not_found(self) -> None:
        t = BTree(order=3)
        t.insert(10)
        with pytest.raises(KeyNotFoundError):
            t.delete(99)

    def test_delete_from_empty(self) -> None:
        t = BTree(order=3)
        with pytest.raises(KeyNotFoundError):
            t.delete(1)

    def test_delete_root(self) -> None:
        t = BTree(order=3)
        t.insert(10)
        t.delete(10)
        assert t.is_empty()


# ---------------------------------------------------------------------------
# 5. Validation
# ---------------------------------------------------------------------------


class TestValidation:
    def test_validate_empty(self) -> None:
        t = BTree(order=3)
        assert t.validate() is True

    def test_validate_non_empty(self) -> None:
        t = BTree(order=3)
        for v in [1, 2, 3, 4, 5]:
            t.insert(v)
        assert t.validate() is True


# ---------------------------------------------------------------------------
# 6. Traversal / iteration
# ---------------------------------------------------------------------------


class TestTraversal:
    def test_inorder(self) -> None:
        t = BTree(order=3)
        for v in [5, 3, 7, 1, 9, 2, 8]:
            t.insert(v)
        assert list(t) == sorted([5, 3, 7, 1, 9, 2, 8])

    def test_iter_empty(self) -> None:
        t = BTree(order=3)
        assert list(t) == []


# ---------------------------------------------------------------------------
# 7. Min / max
# ---------------------------------------------------------------------------


class TestMinMax:
    def test_min(self) -> None:
        t = BTree(order=3)
        for v in [5, 3, 7, 1, 9]:
            t.insert(v)
        assert t.min() == 1

    def test_max(self) -> None:
        t = BTree(order=3)
        for v in [5, 3, 7, 1, 9]:
            t.insert(v)
        assert t.max() == 9

    def test_min_empty(self) -> None:
        t = BTree(order=3)
        with pytest.raises(EmptyTreeError):
            t.min()

    def test_max_empty(self) -> None:
        t = BTree(order=3)
        with pytest.raises(EmptyTreeError):
            t.max()


# ---------------------------------------------------------------------------
# 8. Clear
# ---------------------------------------------------------------------------


class TestClear:
    def test_clear(self) -> None:
        t = BTree(order=3)
        for v in range(20):
            t.insert(v)
        t.clear()
        assert t.is_empty()

    def test_clear_reuse(self) -> None:
        t = BTree(order=3)
        t.insert(1)
        t.clear()
        t.insert(99)
        assert 99 in t


# ---------------------------------------------------------------------------
# 9. Split / overflow
# ---------------------------------------------------------------------------


class TestSplitOverflow:
    def test_split_on_overflow(self) -> None:
        t = BTree(order=3)
        for v in range(10):
            t.insert(v)
        assert t.validate()
        assert t.size() == 10

    def test_repeated_splits(self) -> None:
        t = BTree(order=4)
        for v in range(200):
            t.insert(v)
        assert t.validate()
        assert t.size() == 200


# ---------------------------------------------------------------------------
# 10. Merge / underflow
# ---------------------------------------------------------------------------


class TestMergeUnderflow:
    def test_merge_on_delete(self) -> None:
        t = BTree(order=3)
        for v in range(10):
            t.insert(v)
        for v in range(10):
            t.delete(v)
        assert t.is_empty()


# ---------------------------------------------------------------------------
# 11. Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_single_element(self) -> None:
        t = BTree(order=3)
        t.insert(42)
        assert t.min() == 42
        assert t.max() == 42
        assert t.size() == 1
        t.delete(42)
        assert t.is_empty()

    def test_duplicate_values(self) -> None:
        t = BTree(order=3)
        t.insert(5, "a")
        t.insert(5, "b")
        assert t.search(5) == "b"
        assert t.size() == 1

    def test_large_random(self) -> None:
        import random
        t = BTree(order=6)
        values = list(range(500))
        random.shuffle(values)
        for v in values:
            t.insert(v)
        assert t.validate()
        assert t.size() == 500
        assert list(t) == list(range(500))
