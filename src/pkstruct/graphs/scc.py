"""
pkstruct.graphs.scc
===================
Strongly connected components algorithms: Kosaraju and Tarjan.
"""

from __future__ import annotations

from typing import Any

from pkstruct.graphs.directed import DirectedGraph
from pkstruct.graphs.exceptions import InvalidGraphOperationError
from pkstruct.graphs.graph import Graph


def kosaraju(graph: Graph) -> list[list[Any]]:
    """Find strongly connected components using Kosaraju's algorithm.

    Parameters
    ----------
    graph : Graph
        A directed graph.

    Returns
    -------
    list[list[Any]]
        List of SCCs, each being a list of vertices.

    Raises
    ------
    InvalidGraphOperationError
        If the graph is undirected.
    """
    if not graph.is_directed():
        raise InvalidGraphOperationError("Kosaraju's algorithm requires a directed graph.")

    visited: set[Any] = set()
    finish_stack: list[Any] = []

    def _dfs(v: Any) -> None:
        visited.add(v)
        for neighbor in graph.get_neighbors(v):
            if neighbor not in visited:
                _dfs(neighbor)
        finish_stack.append(v)

    for v in graph:
        if v not in visited:
            _dfs(v)

    if isinstance(graph, DirectedGraph):
        transposed = graph.reverse()
    else:
        transposed = DirectedGraph()
        for v in graph:
            transposed.add_vertex(v)
        for u in graph:
            for v, w in {n: graph.get_weight(u, n) for n in graph.get_neighbors(u)}.items():
                transposed.add_edge(v, u, w)

    visited.clear()
    sccs: list[list[Any]] = []

    def _dfs_reverse(v: Any, component: list[Any]) -> None:
        visited.add(v)
        component.append(v)
        for neighbor in transposed.get_neighbors(v):
            if neighbor not in visited:
                _dfs_reverse(neighbor, component)

    while finish_stack:
        v = finish_stack.pop()
        if v not in visited:
            component: list[Any] = []
            _dfs_reverse(v, component)
            sccs.append(component)

    return sccs


def tarjan(graph: Graph) -> list[list[Any]]:
    """Find strongly connected components using Tarjan's algorithm.

    Parameters
    ----------
    graph : Graph
        A directed graph.

    Returns
    -------
    list[list[Any]]
        List of SCCs, each being a list of vertices.

    Raises
    ------
    InvalidGraphOperationError
        If the graph is undirected.
    """
    if not graph.is_directed():
        raise InvalidGraphOperationError("Tarjan's algorithm requires a directed graph.")

    index_counter: int = 0
    index: dict[Any, int] = {}
    lowlink: dict[Any, int] = {}
    stack: list[Any] = []
    on_stack: set[Any] = set()
    sccs: list[list[Any]] = []

    def _strongconnect(v: Any) -> None:
        nonlocal index_counter
        index[v] = index_counter
        lowlink[v] = index_counter
        index_counter += 1
        stack.append(v)
        on_stack.add(v)

        for neighbor in graph.get_neighbors(v):
            if neighbor not in index:
                _strongconnect(neighbor)
                lowlink[v] = min(lowlink[v], lowlink[neighbor])
            elif neighbor in on_stack:
                lowlink[v] = min(lowlink[v], index[neighbor])

        if lowlink[v] == index[v]:
            component: list[Any] = []
            while True:
                w = stack.pop()
                on_stack.discard(w)
                component.append(w)
                if w == v:
                    break
            sccs.append(component)

    for v in graph:
        if v not in index:
            _strongconnect(v)

    return sccs
