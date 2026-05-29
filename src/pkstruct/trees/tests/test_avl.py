"""
pkstruct.trees.tests.test_avl
=============================
Comprehensive tests for AVLTree.
"""

from __future__ import annotations

import pytest

from pkstruct.trees.avl import AVLTree

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build(values: list) -> AVLTree:
    t = AVLTree()
    for v in values:
        t.insert(v)
    return t


# ---------------------------------------------------------------------------
# 1. Creation / empty state
# ---------------------------------------------------------------------------


class TestCreation:
    def test_create_empty(self) -> None:
        t = AVLTree()
        assert t.is_empty()
        assert len(t) == 0
        assert t.size() == 0

    def test_empty_height(self) -> None:
        t = AVLTree()
        assert t.height() == -1

    def test_empty_min_raises(self) -> None:
        with pytest.raises(ValueError):
            AVLTree().min()

    def test_empty_max_raises(self) -> None:
        with pytest.raises(ValueError):
            AVLTree().max()


# ---------------------------------------------------------------------------
# 2. Insertion and AVL balance
# ---------------------------------------------------------------------------


class TestInsertion:
    def test_insert_single(self) -> None:
        t = AVLTree()
        t.insert(10)
        assert len(t) == 1
        assert t.height() == 0

    def test_insert_in_order(self) -> None:
        t = _build([1, 2, 3])
        assert list(t) == [1, 2, 3]
        assert t.is_avl_valid()

    def test_insert_reverse_order(self) -> None:
        t = _build([3, 2, 1])
        assert list(t) == [1, 2, 3]
        assert t.is_avl_valid()

    def test_insert_random_order(self) -> None:
        t = _build([5, 3, 7, 2, 4, 6, 8, 1, 9])
        assert list(t) == [1, 2, 3, 4, 5, 6, 7, 8, 9]
        assert t.is_avl_valid()

    def test_insert_duplicate_default(self) -> None:
        t = AVLTree()
        t.insert(5)
        t.insert(5)
        assert len(t) == 1

    def test_insert_duplicate_rejected(self) -> None:
        t = AVLTree(allow_duplicates=True)
        t.insert(1)
        with pytest.raises(ValueError, match="Duplicate"):
            t.insert(1)

    def test_insert_with_value(self) -> None:
        t = AVLTree()
        t.insert(42, "payload")
        assert t.search(42) == "payload"


# ---------------------------------------------------------------------------
# 3. LL rotation (right-right imbalance)
# ---------------------------------------------------------------------------


class TestLLRotation:
    def test_ll_rotation(self) -> None:
        t = AVLTree()
        t.insert(3)
        t.insert(2)
        t.insert(1)
        assert t.is_avl_valid()
        assert t.height() == 1

    def test_root_after_ll(self) -> None:
        t = AVLTree()
        t.insert(3)
        t.insert(2)
        t.insert(1)
        assert t.min() == 1
        assert t.max() == 3


# ---------------------------------------------------------------------------
# 4. RR rotation (left-left imbalance)
# ---------------------------------------------------------------------------


class TestRRRotation:
    def test_rr_rotation(self) -> None:
        t = AVLTree()
        t.insert(1)
        t.insert(2)
        t.insert(3)
        assert t.is_avl_valid()
        assert t.height() == 1

    def test_root_after_rr(self) -> None:
        t = AVLTree()
        t.insert(1)
        t.insert(2)
        t.insert(3)
        assert t.min() == 1
        assert t.max() == 3


# ---------------------------------------------------------------------------
# 5. LR rotation (left-right imbalance)
# ---------------------------------------------------------------------------


class TestLRRotation:
    def test_lr_rotation(self) -> None:
        t = AVLTree()
        t.insert(3)
        t.insert(1)
        t.insert(2)
        assert t.is_avl_valid()
        assert t.height() == 1

    def test_root_after_lr(self) -> None:
        t = AVLTree()
        t.insert(3)
        t.insert(1)
        t.insert(2)
        assert list(t) == [1, 2, 3]
        assert t.size() == 3


# ---------------------------------------------------------------------------
# 6. RL rotation (right-left imbalance)
# ---------------------------------------------------------------------------


class TestRLRotation:
    def test_rl_rotation(self) -> None:
        t = AVLTree()
        t.insert(1)
        t.insert(3)
        t.insert(2)
        assert t.is_avl_valid()
        assert t.height() == 1

    def test_root_after_rl(self) -> None:
        t = AVLTree()
        t.insert(1)
        t.insert(3)
        t.insert(2)
        assert list(t) == [1, 2, 3]


# ---------------------------------------------------------------------------
# 7. Deletion
# ---------------------------------------------------------------------------


