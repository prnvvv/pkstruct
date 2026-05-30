"""Tests for pkstruct.graphs module."""

from __future__ import annotations

import math
import pytest
from pkstruct.graphs import (
    Graph,
    DirectedGraph,
    WeightedGraph,
    bfs,
    dfs,
    bfs_paths,
    dfs_paths,
    dijkstra,
    bellman_ford,
    floyd_warshall,
    reconstruct_path,
    kruskal,
    prim,
    connected_components,
    is_connected,
    is_bipartite,
    has_cycle,
    has_cycle_directed,
    topological_sort_kahn,
    topological_sort_dfs,
    kosaraju,
    tarjan,
    visualize,
    adjacency_matrix,
)
from pkstruct.graphs.exceptions import (
    VertexNotFoundError,
    EdgeNotFoundError,
    NegativeCycleError,
    NoPathError,
    InvalidGraphOperationError,
)


# ======================================================================
# Graph — Basic CRUD
# ======================================================================


class TestGraphCreation:
    def test_create_empty(self):
        g = Graph()
        assert g.order() == 0
        assert g.edge_count() == 0
        assert g.is_empty()
        assert not g.is_directed()
        assert len(g) == 0

    def test_create_directed(self):
        g = Graph(directed=True)
        assert g.is_directed()

    def test_add_vertex(self):
        g = Graph()
        g.add_vertex("A")
        assert "A" in g
        assert g.order() == 1

    def test_add_vertex_duplicate(self):
        g = Graph()
        g.add_vertex("A")
        g.add_vertex("A")
        assert g.order() == 1

    def test_has_vertex(self):
        g = Graph()
        g.add_vertex("A")
        assert g.has_vertex("A")
        assert not g.has_vertex("B")


class TestGraphEdges:
    def test_add_edge_undirected(self):
        g = Graph()
        g.add_edge("A", "B")
        assert g.has_edge("A", "B")
        assert g.has_edge("B", "A")
        assert g.edge_count() == 1

    def test_add_edge_directed(self):
        g = Graph(directed=True)
        g.add_edge("A", "B")
        assert g.has_edge("A", "B")
        assert not g.has_edge("B", "A")
        assert g.edge_count() == 1

    def test_add_edge_with_weight(self):
        g = Graph()
        g.add_edge("A", "B", weight=4.5)
        assert g.get_weight("A", "B") == 4.5
        assert g.get_weight("B", "A") == 4.5

    def test_get_weight_raises(self):
        g = Graph()
        g.add_vertex("A")
        with pytest.raises(EdgeNotFoundError):
            g.get_weight("A", "B")

    def test_set_weight(self):
        g = Graph()
        g.add_edge("A", "B", weight=1.0)
        g.set_weight("A", "B", 5.0)
        assert g.get_weight("A", "B") == 5.0

    def test_remove_edge(self):
        g = Graph()
        g.add_edge("A", "B")
        g.remove_edge("A", "B")
        assert not g.has_edge("A", "B")
        assert not g.has_edge("B", "A")

    def test_remove_edge_raises(self):
        g = Graph()
        g.add_vertex("A")
        g.add_vertex("B")
        with pytest.raises(EdgeNotFoundError):
            g.remove_edge("A", "B")

    def test_remove_vertex(self):
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("A", "C")
        g.remove_vertex("A")
        assert "A" not in g
        assert g.edge_count() == 0

    def test_remove_vertex_raises(self):
        g = Graph()
        with pytest.raises(VertexNotFoundError):
            g.remove_vertex("A")


