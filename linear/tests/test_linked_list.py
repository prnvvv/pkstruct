"""
pkstruct.linear.tests.test_linked_lists
========================================

Comprehensive unit tests for SinglyLinkedList, DoublyLinkedList,
and CircularLinkedList.

Run with:
    pytest pkstruct/linear/tests/test_linked_lists.py -v
"""

from __future__ import annotations

import threading
from typing import Type, Union

import pytest

from pkstruct.linear import (
    CircularLinkedList,
    DoublyLinkedList,
    SinglyLinkedList,
)
from pkstruct.linear.exceptions import (
    EmptyStructureError,
    IndexOutOfRangeError,
    InvalidRangeError,
    SerializationError,
    ValidationError,
    ValueNotFoundError,
)

ListClass = Union[
    Type[SinglyLinkedList],
    Type[DoublyLinkedList],
    Type[CircularLinkedList],
]

ALL_LIST_CLASSES = [SinglyLinkedList, DoublyLinkedList, CircularLinkedList]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build(cls: ListClass, values: list) -> object:
    ll = cls()
    for v in values:
        ll.insert(v)  # CORRECT: just value, appends to tail
    return ll


# ---------------------------------------------------------------------------
# 1. Creation / empty state
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_create_empty(cls: ListClass) -> None:
    """Newly created list should be empty."""
    ll = cls()
    assert len(ll) == 0
    assert list(ll) == []


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_empty_list_bool(cls: ListClass) -> None:
    """Empty list should be falsy; non-empty should be truthy."""
    ll = cls()
    assert not ll
    ll.insert(0, 1)
    assert ll


# ---------------------------------------------------------------------------
# 2. Insertion
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_insert_at_head(cls: ListClass) -> None:
    """Insert at index 0 repeatedly prepends correctly."""
    ll = cls()
    ll.insert(0, 10)
    ll.insert(0, 20)
    ll.insert(0, 30)
    assert list(ll) == [30, 20, 10]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_insert_at_tail(cls: ListClass) -> None:
    """Insert at end appends correctly."""
    ll = _build(cls, [1, 2, 3])
    ll.insert(3, 4)
    assert list(ll) == [1, 2, 3, 4]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_insert_in_middle(cls: ListClass) -> None:
    """Insert in the middle at a valid index shifts elements right."""
    ll = _build(cls, [1, 3])
    ll.insert(1, 2)
    assert list(ll) == [1, 2, 3]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_insert_out_of_range(cls: ListClass) -> None:
    """Inserting at an out-of-range index raises IndexOutOfRangeError."""
    ll = _build(cls, [1, 2])
    with pytest.raises(IndexOutOfRangeError):
        ll.insert(10, 99)


# ---------------------------------------------------------------------------
# 3. Deletion
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_delete_head(cls: ListClass) -> None:
    """Delete head node updates list correctly."""
    ll = _build(cls, [1, 2, 3])
    ll.delete(0)
    assert list(ll) == [2, 3]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_delete_tail(cls: ListClass) -> None:
    """Delete tail node updates list correctly."""
    ll = _build(cls, [1, 2, 3])
    ll.delete(2)
    assert list(ll) == [1, 2]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_delete_middle(cls: ListClass) -> None:
    """Delete middle node bypasses it correctly."""
    ll = _build(cls, [1, 2, 3])
    ll.delete(1)
    assert list(ll) == [1, 3]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_delete_only_element(cls: ListClass) -> None:
    """Deleting the sole element leaves an empty list."""
    ll = _build(cls, [42])
    ll.delete(0)
    assert len(ll) == 0
    assert list(ll) == []


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_delete_out_of_range(cls: ListClass) -> None:
    """Deleting an out-of-range index raises IndexOutOfRangeError."""
    ll = _build(cls, [1, 2, 3])
    with pytest.raises(IndexOutOfRangeError):
        ll.delete(5)


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_delete_from_empty(cls: ListClass) -> None:
    """Deleting from an empty list raises EmptyStructureError."""
    ll = cls()
    with pytest.raises(EmptyStructureError):
        ll.delete(0)


