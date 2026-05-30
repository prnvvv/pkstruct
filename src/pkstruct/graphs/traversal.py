"""
pkstruct.graphs.traversal
=========================
Graph traversal algorithms: BFS and DFS.

All functions operate on any ``Graph``-like object that provides
``get_neighbors(v)`` and ``has_vertex(v)``.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Iterator
from typing import Any

from pkstruct.graphs.graph import Graph


def bfs(graph: Graph, start: Any) -> list[Any]:
    """Breadth-first search returning vertices in visitation order.

    Parameters
    ----------
    graph : Graph
        The graph to traverse.
    start : Any
        The starting vertex.

    Returns
    -------
    list[Any]
        Vertices in BFS order.

    Raises
    ------
    VertexNotFoundError
        If *start* is not in the graph.
    """
    if not graph.has_vertex(start):
        from pkstruct.graphs.exceptions import VertexNotFoundError

        raise VertexNotFoundError(start)

    visited: set[Any] = set()
    result: list[Any] = []
    queue: deque[Any] = deque([start])
    visited.add(start)

    while queue:
        v = queue.popleft()
        result.append(v)
        for neighbor in graph.get_neighbors(v):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return result


def dfs(graph: Graph, start: Any) -> list[Any]:
    """Depth-first search returning vertices in visitation order.

    Parameters
    ----------
    graph : Graph
        The graph to traverse.
    start : Any
        The starting vertex.

    Returns
    -------
    list[Any]
        Vertices in DFS order.

    Raises
    ------
    VertexNotFoundError
        If *start* is not in the graph.
    """
    if not graph.has_vertex(start):
        from pkstruct.graphs.exceptions import VertexNotFoundError

        raise VertexNotFoundError(start)

    visited: set[Any] = set()
    result: list[Any] = []
    _dfs_recursive(graph, start, visited, result)
    return result


def _dfs_recursive(graph: Graph, v: Any, visited: set[Any], result: list[Any]) -> None:
    visited.add(v)
    result.append(v)
    for neighbor in graph.get_neighbors(v):
        if neighbor not in visited:
            _dfs_recursive(graph, neighbor, visited, result)


def bfs_paths(graph: Graph, start: Any, goal: Any) -> list[list[Any]]:
    """Return all shortest paths from *start* to *goal* using BFS.

    Parameters
    ----------
    graph : Graph
        The graph to search.
    start : Any
        Starting vertex.
    goal : Any
        Target vertex.

    Returns
    -------
    list[list[Any]]
        All shortest paths from start to goal (may be multiple if
        there are multiple shortest paths).
    """
    queue: deque[list[Any]] = deque([[start]])
    result: list[list[Any]] = []
    shortest: int | None = None

    while queue:
        path = queue.popleft()
        v = path[-1]
        if v == goal:
            if shortest is None:
                shortest = len(path)
            if len(path) == shortest:
                result.append(path)
            continue
        if shortest is not None and len(path) >= shortest:
            continue
        for neighbor in graph.get_neighbors(v):
            if neighbor not in path:
                queue.append(path + [neighbor])

    return result


def dfs_paths(graph: Graph, start: Any, goal: Any) -> list[list[Any]]:
    """Return all paths from *start* to *goal* using DFS.

    Parameters
    ----------
    graph : Graph
        The graph to search.
    start : Any
        Starting vertex.
    goal : Any
        Target vertex.

    Returns
    -------
    list[list[Any]]
        All paths from start to goal.
    """
    result: list[list[Any]] = []
    _dfs_paths_recursive(graph, start, goal, [start], result)
    return result


def _dfs_paths_recursive(
    graph: Graph,
    v: Any,
    goal: Any,
    path: list[Any],
    result: list[list[Any]],
) -> None:
    if v == goal:
        result.append(list(path))
        return
    for neighbor in graph.get_neighbors(v):
        if neighbor not in path:
            path.append(neighbor)
            _dfs_paths_recursive(graph, neighbor, goal, path, result)
            path.pop()
