"""
pkstruct.trees.tests.test_bplus
================================
Comprehensive tests for BPlusTree.
"""

from __future__ import annotations

import pytest
from pkstruct.trees.bplus import BPlusTree
from pkstruct.trees.exceptions import EmptyTreeError, InvalidOrderError, KeyNotFoundError


# ---------------------------------------------------------------------------
# 1. Creation
# ---------------------------------------------------------------------------


class TestCreation:
    def test_create_default(self) -> None:
        t = BPlusTree()
        assert t.is_empty()
        assert len(t) == 0

    def test_create_with_order(self) -> None:
        t = BPlusTree(order=3)
        assert t.is_empty()

    def test_create_invalid_order(self) -> None:
        with pytest.raises(InvalidOrderError):
            BPlusTree(order=1)

    def test_create_order_two(self) -> None:
        t = BPlusTree(order=2)
        assert t.order >= 2


# ---------------------------------------------------------------------------
# 2. Insertion
# ---------------------------------------------------------------------------


class TestInsertion:
    def test_insert_single(self) -> None:
        t = BPlusTree(order=3)
        t.insert(10)
        assert len(t) == 1
        assert 10 in t

    def test_insert_multiple(self) -> None:
        t = BPlusTree(order=3)
        for v in [10, 20, 30, 40, 50]:
            t.insert(v)
        assert len(t) == 5

    def test_insert_causes_split(self) -> None:
        t = BPlusTree(order=3)
        for v in range(20):
            t.insert(v)
        assert t.validate()

    def test_insert_duplicate_default(self) -> None:
        t = BPlusTree(order=3)
        t.insert(10)
        t.insert(10)
        assert len(t) == 1

    def test_insert_large(self) -> None:
        t = BPlusTree(order=4)
        for i in range(200):
            t.insert(i)
        assert t.size() == 200
        assert t.validate()


# ---------------------------------------------------------------------------
# 3. Search / contains
# ---------------------------------------------------------------------------


class TestSearch:
    def test_search_found(self) -> None:
        t = BPlusTree(order=3)
        for v in [10, 20, 30, 40, 50]:
            t.insert(v)
        assert t.contains(30)
        assert t.search(99) is None

    def test_search_not_found(self) -> None:
        t = BPlusTree(order=3)
        t.insert(10)
        assert t.search(99) is None

    def test_contains(self) -> None:
        t = BPlusTree(order=3)
        t.insert(25)
        assert 25 in t
        assert 99 not in t


# ---------------------------------------------------------------------------
# 4. Deletion
# ---------------------------------------------------------------------------


class TestDeletion:
    def test_delete_leaf(self) -> None:
        t = BPlusTree(order=3)
        t.insert(10)
        t.insert(20)
        t.delete(10)
        assert 10 not in t
        assert len(t) == 1

    def test_delete_not_found(self) -> None:
        t = BPlusTree(order=3)
        t.insert(10)
        with pytest.raises(KeyNotFoundError):
            t.delete(99)

    def test_delete_from_empty(self) -> None:
        t = BPlusTree(order=3)
        with pytest.raises(KeyNotFoundError):
            t.delete(1)

    def test_delete_root(self) -> None:
        t = BPlusTree(order=3)
        t.insert(10)
        t.delete(10)
        assert t.is_empty()


# ---------------------------------------------------------------------------
# 5. Leaf linking / leaf traversal
# ---------------------------------------------------------------------------


class TestLeafLinking:
    def test_leaf_link_chain(self) -> None:
        t = BPlusTree(order=3)
        for v in range(50):
            t.insert(v)
        leaves = t.leaf_traversal()
        assert len(leaves) == 50

    def test_leaf_traversal_order(self) -> None:
        t = BPlusTree(order=3)
        values = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
        for v in values:
            t.insert(v)
        leaves = t.leaf_traversal()
        assert leaves == sorted(set(values))


# ---------------------------------------------------------------------------
# 6. Range query
# ---------------------------------------------------------------------------


class TestRangeQuery:
    def test_range_query_basic(self) -> None:
        t = BPlusTree(order=3)
        for v in range(100):
            t.insert(v)
        result = t.range_query(20, 30)
        assert result == list(range(20, 31))

    def test_range_query_single(self) -> None:
        t = BPlusTree(order=3)
        for v in range(10):
            t.insert(v)
        assert t.range_query(5, 5) == [5]

    def test_range_query_empty(self) -> None:
        t = BPlusTree(order=3)
        for v in range(10):
            t.insert(v)
        assert t.range_query(100, 200) == []


# ---------------------------------------------------------------------------
# 7. Validation
# ---------------------------------------------------------------------------


class TestValidation:
    def test_validate_empty(self) -> None:
        t = BPlusTree(order=3)
        assert t.validate() is True

    def test_validate_non_empty(self) -> None:
        t = BPlusTree(order=3)
        for v in range(50):
            t.insert(v)
        assert t.validate() is True


# ---------------------------------------------------------------------------
# 8. Traversal / iteration
# ---------------------------------------------------------------------------


class TestTraversal:
    def test_inorder(self) -> None:
        t = BPlusTree(order=3)
        for v in [5, 3, 7, 1, 9, 2, 8]:
            t.insert(v)
        assert list(t) == sorted([5, 3, 7, 1, 9, 2, 8])

    def test_iter_empty(self) -> None:
        t = BPlusTree(order=3)
        assert list(t) == []


# ---------------------------------------------------------------------------
# 9. Min / max
# ---------------------------------------------------------------------------


class TestMinMax:
    def test_min(self) -> None:
        t = BPlusTree(order=3)
        for v in [5, 3, 7, 1, 9]:
            t.insert(v)
        assert t.min() == 1

    def test_max(self) -> None:
        t = BPlusTree(order=3)
        for v in [5, 3, 7, 1, 9]:
            t.insert(v)
        assert t.max() == 9

    def test_min_empty(self) -> None:
        t = BPlusTree(order=3)
        with pytest.raises(EmptyTreeError):
            t.min()


# ---------------------------------------------------------------------------
# 10. Clear
# ---------------------------------------------------------------------------


class TestClear:
    def test_clear(self) -> None:
        t = BPlusTree(order=3)
        for v in range(20):
            t.insert(v)
        t.clear()
        assert t.is_empty()

    def test_clear_reuse(self) -> None:
        t = BPlusTree(order=3)
        t.insert(1)
        t.clear()
        t.insert(99)
        assert 99 in t


# ---------------------------------------------------------------------------
# 11. Split / merge
# ---------------------------------------------------------------------------


class TestSplitMerge:
    def test_splits_on_insert(self) -> None:
        t = BPlusTree(order=3)
        for v in range(100):
            t.insert(v)
        assert t.validate()

    def test_merges_on_delete(self) -> None:
        t = BPlusTree(order=3)
        for v in range(50):
            t.insert(v)
        for v in range(50):
            t.delete(v)
        assert t.is_empty()


# ---------------------------------------------------------------------------
# 12. Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_single_element(self) -> None:
        t = BPlusTree(order=3)
        t.insert(42)
        assert t.min() == 42
        assert t.max() == 42
        assert t.size() == 1
        t.delete(42)
        assert t.is_empty()

    def test_large_random(self) -> None:
        import random
        t = BPlusTree(order=5)
        values = list(range(500))
        random.shuffle(values)
        for v in values:
            t.insert(v)
        assert t.validate()
        assert t.size() == 500

    def test_range_query_uses_leaf_chain(self) -> None:
        t = BPlusTree(order=4)
        for v in range(100):
            t.insert(v)
        result = t.range_query(10, 19)
        assert result == list(range(10, 20))
