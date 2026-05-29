"""
pkstruct.linear.queues
======================

FIFO (first-in, first-out) queue data structures for the pkstruct ecosystem.

Provides multiple concrete queue implementations and a shared abstract base.

Classes
-------
Queue
    Abstract base class defining the queue interface.
LinkedQueue
    Queue backed by ``SinglyLinkedList`` (node-based, thread-safe).
CircularQueue
    Fixed-capacity queue backed by a ring buffer.
PriorityQueue
    Min-heap priority queue backed by ``heapq``.

Example
-------
>>> from pkstruct.linear.queues import LinkedQueue
>>> q = LinkedQueue([1, 2, 3])
>>> q.enqueue(4)
>>> q.dequeue()
1
>>> list(q)
[2, 3, 4]
"""

from pkstruct.linear.queues.circular_queue import CircularQueue, QueueFullError
from pkstruct.linear.queues.linked_queue import LinkedQueue
from pkstruct.linear.queues.priority_queue import PriorityQueue
from pkstruct.linear.queues.queue import Queue

__all__ = [
    # Queue classes
    "CircularQueue",
    "LinkedQueue",
    "PriorityQueue",
    "Queue",
    # Exceptions
    "QueueFullError",
]
