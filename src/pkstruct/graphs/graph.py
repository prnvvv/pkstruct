"""
pkstruct.graphs.graph
=====================
Core graph data structure using adjacency-list representation.

Supports both directed and undirected modes, with optional edge weights.
All public operations are thread-safe via ``StructureLock``.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Iterator
from typing import Any

from pkstruct._help import HelpMixin
from pkstruct._str import StrMixin
from pkstruct.graphs.exceptions import EdgeNotFoundError, VertexNotFoundError
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

    def validate(self) -> bool:
        """Verify internal graph consistency.

        Checks:
          1. All adjacency entries reference existing vertices.
          2. Edge count matches actual stored edges.
          3. For undirected graphs, adjacency is symmetric.

        Returns
        -------
        bool
            *True* if all invariants hold.
        """
        with self._lock:
            for u in self._adj:
                for v in self._adj[u]:
                    if v not in self._adj:
                        return False
            actual = sum(len(nbrs) for nbrs in self._adj.values())
            if not self._directed:
                actual //= 2
            if actual != self._edge_count:
                return False
            if not self._directed:
                for u in self._adj:
                    for v in self._adj[u]:
                        if u not in self._adj[v] or self._adj[u][v] != self._adj[v][u]:
                            return False
            return True

    def to_list(self) -> list[Any]:
        """Return a list of all vertices in the graph."""
        return self.get_vertices()

    @classmethod
    def from_list(cls, items: list[Any]) -> Graph:
        """Create a graph from a list of vertices and/or edges.

        Each item can be:
          - A hashable vertex to add.
          - A ``(u, v)`` tuple to add an edge with default weight.
          - A ``(u, v, weight)`` tuple to add a weighted edge.

        Parameters
        ----------
        items:
            List of vertices and/or edge tuples.

        Returns
        -------
        Graph
        """
        g = cls()
        for item in items:
            if isinstance(item, tuple) and len(item) == 3:
                u, v, w = item
                g.add_edge(u, v, w)
            elif isinstance(item, tuple) and len(item) == 2:
                u, v = item
                g.add_edge(u, v)
            else:
                g.add_vertex(item)
        return g

    def copy(self) -> Graph:
        """Return a deep copy of the graph."""
        with self._lock:
            cls = type(self)
            new_graph = cls(directed=self._directed) if cls is Graph else cls()
            for v in self._adj:
                new_graph._adj[v] = dict(self._adj[v])
            new_graph._edge_count = self._edge_count
            return new_graph

    def size(self) -> int:
        """Return the number of vertices in the graph."""
        return self.order()

    def visualize(self, show_weights: bool = True) -> str:
        """Return an ASCII representation of the graph.

        Parameters
        ----------
        show_weights:
            If *True*, display edge weights.
        """
        from pkstruct.graphs.visualization import visualize as _viz

        return _viz(self, show_weights=show_weights)

    # ------------------------------------------------------------------
    # LeetCode-style methods
    # ------------------------------------------------------------------

    def clone_graph(self) -> Graph:
        from copy import deepcopy
        with self._lock:
            cls = type(self)
            new_graph = cls(directed=self._directed) if cls is Graph else cls()
            new_graph._adj = deepcopy(self._adj)
            new_graph._edge_count = self._edge_count
            return new_graph

    @classmethod
    def number_of_islands(cls, grid: list[list[str]]) -> int:
        if not grid:
            return 0
        rows, cols = len(grid), len(grid[0])
        visited = [[False] * cols for _ in range(rows)]

        def dfs(r: int, c: int) -> None:
            if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] == '0' or visited[r][c]:
                return
            visited[r][c] = True
            dfs(r + 1, c)
            dfs(r - 1, c)
            dfs(r, c + 1)
            dfs(r, c - 1)

        count = 0
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == '1' and not visited[r][c]:
                    dfs(r, c)
                    count += 1
        return count

    @classmethod
    def course_schedule(cls, num_courses: int, prerequisites: list[list[int]]) -> bool:
        adj: list[list[int]] = [[] for _ in range(num_courses)]
        indegree = [0] * num_courses
        for u, v in prerequisites:
            adj[v].append(u)
            indegree[u] += 1
        q = deque([i for i in range(num_courses) if indegree[i] == 0])
        count = 0
        while q:
            v = q.popleft()
            count += 1
            for neighbor in adj[v]:
                indegree[neighbor] -= 1
                if indegree[neighbor] == 0:
                    q.append(neighbor)
        return count == num_courses

    @classmethod
    def alien_order(cls, words: list[str]) -> str:
        from collections import defaultdict
        adj: dict[str, set[str]] = defaultdict(set)
        indegree: dict[str, int] = defaultdict(int)
        for word in words:
            for c in word:
                indegree[c] = 0
        for i in range(len(words) - 1):
            w1, w2 = words[i], words[i + 1]
            min_len = min(len(w1), len(w2))
            if len(w1) > len(w2) and w1[:min_len] == w2[:min_len]:
                return ""
            for j in range(min_len):
                if w1[j] != w2[j]:
                    if w2[j] not in adj[w1[j]]:
                        adj[w1[j]].add(w2[j])
                        indegree[w2[j]] += 1
                    break
        q = deque([c for c in indegree if indegree[c] == 0])
        result: list[str] = []
        while q:
            c = q.popleft()
            result.append(c)
            for neighbor in adj[c]:
                indegree[neighbor] -= 1
                if indegree[neighbor] == 0:
                    q.append(neighbor)
        if len(result) != len(indegree):
            return ""
        return "".join(result)

    @classmethod
    def network_delay_time(cls, times: list[list[int]], n: int, k: int) -> int:
        import heapq
        adj: list[list[tuple[int, int]]] = [[] for _ in range(n + 1)]
        for u, v, w in times:
            adj[u].append((v, w))
        dist = [float('inf')] * (n + 1)
        dist[k] = 0
        pq = [(0, k)]
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[u]:
                continue
            for v, w in adj[u]:
                nd = d + w
                if nd < dist[v]:
                    dist[v] = nd
                    heapq.heappush(pq, (nd, v))
        max_dist = max(dist[1:])
        return -1 if max_dist == float('inf') else int(max_dist)

    # ------------------------------------------------------------------
    # Dunders
    # ------------------------------------------------------------------

    def __bool__(self) -> bool:
        """Return True if the graph has at least one vertex."""
        return self.order() > 0

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

    def __eq__(self, other: object) -> bool:
        """Return True if two graphs have the same vertices, edges, and weights."""
        if not isinstance(other, Graph):
            return NotImplemented
        with self._lock:
            my_directed = self._directed
            my_edge_count = self._edge_count
            my_adj = {v: dict(edges) for v, edges in self._adj.items()}
        with other._lock:
            return (
                my_directed == other._directed
                and my_edge_count == other._edge_count
                and my_adj == other._adj
            )

    def debug(self) -> dict[str, object]:
        """Return internal state for debugging purposes."""
        with self._lock:
            return {
                "type": type(self).__name__,
                "directed": self._directed,
                "vertices": len(self._adj),
                "edges": self._edge_count,
                "adjacency": {k: dict(v) for k, v in self._adj.items()},
            }