class TestGraphAccess:
    def test_get_vertices(self):
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("C", "D")
        assert sorted(g.get_vertices()) == ["A", "B", "C", "D"]

    def test_get_edges_undirected(self):
        g = Graph()
        g.add_edge("A", "B", weight=1.0)
        g.add_edge("C", "D", weight=2.0)
        edges = g.get_edges()
        assert len(edges) == 2
        assert ("A", "B", 1.0) in edges or ("B", "A", 1.0) in edges

    def test_get_neighbors(self):
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("A", "C")
        assert sorted(g.get_neighbors("A")) == ["B", "C"]

    def test_get_neighbors_raises(self):
        g = Graph()
        with pytest.raises(VertexNotFoundError):
            g.get_neighbors("X")

    def test_degree(self):
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("A", "C")
        assert g.degree("A") == 2
        assert g.degree("B") == 1

    def test_degree_raises(self):
        g = Graph()
        with pytest.raises(VertexNotFoundError):
            g.degree("X")


class TestGraphOps:
    def test_clear(self):
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("C", "D")
        g.clear()
        assert g.is_empty()
        assert g.edge_count() == 0

    def test_copy(self):
        g = Graph()
        g.add_edge("A", "B", weight=3.0)
        g2 = g.copy()
        assert g2.has_edge("A", "B")
        assert g2.get_weight("A", "B") == 3.0
        g2.add_edge("C", "D")
        assert not g.has_edge("C", "D")

    def test_iter(self):
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("C", "D")
        assert sorted(iter(g)) == ["A", "B", "C", "D"]

    def test_repr(self):
        g = Graph()
        g.add_edge("A", "B")
        r = repr(g)
        assert "Graph" in r
        assert "vertices=2" in r
        assert "edges=1" in r


# ======================================================================
# DirectedGraph
# ======================================================================


class TestDirectedGraph:
    def test_create(self):
        dg = DirectedGraph()
        assert dg.is_directed()

    def test_in_degree(self):
        dg = DirectedGraph()
        dg.add_edge("A", "B")
        dg.add_edge("C", "B")
        assert dg.in_degree("B") == 2
        assert dg.in_degree("A") == 0

    def test_out_degree(self):
        dg = DirectedGraph()
        dg.add_edge("A", "B")
        dg.add_edge("A", "C")
        assert dg.out_degree("A") == 2

    def test_sources(self):
        dg = DirectedGraph()
        dg.add_edge("A", "B")
        dg.add_edge("B", "C")
        assert dg.sources() == ["A"]

    def test_sinks(self):
        dg = DirectedGraph()
        dg.add_edge("A", "B")
        dg.add_edge("B", "C")
        assert dg.sinks() == ["C"]

    def test_reverse(self):
        dg = DirectedGraph()
        dg.add_edge("A", "B")
        dg.add_edge("B", "C")
        rev = dg.reverse()
        assert rev.has_edge("B", "A")
        assert rev.has_edge("C", "B")
        assert not rev.has_edge("A", "B")


# ======================================================================
# WeightedGraph
# ======================================================================


class TestWeightedGraph:
    def test_create(self):
        wg = WeightedGraph()
        assert not wg.is_directed()

    def test_weighted_edge(self):
        wg = WeightedGraph()
        wg.add_edge("A", "B", 2.5)
        assert wg.get_weight("A", "B") == 2.5
        assert wg.get_weight("B", "A") == 2.5


# ======================================================================
# Traversal
# ======================================================================


class TestTraversal:
    def test_bfs(self):
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        g.add_edge("A", "C")
        assert bfs(g, "A") == ["A", "B", "C"]

    def test_bfs_raises(self):
        g = Graph()
        with pytest.raises(VertexNotFoundError):
            bfs(g, "X")

    def test_dfs(self):
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        g.add_edge("A", "D")
        result = dfs(g, "A")
        assert result[0] == "A"
        assert set(result) == {"A", "B", "C", "D"}

    def test_dfs_raises(self):
        g = Graph()
        with pytest.raises(VertexNotFoundError):
            dfs(g, "X")

    def test_bfs_paths(self):
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        g.add_edge("A", "C")
        paths = bfs_paths(g, "A", "C")
        assert len(paths) >= 1
        for p in paths:
            assert p[0] == "A"
            assert p[-1] == "C"

    def test_dfs_paths(self):
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        g.add_edge("A", "C")
        paths = dfs_paths(g, "A", "C")
        assert len(paths) >= 1


