"""
pkstruct.graphs.shortest_path
==============================
Shortest-path algorithms: Dijkstra, Bellman-Ford, Floyd-Warshall.
"""

from __future__ import annotations

import heapq
import math
from typing import Any

from pkstruct.graphs.graph import Graph
from pkstruct.graphs.exceptions import (
    NegativeCycleError,
    NoPathError,
    VertexNotFoundError,
)


def dijkstra(
    graph: Graph, source: Any, target: Any | None = None
) -> tuple[dict[Any, float], dict[Any, Any | None]]:
    """Compute shortest paths from *source* using Dijkstra's algorithm.

    Parameters
    ----------
    graph : Graph
        Weighted graph (edge weights must be non-negative).
    source : Any
        Starting vertex.
    target : Any, optional
        If provided, early-exit when *target* is reached.

    Returns
    -------
    tuple[dict[Any, float], dict[Any, Any | None]]
        ``(distances, predecessors)`` where *distances* maps each vertex
        to its shortest distance from *source*, and *predecessors* maps
        each vertex to its predecessor on the shortest path.

    Raises
    ------
    VertexNotFoundError
        If *source* is not in the graph.
    """
    if not graph.has_vertex(source):
        raise VertexNotFoundError(source)

    distances: dict[Any, float] = {v: math.inf for v in graph}
    predecessors: dict[Any, Any | None] = {v: None for v in graph}
    distances[source] = 0.0

    pq: list[tuple[float, Any]] = [(0.0, source)]
    visited: set[Any] = set()

    while pq:
        d, v = heapq.heappop(pq)
        if v in visited:
            continue
        visited.add(v)
        if target is not None and v == target:
            break
        for neighbor in graph.get_neighbors(v):
            if neighbor in visited:
                continue
            weight = graph.get_weight(v, neighbor)
            new_dist = d + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                predecessors[neighbor] = v
                heapq.heappush(pq, (new_dist, neighbor))

    return distances, predecessors


def bellman_ford(graph: Graph, source: Any) -> tuple[dict[Any, float], dict[Any, Any | None]]:
    """Compute shortest paths from *source* using Bellman-Ford.

    Supports negative edge weights. Raises an error if a negative cycle
    is reachable from *source*.

    Parameters
    ----------
    graph : Graph
        Weighted graph (may contain negative edge weights).
    source : Any
        Starting vertex.

    Returns
    -------
    tuple[dict[Any, float], dict[Any, Any | None]]
        ``(distances, predecessors)``.

    Raises
    ------
    VertexNotFoundError
        If *source* is not in the graph.
    NegativeCycleError
        If a negative-weight cycle is reachable from *source*.
    """
    if not graph.has_vertex(source):
        raise VertexNotFoundError(source)

    distances: dict[Any, float] = {v: math.inf for v in graph}
    predecessors: dict[Any, Any | None] = {v: None for v in graph}
    distances[source] = 0.0

    vertices = list(graph)
    n = len(vertices)
    edges: list[tuple[Any, Any, float]] = []
    for u in vertices:
        for v in graph.get_neighbors(u):
            w = graph.get_weight(u, v)
            edges.append((u, v, w))

    for _ in range(n - 1):
        updated = False
        for u, v, w in edges:
            if distances[u] != math.inf and distances[u] + w < distances[v]:
                distances[v] = distances[u] + w
                predecessors[v] = u
                updated = True
        if not updated:
            break

    for u, v, w in edges:
        if distances[u] != math.inf and distances[u] + w < distances[v]:
            raise NegativeCycleError()

    return distances, predecessors


def floyd_warshall(
    graph: Graph,
) -> tuple[dict[Any, dict[Any, float]], dict[Any, dict[Any, Any | None]]]:
    """Compute all-pairs shortest paths using Floyd-Warshall.

    Parameters
    ----------
    graph : Graph
        Weighted graph.

    Returns
    -------
    tuple[dict[Any, dict[Any, float]], dict[Any, dict[Any, Any | None]]]
        ``(distances, next_nodes)`` where *distances[u][v]* is the
        shortest distance from *u* to *v*, and *next_nodes[u][v]* is
        the next vertex on the shortest path from *u* to *v* (for path
        reconstruction).

    Raises
    ------
    NegativeCycleError
        If the graph contains a negative-weight cycle.
    """
    vertices = list(graph)
    dist: dict[Any, dict[Any, float]] = {u: {v: math.inf for v in vertices} for u in vertices}
    nxt: dict[Any, dict[Any, Any | None]] = {u: {v: None for v in vertices} for u in vertices}

    for v in vertices:
        dist[v][v] = 0.0

    for u in vertices:
        for v in graph.get_neighbors(u):
            w = graph.get_weight(u, v)
            if w < dist[u][v]:
                dist[u][v] = w
                nxt[u][v] = v

    for k in vertices:
        for i in vertices:
            for j in vertices:
                if dist[i][k] != math.inf and dist[k][j] != math.inf:
                    new_dist = dist[i][k] + dist[k][j]
                    if new_dist < dist[i][j]:
                        dist[i][j] = new_dist
                        nxt[i][j] = nxt[i][k]

    for v in vertices:
        if dist[v][v] < 0:
            raise NegativeCycleError()

    return dist, nxt


def reconstruct_path(predecessors: dict[Any, Any | None], source: Any, target: Any) -> list[Any]:
    """Reconstruct a shortest path from a predecessors dictionary.

    Parameters
    ----------
    predecessors : dict[Any, Any | None]
        Predecessor map from Dijkstra or Bellman-Ford.
    source : Any
        Starting vertex.
    target : Any
        Target vertex.

    Returns
    -------
    list[Any]
        The path from *source* to *target* as a list of vertices.

    Raises
    ------
    NoPathError
        If no path exists.
    """
    path: list[Any] = []
    v = target
    while v is not None:
        path.append(v)
        v = predecessors[v]
    path.reverse()
    if path[0] != source:
        raise NoPathError(source, target)
    return path


def reconstruct_path_fw(
    next_nodes: dict[Any, dict[Any, Any | None]], source: Any, target: Any
) -> list[Any]:
    """Reconstruct a shortest path from Floyd-Warshall's next_nodes table.

    Parameters
    ----------
    next_nodes : dict[Any, dict[Any, Any | None]]
        Next-node map from :func:`floyd_warshall`.
    source : Any
        Starting vertex.
    target : Any
        Target vertex.

    Returns
    -------
    list[Any]
        The path from *source* to *target*.

    Raises
    ------
    NoPathError
        If no path exists.
    """
    if next_nodes[source][target] is None and source != target:
        raise NoPathError(source, target)
    path: list[Any] = [source]
    while source != target:
        source = next_nodes[source][target]
        path.append(source)
    return path
