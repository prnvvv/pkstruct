"""
pkstruct.trees.tests.test_fenwick_tree
=======================================
Comprehensive tests for FenwickTree.
"""

from __future__ import annotations

import pytest
from pkstruct.trees.fenwick_tree import FenwickTree


# ---------------------------------------------------------------------------
# 1. Creation
# ---------------------------------------------------------------------------


class TestCreation:
    def test_create_with_data(self) -> None:
        ft = FenwickTree([3, 2, -1, 6, 5, 4, -3, 3, 7, 2, 3])
        assert ft.size == 11
        assert len(ft) == 11

    def test_create_with_n(self) -> None:
        ft = FenwickTree(n=10)
        assert ft.size == 10

    def test_create_no_args_raises(self) -> None:
        with pytest.raises(ValueError, match="Provide"):
            FenwickTree()

    def test_create_non_numeric_raises(self) -> None:
        with pytest.raises(TypeError):
            FenwickTree([1, "two", 3])


# ---------------------------------------------------------------------------
# 2. Build
# ---------------------------------------------------------------------------


class TestBuild:
    def test_build_override(self) -> None:
        ft = FenwickTree(n=5)
        ft.build([1, 2, 3, 4, 5])
        assert ft.size == 5

    def test_build_empty_raises(self) -> None:
        ft = FenwickTree(n=3)
        with pytest.raises(TypeError):
            ft.build([])


# ---------------------------------------------------------------------------
# 3. Prefix sum / query
# ---------------------------------------------------------------------------


class TestPrefixSum:
    def test_prefix_sum_basic(self) -> None:
        ft = FenwickTree([3, 2, -1, 6, 5, 4, -3, 3, 7, 2, 3])
        assert ft.prefix_sum(6) == 19

    def test_query_alias(self) -> None:
        ft = FenwickTree([1, 2, 3, 4, 5])
        assert ft.query(3) == ft.prefix_sum(3)

    def test_prefix_sum_full(self) -> None:
        ft = FenwickTree([1, 2, 3, 4, 5])
        assert ft.query(5) == 15

    def test_prefix_sum_first(self) -> None:
        ft = FenwickTree([1, 2, 3])
        assert ft.query(1) == 1

    def test_prefix_sum_out_of_bounds(self) -> None:
        ft = FenwickTree([1, 2, 3])
        with pytest.raises(IndexError):
            ft.query(0)
        with pytest.raises(IndexError):
            ft.query(10)


# ---------------------------------------------------------------------------
# 4. Range query
# ---------------------------------------------------------------------------


class TestRangeQuery:
    def test_range_query_basic(self) -> None:
        ft = FenwickTree([3, 2, -1, 6, 5, 4, -3, 3, 7, 2, 3])
        assert ft.range_query(1, 6) == 19

    def test_range_query_single(self) -> None:
        ft = FenwickTree([1, 2, 3, 4, 5])
        assert ft.range_query(3, 3) == 3

    def test_range_query_invalid(self) -> None:
        ft = FenwickTree([1, 2, 3])
        with pytest.raises(ValueError, match="left.*right"):
            ft.range_query(3, 1)

    def test_range_query_out_of_bounds(self) -> None:
        ft = FenwickTree([1, 2, 3])
        with pytest.raises(IndexError):
            ft.range_query(1, 10)


# ---------------------------------------------------------------------------
# 5. Update
# ---------------------------------------------------------------------------


class TestUpdate:
    def test_update_add(self) -> None:
        ft = FenwickTree([3, 2, -1, 6, 5, 4, -3, 3, 7, 2, 3])
        ft.update(3, 6)
        assert ft.range_query(1, 6) == 25

    def test_update_reflected(self) -> None:
        ft = FenwickTree([1, 2, 3, 4, 5])
        ft.update(2, 10)
        assert ft.query(2) == 1 + 2 + 10

    def test_update_invalid_index(self) -> None:
        ft = FenwickTree([1, 2, 3])
        with pytest.raises(IndexError):
            ft.update(0, 5)
        with pytest.raises(IndexError):
            ft.update(10, 5)


# ---------------------------------------------------------------------------
# 6. Lower bound
# ---------------------------------------------------------------------------


class TestLowerBound:
    def test_lower_bound_basic(self) -> None:
        ft = FenwickTree([3, 2, -1, 6, 5, 4, -3, 3, 7, 2, 3])
        p = ft.lower_bound(25)
        assert p == 9

    def test_lower_bound_exact(self) -> None:
        ft = FenwickTree([1, 2, 3, 4, 5])
        assert ft.lower_bound(6) == 3

    def test_lower_bound_first(self) -> None:
        ft = FenwickTree([1, 2, 3])
        assert ft.lower_bound(1) == 1

    def test_lower_bound_beyond_sum(self) -> None:
        ft = FenwickTree([1, 2, 3])
        p = ft.lower_bound(100)
        assert p == ft.size + 1


# ---------------------------------------------------------------------------
# 7. Clear
# ---------------------------------------------------------------------------


class TestClear:
    def test_clear_resets(self) -> None:
        ft = FenwickTree([1, 2, 3, 4, 5])
        ft.clear()
        for i in range(1, 6):
            assert ft.query(i) == 0

    def test_clear_preserves_size(self) -> None:
        ft = FenwickTree([1, 2, 3])
        ft.clear()
        assert ft.size == 3


# ---------------------------------------------------------------------------
# 8. Validate
# ---------------------------------------------------------------------------


class TestValidate:
    def test_validate_basic(self) -> None:
        ft = FenwickTree([1, 2, 3, 4, 5])
        assert ft.validate() is True


# ---------------------------------------------------------------------------
# 9. Dunder
# ---------------------------------------------------------------------------


class TestDunders:
    def test_len(self) -> None:
        ft = FenwickTree([1, 2, 3])
        assert len(ft) == 3

    def test_repr(self) -> None:
        ft = FenwickTree([1, 2, 3])
        r = repr(ft)
        assert "FenwickTree" in r


# ---------------------------------------------------------------------------
# 10. Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_single_element(self) -> None:
        ft = FenwickTree([42])
        assert ft.query(1) == 42
        assert ft.range_query(1, 1) == 42
        ft.update(1, 10)
        assert ft.query(1) == 52

    def test_negative_numbers(self) -> None:
        ft = FenwickTree([-5, 10, -3, 7])
        assert ft.query(2) == 5
        assert ft.query(4) == 9

    def test_large(self) -> None:
        data = list(range(1, 1001))
        ft = FenwickTree(data)
        assert ft.query(1000) == sum(data)
        ft.update(500, 100)
        assert ft.query(1000) == sum(data) + 100

    def test_zeroes(self) -> None:
        ft = FenwickTree([0, 0, 0, 0])
        assert ft.query(4) == 0
        ft.update(2, 5)
        assert ft.query(4) == 5
