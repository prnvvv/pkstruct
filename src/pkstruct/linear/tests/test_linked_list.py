from __future__ import annotations

import threading
from typing import TYPE_CHECKING

import pytest

from pkstruct.linear import (
    CircularLinkedList,
    DoublyLinkedList,
    SinglyLinkedList,
)
from pkstruct.linear.exceptions import (
    EmptyStructureError,
    IndexOutOfRangeError,
    SerializationError,
    ValidationError,
    ValueNotFoundError,
)

if TYPE_CHECKING:
    ListClass = type[SinglyLinkedList] | type[DoublyLinkedList] | type[CircularLinkedList]
else:
    ListClass = type[SinglyLinkedList] | type[DoublyLinkedList] | type[CircularLinkedList]

ALL_LIST_CLASSES = [SinglyLinkedList, DoublyLinkedList, CircularLinkedList]


def _build(cls: ListClass, values: list) -> SinglyLinkedList | DoublyLinkedList | CircularLinkedList:
    ll = cls()
    for v in values:
        ll.insert(v)
    return ll


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_create_empty(cls: ListClass) -> None:
    ll = cls()
    assert len(ll) == 0
    assert list(ll) == []


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_empty_list_bool(cls: ListClass) -> None:
    ll = cls()
    assert not ll
    ll.insert(1, position=0)
    assert ll


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_insert_at_head(cls: ListClass) -> None:
    ll = cls()
    ll.insert(10, position=0)
    ll.insert(20, position=0)
    ll.insert(30, position=0)
    assert list(ll) == [30, 20, 10]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_insert_at_tail(cls: ListClass) -> None:
    ll = _build(cls, [1, 2, 3])
    ll.insert(4)
    assert list(ll) == [1, 2, 3, 4]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_insert_in_middle(cls: ListClass) -> None:
    ll = _build(cls, [1, 3])
    ll.insert(2, position=1)
    assert list(ll) == [1, 2, 3]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_insert_out_of_range(cls: ListClass) -> None:
    ll = _build(cls, [1, 2])
    with pytest.raises(IndexOutOfRangeError):
        ll.insert(99, position=10)


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_delete_head(cls: ListClass) -> None:
    ll = _build(cls, [1, 2, 3])
    ll.delete(position=0)
    assert list(ll) == [2, 3]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_delete_tail(cls: ListClass) -> None:
    ll = _build(cls, [1, 2, 3])
    ll.delete(position=2)
    assert list(ll) == [1, 2]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_delete_middle(cls: ListClass) -> None:
    ll = _build(cls, [1, 2, 3])
    ll.delete(position=1)
    assert list(ll) == [1, 3]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_delete_only_element(cls: ListClass) -> None:
    ll = _build(cls, [42])
    ll.delete(position=0)
    assert len(ll) == 0
    assert list(ll) == []


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_delete_out_of_range(cls: ListClass) -> None:
    ll = _build(cls, [1, 2, 3])
    with pytest.raises(IndexOutOfRangeError):
        ll.delete(position=5)


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_delete_from_empty(cls: ListClass) -> None:
    ll = cls()
    with pytest.raises(EmptyStructureError):
        ll.delete(position=0)


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_get_valid_index(cls: ListClass) -> None:
    ll = _build(cls, [10, 20, 30])
    assert ll.get(0) == 10
    assert ll.get(1) == 20
    assert ll.get(2) == 30


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_getitem_valid(cls: ListClass) -> None:
    ll = _build(cls, [10, 20, 30])
    assert ll[0] == 10
    assert ll[2] == 30


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_get_invalid_index(cls: ListClass) -> None:
    ll = _build(cls, [1, 2])
    with pytest.raises(IndexOutOfRangeError):
        ll.get(5)


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_get_from_empty(cls: ListClass) -> None:
    ll = cls()
    with pytest.raises(EmptyStructureError):
        ll.get(0)


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_index_found(cls: ListClass) -> None:
    ll = _build(cls, [10, 20, 30])
    assert ll.index(20) == 1


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_index_not_found(cls: ListClass) -> None:
    ll = _build(cls, [1, 2, 3])
    with pytest.raises(ValueNotFoundError):
        ll.index(99)


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_contains(cls: ListClass) -> None:
    ll = _build(cls, [5, 10, 15])
    assert 10 in ll
    assert 99 not in ll


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_replace_valid(cls: ListClass) -> None:
    ll = _build(cls, [1, 2, 3])
    ll.replace(new_value=99, position=1)
    assert ll[1] == 99


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_setitem_valid(cls: ListClass) -> None:
    ll = _build(cls, [1, 2, 3])
    ll[2] = 77
    assert ll[2] == 77


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_replace_invalid_index(cls: ListClass) -> None:
    ll = _build(cls, [1, 2])
    with pytest.raises(IndexOutOfRangeError):
        ll.replace(new_value=5, position=10)


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_len_tracks_inserts_and_deletes(cls: ListClass) -> None:
    ll = cls()
    assert len(ll) == 0
    ll.insert(1, position=0)
    assert len(ll) == 1
    ll.insert(2, position=1)
    assert len(ll) == 2
    ll.delete(position=0)
    assert len(ll) == 1


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_iter_order(cls: ListClass) -> None:
    ll = _build(cls, [1, 2, 3, 4, 5])
    assert list(ll) == [1, 2, 3, 4, 5]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_iter_empty(cls: ListClass) -> None:
    ll = cls()
    assert list(ll) == []


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_eq_same_values(cls: ListClass) -> None:
    ll1 = _build(cls, [1, 2, 3])
    ll2 = _build(cls, [1, 2, 3])
    assert ll1 == ll2


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_eq_different_values(cls: ListClass) -> None:
    ll1 = _build(cls, [1, 2, 3])
    ll2 = _build(cls, [1, 2, 4])
    assert ll1 != ll2


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_eq_different_lengths(cls: ListClass) -> None:
    ll1 = _build(cls, [1, 2])
    ll2 = _build(cls, [1, 2, 3])
    assert ll1 != ll2


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_reverse_multiple(cls: ListClass) -> None:
    ll = _build(cls, [1, 2, 3, 4])
    ll.reverse()
    assert list(ll) == [4, 3, 2, 1]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_reverse_single(cls: ListClass) -> None:
    ll = _build(cls, [42])
    ll.reverse()
    assert list(ll) == [42]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_reverse_empty(cls: ListClass) -> None:
    ll = cls()
    with pytest.raises(EmptyStructureError):
        ll.reverse()


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_rotate_right(cls: ListClass) -> None:
    ll = _build(cls, [1, 2, 3, 4, 5])
    ll.rotate(2)
    assert list(ll) == [4, 5, 1, 2, 3]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_rotate_left(cls: ListClass) -> None:
    ll = _build(cls, [1, 2, 3, 4, 5])
    ll.rotate(-2)
    assert list(ll) == [3, 4, 5, 1, 2]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_rotate_by_zero(cls: ListClass) -> None:
    ll = _build(cls, [1, 2, 3])
    ll.rotate(0)
    assert list(ll) == [1, 2, 3]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_rotate_by_full_length(cls: ListClass) -> None:
    ll = _build(cls, [1, 2, 3])
    ll.rotate(3)
    assert list(ll) == [1, 2, 3]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_swap_two_elements(cls: ListClass) -> None:
    ll = _build(cls, [1, 2, 3])
    ll.swap(pos1=0, pos2=2)
    assert list(ll) == [3, 2, 1]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_swap_same_index(cls: ListClass) -> None:
    ll = _build(cls, [1, 2, 3])
    ll.swap(pos1=1, pos2=1)
    assert list(ll) == [1, 2, 3]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_swap_invalid_index(cls: ListClass) -> None:
    ll = _build(cls, [1, 2, 3])
    with pytest.raises(IndexOutOfRangeError):
        ll.swap(pos1=0, pos2=10)


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_merge_two_lists(cls: ListClass) -> None:
    ll1 = _build(cls, [1, 2, 3])
    ll2 = _build(cls, [4, 5, 6])
    ll1.merge(ll2)
    assert list(ll1) == [1, 2, 3, 4, 5, 6]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_merge_empty_other(cls: ListClass) -> None:
    ll1 = _build(cls, [1, 2])
    ll2 = cls()
    ll1.merge(ll2)
    assert list(ll1) == [1, 2]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_merge_into_empty(cls: ListClass) -> None:
    ll1 = cls()
    ll2 = _build(cls, [3, 4])
    ll1.merge(ll2)
    assert list(ll1) == [3, 4]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_sort_ascending(cls: ListClass) -> None:
    ll = _build(cls, [5, 1, 4, 2, 3])
    ll.sort()
    assert list(ll) == [1, 2, 3, 4, 5]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_sort_descending(cls: ListClass) -> None:
    ll = _build(cls, [3, 1, 4, 1, 5, 9])
    ll.sort(reverse=True)
    assert list(ll) == [9, 5, 4, 3, 1, 1]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_sort_already_sorted(cls: ListClass) -> None:
    ll = _build(cls, [1, 2, 3])
    ll.sort()
    assert list(ll) == [1, 2, 3]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_sort_single(cls: ListClass) -> None:
    ll = _build(cls, [7])
    ll.sort()
    assert list(ll) == [7]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_partition_basic(cls: ListClass) -> None:
    ll = _build(cls, [3, 1, 4, 1, 5, 9, 2, 6])
    ll.partition(lambda x: x < 4)
    values = list(ll)
    pivot_index = next(i for i, v in enumerate(values) if v >= 4)
    assert all(v < 4 for v in values[:pivot_index])
    assert all(v >= 4 for v in values[pivot_index:])


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_partition_all_less(cls: ListClass) -> None:
    ll = _build(cls, [1, 2, 3])
    ll.partition(10)
    assert all(v < 10 for v in list(ll))


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_palindrome_true(cls: ListClass) -> None:
    ll = _build(cls, [1, 2, 3, 2, 1])
    assert ll.palindrome() is True


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_palindrome_false(cls: ListClass) -> None:
    ll = _build(cls, [1, 2, 3])
    assert ll.palindrome() is False


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_palindrome_single(cls: ListClass) -> None:
    ll = _build(cls, [5])
    assert ll.palindrome() is True


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_palindrome_empty(cls: ListClass) -> None:
    ll = cls()
    with pytest.raises(EmptyStructureError):
        ll.palindrome()


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_reorder_basic(cls: ListClass) -> None:
    ll = _build(cls, [1, 2, 3, 4])
    ll.reorder()
    values = list(ll)
    assert len(values) == 4


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_reorder_preserves_length(cls: ListClass) -> None:
    ll = _build(cls, [1, 2, 3, 4, 5])
    original_len = len(ll)
    ll.reorder()
    assert len(ll) == original_len


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_segregate_even_odd(cls: ListClass) -> None:
    ll = _build(cls, [1, 2, 3, 4, 5, 6])
    ll.segregate_even_odd()
    values = list(ll)
    first_odd = next((i for i, v in enumerate(values) if v % 2 != 0), len(values))
    assert all(v % 2 == 0 for v in values[:first_odd])
    assert all(v % 2 != 0 for v in values[first_odd:])


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_segregate_all_even(cls: ListClass) -> None:
    ll = _build(cls, [2, 4, 6])
    ll.segregate_even_odd()
    assert all(v % 2 == 0 for v in list(ll))


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_segregate_all_odd(cls: ListClass) -> None:
    ll = _build(cls, [1, 3, 5])
    ll.segregate_even_odd()
    assert all(v % 2 != 0 for v in list(ll))


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_detect_cycle_no_cycle(cls: ListClass) -> None:
    ll = _build(cls, [1, 2, 3, 4])
    result = ll.detect_cycle()
    if isinstance(ll, CircularLinkedList):
        assert isinstance(result, bool)
    else:
        assert result is False


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_serialize_roundtrip(cls: ListClass) -> None:
    ll = _build(cls, [1, 2, 3, 4, 5])
    json_str = ll.to_json()
    assert isinstance(json_str, str)
    ll2 = cls.from_json(json_str)
    assert list(ll2) == [1, 2, 3, 4, 5]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_serialize_empty(cls: ListClass) -> None:
    ll = cls()
    json_str = ll.to_json()
    assert isinstance(json_str, str)
    ll2 = cls.from_json(json_str)
    assert list(ll2) == []


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_deserialize_invalid_json(cls: ListClass) -> None:
    ll = cls()
    with pytest.raises(SerializationError):
        ll.from_json("not valid json {{{")


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_visualize_returns_string(cls: ListClass) -> None:
    ll = _build(cls, [1, 2, 3])
    result = ll.visualize()
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_debug_returns_dict(cls: ListClass) -> None:
    ll = _build(cls, [10, 20])
    result = ll.debug()
    assert isinstance(result, dict)
    assert "length" in result


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_single_element_all_ops(cls: ListClass) -> None:
    ll = _build(cls, [42])
    assert ll[0] == 42
    assert 42 in ll
    ll[0] = 99
    assert ll[0] == 99
    assert list(ll) == [99]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_large_list_insert_and_iter(cls: ListClass) -> None:
    ll = cls()
    n = 10_000
    for i in range(n):
        ll.insert(i, position=i)
    assert len(ll) == n
    values = list(ll)
    assert values[0] == 0
    assert values[-1] == n - 1


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_large_list_sort(cls: ListClass) -> None:
    import random
    ll = cls()
    data = list(range(10_000))
    random.shuffle(data)
    for i, v in enumerate(data):
        ll.insert(v, position=i)
    ll.sort()
    assert list(ll) == list(range(10_000))


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_concurrent_inserts(cls: ListClass) -> None:
    ll = cls()
    errors: list[Exception] = []
    lock = threading.Lock()

    def worker() -> None:
        try:
            for _ in range(100):
                with lock:
                    pos = len(ll)
                ll.insert(1, position=pos)
        except Exception as exc:
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
    ll = _build(cls, list(range(50)))
    errors: list[Exception] = []

    def reader() -> None:
        try:
            for _ in range(100):
                _ = list(ll)
        except Exception as exc:
            errors.append(exc)

    def writer() -> None:
        try:
            for i in range(50):
                ll.replace(new_value=i * 2, position=i % len(ll))
        except Exception as exc:
            errors.append(exc)

    threads = [threading.Thread(target=reader) for _ in range(3)]
    threads += [threading.Thread(target=writer) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"Thread errors: {errors}"


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_negative_index_raises(cls: ListClass) -> None:
    ll = _build(cls, [1, 2, 3])
    with pytest.raises((IndexOutOfRangeError, ValidationError)):
        ll.get(-1)


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_insert_negative_index_raises(cls: ListClass) -> None:
    ll = _build(cls, [1, 2])
    with pytest.raises((IndexOutOfRangeError, ValidationError)):
        ll.insert(99, position=-1)


def test_doubly_backward_iter() -> None:
    from pkstruct.linear.utils.iterators import BackwardIterator
    ll = _build(DoublyLinkedList, [1, 2, 3, 4, 5])
    it = BackwardIterator(ll)
    assert list(it) == [5, 4, 3, 2, 1]


def test_circular_wrap_around_iteration() -> None:
    from pkstruct.linear.utils.iterators import CircularIterator
    ll = _build(CircularLinkedList, [1, 2, 3])
    it = CircularIterator(ll, max_steps=6)
    values = list(it)
    assert values == [1, 2, 3, 1, 2, 3]


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_repr_is_string(cls: ListClass) -> None:
    ll = _build(cls, [1, 2, 3])
    r = repr(ll)
    assert isinstance(r, str)
    assert len(r) > 0


@pytest.mark.parametrize("cls", ALL_LIST_CLASSES)
def test_str_is_string(cls: ListClass) -> None:
    ll = _build(cls, [1, 2])
    s = str(ll)
    assert isinstance(s, str)
    assert len(s) > 0


def test_benchmark_operations_smoke() -> None:
    from pkstruct.linear.utils.benchmark import benchmark_operations
    result = benchmark_operations(SinglyLinkedList, n=100)
    assert isinstance(result, dict)
    assert len(result) > 0


def test_compare_with_builtins_smoke() -> None:
    from pkstruct.linear.utils.benchmark import compare_with_builtins
    compare_with_builtins(n=100)


def test_merge_sorted_lists() -> None:
    from pkstruct.linear.utils.helpers import merge_sorted_lists
    ll1 = _build(SinglyLinkedList, [1, 3, 5])
    ll2 = _build(SinglyLinkedList, [2, 4, 6])
    merged = merge_sorted_lists(ll1, ll2)
    assert list(merged) == [1, 2, 3, 4, 5, 6]


def test_list_equal() -> None:
    from pkstruct.linear.utils.helpers import list_equal
    ll1 = _build(SinglyLinkedList, [1, 2, 3])
    ll2 = _build(SinglyLinkedList, [1, 2, 3])
    ll3 = _build(SinglyLinkedList, [1, 2, 9])
    assert list_equal(ll1, ll2) is True
    assert list_equal(ll1, ll3) is False


def test_to_array() -> None:
    from pkstruct.linear.utils.helpers import to_array
    ll = _build(SinglyLinkedList, [7, 8, 9])
    assert to_array(ll) == [7, 8, 9]


def test_memory_usage_returns_int() -> None:
    from pkstruct.linear.utils.debug_tools import memory_usage
    ll = _build(SinglyLinkedList, [1, 2, 3])
    mem = memory_usage(ll)
    assert isinstance(mem, int)
    assert mem > 0


def test_validate_integrity_passes() -> None:
    from pkstruct.linear.utils.debug_tools import validate_integrity
    ll = _build(SinglyLinkedList, [1, 2, 3])
    validate_integrity(ll)
