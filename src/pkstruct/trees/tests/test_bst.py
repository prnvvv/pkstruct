"""
pkstruct.trees.tests.test_bst
=============================
Comprehensive tests for BinarySearchTree.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from pkstruct.trees.bst import BinarySearchTree

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build(values: list[Any]) -> BinarySearchTree:
    bst = BinarySearchTree()
    for v in values:
        bst.insert(v)
    return bst


# ---------------------------------------------------------------------------
# 1. Creation / empty state
# ---------------------------------------------------------------------------


class TestCreation:
    def test_create_empty(self) -> None:
        bst = BinarySearchTree()
        assert bst.is_empty()
        assert len(bst) == 0
        assert bst.size() == 0
        assert list(bst) == []

    def test_empty_contains(self) -> None:
        bst = BinarySearchTree()
        assert 1 not in bst

    def test_empty_height(self) -> None:
        bst = BinarySearchTree()
        assert bst.height() == -1

    def test_empty_min_raises(self) -> None:
        bst = BinarySearchTree()
        with pytest.raises(ValueError, match="empty"):
            bst.min()

    def test_empty_max_raises(self) -> None:
        bst = BinarySearchTree()
        with pytest.raises(ValueError, match="empty"):
            bst.max()


# ---------------------------------------------------------------------------
# 2. Insertion
# ---------------------------------------------------------------------------


class TestInsertion:
    def test_insert_single(self) -> None:
        bst = _build([10])
        assert len(bst) == 1
        assert 10 in bst

    def test_insert_multiple(self) -> None:
        bst = _build([5, 3, 7, 2, 4, 6, 8])
        assert len(bst) == 7
        assert list(bst) == [2, 3, 4, 5, 6, 7, 8]

    def test_insert_duplicate_default(self) -> None:
        bst = _build([5, 3, 5])
        assert len(bst) == 2

    def test_insert_duplicate_updates_value(self) -> None:
        bst = BinarySearchTree()
        bst.insert("a", 1)
        bst.insert("a", 2)
        assert bst.search("a") == 2
        assert len(bst) == 1

    def test_insert_duplicate_rejected(self) -> None:
        bst = BinarySearchTree(allow_duplicates=True)
        bst.insert(1)
        with pytest.raises(ValueError, match="Duplicate"):
            bst.insert(1)

    def test_insert_with_value(self) -> None:
        bst = BinarySearchTree()
        bst.insert(42, "hello")
        assert bst.search(42) == "hello"


# ---------------------------------------------------------------------------
# 3. Search / contains
# ---------------------------------------------------------------------------


class TestSearch:
    def test_search_found(self) -> None:
        bst = _build([10, 20, 30])
        assert 20 in bst

    def test_search_not_found(self) -> None:
        bst = _build([1, 2, 3])
        assert bst.search(99) is None

    def test_search_empty(self) -> None:
        bst = BinarySearchTree()
        assert bst.search(1) is None

    def test_contains_operator(self) -> None:
        bst = _build([5, 15, 25])
        assert 15 in bst
        assert 99 not in bst


# ---------------------------------------------------------------------------
# 4. Deletion
# ---------------------------------------------------------------------------


class TestDeletion:
    def test_delete_leaf(self) -> None:
        bst = _build([5, 3, 7])
        bst.delete(3)
        assert list(bst) == [5, 7]
        assert len(bst) == 2

    def test_delete_node_with_one_child(self) -> None:
        bst = _build([5, 3, 7, 2])
        bst.delete(3)
        assert list(bst) == [2, 5, 7]
        assert len(bst) == 3

    def test_delete_node_with_two_children(self) -> None:
        bst = _build([5, 3, 7, 2, 4, 6, 8])
        bst.delete(5)
        assert list(bst) == [2, 3, 4, 6, 7, 8]
        assert len(bst) == 6

    def test_delete_root(self) -> None:
        bst = _build([10])
        bst.delete(10)
        assert bst.is_empty()

    def test_delete_not_found(self) -> None:
        bst = _build([1, 2, 3])
        with pytest.raises(KeyError):
            bst.delete(99)

    def test_delete_from_empty(self) -> None:
        bst = BinarySearchTree()
        with pytest.raises(KeyError):
            bst.delete(1)

    def test_delete_all(self) -> None:
        bst = _build([4, 2, 6, 1, 3, 5, 7])
        for v in [1, 2, 3, 4, 5, 6, 7]:
            bst.delete(v)
        assert bst.is_empty()


# ---------------------------------------------------------------------------
# 5. Update
# ---------------------------------------------------------------------------


class TestUpdate:
    def test_update_existing(self) -> None:
        bst = BinarySearchTree()
        bst.insert("x", 1)
        bst.update("x", 99)
        assert bst.search("x") == 99

    def test_update_missing(self) -> None:
        bst = BinarySearchTree()
        with pytest.raises(KeyError):
            bst.update("missing", 1)


# ---------------------------------------------------------------------------
# 6. Metrics
# ---------------------------------------------------------------------------


class TestMetrics:
    def test_size(self) -> None:
        bst = _build([5, 3, 7, 2])
        assert bst.size() == 4
        assert len(bst) == 4

    def test_height(self) -> None:
        bst = _build([10, 5, 15, 3, 7])
        assert bst.height() == 2

    def test_height_single(self) -> None:
        bst = _build([1])
        assert bst.height() == 0

    def test_is_empty_false(self) -> None:
        bst = _build([1])
        assert not bst.is_empty()

    def test_min(self) -> None:
        bst = _build([5, 3, 7, 1, 9])
        assert bst.min() == 1

    def test_max(self) -> None:
        bst = _build([5, 3, 7, 1, 9])
        assert bst.max() == 9

    def test_floor(self) -> None:
        bst = _build([5, 3, 7])
        assert bst.floor(4) == 3
        assert bst.floor(5) == 5
        assert bst.floor(2) is None

    def test_ceil(self) -> None:
        bst = _build([5, 3, 7])
        assert bst.ceil(4) == 5
        assert bst.ceil(7) == 7
        assert bst.ceil(8) is None


# ---------------------------------------------------------------------------
# 7. Navigation
# ---------------------------------------------------------------------------


class TestNavigation:
    def test_predecessor(self) -> None:
        bst = _build([5, 3, 7, 2, 4, 6, 8])
        assert bst.predecessor(5) == 4
        assert bst.predecessor(3) == 2
        assert bst.predecessor(2) is None

    def test_predecessor_missing_key(self) -> None:
        bst = _build([1, 2, 3])
        with pytest.raises(KeyError):
            bst.predecessor(99)

    def test_successor(self) -> None:
        bst = _build([5, 3, 7, 2, 4, 6, 8])
        assert bst.successor(5) == 6
        assert bst.successor(7) == 8
        assert bst.successor(8) is None

    def test_successor_missing_key(self) -> None:
        bst = _build([1, 2, 3])
        with pytest.raises(KeyError):
            bst.successor(99)


# ---------------------------------------------------------------------------
# 8. Structural utilities
# ---------------------------------------------------------------------------


class TestStructural:
    def test_validate_valid(self) -> None:
        bst = _build([5, 3, 7, 2, 4, 6, 8])
        assert bst.validate() is True

    def test_validate_empty(self) -> None:
        bst = BinarySearchTree()
        assert bst.validate() is True

    def test_copy_is_deep(self) -> None:
        bst = _build([5, 3, 7])
        cp = bst.copy()
        assert list(cp) == [3, 5, 7]
        cp.insert(99)
        assert 99 not in bst

    def test_invert(self) -> None:
        bst = _build([5, 3, 7, 2, 4])
        bst.invert()
        assert list(bst) == [7, 5, 4, 3, 2]

    def test_is_balanced_empty(self) -> None:
        bst = BinarySearchTree()
        assert bst.is_balanced() is True

    def test_is_balanced_single(self) -> None:
        bst = _build([1])
        assert bst.is_balanced() is True

    def test_diameter(self) -> None:
        bst = _build([5, 3, 7, 2, 4, 6, 8])
        assert bst.diameter() == 4

    def test_diameter_single(self) -> None:
        bst = _build([1])
        assert bst.diameter() == 0

    def test_width(self) -> None:
        bst = _build([5, 3, 7, 2, 4, 6, 8])
        assert bst.width() == 4

    def test_width_empty(self) -> None:
        bst = BinarySearchTree()
        assert bst.width() == 0


# ---------------------------------------------------------------------------
# 9. Traversals
# ---------------------------------------------------------------------------


class TestTraversals:
    def test_inorder(self) -> None:
        bst = _build([5, 3, 7, 2, 4, 6, 8])
        assert list(bst._traverse("inorder")) == [2, 3, 4, 5, 6, 7, 8]

    def test_preorder(self) -> None:
        bst = _build([5, 3, 7, 2, 4, 6, 8])
        assert list(bst._traverse("preorder")) == [5, 3, 2, 4, 7, 6, 8]

    def test_postorder(self) -> None:
        bst = _build([5, 3, 7, 2, 4, 6, 8])
        assert list(bst._traverse("postorder")) == [2, 4, 3, 6, 8, 7, 5]

    def test_level_order(self) -> None:
        bst = _build([5, 3, 7, 2, 4, 6, 8])
        assert list(bst._traverse("levelorder")) == [5, 3, 7, 2, 4, 6, 8]

    def test_unknown_order(self) -> None:
        bst = _build([1])
        with pytest.raises(ValueError, match="Unknown"):
            list(bst._traverse("invalid"))

    def test_zigzag_order(self) -> None:
        bst = _build([5, 3, 7, 2, 4, 6, 8])
        assert bst.zigzag_order() == [[5], [7, 3], [2, 4, 6, 8]]

    def test_vertical_order(self) -> None:
        bst = _build([5, 3, 7, 2, 4, 6, 8])
        result = bst.vertical_order()
        assert len(result) == 5

    def test_boundary_traversal(self) -> None:
        bst = _build([5, 3, 7, 2, 4, 6, 8])
        assert bst.boundary_traversal() == [5, 3, 2, 4, 6, 8, 7]

    def test_iterator(self) -> None:
        bst = _build([5, 3, 7, 2, 4, 6, 8])
        assert list(bst) == [2, 3, 4, 5, 6, 7, 8]

    def test_iter_empty(self) -> None:
        bst = BinarySearchTree()
        assert list(bst) == []


# ---------------------------------------------------------------------------
# 10. Interview utilities
# ---------------------------------------------------------------------------


class TestInterviewUtilities:
    def test_find_lca(self) -> None:
        bst = _build([5, 3, 7, 2, 4, 6, 8])
        assert bst.find_lca(2, 4) == 3
        assert bst.find_lca(2, 8) == 5
        assert bst.find_lca(6, 8) == 7

    def test_find_lca_missing(self) -> None:
        bst = _build([1, 2, 3])
        with pytest.raises(KeyError):
            bst.find_lca(1, 99)

    def test_kth_smallest(self) -> None:
        bst = _build([5, 3, 7, 2, 4, 6, 8])
        assert bst.kth_smallest(1) == 2
        assert bst.kth_smallest(4) == 5
        assert bst.kth_smallest(7) == 8

    def test_kth_smallest_out_of_range(self) -> None:
        bst = _build([1, 2])
        with pytest.raises(ValueError):
            bst.kth_smallest(0)
        with pytest.raises(ValueError):
            bst.kth_smallest(99)

    def test_kth_largest(self) -> None:
        bst = _build([5, 3, 7, 2, 4, 6, 8])
        assert bst.kth_largest(1) == 8
        assert bst.kth_largest(4) == 5
        assert bst.kth_largest(7) == 2

    def test_kth_largest_out_of_range(self) -> None:
        bst = _build([1, 2])
        with pytest.raises(ValueError):
            bst.kth_largest(0)
        with pytest.raises(ValueError):
            bst.kth_largest(99)

    def test_range_query(self) -> None:
        bst = _build([5, 3, 7, 2, 4, 6, 8])
        assert bst.range_query(3, 6) == [3, 4, 5, 6]

    def test_range_query_empty(self) -> None:
        bst = BinarySearchTree()
        assert bst.range_query(1, 10) == []

    def test_path_sum_true(self) -> None:
        bst = _build([5, 3, 7, 2, 4, 6, 8])
        assert bst.path_sum(10) is True

    def test_path_sum_false(self) -> None:
        bst = _build([5, 3, 7])
        assert bst.path_sum(999) is False

    def test_path_sum_empty(self) -> None:
        bst = BinarySearchTree()
        assert bst.path_sum(0) is False

    def test_root_to_leaf_paths(self) -> None:
        bst = _build([5, 3, 7])
        paths = bst.root_to_leaf_paths()
        assert [5, 3] in paths
        assert [5, 7] in paths

    def test_root_to_leaf_paths_empty(self) -> None:
        bst = BinarySearchTree()
        assert bst.root_to_leaf_paths() == []


# ---------------------------------------------------------------------------
# 11. Serialization
# ---------------------------------------------------------------------------


class TestSerialization:
    def test_serialize_roundtrip(self) -> None:
        bst = _build([5, 3, 7, 2, 4, 6, 8])
        data = bst.serialize()
        restored = BinarySearchTree()
        restored.deserialize(data)
        assert list(restored) == [2, 3, 4, 5, 6, 7, 8]
        assert len(restored) == len(bst)

    def test_serialize_empty(self) -> None:
        bst = BinarySearchTree()
        data = bst.serialize()
        assert data == "[]"
        restored = BinarySearchTree()
        restored.deserialize(data)
        assert restored.is_empty()

    def test_deserialize_empty_array(self) -> None:
        bst = BinarySearchTree()
        bst.deserialize("[]")
        assert bst.is_empty()

    def test_serialize_is_json(self) -> None:
        bst = _build([1, 2, 3])
        data = bst.serialize()
        parsed = json.loads(data)
        assert isinstance(parsed, list)


# ---------------------------------------------------------------------------
# 12. Dunder methods
# ---------------------------------------------------------------------------


class TestDunders:
    def test_len(self) -> None:
        bst = _build([1, 2, 3, 4, 5])
        assert len(bst) == 5

    def test_contains(self) -> None:
        bst = _build([10, 20, 30])
        assert 20 in bst
        assert 99 not in bst

    def test_iter(self) -> None:
        bst = _build([3, 1, 2])
        assert list(bst) == [1, 2, 3]

    def test_repr(self) -> None:
        bst = _build([1, 2, 3])
        r = repr(bst)
        assert "BinarySearchTree" in r
        assert "size" in r


# ---------------------------------------------------------------------------
# 13. Clear
# ---------------------------------------------------------------------------


class TestClear:
    def test_clear_empty(self) -> None:
        bst = BinarySearchTree()
        bst.clear()
        assert bst.is_empty()

    def test_clear_non_empty(self) -> None:
        bst = _build([1, 2, 3, 4, 5])
        bst.clear()
        assert bst.is_empty()
        assert len(bst) == 0

    def test_clear_allows_reuse(self) -> None:
        bst = _build([1, 2, 3])
        bst.clear()
        bst.insert(99)
        assert 99 in bst


# ---------------------------------------------------------------------------
# 14. Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_single_element_ops(self) -> None:
        bst = _build([42])
        assert bst.min() == 42
        assert bst.max() == 42
        assert bst.height() == 0
        assert bst.diameter() == 0
        assert bst.width() == 1
        assert bst.is_balanced() is True
        assert bst.validate() is True
        bst.delete(42)
        assert bst.is_empty()

    def test_large_insertion_order(self) -> None:
        bst = BinarySearchTree()
        n = 1000
        for i in range(n):
            bst.insert(i)
        assert len(bst) == n
        assert list(bst) == list(range(n))

    def test_range_query_no_results(self) -> None:
        bst = _build([10, 20, 30])
        assert bst.range_query(1, 5) == []

    def test_floor_ceil_edge(self) -> None:
        bst = _build([5])
        assert bst.floor(5) == 5
        assert bst.ceil(5) == 5
        assert bst.floor(1) is None
        assert bst.ceil(10) is None
