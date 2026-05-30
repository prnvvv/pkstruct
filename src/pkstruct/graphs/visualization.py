"""
pkstruct.graphs.visualization
=============================
ASCII visualization utilities for graphs.
"""

from __future__ import annotations

from typing import Any

from pkstruct.graphs.graph import Graph
from pkstruct.graphs.exceptions import VertexNotFoundError


def visualize(graph: Graph, show_weights: bool = True) -> str:
    """Return an ASCII representation of the graph.

    Parameters
    ----------
    graph : Graph
        The graph to visualize.
    show_weights : bool, default=True
        If *True*, display edge weights.

    Returns
    -------
    str
        Multi-line ASCII art of the graph.
    """
    lines: list[str] = []
    lines.append(
        f"Graph (directed={graph.is_directed()}, vertices={graph.order()}, edges={graph.edge_count()})"
    )
    lines.append("")

    if graph.is_empty():
        lines.append("(empty)")
        return "\n".join(lines)

    for v in graph:
        neighbors = graph.get_neighbors(v)
        if not neighbors:
            lines.append(f"  {v!r} -> (isolated)")
        else:
            parts: list[str] = []
            for n in neighbors:
                w = graph.get_weight(v, n)
                if show_weights:
                    parts.append(f"{n!r} [{w}]")
                else:
                    parts.append(f"{n!r}")
            arrow = " <-> " if not graph.is_directed() else " -> "
            lines.append(f"  {v!r} -> {arrow.join(parts)}")

    return "\n".join(lines)


def adjacency_matrix(graph: Graph) -> str:
    """Return the adjacency matrix as a formatted string.

    Parameters
    ----------
    graph : Graph
        The graph to render.

    Returns
    -------
    str
        String representation of the adjacency matrix.
    """
    vertices = list(graph)
    n = len(vertices)
    if n == 0:
        return "(empty)"

    idx = {v: i for i, v in enumerate(vertices)}
    matrix: list[list[str]] = [["."] * n for _ in range(n)]

    for u in vertices:
        for v in graph.get_neighbors(u):
            w = graph.get_weight(u, v)
            matrix[idx[u]][idx[v]] = str(w)

    header = "    " + "  ".join(f"{v!r:>4}" for v in vertices)
    rows: list[str] = [header]
    for i, v in enumerate(vertices):
        row = f"{v!r:>3} " + "  ".join(f"{matrix[i][j]:>4}" for j in range(n))
        rows.append(row)

    return "\n".join(rows)
