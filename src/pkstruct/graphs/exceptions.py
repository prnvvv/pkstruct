"""
pkstruct.graphs.exceptions
==========================
Custom exception hierarchy for the graphs module.

All graph-specific exceptions inherit from :class:`GraphError` so callers
can catch the entire family with a single ``except GraphError`` clause.
"""

from __future__ import annotations

__all__ = [
    "GraphError",
    "VertexNotFoundError",
    "EdgeNotFoundError",
    "InvalidGraphOperationError",
    "NegativeCycleError",
    "NoPathError",
]


class GraphError(Exception):
    """Base exception for all graph-related errors."""


class VertexNotFoundError(GraphError):
    """Raised when a vertex does not exist in the graph."""

    def __init__(self, vertex: object) -> None:
        super().__init__(f"Vertex not found: {vertex!r}")
        self.vertex = vertex


class EdgeNotFoundError(GraphError):
    """Raised when an edge does not exist in the graph."""

    def __init__(self, u: object, v: object) -> None:
        super().__init__(f"Edge not found: ({u!r}, {v!r})")
        self.u = u
        self.v = v


class InvalidGraphOperationError(GraphError):
    """Raised when an operation is invalid for the current graph state."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class NegativeCycleError(GraphError):
    """Raised when a negative-weight cycle is detected."""

    def __init__(self, message: str = "Graph contains a negative-weight cycle") -> None:
        super().__init__(message)


class NoPathError(GraphError):
    """Raised when no path exists between two vertices."""

    def __init__(self, source: object, target: object) -> None:
        super().__init__(f"No path from {source!r} to {target!r}")
        self.source = source
        self.target = target
