"""
pkstruct.linear
===============

Linear data structures module for the pkstruct ecosystem.

Provides production-grade implementations of singly, doubly, and circular
linked lists with full thread safety, debug tracing, benchmarking, and
ASCII visualization support.

Classes
-------
SinglyLinkedList
    A singly linked list with forward traversal.
DoublyLinkedList
    A doubly linked list with both forward and backward traversal.
CircularLinkedList
    A circular linked list maintaining the circular invariant.

Exceptions
----------
PkstructError, ValidationError, IndexOutOfRangeError, ValueNotFoundError,
EmptyStructureError, SerializationError, ConcurrencyError, InvalidRangeError

Example
-------
>>> from pkstruct.linear import SinglyLinkedList
>>> ll = SinglyLinkedList()
>>> ll.insert(0, 10)
>>> ll.insert(1, 20)
>>> len(ll)
2
"""

from pkstruct.linear.linked_lists.singly_linked_list import SinglyLinkedList
from pkstruct.linear.linked_lists.doubly_linked_list import DoublyLinkedList
from pkstruct.linear.linked_lists.circular_linked_list import CircularLinkedList

from pkstruct.linear.exceptions import (
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
    # Linked list classes
    "SinglyLinkedList",
    "DoublyLinkedList",
    "CircularLinkedList",
    # Exceptions
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