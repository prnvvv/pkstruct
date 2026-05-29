"""
pkstruct.trees.tests.test_interval_tree
========================================
Comprehensive tests for IntervalTree.
"""

from __future__ import annotations

import pytest

from pkstruct.trees.interval_tree import IntervalTree

# ---------------------------------------------------------------------------
# 1. Creation / empty state
# ---------------------------------------------------------------------------


class TestCreation:
    def test_create_empty(self) -> None:
        t = IntervalTree()
        assert len(t) == 0
        assert t.size == 0
        assert t.height() == 0
        assert t.max_endpoint is None

    def test_empty_iter(self) -> None:
        t = IntervalTree()
        assert list(t) == []

    def test_empty_contains(self) -> None:
        t = IntervalTree()
        assert (1, 2) not in t

    def test_empty_search(self) -> None:
        t = IntervalTree()
        assert t.search(1, 10) == []

    def test_empty_overlap(self) -> None:
        t = IntervalTree()
        assert t.overlap(1, 10) is False

    def test_empty_contains_point(self) -> None:
        t = IntervalTree()
        assert t.contains_point(5) == []


# ---------------------------------------------------------------------------
# 2. Insertion
# ---------------------------------------------------------------------------


class TestInsertion:
    def test_insert_single(self) -> None:
        t = IntervalTree()
        t.insert(15, 20)
        assert len(t) == 1
        assert (15, 20) in t

    def test_insert_multiple(self) -> None:
        t = IntervalTree()
        t.insert(15, 20)
        t.insert(10, 30)
        t.insert(17, 19)
        assert len(t) == 3

    def test_insert_invalid_interval(self) -> None:
        t = IntervalTree()
        with pytest.raises(ValueError, match="Invalid"):
            t.insert(10, 5)

    def test_insert_maintains_height(self) -> None:
        t = IntervalTree()
        for i in range(100):
            t.insert(i, i + 1)
        h = t.height()
        import math
        max_possible = int(2 * math.log2(100)) + 1
        assert h <= max_possible


# ---------------------------------------------------------------------------
# 3. Search / overlap
# ---------------------------------------------------------------------------


class TestSearch:
    def test_search_overlap(self) -> None:
        t = IntervalTree()
        t.insert(15, 20)
        t.insert(10, 30)
        t.insert(17, 19)
        t.insert(5, 7)
        results = t.search(14, 16)
        assert (15, 20) in results
        assert (10, 30) in results
        assert (5, 7) not in results

    def test_search_no_results(self) -> None:
        t = IntervalTree()
        t.insert(1, 5)
        t.insert(10, 15)
        assert t.search(6, 9) == []

    def test_search_empty(self) -> None:
        t = IntervalTree()
        assert t.search(1, 10) == []

    def test_overlap_true(self) -> None:
        t = IntervalTree()
        t.insert(15, 20)
        assert t.overlap(14, 16) is True
        assert t.overlap(19, 21) is True
        assert t.overlap(10, 14) is False

    def test_overlap_false(self) -> None:
        t = IntervalTree()
        t.insert(5, 10)
        assert t.overlap(1, 4) is False
        assert t.overlap(11, 15) is False

    def test_all_overlaps_alias(self) -> None:
        t = IntervalTree()
        t.insert(15, 20)
        t.insert(10, 30)
        assert t.all_overlaps(14, 16) == t.search(14, 16)


# ---------------------------------------------------------------------------
# 4. Contains point
# ---------------------------------------------------------------------------


class TestContainsPoint:
    def test_contains_point(self) -> None:
        t = IntervalTree()
        t.insert(15, 20)
        t.insert(10, 30)
        t.insert(17, 19)
        results = t.contains_point(18)
        assert (15, 20) in results
        assert (10, 30) in results
        assert (17, 19) in results

    def test_contains_point_missing(self) -> None:
        t = IntervalTree()
        t.insert(1, 5)
        assert t.contains_point(10) == []


# ---------------------------------------------------------------------------
# 5. Deletion
# ---------------------------------------------------------------------------


