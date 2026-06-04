"""
pkstruct.graphs.topo_sort
=========================
Topological sort algorithms: Kahn's algorithm and DFS-based sort.
"""

from __future__ import annotations

from collections import deque
from typing import Any

from pkstruct.graphs.exceptions import InvalidGraphOperationError
from pkstruct.graphs.graph import Graph


def topological_sort_kahn(graph: Graph) -> list[Any]:
    """Topological sort using Kahn's algorithm (BFS-based).

    Parameters
    ----------
    graph : Graph
        A directed graph.

    Returns
    -------
    list[Any]
        Vertices in topological order.

    Raises
    ------
    InvalidGraphOperationError
        If the graph is undirected or contains a cycle.
    """
    if not graph.is_directed():
        raise InvalidGraphOperationError("Topological sort requires a directed graph.")

    in_degree: dict[Any, int] = {v: 0 for v in graph}
    for u in graph:
        for v in graph.get_neighbors(u):
            in_degree[v] += 1

    queue: deque[Any] = deque([v for v in graph if in_degree[v] == 0])
    result: list[Any] = []

    while queue:
        v = queue.popleft()
        result.append(v)
        for neighbor in graph.get_neighbors(v):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(result) != len(list(graph)):
        raise InvalidGraphOperationError("Graph contains a cycle; topological sort not possible.")

    return result


def topological_sort_dfs(graph: Graph) -> list[Any]:
    """Topological sort using DFS-based algorithm.

    Parameters
    ----------
    graph : Graph
        A directed graph.

    Returns
    -------
    list[Any]
        Vertices in topological order.

    Raises
    ------
    InvalidGraphOperationError
        If the graph is undirected or contains a cycle.
    """
    if not graph.is_directed():
        raise InvalidGraphOperationError("Topological sort requires a directed graph.")

    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[Any, int] = {v: WHITE for v in graph}
    result: list[Any] = []
    has_cycle: bool = False

    def _dfs(v: Any) -> None:
        nonlocal has_cycle
        if has_cycle:
            return
        color[v] = GRAY
        for neighbor in graph.get_neighbors(v):
            if color[neighbor] == GRAY:
                has_cycle = True
                return
            if color[neighbor] == WHITE:
                _dfs(neighbor)
        color[v] = BLACK
        result.append(v)

    for v in graph:
        if color[v] == WHITE:
            _dfs(v)
            if has_cycle:
                raise InvalidGraphOperationError(
                    "Graph contains a cycle; topological sort not possible."
                )

    result.reverse()
    return result