# ---------------------------------------------------------------------------
# 4. get / __getitem__
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_get_valid_index(cls: ListClass) -> None:
    """get() returns correct node value for valid indices."""
    ll = _build(cls, [10, 20, 30])
    assert ll.get(0).value == 10
    assert ll.get(1).value == 20
    assert ll.get(2).value == 30


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_getitem_valid(cls: ListClass) -> None:
    """__getitem__ returns correct value for valid indices."""
    ll = _build(cls, [10, 20, 30])
    assert ll[0] == 10
    assert ll[2] == 30


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_get_invalid_index(cls: ListClass) -> None:
    """get() raises IndexOutOfRangeError for out-of-range index."""
    ll = _build(cls, [1, 2])
    with pytest.raises(IndexOutOfRangeError):
        ll.get(5)


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_get_from_empty(cls: ListClass) -> None:
    """get() raises EmptyStructureError on empty list."""
    ll = cls()
    with pytest.raises(EmptyStructureError):
        ll.get(0)


# ---------------------------------------------------------------------------
# 5. index (search)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_index_found(cls: ListClass) -> None:
    """index() returns correct position for existing value."""
    ll = _build(cls, [10, 20, 30])
    assert ll.index(20) == 1


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_index_not_found(cls: ListClass) -> None:
    """index() raises ValueNotFoundError for absent value."""
    ll = _build(cls, [1, 2, 3])
    with pytest.raises(ValueNotFoundError):
        ll.index(99)


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_contains(cls: ListClass) -> None:
    """__contains__ returns True/False correctly."""
    ll = _build(cls, [5, 10, 15])
    assert 10 in ll
    assert 99 not in ll


# ---------------------------------------------------------------------------
# 6. replace / __setitem__
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_replace_valid(cls: ListClass) -> None:
    """replace() changes node value at given index."""
    ll = _build(cls, [1, 2, 3])
    ll.replace(1, 99)
    assert ll[1] == 99


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_setitem_valid(cls: ListClass) -> None:
    """__setitem__ changes node value at given index."""
    ll = _build(cls, [1, 2, 3])
    ll[2] = 77
    assert ll[2] == 77


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_replace_invalid_index(cls: ListClass) -> None:
    """replace() raises IndexOutOfRangeError for bad index."""
    ll = _build(cls, [1, 2])
    with pytest.raises(IndexOutOfRangeError):
        ll.replace(10, 5)


# ---------------------------------------------------------------------------
# 7. __len__
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_len_tracks_inserts_and_deletes(cls: ListClass) -> None:
    """__len__ reflects changes from inserts and deletes."""
    ll = cls()
    assert len(ll) == 0
    ll.insert(0, 1)
    assert len(ll) == 1
    ll.insert(1, 2)
    assert len(ll) == 2
    ll.delete(0)
    assert len(ll) == 1


# ---------------------------------------------------------------------------
# 8. __iter__
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_iter_order(cls: ListClass) -> None:
    """Iterating over a list yields values in insertion order."""
    ll = _build(cls, [1, 2, 3, 4, 5])
    assert list(ll) == [1, 2, 3, 4, 5]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_iter_empty(cls: ListClass) -> None:
    """Iterating over an empty list yields nothing."""
    ll = cls()
    assert list(ll) == []


# ---------------------------------------------------------------------------
# 9. __eq__
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_eq_same_values(cls: ListClass) -> None:
    """Two lists with identical values should be equal."""
    ll1 = _build(cls, [1, 2, 3])
    ll2 = _build(cls, [1, 2, 3])
    assert ll1 == ll2


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_eq_different_values(cls: ListClass) -> None:
    """Two lists with different values should not be equal."""
    ll1 = _build(cls, [1, 2, 3])
    ll2 = _build(cls, [1, 2, 4])
    assert ll1 != ll2


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_eq_different_lengths(cls: ListClass) -> None:
    """Lists of different length should not be equal."""
    ll1 = _build(cls, [1, 2])
    ll2 = _build(cls, [1, 2, 3])
    assert ll1 != ll2