class TestDeletion:
    def test_delete_leaf(self) -> None:
        t = _build([5, 3, 7])
        t.delete(3)
        assert list(t) == [5, 7]
        assert t.is_avl_valid()

    def test_delete_node_with_one_child(self) -> None:
        t = _build([5, 3, 7, 2])
        t.delete(3)
        assert list(t) == [2, 5, 7]
        assert t.is_avl_valid()

    def test_delete_node_with_two_children(self) -> None:
        t = _build([5, 3, 7, 2, 4, 6, 8])
        t.delete(5)
        assert list(t) == [2, 3, 4, 6, 7, 8]
        assert t.is_avl_valid()

    def test_delete_root(self) -> None:
        t = _build([10])
        t.delete(10)
        assert t.is_empty()

    def test_delete_triggers_rotation(self) -> None:
        t = _build([5, 3, 7, 2, 4, 6, 8, 1])
        t.delete(8)
        assert t.is_avl_valid()
        assert list(t) == [1, 2, 3, 4, 5, 6, 7]

    def test_delete_not_found(self) -> None:
        t = _build([1, 2, 3])
        with pytest.raises(KeyError):
            t.delete(99)

    def test_delete_from_empty(self) -> None:
        with pytest.raises(KeyError):
            AVLTree().delete(1)

    def test_delete_maintains_balance(self) -> None:
        import random
        t = AVLTree()
        values = list(range(100))
        random.shuffle(values)
        for v in values:
            t.insert(v)
        for v in values[:50]:
            t.delete(v)
        assert t.is_avl_valid()


# ---------------------------------------------------------------------------
# 8. Search / contains
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
# 9. Balance factor
# ---------------------------------------------------------------------------


class TestBalanceFactor:
    def test_balance_factor_exists(self) -> None:
        t = _build([5, 3, 7])
        bf = t.balance_factor(5)
        assert isinstance(bf, int)

    def test_balance_factor_missing(self) -> None:
        t = _build([1, 2])
        with pytest.raises(KeyError):
            t.balance_factor(99)


# ---------------------------------------------------------------------------
# 10. Validation
# ---------------------------------------------------------------------------


class TestValidation:
    def test_is_avl_valid_empty(self) -> None:
        assert AVLTree().is_avl_valid() is True

    def test_is_avl_valid_single(self) -> None:
        t = _build([1])
        assert t.is_avl_valid() is True

    def test_is_avl_valid_complex(self) -> None:
        t = _build([10, 5, 15, 3, 7, 12, 18, 1, 4, 6, 8])
        assert t.is_avl_valid() is True

    def test_validate_method(self) -> None:
        t = _build([5, 3, 7])
        assert t.validate() is True

    def test_height_maintained_on_rotation(self) -> None:
        t = _build([1, 2, 3, 4, 5, 6, 7])
        h = t.height()
        assert h == 2
        assert t.is_avl_valid()


# ---------------------------------------------------------------------------
# 11. Traversal / inherited methods
# ---------------------------------------------------------------------------


class TestInheritedBehavior:
    def test_inorder(self) -> None:
        t = _build([5, 3, 7, 2, 4, 6, 8])
        assert list(t) == [2, 3, 4, 5, 6, 7, 8]

    def test_predecessor(self) -> None:
        t = _build([5, 3, 7])
        assert t.predecessor(5) == 3
        assert t.predecessor(3) is None

    def test_successor(self) -> None:
        t = _build([5, 3, 7])
        assert t.successor(5) == 7
        assert t.successor(7) is None

    def test_min_max(self) -> None:
        t = _build([5, 2, 8, 1, 9])
        assert t.min() == 1
        assert t.max() == 9

    def test_floor_ceil(self) -> None:
        t = _build([5, 3, 7])
        assert t.floor(4) == 3
        assert t.ceil(4) == 5

    def test_copy(self) -> None:
        t = _build([5, 3, 7])
        cp = t.copy()
        assert list(cp) == [3, 5, 7]
        cp.insert(99)
        assert 99 not in t

    def test_range_query(self) -> None:
        t = _build([5, 3, 7, 2, 4, 6, 8])
        assert t.range_query(3, 6) == [3, 4, 5, 6]

    def test_kth_smallest(self) -> None:
        t = _build([5, 3, 7, 2, 4, 6, 8])
        assert t.kth_smallest(1) == 2
        assert t.kth_smallest(4) == 5

    def test_kth_largest(self) -> None:
        t = _build([5, 3, 7, 2, 4, 6, 8])
        assert t.kth_largest(1) == 8
        assert t.kth_largest(4) == 5

    def test_serialize_roundtrip(self) -> None:
        t = _build([5, 3, 7, 2, 4, 6, 8])
        data = t.serialize()
        restored = AVLTree()
        restored.deserialize(data)
        assert list(restored) == [2, 3, 4, 5, 6, 7, 8]
        assert restored.is_avl_valid()


# ---------------------------------------------------------------------------
# 12. Clear
# ---------------------------------------------------------------------------


class TestClear:
    def test_clear(self) -> None:
        t = _build([1, 2, 3, 4, 5])
        t.clear()
        assert t.is_empty()
        assert t.is_avl_valid()

    def test_clear_reuse(self) -> None:
        t = _build([1, 2, 3])
        t.clear()
        t.insert(99)
        assert 99 in t


# ---------------------------------------------------------------------------
# 13. Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_single_element(self) -> None:
        t = _build([42])
        assert t.height() == 0
        assert t.is_avl_valid()
        assert t.validate()

    def test_large_random(self) -> None:
        import random
        t = AVLTree()
        values = list(range(1000))
        random.shuffle(values)
        for v in values:
            t.insert(v)
        assert t.is_avl_valid()
        assert t.size() == 1000
        assert list(t) == list(range(1000))

    def test_duplicate_values(self) -> None:
        t = AVLTree()
        t.insert(5, "a")
        t.insert(5, "b")
        assert t.search(5) == "b"
        assert t.size() == 1
