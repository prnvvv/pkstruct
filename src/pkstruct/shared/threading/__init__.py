"""
pkstruct.shared.threading
~~~~~~~~~~~~~~~~~~~~~~~~~
Thread-safety primitives for pkstruct data structures.

Uses ``threading.RLock`` so a single thread can re-acquire the lock without
deadlock (important for recursive operations like merge-sort).
"""
from __future__ import annotations

import threading
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any


class StructureLock:
    """A thin wrapper around :class:`threading.RLock` with context-manager support.

    Attach one instance to each data structure. All mutating operations should
    acquire this lock. Read-only operations that must be atomic (e.g., ``size()``,
    ``to_list()``) should also acquire it.

    Zero overhead for single-threaded usage due to Python's fast-path for
    uncontested RLocks.
    """

    __slots__ = ("_lock",)

    def __init__(self) -> None:
        self._lock: threading.RLock = threading.RLock()

    @contextmanager
    def acquire(self) -> Generator[None, Any, None]:
        """Context manager that acquires and releases the lock."""
        self._lock.acquire()
        try:
            yield
        finally:
            self._lock.release()

    def __enter__(self) -> "StructureLock":
        self._lock.acquire()
        return self

    def __exit__(self, *_: object) -> None:
        self._lock.release()
    def acquire(self) -> None:
        """Acquire the lock."""
        self._lock.acquire()

    def release(self) -> None:
        """Release the lock."""
        self._lock.release()