# ======================================================================
# Shortest Path
# ======================================================================


class TestShortestPath:
    def test_dijkstra(self):
        g = Graph()
        g.add_edge("A", "B", weight=4.0)
        g.add_edge("B", "C", weight=2.0)
        g.add_edge("A", "C", weight=10.0)
        dist, pred = dijkstra(g, "A")
        assert dist["C"] == 6.0  # A->B->C = 4+2
        assert dist["B"] == 4.0

    def test_dijkstra_raises(self):
        g = Graph()
        with pytest.raises(VertexNotFoundError):
            dijkstra(g, "X")

    def test_bellman_ford(self):
        g = Graph(directed=True)
        g.add_edge("A", "B", weight=4.0)
        g.add_edge("B", "C", weight=2.0)
        g.add_edge("A", "C", weight=1.0)
        dist, _ = bellman_ford(g, "A")
        assert dist["C"] == 1.0
        assert dist["B"] == 4.0

    def test_bellman_ford_negative(self):
        g = Graph(directed=True)
        g.add_edge("A", "B", weight=1.0)
        g.add_edge("B", "C", weight=-3.0)
        g.add_edge("C", "A", weight=1.0)
        with pytest.raises(NegativeCycleError):
            bellman_ford(g, "A")

    def test_floyd_warshall(self):
        g = Graph()
        g.add_edge("A", "B", weight=3.0)
        g.add_edge("B", "C", weight=1.0)
        g.add_edge("A", "C", weight=10.0)
        dist, _ = floyd_warshall(g)
        assert dist["A"]["C"] == 4.0  # A->B->C is shorter

    def test_reconstruct_path(self):
        g = Graph()
        g.add_edge("A", "B", weight=1.0)
        g.add_edge("B", "C", weight=1.0)
        _, pred = dijkstra(g, "A")
        path = reconstruct_path(pred, "A", "C")
        assert path == ["A", "B", "C"]

    def test_reconstruct_path_no_path(self):
        g = Graph()
        g.add_vertex("A")
        g.add_vertex("B")
        _, pred = dijkstra(g, "A")
        with pytest.raises(NoPathError):
            reconstruct_path(pred, "A", "B")


# ======================================================================
# MST
# ======================================================================


class TestMST:
    def test_kruskal(self):
        g = Graph()
        g.add_edge("A", "B", weight=4.0)
        g.add_edge("B", "C", weight=2.0)
        g.add_edge("A", "C", weight=1.0)
        mst = kruskal(g)
        total = sum(w for _, _, w in mst)
        assert total == 3.0  # A-C (1) + B-C (2)
        assert len(mst) == 2

    def test_kruskal_directed_raises(self):
        g = Graph(directed=True)
        g.add_edge("A", "B")
        with pytest.raises(InvalidGraphOperationError):
            kruskal(g)

    def test_prim(self):
        g = Graph()
        g.add_edge("A", "B", weight=4.0)
        g.add_edge("B", "C", weight=2.0)
        g.add_edge("A", "C", weight=1.0)
        mst = prim(g)
        total = sum(w for _, _, w in mst)
        assert total == 3.0
        assert len(mst) == 2

    def test_prim_empty_raises(self):
        g = Graph()
        with pytest.raises(InvalidGraphOperationError):
            prim(g)

    def test_kruskal_more_vertices(self):
        g = Graph()
        g.add_edge(1, 2, 1.0)
        g.add_edge(2, 3, 2.0)
        g.add_edge(3, 4, 3.0)
        g.add_edge(1, 4, 4.0)
        g.add_edge(2, 4, 5.0)
        mst = kruskal(g)
        total = sum(w for _, _, w in mst)
        assert total == 6.0  # 1 + 2 + 3
        assert len(mst) == 3


# ======================================================================
# Connectivity
# ======================================================================


