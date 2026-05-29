"""Tests for ASCII visualization of linked lists."""
from __future__ import annotations

import pytest

from pkstruct.linear import (
    CircularLinkedList,
    DoublyLinkedList,
    SinglyLinkedList,
)

LIST_CLASSES = [SinglyLinkedList, DoublyLinkedList, CircularLinkedList]


@pytest.mark.parametrize("ListClass", LIST_CLASSES)
class TestVisualization:
    def test_visualize_returns_string(self, ListClass):
        lst = ListClass.from_list([10, 20, 30])
        output = lst.visualize()
        assert isinstance(output, str)
        assert len(output) > 0

    def test_visualize_contains_values(self, ListClass):
        lst = ListClass.from_list([10, 20, 30])
        output = lst.visualize()
        assert "10" in output
        assert "20" in output
        assert "30" in output

    def test_empty_list_visualize(self, ListClass):
        lst = ListClass()
        output = lst.visualize()
        assert isinstance(output, str)
        assert "empty" in output.lower() or "null" in output.lower()

    def test_single_element_visualize(self, ListClass):
        lst = ListClass.from_list([42])
        output = lst.visualize()
        assert "42" in output
        assert len(output) > 0


class TestSinglyVisualization:
    def test_singly_format(self):
        sll = SinglyLinkedList.from_list([10, 20, 30])
        output = sll.visualize()
        # Should have arrow separators
        assert "->" in output or "→" in output
        assert "None" in output or "NULL" in output


class TestDoublyVisualization:
    def test_doubly_format(self):
        dll = DoublyLinkedList.from_list([10, 20, 30])
        output = dll.visualize()
        # Should show bidirectional representation
        assert "<->" in output or "→" in output
        assert "None" in output or "NULL" in output


class TestCircularVisualization:
    def test_circular_format(self):
        cll = CircularLinkedList.from_list([10, 20, 30])
        output = cll.visualize()
        # Should indicate circular nature
        assert "back to head" in output.lower() or "circular" in output.lower()


@pytest.mark.parametrize("ListClass", LIST_CLASSES)
class TestDebugOutput:
    def test_debug_returns_dict(self, ListClass):
        lst = ListClass.from_list([10, 20, 30])
        debug = lst.debug()
        assert isinstance(debug, dict)

    def test_debug_contains_keys(self, ListClass):
        lst = ListClass.from_list([10, 20, 30])
        debug = lst.debug()
        expected_keys = ["type", "size"]
        for key in expected_keys:
            assert key in debug

    def test_debug_size_matches(self, ListClass):
        lst = ListClass.from_list([10, 20, 30])
        debug = lst.debug()
        assert debug["size"] == 3

    def test_debug_values_list(self, ListClass):
        lst = ListClass.from_list([10, 20, 30])
        debug = lst.debug()
        if "values" in debug:
            assert debug["values"] == [10, 20, 30]