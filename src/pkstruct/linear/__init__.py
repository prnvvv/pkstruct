"""
pkstruct.linear
===============

Linear data structures module for the pkstruct ecosystem.

Provides production-grade implementations of linked lists, stacks, queues,
and deques with full thread safety, debug tracing, benchmarking, and
ASCII visualization support.

Classes
-------
SinglyLinkedList
    A singly linked list with forward traversal.
DoublyLinkedList
    A doubly linked list with both forward and backward traversal.
CircularLinkedList
    A circular linked list maintaining the circular invariant.
ArrayStack
    LIFO stack backed by a dynamic array.
LinkedStack
    LIFO stack backed by ``SinglyLinkedList``.
LinkedQueue
    FIFO queue backed by ``SinglyLinkedList``.
CircularQueue
    Fixed-capacity FIFO queue backed by a ring buffer.
PriorityQueue
    Min-heap priority queue.
LinkedDeque
    Double-ended queue backed by ``DoublyLinkedList``.

Exceptions
----------
PkstructError, ValidationError, IndexOutOfRangeError, ValueNotFoundError,
EmptyStructureError, SerializationError, ConcurrencyError, InvalidRangeError,
QueueFullError

Example
-------
>>> from pkstruct.linear import SinglyLinkedList, LinkedStack
>>> ll = SinglyLinkedList()
>>> ll.insert(10)
>>> s = LinkedStack([1, 2, 3])
>>> s.pop()
3
"""

from pkstruct.linear.deques.linked_deque import LinkedDeque
from pkstruct.linear.exceptions import (
    ConcurrencyError,
    EmptyStructureError,
    IndexOutOfRangeError,
    InvalidRangeError,
    PkstructError,
    SerializationError,
    ValidationError,
    ValueNotFoundError,
)
from pkstruct.linear.linked_lists.circular_linked_list import CircularLinkedList
from pkstruct.linear.linked_lists.doubly_linked_list import DoublyLinkedList
from pkstruct.linear.linked_lists.singly_linked_list import SinglyLinkedList
from pkstruct.linear.queues.circular_queue import CircularQueue, QueueFullError
from pkstruct.linear.queues.linked_queue import LinkedQueue
from pkstruct.linear.queues.priority_queue import PriorityQueue
from pkstruct.linear.stacks.array_stack import ArrayStack
from pkstruct.linear.stacks.linked_stack import LinkedStack

__all__ = [
    # Linked list classes
    "SinglyLinkedList",
    "DoublyLinkedList",
    "CircularLinkedList",
    # Stack classes
    "ArrayStack",
    "LinkedStack",
    # Queue classes
    "LinkedQueue",
    "CircularQueue",
    "PriorityQueue",
    # Deque classes
    "LinkedDeque",
    # Exceptions
    "PkstructError",
    "ValidationError",
    "IndexOutOfRangeError",
    "ValueNotFoundError",
    "EmptyStructureError",
    "SerializationError",
    "ConcurrencyError",
    "InvalidRangeError",
    "QueueFullError",
]

__version__ = "0.1.1"
__author__ = "pkstruct contributors"