class TestConnectivity:
    def test_connected_components(self):
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("C", "D")
        comps = connected_components(g)
        assert len(comps) == 2

    def test_is_connected(self):
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        assert is_connected(g)

    def test_is_not_connected(self):
        g = Graph()
        g.add_edge("A", "B")
        g.add_vertex("C")
        assert not is_connected(g)

    def test_is_bipartite(self):
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        g.add_edge("C", "D")
        assert is_bipartite(g)

    def test_is_not_bipartite(self):
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        g.add_edge("C", "A")
        assert not is_bipartite(g)

    def test_has_cycle(self):
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        g.add_edge("C", "A")
        assert has_cycle(g)

    def test_no_cycle(self):
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        assert not has_cycle(g)

    def test_has_cycle_directed(self):
        g = Graph(directed=True)
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        g.add_edge("C", "A")
        assert has_cycle_directed(g)

    def test_no_cycle_directed(self):
        g = Graph(directed=True)
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        assert not has_cycle_directed(g)


# ======================================================================
# Topological Sort
# ======================================================================


class TestTopoSort:
    def test_kahn(self):
        g = Graph(directed=True)
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        g.add_edge("A", "C")
        order = topological_sort_kahn(g)
        assert order.index("A") < order.index("B")
        assert order.index("A") < order.index("C")
        assert order.index("B") < order.index("C")

    def test_kahn_undirected_raises(self):
        g = Graph()
        with pytest.raises(InvalidGraphOperationError):
            topological_sort_kahn(g)

    def test_kahn_cycle_raises(self):
        g = Graph(directed=True)
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        g.add_edge("C", "A")
        with pytest.raises(InvalidGraphOperationError):
            topological_sort_kahn(g)

    def test_dfs_sort(self):
        g = Graph(directed=True)
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        g.add_edge("A", "C")
        order = topological_sort_dfs(g)
        assert order.index("A") < order.index("B")
        assert order.index("A") < order.index("C")
        assert order.index("B") < order.index("C")

    def test_dfs_undirected_raises(self):
        g = Graph()
        with pytest.raises(InvalidGraphOperationError):
            topological_sort_dfs(g)


# ======================================================================
# SCC
# ======================================================================


class TestSCC:
    def test_kosaraju_single(self):
        g = Graph(directed=True)
        g.add_edge("A", "B")
        g.add_edge("B", "A")
        sccs = kosaraju(g)
        assert len(sccs) == 1
        assert set(sccs[0]) == {"A", "B"}

    def test_kosaraju_multiple(self):
        g = Graph(directed=True)
        g.add_edge("A", "B")
        g.add_edge("B", "A")
        g.add_edge("C", "D")
        g.add_edge("D", "C")
        sccs = kosaraju(g)
        assert len(sccs) == 2
        assert set(sccs[0]) == {"A", "B"} or set(sccs[0]) == {"C", "D"}

    def test_kosaraju_undirected_raises(self):
        g = Graph()
        with pytest.raises(InvalidGraphOperationError):
            kosaraju(g)

    def test_tarjan_single(self):
        g = Graph(directed=True)
        g.add_edge("A", "B")
        g.add_edge("B", "A")
        sccs = tarjan(g)
        assert len(sccs) == 1
        assert set(sccs[0]) == {"A", "B"}

    def test_tarjan_multiple(self):
        g = Graph(directed=True)
        g.add_edge("A", "B")
        g.add_edge("B", "A")
        g.add_edge("C", "D")
        g.add_edge("D", "C")
        sccs = tarjan(g)
        assert len(sccs) == 2

    def test_tarjan_undirected_raises(self):
        g = Graph()
        with pytest.raises(InvalidGraphOperationError):
            tarjan(g)


# ======================================================================
# Visualization
# ======================================================================


class TestVisualization:
    def test_visualize_returns_string(self):
        g = Graph()
        g.add_edge("A", "B")
        result = visualize(g)
        assert isinstance(result, str)
        assert "A" in result
        assert "B" in result

    def test_visualize_empty(self):
        g = Graph()
        result = visualize(g)
        assert "(empty)" in result

    def test_adjacency_matrix(self):
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        result = adjacency_matrix(g)
        assert isinstance(result, str)
        assert "A" in result
