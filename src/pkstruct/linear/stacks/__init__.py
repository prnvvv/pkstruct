"""
pkstruct.linear.stacks
======================

LIFO (last-in, first-out) stack data structures for the pkstruct ecosystem.

Provides two concrete stack implementations and a shared abstract base.

Classes
-------
Stack
    Abstract base class defining the stack interface.
LinkedStack
    Stack backed by ``SinglyLinkedList`` (node-based, thread-safe).
ArrayStack
    Stack backed by a Python ``list`` (compact, cache-local).

Example
-------
>>> from pkstruct.linear.stacks import LinkedStack
>>> s = LinkedStack([1, 2, 3])
>>> s.push(4)
>>> s.pop()
4
>>> list(s)
[3, 2, 1]
"""

from pkstruct.linear.stacks.array_stack import ArrayStack
from pkstruct.linear.stacks.linked_stack import LinkedStack
from pkstruct.linear.stacks.stack import Stack

__all__ = [
    # Stack classes
    "ArrayStack",
    "LinkedStack",
    "Stack",
]
