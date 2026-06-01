"""
pkstruct.graphs.weighted
========================
Weighted graph convenience class and weighted-graph utility functions.
"""

from __future__ import annotations

from typing import Any

from pkstruct.graphs.graph import Graph


class WeightedGraph(Graph):
    """A weighted undirected graph (convenience subclass of ``Graph``).

    Every edge carries a numeric weight (default ``1.0``).
    Useful as a shorthand when all edges are expected to have meaningful
    weights (e.g., for shortest-path or MST algorithms).

    Example
    -------
    >>> g = WeightedGraph()
    >>> g.add_edge("A", "B", 4.2)
    >>> g.add_edge("B", "C", 2.7)
    >>> g.get_weight("A", "B")
    4.2
    """

    def add_edge(self, u: Any, v: Any, weight: float = 1.0) -> None:
        super().add_edge(u, v, weight)

    def __repr__(self) -> str:
        with self._lock:
            vertices = list(self._adj.keys())
            edges = self.get_edges()
            return f"WeightedGraph(vertices={len(vertices)}, edges={len(edges)})"

    def debug(self) -> dict[str, object]:
        """Return internal state for debugging purposes."""
        with self._lock:
            return {
                "type": "WeightedGraph",
                "vertices": len(self._adj),
                "edges": self._edge_count,
                "adjacency": {k: dict(v) for k, v in self._adj.items()},
            }
