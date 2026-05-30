"""
pkstruct.graphs
===============

Graph data structures module for the pkstruct ecosystem.

Provides production-grade implementations of graph representations and
classic graph algorithms with thread safety and ASCII visualization.

Classes
-------
Graph
    Adjacency-list based graph supporting directed/undirected and weighted modes.
DirectedGraph
    Directed graph with in-degree, out-degree, reverse, sources, and sinks.
WeightedGraph
    Convenience subclass for weighted undirected graphs.

Algorithms
----------
Traversal:
    bfs, dfs, bfs_paths, dfs_paths
Shortest Path:
    dijkstra, bellman_ford, floyd_warshall
Minimum Spanning Tree:
    kruskal, prim
Connectivity:
    connected_components, is_connected, is_bipartite, has_cycle, has_cycle_directed
Topological Sort:
    topological_sort_kahn, topological_sort_dfs
Strongly Connected Components:
    kosaraju, tarjan

Exceptions
----------
GraphError, VertexNotFoundError, EdgeNotFoundError, InvalidGraphOperationError,
NegativeCycleError, NoPathError

Example
-------
>>> from pkstruct.graphs import Graph
>>> g = Graph()
>>> g.add_edge("A", "B")
>>> g.add_edge("B", "C")
>>> g.add_edge("A", "C")
>>> list(g.get_neighbors("A"))
['B', 'C']
>>> len(g)
3
"""

from pkstruct.graphs.connectivity import (
    connected_components,
    has_cycle,
    has_cycle_directed,
    is_bipartite,
    is_connected,
)
from pkstruct.graphs.directed import DirectedGraph
from pkstruct.graphs.exceptions import (
    EdgeNotFoundError,
    GraphError,
    InvalidGraphOperationError,
    NegativeCycleError,
    NoPathError,
    VertexNotFoundError,
)
from pkstruct.graphs.graph import Graph
from pkstruct.graphs.mst import kruskal, prim
from pkstruct.graphs.scc import kosaraju, tarjan
from pkstruct.graphs.shortest_path import (
    bellman_ford,
    dijkstra,
    floyd_warshall,
    reconstruct_path,
    reconstruct_path_fw,
)
from pkstruct.graphs.topo_sort import topological_sort_dfs, topological_sort_kahn
from pkstruct.graphs.traversal import bfs, bfs_paths, dfs, dfs_paths
from pkstruct.graphs.visualization import adjacency_matrix, visualize
from pkstruct.graphs.weighted import WeightedGraph

__all__ = [
    # Graph classes
    "Graph",
    "DirectedGraph",
    "WeightedGraph",
    # Traversal
    "bfs",
    "dfs",
    "bfs_paths",
    "dfs_paths",
    # Shortest Path
    "dijkstra",
    "bellman_ford",
    "floyd_warshall",
    "reconstruct_path",
    "reconstruct_path_fw",
    # MST
    "kruskal",
    "prim",
    # Connectivity
    "connected_components",
    "is_connected",
    "is_bipartite",
    "has_cycle",
    "has_cycle_directed",
    # Topological Sort
    "topological_sort_kahn",
    "topological_sort_dfs",
    # SCC
    "kosaraju",
    "tarjan",
    # Visualization
    "visualize",
    "adjacency_matrix",
    # Exceptions
    "GraphError",
    "VertexNotFoundError",
    "EdgeNotFoundError",
    "InvalidGraphOperationError",
    "NegativeCycleError",
    "NoPathError",
]

__version__ = "0.1.0"
__author__ = "pkstruct contributors"
