"""
pkstruct.shared.debugging
~~~~~~~~~~~~~~~~~~~~~~~~~
Step-tracing and introspection helpers for pkstruct structures.
"""
from __future__ import annotations

import time
from typing import Any


class DebugTracer:
    """Lightweight operation tracer for debugging data structure mutations.

    Keeps a bounded in-memory trace log (FIFO).  Disabled by default to avoid
    any overhead in production paths.

    Example::

        tracer = DebugTracer(enabled=True, max_entries=50)
        tracer.record("insert", position=0, value=42)
        for entry in tracer.entries:
            print(entry)
    """

    __slots__ = ("enabled", "max_entries", "_entries")

    def __init__(self, *, enabled: bool = False, max_entries: int = 200) -> None:
        self.enabled = enabled
        self.max_entries = max_entries
        self._entries: list[dict[str, Any]] = []

    def record(self, operation: str, **kwargs: Any) -> None:
        """Record a single operation event.

        Args:
            operation: Human-readable operation name (e.g. ``"insert"``).
            **kwargs:  Arbitrary key-value context (e.g. ``position=2, value=99``).
        """
        if not self.enabled:
            return
        entry: dict[str, Any] = {
            "op": operation,
            "ts": time.monotonic(),
            **kwargs,
        }
        self._entries.append(entry)
        if len(self._entries) > self.max_entries:
            self._entries.pop(0)

    @property
    def entries(self) -> list[dict[str, Any]]:
        """Return a shallow copy of the trace log."""
        return list(self._entries)

    def clear(self) -> None:
        """Clear the trace log."""
        self._entries.clear()

    def summary(self) -> dict[str, int]:
        """Return a count of each operation type."""
        counts: dict[str, int] = {}
        for e in self._entries:
            counts[e["op"]] = counts.get(e["op"], 0) + 1
        return counts
    
    def get_events(self) -> list[dict[str, Any]]:
        """Return all recorded events."""
        return self._entries