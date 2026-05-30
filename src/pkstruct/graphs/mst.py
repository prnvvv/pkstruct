"""
pkstruct.graphs.mst
===================
Minimum spanning tree algorithms: Kruskal and Prim.
"""

from __future__ import annotations

import heapq
from typing import Any

from pkstruct.graphs.graph import Graph
from pkstruct.graphs.exceptions import InvalidGraphOperationError


def kruskal(graph: Graph) -> list[tuple[Any, Any, float]]:
    """Compute the Minimum Spanning Tree using Kruskal's algorithm.

    Parameters
    ----------
    graph : Graph
        An undirected weighted graph.

    Returns
    -------
    list[tuple[Any, Any, float]]
        Edges of the MST as ``(u, v, weight)`` tuples.

    Raises
    ------
    InvalidGraphOperationError
        If the graph is directed.
    """
    if graph.is_directed():
        raise InvalidGraphOperationError("Kruskal's algorithm requires an undirected graph.")

    edges = sorted(graph.get_edges(), key=lambda e: e[2])
    parent: dict[Any, Any] = {}
    rank: dict[Any, int] = {}

    def find(x: Any) -> Any:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x: Any, y: Any) -> None:
        rx, ry = find(x), find(y)
        if rx == ry:
            return
        if rank[rx] < rank[ry]:
            parent[rx] = ry
        elif rank[rx] > rank[ry]:
            parent[ry] = rx
        else:
            parent[ry] = rx
            rank[rx] += 1

    for v in graph:
        parent[v] = v
        rank[v] = 0

    mst: list[tuple[Any, Any, float]] = []
    for u, v, w in edges:
        if find(u) != find(v):
            union(u, v)
            mst.append((u, v, w))

    return mst


def prim(graph: Graph) -> list[tuple[Any, Any, float]]:
    """Compute the Minimum Spanning Tree using Prim's algorithm.

    Parameters
    ----------
    graph : Graph
        An undirected weighted graph.

    Returns
    -------
    list[tuple[Any, Any, float]]
        Edges of the MST as ``(u, v, weight)`` tuples.

    Raises
    ------
    InvalidGraphOperationError
        If the graph is directed or empty.
    """
    if graph.is_directed():
        raise InvalidGraphOperationError("Prim's algorithm requires an undirected graph.")

    vertices = list(graph)
    if not vertices:
        raise InvalidGraphOperationError("Graph is empty.")

    start = vertices[0]
    visited: set[Any] = {start}
    pq: list[tuple[float, Any, Any]] = []

    for neighbor in graph.get_neighbors(start):
        weight = graph.get_weight(start, neighbor)
        heapq.heappush(pq, (weight, start, neighbor))

    mst: list[tuple[Any, Any, float]] = []

    while pq and len(visited) < len(vertices):
        w, u, v = heapq.heappop(pq)
        if v in visited:
            continue
        visited.add(v)
        mst.append((u, v, w))
        for neighbor in graph.get_neighbors(v):
            if neighbor not in visited:
                weight = graph.get_weight(v, neighbor)
                heapq.heappush(pq, (weight, v, neighbor))

    return mst
