"""
pkstruct.graphs.connectivity
============================
Graph connectivity algorithms: connected components, bipartite check.
"""

from __future__ import annotations

from collections import deque
from typing import Any

from pkstruct.graphs.graph import Graph


def connected_components(graph: Graph) -> list[list[Any]]:
    """Return all connected components of an undirected graph.

    Parameters
    ----------
    graph : Graph
        An undirected graph.

    Returns
    -------
    list[list[Any]]
        List of components, each being a list of vertices.
    """
    visited: set[Any] = set()
    components: list[list[Any]] = []

    for v in graph:
        if v not in visited:
            component: list[Any] = []
            queue: deque[Any] = deque([v])
            visited.add(v)
            while queue:
                current = queue.popleft()
                component.append(current)
                for neighbor in graph.get_neighbors(current):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
            components.append(component)

    return components


def is_connected(graph: Graph) -> bool:
    """Return *True* if the undirected graph is connected.

    Parameters
    ----------
    graph : Graph
        An undirected graph.

    Returns
    -------
    bool
    """
    if graph.is_empty():
        return True
    components = connected_components(graph)
    return len(components) == 1


def is_bipartite(graph: Graph) -> bool:
    """Check if a graph is bipartite using BFS coloring.

    Parameters
    ----------
    graph : Graph
        An undirected graph.

    Returns
    -------
    bool
        *True* if the graph is bipartite.
    """
    color: dict[Any, int] = {}

    for start in graph:
        if start not in color:
            color[start] = 0
            queue: deque[Any] = deque([start])
            while queue:
                v = queue.popleft()
                for neighbor in graph.get_neighbors(v):
                    if neighbor not in color:
                        color[neighbor] = 1 - color[v]
                        queue.append(neighbor)
                    elif color[neighbor] == color[v]:
                        return False
    return True


def has_cycle(graph: Graph) -> bool:
    """Detect if an undirected graph contains a cycle.

    Parameters
    ----------
    graph : Graph
        An undirected graph.

    Returns
    -------
    bool
    """
    visited: set[Any] = set()

    def _dfs(v: Any, parent: Any | None) -> bool:
        visited.add(v)
        for neighbor in graph.get_neighbors(v):
            if neighbor not in visited:
                if _dfs(neighbor, v):
                    return True
            elif neighbor != parent:
                return True
        return False

    return any(v not in visited and _dfs(v, None) for v in graph)


def has_cycle_directed(graph: Graph) -> bool:
    """Detect if a directed graph contains a cycle using DFS coloring.

    Parameters
    ----------
    graph : Graph
        A directed graph.

    Returns
    -------
    bool
    """
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[Any, int] = {v: WHITE for v in graph}

    def _dfs(v: Any) -> bool:
        color[v] = GRAY
        for neighbor in graph.get_neighbors(v):
            if color[neighbor] == GRAY:
                return True
            if color[neighbor] == WHITE and _dfs(neighbor):
                return True
        color[v] = BLACK
        return False

    return any(color[v] == WHITE and _dfs(v) for v in graph)
