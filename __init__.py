"""
pkstruct - Production-grade modular data structures toolkit for Python.

This package provides industrial-strength implementations of fundamental
data structures with thread safety, serialization, visualization, and
comprehensive algorithmic helpers.

Modules
-------
linear
    SinglyLinkedList, DoublyLinkedList, CircularLinkedList
shared
    Infrastructure components (exceptions, validators, serializers, etc.)

Example
-------
>>> from pkstruct import SinglyLinkedList
>>> ll = SinglyLinkedList.from_list([1, 2, 3])
>>> ll.insert(4)
>>> ll.reverse()
>>> list(ll)
[4, 3, 2, 1]
"""

from pkstruct.linear import (
    SinglyLinkedList,
    DoublyLinkedList,
    CircularLinkedList,
    PkstructError,
    ValidationError,
    IndexOutOfRangeError,
    ValueNotFoundError,
    EmptyStructureError,
    SerializationError,
    ConcurrencyError,
    InvalidRangeError,
)

__all__ = [
    "SinglyLinkedList",
    "DoublyLinkedList",
    "CircularLinkedList",
    "PkstructError",
    "ValidationError",
    "IndexOutOfRangeError",
    "ValueNotFoundError",
    "EmptyStructureError",
    "SerializationError",
    "ConcurrencyError",
    "InvalidRangeError",
]

__version__ = "0.1.0"
__author__ = "pkstruct contributors"