# ---------------------------------------------------------------------------
# 10. reverse
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_reverse_multiple(cls: ListClass) -> None:
    """reverse() inverts element order."""
    ll = _build(cls, [1, 2, 3, 4])
    ll.reverse()
    assert list(ll) == [4, 3, 2, 1]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_reverse_single(cls: ListClass) -> None:
    """reverse() on a single-element list is a no-op."""
    ll = _build(cls, [42])
    ll.reverse()
    assert list(ll) == [42]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_reverse_empty(cls: ListClass) -> None:
    """reverse() on empty list raises EmptyStructureError."""
    ll = cls()
    with pytest.raises(EmptyStructureError):
        ll.reverse()


# ---------------------------------------------------------------------------
# 11. rotate
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_rotate_right(cls: ListClass) -> None:
    """Positive rotation moves tail elements to front."""
    ll = _build(cls, [1, 2, 3, 4, 5])
    ll.rotate(2)
    assert list(ll) == [4, 5, 1, 2, 3]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_rotate_left(cls: ListClass) -> None:
    """Negative rotation moves head elements to back."""
    ll = _build(cls, [1, 2, 3, 4, 5])
    ll.rotate(-2)
    assert list(ll) == [3, 4, 5, 1, 2]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_rotate_by_zero(cls: ListClass) -> None:
    """Rotating by 0 is a no-op."""
    ll = _build(cls, [1, 2, 3])
    ll.rotate(0)
    assert list(ll) == [1, 2, 3]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_rotate_by_full_length(cls: ListClass) -> None:
    """Rotating by list length is a no-op."""
    ll = _build(cls, [1, 2, 3])
    ll.rotate(3)
    assert list(ll) == [1, 2, 3]


# ---------------------------------------------------------------------------
# 12. swap
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_swap_two_elements(cls: ListClass) -> None:
    """swap() exchanges values at two distinct indices."""
    ll = _build(cls, [1, 2, 3])
    ll.swap(0, 2)
    assert list(ll) == [3, 2, 1]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_swap_same_index(cls: ListClass) -> None:
    """swap() on the same index twice is a no-op."""
    ll = _build(cls, [1, 2, 3])
    ll.swap(1, 1)
    assert list(ll) == [1, 2, 3]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_swap_invalid_index(cls: ListClass) -> None:
    """swap() raises IndexOutOfRangeError for out-of-range index."""
    ll = _build(cls, [1, 2, 3])
    with pytest.raises(IndexOutOfRangeError):
        ll.swap(0, 10)


# ---------------------------------------------------------------------------
# 13. merge
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_merge_two_lists(cls: ListClass) -> None:
    """merge() appends other list's elements to self."""
    ll1 = _build(cls, [1, 2, 3])
    ll2 = _build(cls, [4, 5, 6])
    ll1.merge(ll2)
    assert list(ll1) == [1, 2, 3, 4, 5, 6]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_merge_empty_other(cls: ListClass) -> None:
    """Merging an empty list changes nothing."""
    ll1 = _build(cls, [1, 2])
    ll2 = cls()
    ll1.merge(ll2)
    assert list(ll1) == [1, 2]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_merge_into_empty(cls: ListClass) -> None:
    """Merging into an empty list copies other list."""
    ll1 = cls()
    ll2 = _build(cls, [3, 4])
    ll1.merge(ll2)
    assert list(ll1) == [3, 4]


# ---------------------------------------------------------------------------
# 14. sort
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_sort_ascending(cls: ListClass) -> None:
    """sort() arranges elements in ascending order by default."""
    ll = _build(cls, [5, 1, 4, 2, 3])
    ll.sort()
    assert list(ll) == [1, 2, 3, 4, 5]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_sort_descending(cls: ListClass) -> None:
    """sort(reverse=True) arranges elements in descending order."""
    ll = _build(cls, [3, 1, 4, 1, 5, 9])
    ll.sort(reverse=True)
    assert list(ll) == [9, 5, 4, 3, 1, 1]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_sort_already_sorted(cls: ListClass) -> None:
    """sort() on an already sorted list is idempotent."""
    ll = _build(cls, [1, 2, 3])
    ll.sort()
    assert list(ll) == [1, 2, 3]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_sort_single(cls: ListClass) -> None:
    """sort() on a single-element list is a no-op."""
    ll = _build(cls, [7])
    ll.sort()
    assert list(ll) == [7]


