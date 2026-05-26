"""Edge case, stress, and concurrency tests for linked lists."""
from __future__ import annotations

import pytest
import threading
from pkstruct.linear import (
    SinglyLinkedList,
    DoublyLinkedList,
    CircularLinkedList,
)
from pkstruct.linear.exceptions import (
    EmptyStructureError,
    IndexOutOfRangeError,
    ValueNotFoundError,
    InvalidRangeError,
)

LIST_CLASSES = [SinglyLinkedList, DoublyLinkedList, CircularLinkedList]


@pytest.mark.parametrize("ListClass", LIST_CLASSES)
class TestEdgeCases:
    def test_empty_list_delete_raises(self, ListClass):
        lst = ListClass()
        with pytest.raises(EmptyStructureError):
            lst.delete(position=0)

    def test_empty_list_get_raises(self, ListClass):
        lst = ListClass()
        with pytest.raises(EmptyStructureError):
            lst.get(0)

    def test_empty_list_reverse_raises(self, ListClass):
        lst = ListClass()
        with pytest.raises(EmptyStructureError):
            lst.reverse()

    def test_empty_list_rotate_raises(self, ListClass):
        lst = ListClass()
        with pytest.raises(EmptyStructureError):
            lst.rotate(0, 0, True, 1)

    def test_single_element_operations(self, ListClass):
        lst = ListClass.from_list([42])
        assert lst.size() == 1
        assert lst.get(0) == 42
        assert lst.index(42) == 0
        lst.delete(position=0)
        assert lst.is_empty() is True

    def test_invalid_position_raises(self, ListClass):
        lst = ListClass.from_list([1, 2, 3])
        with pytest.raises(IndexOutOfRangeError):
            lst.get(10)
        with pytest.raises(IndexOutOfRangeError):
            lst.get(-10)

    def test_invalid_range_raises(self, ListClass):
        lst = ListClass.from_list([1, 2, 3, 4, 5])
        with pytest.raises(InvalidRangeError):
            lst.delete(range=(3, 1))

    def test_value_not_found_raises(self, ListClass):
        lst = ListClass.from_list([1, 2, 3])
        with pytest.raises(ValueNotFoundError):
            lst.index(99)

    def test_large_list_performance(self, ListClass):
        """Test with 10,000 elements - no recursion depth issues."""
        lst = ListClass()
        for i in range(10000):
            lst.insert(i)
        assert lst.size() == 10000
        assert lst.get(5000) == 5000
        assert lst.index(9999) == 9999


@pytest.mark.parametrize("ListClass", LIST_CLASSES)
class TestConcurrency:
    def test_concurrent_inserts(self, ListClass):
        lst = ListClass()
        errors = []

        def insert_values(start, count):
            try:
                for i in range(start, start + count):
                    lst.insert(i)
            except Exception as e:
                errors.append(e)

        threads = []
        for t in range(5):
            thread = threading.Thread(target=insert_values, args=(t * 100, 100))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        assert len(errors) == 0
        assert lst.size() == 500

    def test_concurrent_mixed_ops(self, ListClass):
        lst = ListClass.from_list(list(range(50)))
        errors = []

        def reader():
            try:
                for _ in range(100):
                    _ = lst.to_list()
                    _ = lst.size()
                    _ = 25 in lst
            except Exception as e:
                errors.append(e)

        def writer():
            try:
                for i in range(50):
                    pos = i % max(1, lst.size())
                    lst.replace(position=pos, new_value=i * 2)
            except Exception as e:
                errors.append(e)

        threads = []
        for _ in range(3):
            threads.append(threading.Thread(target=reader))
        for _ in range(2):
            threads.append(threading.Thread(target=writer))

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0


@pytest.mark.parametrize("ListClass", LIST_CLASSES)
class TestSerialization:
    def test_json_roundtrip(self, ListClass):
        original = ListClass.from_list([1, "two", 3.0, None, True])
        json_str = original.to_json()
        restored = ListClass.from_json(json_str)
        assert restored.to_list() == original.to_list()

    def test_json_empty_list(self, ListClass):
        original = ListClass()
        json_str = original.to_json()
        restored = ListClass.from_json(json_str)
        assert restored.to_list() == []

    def test_invalid_json_raises(self, ListClass):
        with pytest.raises(Exception):
            ListClass.from_json("invalid json")


class TestDoublyLinkedListSpecific:
    def test_backward_traversal(self):
        dll = DoublyLinkedList.from_list([1, 2, 3])
        values = []
        current = dll._tail
        while current:
            values.append(current.value)
            current = current.prev
        assert values == [3, 2, 1]


class TestCircularLinkedListSpecific:
    def test_circular_wrap(self):
        cll = CircularLinkedList.from_list([1, 2, 3])
        assert cll._tail.next is cll._head
        assert cll._tail.next.value == 1


@pytest.mark.parametrize("ListClass", LIST_CLASSES)
class TestMemoryAndIntegrity:
    def test_memory_usage_returns_int(self, ListClass):
        from pkstruct.linear.utils.debug_tools import memory_usage
        lst = ListClass.from_list([1, 2, 3])
        mem = memory_usage(lst)
        assert isinstance(mem, int)
        assert mem > 0

    def test_validate_integrity_passes(self, ListClass):
        from pkstruct.linear.utils.debug_tools import validate_integrity
        lst = ListClass.from_list([1, 2, 3])
        result = validate_integrity(lst)
        assert result["valid"] is True
        assert len(result["errors"]) == 0