class TestDeletion:
    def test_delete_interval(self) -> None:
        t = IntervalTree()
        t.insert(15, 20)
        t.insert(10, 30)
        t.delete(15, 20)
        assert (15, 20) not in t
        assert len(t) == 1

    def test_delete_not_found(self) -> None:
        t = IntervalTree()
        t.insert(1, 5)
        with pytest.raises(KeyError):
            t.delete(10, 15)

    def test_delete_from_empty(self) -> None:
        t = IntervalTree()
        with pytest.raises(KeyError):
            t.delete(1, 2)

    def test_delete_maintains_structure(self) -> None:
        t = IntervalTree()
        intervals = [(15, 20), (10, 30), (17, 19), (5, 7), (1, 3)]
        for s, e in intervals:
            t.insert(s, e)
        t.delete(15, 20)
        assert t.size == 4
        assert t.height() >= 0


# ---------------------------------------------------------------------------
# 6. Merge overlaps
# ---------------------------------------------------------------------------


class TestMergeOverlaps:
    def test_merge_overlapping(self) -> None:
        t = IntervalTree()
        t.insert(1, 3)
        t.insert(2, 6)
        t.insert(8, 10)
        t.insert(15, 18)
        t.insert(17, 20)
        t.merge_overlaps()
        intervals = list(t)
        assert (1, 6) in intervals
        assert (8, 10) in intervals
        assert (15, 20) in intervals

    def test_merge_empty(self) -> None:
        t = IntervalTree()
        t.merge_overlaps()
        assert t.size == 0

    def test_merge_touching(self) -> None:
        t = IntervalTree()
        t.insert(1, 5)
        t.insert(6, 10)
        t.merge_overlaps()
        assert list(t) == [(1, 10)]

    def test_merge_single(self) -> None:
        t = IntervalTree()
        t.insert(1, 5)
        t.merge_overlaps()
        assert list(t) == [(1, 5)]


# ---------------------------------------------------------------------------
# 7. Validate
# ---------------------------------------------------------------------------


class TestValidate:
    def test_validate_empty(self) -> None:
        t = IntervalTree()
        assert t.validate() is True

    def test_validate_non_empty(self) -> None:
        t = IntervalTree()
        t.insert(15, 20)
        t.insert(10, 30)
        t.insert(17, 19)
        assert t.validate() is True


# ---------------------------------------------------------------------------
# 8. Clear
# ---------------------------------------------------------------------------


class TestClear:
    def test_clear(self) -> None:
        t = IntervalTree()
        t.insert(1, 5)
        t.insert(10, 15)
        t.clear()
        assert t.size == 0
        assert t.height() == 0
        assert t.max_endpoint is None

    def test_clear_reuse(self) -> None:
        t = IntervalTree()
        t.insert(1, 5)
        t.clear()
        t.insert(10, 20)
        assert list(t) == [(10, 20)]


# ---------------------------------------------------------------------------
# 9. Dunder
# ---------------------------------------------------------------------------


class TestDunders:
    def test_len(self) -> None:
        t = IntervalTree()
        t.insert(1, 5)
        t.insert(10, 15)
        assert len(t) == 2

    def test_contains(self) -> None:
        t = IntervalTree()
        t.insert(15, 20)
        assert (15, 20) in t
        assert (1, 2) not in t
        assert "invalid" not in t

    def test_iter(self) -> None:
        t = IntervalTree()
        t.insert(5, 10)
        t.insert(1, 3)
        assert list(t) == [(1, 3), (5, 10)]

    def test_repr(self) -> None:
        t = IntervalTree()
        t.insert(15, 20)
        r = repr(t)
        assert "IntervalTree" in r


# ---------------------------------------------------------------------------
# 10. Max endpoint maintenance
# ---------------------------------------------------------------------------


class TestMaxEndpoint:
    def test_max_endpoint_after_insert(self) -> None:
        t = IntervalTree()
        t.insert(1, 5)
        assert t.max_endpoint == 5
        t.insert(10, 20)
        assert t.max_endpoint == 20

    def test_max_endpoint_after_delete(self) -> None:
        t = IntervalTree()
        t.insert(1, 5)
        t.insert(10, 20)
        t.delete(10, 20)
        assert t.max_endpoint == 5


# ---------------------------------------------------------------------------
# 11. Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_point_intervals(self) -> None:
        t = IntervalTree()
        t.insert(5, 5)
        t.insert(10, 10)
        assert t.search(5, 5) == [(5, 5)]
        assert t.contains_point(5) == [(5, 5)]

    def test_large_insertion(self) -> None:
        t = IntervalTree()
        n = 500
        for i in range(n):
            t.insert(i, i + 10)
        assert t.size == n
        assert t.validate() is True
