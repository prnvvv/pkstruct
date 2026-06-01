"""
pkstruct.graphs.directed
========================
Directed graph implementation with direction-specific operations.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from pkstruct.graphs.exceptions import VertexNotFoundError
from pkstruct.graphs.graph import Graph


class DirectedGraph(Graph):
    """A directed graph (convenience subclass of ``Graph`` with ``directed=True``).

    Provides additional methods specific to directed graphs such as
    in-degree, out-degree, transpose, sources, and sinks.

    Example
    -------
    >>> g = DirectedGraph()
    >>> g.add_edge("A", "B")
    >>> g.add_edge("B", "C")
    >>> g.add_edge("A", "C")
    >>> g.out_degree("A")
    2
    >>> g.in_degree("C")
    2
    """

    def __init__(self) -> None:
        super().__init__(directed=True)

    def in_degree(self, v: Any) -> int:
        """Return the number of incoming edges to *v*.

        Raises
        ------
        VertexNotFoundError
            If *v* is not in the graph.
        """
        with self._lock:
            if v not in self._adj:
                raise VertexNotFoundError(v)
            count = 0
            for u in self._adj:
                if v in self._adj[u]:
                    count += 1
            return count

    def out_degree(self, v: Any) -> int:
        """Return the number of outgoing edges from *v*.

        Raises
        ------
        VertexNotFoundError
            If *v* is not in the graph.
        """
        return self.degree(v)

    def sources(self) -> list[Any]:
        """Return all vertices with in-degree 0."""
        with self._lock:
            return [v for v in self._adj if self.in_degree(v) == 0]

    def sinks(self) -> list[Any]:
        """Return all vertices with out-degree 0."""
        with self._lock:
            return [v for v in self._adj if self.out_degree(v) == 0]

    def reverse(self) -> DirectedGraph:
        """Return the transpose (reverse all edges).

        Returns
        -------
        DirectedGraph
            A new graph with every edge (u, v) replaced by (v, u).
        """
        with self._lock:
            rev = DirectedGraph()
            for u in self._adj:
                rev.add_vertex(u)
            for u in self._adj:
                for v, w in self._adj[u].items():
                    rev.add_edge(v, u, w)
            return rev

    def __repr__(self) -> str:
        with self._lock:
            vertices = list(self._adj.keys())
            edges = self.get_edges()
            return f"DirectedGraph(vertices={len(vertices)}, edges={len(edges)})"

    def debug(self) -> dict[str, object]:
        """Return internal state for debugging purposes."""
        with self._lock:
            return {
                "type": "DirectedGraph",
                "vertices": len(self._adj),
                "edges": self._edge_count,
                "sources": self.sources(),
                "sinks": self.sinks(),
                "adjacency": {k: dict(v) for k, v in self._adj.items()},
            }