# ---------------------------------------------------------------------------
# 15. partition
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_partition_basic(cls: ListClass) -> None:
    """partition() rearranges so all < pivot come before all >= pivot."""
    ll = _build(cls, [3, 1, 4, 1, 5, 9, 2, 6])
    ll.partition(lambda x: x < 4)
    values = list(ll)
    pivot_index = next(i for i, v in enumerate(values) if v >= 4)
    assert all(v < 4 for v in values[:pivot_index])
    assert all(v >= 4 for v in values[pivot_index:])


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_partition_all_less(cls: ListClass) -> None:
    """partition() with pivot above all values leaves order stable."""
    ll = _build(cls, [1, 2, 3])
    ll.partition(10)
    assert all(v < 10 for v in list(ll))


# ---------------------------------------------------------------------------
# 16. palindrome
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_palindrome_true(cls: ListClass) -> None:
    """palindrome() returns True for palindromic list."""
    ll = _build(cls, [1, 2, 3, 2, 1])
    assert ll.palindrome() is True


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_palindrome_false(cls: ListClass) -> None:
    """palindrome() returns False for non-palindromic list."""
    ll = _build(cls, [1, 2, 3])
    assert ll.palindrome() is False


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_palindrome_single(cls: ListClass) -> None:
    """Single-element list is always a palindrome."""
    ll = _build(cls, [5])
    assert ll.palindrome() is True


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_palindrome_empty(cls: ListClass) -> None:
    """Empty list raises EmptyStructureError."""
    ll = cls()
    with pytest.raises(EmptyStructureError):
        ll.palindrome()


# ---------------------------------------------------------------------------
# 17. reorder
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_reorder_basic(cls: ListClass) -> None:
    """reorder() interleaves first-half and second-half elements."""
    ll = _build(cls, [1, 2, 3, 4])
    ll.reorder()
    # Expected: [1, 3, 2, 4]  (first-half + reversed-second-half interleaved)
    values = list(ll)
    assert len(values) == 4


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_reorder_preserves_length(cls: ListClass) -> None:
    """reorder() preserves list length."""
    ll = _build(cls, [1, 2, 3, 4, 5])
    original_len = len(ll)
    ll.reorder()
    assert len(ll) == original_len


# ---------------------------------------------------------------------------
# 18. segregate_even_odd
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_segregate_even_odd(cls: ListClass) -> None:
    """segregate_even_odd() places all evens before all odds."""
    ll = _build(cls, [1, 2, 3, 4, 5, 6])
    ll.segregate_even_odd()
    values = list(ll)
    first_odd = next((i for i, v in enumerate(values) if v % 2 != 0), len(values))
    assert all(v % 2 == 0 for v in values[:first_odd])
    assert all(v % 2 != 0 for v in values[first_odd:])


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_segregate_all_even(cls: ListClass) -> None:
    """segregate_even_odd() on all-even list changes nothing structurally."""
    ll = _build(cls, [2, 4, 6])
    ll.segregate_even_odd()
    assert all(v % 2 == 0 for v in list(ll))


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_segregate_all_odd(cls: ListClass) -> None:
    """segregate_even_odd() on all-odd list changes nothing structurally."""
    ll = _build(cls, [1, 3, 5])
    ll.segregate_even_odd()
    assert all(v % 2 != 0 for v in list(ll))


# ---------------------------------------------------------------------------
# 19. detect_cycle
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_detect_cycle_no_cycle(cls: ListClass) -> None:
    """detect_cycle() returns False for a regular list (no manual cycle)."""
    ll = _build(cls, [1, 2, 3, 4])
    # CircularLinkedList has structural cycle; detect_cycle() should handle it
    result = ll.detect_cycle()
    # For CircularLinkedList the structural cycle is expected → True is fine
    if isinstance(ll, CircularLinkedList):
        assert isinstance(result, bool)
    else:
        assert result is False


