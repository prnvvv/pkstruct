"""
pkstruct.trees.tests.test_segment_tree
=======================================
Comprehensive tests for SegmentTree.
"""

from __future__ import annotations

import pytest

from pkstruct.trees.segment_tree import SegmentTree

# ---------------------------------------------------------------------------
# 1. Creation / building
# ---------------------------------------------------------------------------


class TestCreation:
    def test_create_from_data(self) -> None:
        st = SegmentTree([1, 3, 5, 7, 9, 11])
        assert st.size == 6
        assert len(st) == 6

    def test_create_empty_raises(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            SegmentTree([])

    def test_create_invalid_operation(self) -> None:
        with pytest.raises(ValueError, match="Unsupported"):
            SegmentTree([1, 2, 3], operation="invalid")

    def test_create_non_int_raises(self) -> None:
        with pytest.raises(TypeError):
            SegmentTree([1, "two", 3])

    def test_all_operations(self) -> None:
        for op in ("sum", "min", "max", "gcd", "xor"):
            st = SegmentTree([1, 2, 3, 4, 5], operation=op)
            assert st.size == 5


# ---------------------------------------------------------------------------
# 2. Query
# ---------------------------------------------------------------------------


class TestQuery:
    def test_query_sum(self) -> None:
        st = SegmentTree([1, 3, 5, 7, 9, 11])
        assert st.query(1, 3) == 15

    def test_query_full_range(self) -> None:
        st = SegmentTree([1, 2, 3, 4, 5])
        assert st.query(0, 4) == 15

    def test_query_single(self) -> None:
        st = SegmentTree([1, 3, 5, 7, 9, 11])
        assert st.query(2, 2) == 5

    def test_query_min(self) -> None:
        st = SegmentTree([3, 1, 4, 1, 5, 9], operation="min")
        assert st.query(0, 5) == 1
        assert st.query(2, 4) == 1

    def test_query_max(self) -> None:
        st = SegmentTree([3, 1, 4, 1, 5, 9], operation="max")
        assert st.query(0, 5) == 9
        assert st.query(0, 2) == 4

    def test_query_gcd(self) -> None:
        st = SegmentTree([12, 18, 24, 36], operation="gcd")
        assert st.query(0, 3) == 6

    def test_query_xor(self) -> None:
        st = SegmentTree([1, 2, 3, 4, 5], operation="xor")
        assert st.query(0, 4) == 1

    def test_query_invalid_range(self) -> None:
        st = SegmentTree([1, 2, 3])
        with pytest.raises(ValueError, match="left.*right"):
            st.query(3, 1)

    def test_query_out_of_bounds(self) -> None:
        st = SegmentTree([1, 2, 3])
        with pytest.raises(IndexError):
            st.query(0, 10)


# ---------------------------------------------------------------------------
# 3. Point update
# ---------------------------------------------------------------------------


class TestPointUpdate:
    def test_update_single(self) -> None:
        st = SegmentTree([1, 3, 5, 7, 9, 11])
        st.update(1, 10)
        assert st.query(1, 3) == 22

    def test_update_verify_full(self) -> None:
        st = SegmentTree([1, 2, 3, 4, 5])
        st.update(2, 10)
        assert st.query(0, 4) == 22
        assert st.query(2, 2) == 10

    def test_update_invalid_index(self) -> None:
        st = SegmentTree([1, 2, 3])
        with pytest.raises(IndexError):
            st.update(10, 5)

    def test_update_non_int(self) -> None:
        st = SegmentTree([1, 2, 3])
        with pytest.raises(TypeError):
            st.update(0, "bad")


# ---------------------------------------------------------------------------
# 4. Range update (lazy propagation)
# ---------------------------------------------------------------------------


class TestRangeUpdate:
    def test_range_update_sum(self) -> None:
        st = SegmentTree([1, 2, 3, 4, 5])
        st.range_update(1, 3, 10)
        assert st.query(1, 3) == 2 + 10 + 3 + 10 + 4 + 10

    def test_range_update_query_full(self) -> None:
        st = SegmentTree([1, 2, 3, 4, 5])
        st.range_update(0, 4, 5)
        assert st.query(0, 4) == 15 + 5 * 5

    def test_range_update_min(self) -> None:
        st = SegmentTree([10, 20, 30, 40], operation="min")
        st.range_update(1, 2, 5)
        assert st.query(1, 2) == 5

    def test_range_update_max(self) -> None:
        st = SegmentTree([10, 20, 30, 40], operation="max")
        st.range_update(0, 1, 50)
        assert st.query(0, 1) == 50

    def test_range_update_invalid(self) -> None:
        st = SegmentTree([1, 2, 3])
        with pytest.raises(ValueError):
            st.range_update(2, 1, 5)


# ---------------------------------------------------------------------------
# 5. Rebuild
# ---------------------------------------------------------------------------


class TestRebuild:
    def test_rebuild_new_data(self) -> None:
        st = SegmentTree([1, 2, 3])
        st.rebuild([10, 20, 30, 40])
        assert st.size == 4
        assert st.query(0, 3) == 100


# ---------------------------------------------------------------------------
# 6. Clear
# ---------------------------------------------------------------------------


class TestClear:
    def test_clear(self) -> None:
        st = SegmentTree([1, 2, 3, 4, 5])
        st.clear()
        assert st.size == 0

    def test_clear_rebuild(self) -> None:
        st = SegmentTree([1, 2, 3])
        st.clear()
        st.build([10, 20])
        assert st.query(0, 1) == 30


# ---------------------------------------------------------------------------
# 7. Validate
# ---------------------------------------------------------------------------


class TestValidate:
    def test_validate_returns_true(self) -> None:
        st = SegmentTree([1, 2, 3, 4, 5])
        assert st.validate() is True

    def test_validate_empty(self) -> None:
        st = SegmentTree([1])
        st.clear()
        assert st.validate() is True


# ---------------------------------------------------------------------------
# 8. Dunder
# ---------------------------------------------------------------------------


class TestDunders:
    def test_len(self) -> None:
        st = SegmentTree([1, 2, 3])
        assert len(st) == 3

    def test_repr(self) -> None:
        st = SegmentTree([1, 2, 3], operation="min")
        r = repr(st)
        assert "SegmentTree" in r
        assert "min" in r


# ---------------------------------------------------------------------------
# 9. Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_single_element(self) -> None:
        st = SegmentTree([42])
        assert st.query(0, 0) == 42
        st.update(0, 99)
        assert st.query(0, 0) == 99

    def test_two_elements(self) -> None:
        st = SegmentTree([5, 10])
        assert st.query(0, 1) == 15
        st.range_update(0, 1, 3)
        assert st.query(0, 1) == 21

    def test_large_array(self) -> None:
        data = list(range(1000))
        st = SegmentTree(data)
        assert st.query(0, 999) == sum(data)
        st.update(500, 0)
        assert st.query(0, 999) == sum(data) - 500

    def test_multiple_operations(self) -> None:
        st = SegmentTree([1, 2, 3, 4, 5])
        st.update(0, 10)
        st.range_update(2, 4, 3)
        assert st.query(0, 4) == 10 + 2 + (3 + 3) + (4 + 3) + (5 + 3)
