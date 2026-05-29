"""
pkstruct.linear.deques
======================

Double-ended queue (deque) data structures for the pkstruct ecosystem.

Provides a concrete doubly-linked-list-backed deque and a shared abstract base.

Classes
-------
Deque
    Abstract base class defining the deque interface.
LinkedDeque
    Deque backed by ``DoublyLinkedList`` (O(1) at both ends, thread-safe).

Example
-------
>>> from pkstruct.linear.deques import LinkedDeque
>>> d = LinkedDeque([1, 2, 3])
>>> d.append(0, side="left")
>>> d.append(4, side="right")
>>> list(d)
[0, 1, 2, 3, 4]
"""

from pkstruct.linear.deques.deque import Deque
from pkstruct.linear.deques.linked_deque import LinkedDeque

__all__ = [
    # Deque classes
    "Deque",
    "LinkedDeque",
]