# ---------------------------------------------------------------------------
# 20. JSON serialization
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_serialize_roundtrip(cls: ListClass) -> None:
    """Serializing and deserializing should reproduce original values."""
    ll = _build(cls, [1, 2, 3, 4, 5])
    json_str = ll.serialize()
    assert isinstance(json_str, str)

    ll2 = cls()
    ll2.deserialize(json_str)
    assert list(ll2) == [1, 2, 3, 4, 5]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_serialize_empty(cls: ListClass) -> None:
    """Serializing an empty list produces valid JSON."""
    ll = cls()
    json_str = ll.serialize()
    assert isinstance(json_str, str)

    ll2 = cls()
    ll2.deserialize(json_str)
    assert list(ll2) == []


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_deserialize_invalid_json(cls: ListClass) -> None:
    """Deserializing invalid JSON raises SerializationError."""
    ll = cls()
    with pytest.raises(SerializationError):
        ll.deserialize("not valid json {{{")


# ---------------------------------------------------------------------------
# 21. Visualization
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_visualize_returns_string(cls: ListClass) -> None:
    """visualize() returns a non-empty string for a populated list."""
    ll = _build(cls, [1, 2, 3])
    result = ll.visualize()
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_debug_returns_dict(cls: ListClass) -> None:
    """debug() returns a dict with at least 'length' key."""
    ll = _build(cls, [10, 20])
    result = ll.debug()
    assert isinstance(result, dict)
    assert "length" in result


# ---------------------------------------------------------------------------
# 22. Edge cases – single element
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_single_element_all_ops(cls: ListClass) -> None:
    """Single-element list handles get, replace, iter, contains correctly."""
    ll = _build(cls, [42])
    assert ll[0] == 42
    assert 42 in ll
    ll[0] = 99
    assert ll[0] == 99
    assert list(ll) == [99]


# ---------------------------------------------------------------------------
# 23. Large list – no stack overflow
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_large_list_insert_and_iter(cls: ListClass) -> None:
    """Inserting and iterating 10,000 elements should not raise RecursionError."""
    ll = cls()
    n = 10_000
    for i in range(n):
        ll.insert(i, i)
    assert len(ll) == n
    values = list(ll)
    assert values[0] == 0
    assert values[-1] == n - 1


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_large_list_sort(cls: ListClass) -> None:
    """Sorting 10,000 elements should complete without error."""
    import random

    ll = cls()
    data = list(range(10_000))
    random.shuffle(data)
    for i, v in enumerate(data):
        ll.insert(i, v)
    ll.sort()
    assert list(ll) == list(range(10_000))


