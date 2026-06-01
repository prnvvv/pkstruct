"""
pkstruct.graphs.graph
=====================
Core graph data structure using adjacency-list representation.

Supports both directed and undirected modes, with optional edge weights.
All public operations are thread-safe via ``StructureLock``.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from pkstruct._help import HelpMixin
from pkstruct._str import StrMixin
from pkstruct.graphs.exceptions import VertexNotFoundError, EdgeNotFoundError
from pkstruct.shared.threading import StructureLock


class Graph(HelpMixin, StrMixin):
    """Adjacency-list based graph supporting directed/undirected and weighted modes.

    Parameters
    ----------
    directed : bool, default=False
        If *True*, edges are one-way; otherwise edges are bidirectional.

    Example
    -------
    >>> g = Graph()
    >>> g.add_vertex("A")
    >>> g.add_edge("A", "B")
    >>> g.add_edge("A", "C")
    >>> len(g)
    3
    >>> list(g.get_neighbors("A"))
    ['B', 'C']
    """

    __slots__ = ("_adj", "_directed", "_lock", "_edge_count")

    def __init__(self, directed: bool = False) -> None:
        self._adj: dict[Any, dict[Any, float]] = {}
        self._directed: bool = directed
        self._lock: StructureLock = StructureLock()
        self._edge_count: int = 0

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def add_vertex(self, v: Any) -> None:
        """Add a vertex to the graph. No-op if already present."""
        with self._lock:
            if v not in self._adj:
                self._adj[v] = {}

    def add_edge(self, u: Any, v: Any, weight: float = 1.0) -> None:
        """Add an edge between *u* and *v* with optional *weight*.

        Vertices are created automatically if they do not exist.
        If the edge already exists, its weight is updated.
        """
        with self._lock:
            self.add_vertex(u)
            self.add_vertex(v)
            if v not in self._adj[u]:
                self._edge_count += 1
            self._adj[u][v] = weight
            if not self._directed and u != v:
                self._adj[v][u] = weight

    def remove_vertex(self, v: Any) -> None:
        """Remove *v* and all incident edges.

        Raises
        ------
        VertexNotFoundError
            If *v* is not in the graph.
        """
        with self._lock:
            if v not in self._adj:
                raise VertexNotFoundError(v)
            for neighbor in list(self._adj[v]):
                self._adj[neighbor].pop(v, None)
            del self._adj[v]
            self._edge_count = sum(len(nbrs) for nbrs in self._adj.values())
            if not self._directed:
                self._edge_count //= 2

    def remove_edge(self, u: Any, v: Any) -> None:
        """Remove the edge from *u* to *v*.

        Raises
        ------
        VertexNotFoundError
            If either vertex does not exist.
        EdgeNotFoundError
            If the edge does not exist.
        """
        with self._lock:
            if u not in self._adj:
                raise VertexNotFoundError(u)
            if v not in self._adj:
                raise VertexNotFoundError(v)
            if v not in self._adj[u]:
                raise EdgeNotFoundError(u, v)
            del self._adj[u][v]
            self._edge_count -= 1
            if not self._directed and u != v:
                self._adj[v].pop(u, None)

    def clear(self) -> None:
        """Remove all vertices and edges."""
        with self._lock:
            self._adj.clear()
            self._edge_count = 0

    # ------------------------------------------------------------------
    # Access
    # ------------------------------------------------------------------

    def has_vertex(self, v: Any) -> bool:
        """Return *True* if *v* is in the graph."""
        with self._lock:
            return v in self._adj

    def has_edge(self, u: Any, v: Any) -> bool:
        """Return *True* if the edge (u, v) exists."""
        with self._lock:
            return u in self._adj and v in self._adj[u]

    def get_weight(self, u: Any, v: Any) -> float:
        """Return the weight of edge (u, v).

        Raises
        ------
        VertexNotFoundError
            If either vertex does not exist.
        EdgeNotFoundError
            If the edge does not exist.
        """
        with self._lock:
            if u not in self._adj:
                raise VertexNotFoundError(u)
            if v not in self._adj[u]:
                raise EdgeNotFoundError(u, v)
            return self._adj[u][v]

    def set_weight(self, u: Any, v: Any, weight: float) -> None:
        """Set the weight of edge (u, v).

        Raises
        ------
        VertexNotFoundError
            If either vertex does not exist.
        EdgeNotFoundError
            If the edge does not exist.
        """
        with self._lock:
            if u not in self._adj:
                raise VertexNotFoundError(u)
            if v not in self._adj[u]:
                raise EdgeNotFoundError(u, v)
            self._adj[u][v] = weight
            if not self._directed and u != v:
                self._adj[v][u] = weight

    def get_neighbors(self, v: Any) -> list[Any]:
        """Return a list of neighbors of *v* (outgoing in directed mode).

        Raises
        ------
        VertexNotFoundError
            If *v* is not in the graph.
        """
        with self._lock:
            if v not in self._adj:
                raise VertexNotFoundError(v)
            return list(self._adj[v].keys())

    def get_vertices(self) -> list[Any]:
        """Return a list of all vertices in the graph."""
        with self._lock:
            return list(self._adj.keys())

    def get_edges(self) -> list[tuple[Any, Any, float]]:
        """Return a list of all edges as (u, v, weight) tuples."""
        with self._lock:
            edges: list[tuple[Any, Any, float]] = []
            seen: set[frozenset] = set()
            for u in self._adj:
                for v, w in self._adj[u].items():
                    if not self._directed:
                        key = frozenset((u, v))
                        if key in seen:
                            continue
                        seen.add(key)
                    edges.append((u, v, w))
            return edges

    def degree(self, v: Any) -> int:
        """Return the degree of vertex *v*.

        For directed graphs, returns the out-degree (number of outgoing edges).

        Raises
        ------
        VertexNotFoundError
            If *v* is not in the graph.
        """
        with self._lock:
            if v not in self._adj:
                raise VertexNotFoundError(v)
            return len(self._adj[v])

    def order(self) -> int:
        """Return the number of vertices in the graph."""
        with self._lock:
            return len(self._adj)

    def edge_count(self) -> int:
        """Return the number of edges in the graph."""
        with self._lock:
            return self._edge_count

    def is_directed(self) -> bool:
        """Return *True* if this is a directed graph."""
        return self._directed

    def is_empty(self) -> bool:
        """Return *True* if the graph has no vertices."""
        with self._lock:
            return len(self._adj) == 0

    def copy(self) -> Graph:
        """Return a deep copy of the graph."""
        with self._lock:
            new_graph = Graph(directed=self._directed)
            for v in self._adj:
                new_graph._adj[v] = dict(self._adj[v])
            new_graph._edge_count = self._edge_count
            return new_graph

    # ------------------------------------------------------------------
    # Dunders
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return self.order()

    def __contains__(self, v: Any) -> bool:
        return self.has_vertex(v)

    def __iter__(self) -> Iterator[Any]:
        vertices = self.get_vertices()
        return iter(vertices)

    def __repr__(self) -> str:
        with self._lock:
            vertices = list(self._adj.keys())
            edges = self.get_edges()
            return f"Graph(directed={self._directed}, vertices={len(vertices)}, edges={len(edges)})"