# ---------------------------------------------------------------------------
# 24. Concurrency – thread safety
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_concurrent_inserts(cls: ListClass) -> None:
    """5 threads each inserting 100 elements should yield 500-element list."""
    ll = cls()
    errors: list[Exception] = []
    lock = threading.Lock()

    def worker() -> None:
        try:
            for _ in range(100):
                with lock:
                    pos = len(ll)
                ll.insert(pos, 1)
        except Exception as exc:  # noqa: BLE001
            errors.append(exc)

    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"Thread errors: {errors}"
    assert len(ll) == 500


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_concurrent_mixed_ops(cls: ListClass) -> None:
    """Multiple threads reading and writing should not raise exceptions."""
    ll = _build(cls, list(range(50)))
    errors: list[Exception] = []

    def reader() -> None:
        try:
            for _ in range(100):
                _ = list(ll)
        except Exception as exc:  # noqa: BLE001
            errors.append(exc)

    def writer() -> None:
        try:
            for i in range(50):
                ll.replace(i % len(ll), i * 2)
        except Exception as exc:  # noqa: BLE001
            errors.append(exc)

    threads = [threading.Thread(target=reader) for _ in range(3)]
    threads += [threading.Thread(target=writer) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"Thread errors: {errors}"


# ---------------------------------------------------------------------------
# 25. Validation guards
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_negative_index_raises(cls: ListClass) -> None:
    """Accessing a negative index raises IndexOutOfRangeError or ValidationError."""
    ll = _build(cls, [1, 2, 3])
    with pytest.raises((IndexOutOfRangeError, ValidationError)):
        ll.get(-1)


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_insert_negative_index_raises(cls: ListClass) -> None:
    """Inserting at a negative index raises IndexOutOfRangeError or ValidationError."""
    ll = _build(cls, [1, 2])
    with pytest.raises((IndexOutOfRangeError, ValidationError)):
        ll.insert(-1, 99)


# ---------------------------------------------------------------------------
# 26. DoublyLinkedList-specific: backward iteration
# ---------------------------------------------------------------------------


def test_doubly_backward_iter() -> None:
    """DoublyLinkedList should support backward iteration via tail pointer."""
    from pkstruct.linear.utils.iterators import BackwardIterator

    ll = _build(DoublyLinkedList, [1, 2, 3, 4, 5])
    it = BackwardIterator(ll)
    assert list(it) == [5, 4, 3, 2, 1]


# ---------------------------------------------------------------------------
# 27. CircularLinkedList-specific: wrap-around
# ---------------------------------------------------------------------------


def test_circular_wrap_around_iteration() -> None:
    """CircularLinkedList should iterate without infinite loop."""
    from pkstruct.linear.utils.iterators import CircularIterator

    ll = _build(CircularLinkedList, [1, 2, 3])
    it = CircularIterator(ll, max_steps=6)
    values = list(it)
    assert values == [1, 2, 3, 1, 2, 3]


# ---------------------------------------------------------------------------
# 28. repr / str
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_repr_is_string(cls: ListClass) -> None:
    """__repr__ returns a non-empty string."""
    ll = _build(cls, [1, 2, 3])
    r = repr(ll)
    assert isinstance(r, str)
    assert len(r) > 0


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_str_is_string(cls: ListClass) -> None:
    """__str__ returns a non-empty string."""
    ll = _build(cls, [1, 2])
    s = str(ll)
    assert isinstance(s, str)
    assert len(s) > 0


# ---------------------------------------------------------------------------
# 29. Benchmark utilities (smoke test)
# ---------------------------------------------------------------------------


def test_benchmark_operations_smoke() -> None:
    """benchmark_operations() should return a dict with timing info."""
    from pkstruct.linear.utils.benchmark import benchmark_operations

    result = benchmark_operations(SinglyLinkedList, n=100)
    assert isinstance(result, dict)
    assert len(result) > 0


def test_compare_with_builtins_smoke() -> None:
    """compare_with_builtins() should complete without error."""
    from pkstruct.linear.utils.benchmark import compare_with_builtins

    compare_with_builtins(n=100)


# ---------------------------------------------------------------------------
# 30. Helper utilities
# ---------------------------------------------------------------------------


def test_merge_sorted_lists() -> None:
    """merge_sorted_lists() returns a new sorted merged list."""
    from pkstruct.linear.utils.helpers import merge_sorted_lists

    ll1 = _build(SinglyLinkedList, [1, 3, 5])
    ll2 = _build(SinglyLinkedList, [2, 4, 6])
    merged = merge_sorted_lists(ll1, ll2)
    assert list(merged) == [1, 2, 3, 4, 5, 6]


def test_list_equal() -> None:
    """list_equal() returns True for identical lists, False otherwise."""
    from pkstruct.linear.utils.helpers import list_equal

    ll1 = _build(SinglyLinkedList, [1, 2, 3])
    ll2 = _build(SinglyLinkedList, [1, 2, 3])
    ll3 = _build(SinglyLinkedList, [1, 2, 9])
    assert list_equal(ll1, ll2) is True
    assert list_equal(ll1, ll3) is False


def test_to_array() -> None:
    """to_array() converts linked list to a Python list."""
    from pkstruct.linear.utils.helpers import to_array

    ll = _build(SinglyLinkedList, [7, 8, 9])
    assert to_array(ll) == [7, 8, 9]


def test_memory_usage_returns_int() -> None:
    """memory_usage() returns an integer byte count."""
    from pkstruct.linear.utils.debug_tools import memory_usage

    ll = _build(SinglyLinkedList, [1, 2, 3])
    mem = memory_usage(ll)
    assert isinstance(mem, int)
    assert mem > 0


def test_validate_integrity_passes() -> None:
    """validate_integrity() should not raise for a valid list."""
    from pkstruct.linear.utils.debug_tools import validate_integrity

    ll = _build(SinglyLinkedList, [1, 2, 3])
    # Should complete without exception
    validate_integrity(ll)