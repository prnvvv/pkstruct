"""Advanced adversarial tests for pkstruct.graphs.

Tests edge cases, stress, exceptions, property-based invariants,
cross-validation, thread-safety, and known-bug reproduction.
"""

from __future__ import annotations

import math
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

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
# Edge-case graphs  (fixtures)
# ======================================================================


@pytest.fixture
def empty_graph():
    return Graph()


@pytest.fixture
def single_vertex_graph():
    g = Graph()
    g.add_vertex("A")
    return g


@pytest.fixture
def single_edge_graph():
    g = Graph()
    g.add_edge("A", "B", weight=1.0)
    return g


@pytest.fixture
def disconnected_graph():
    g = Graph()
    g.add_edge("A", "B")
    g.add_edge("C", "D")
    g.add_vertex("E")
    return g


@pytest.fixture
def triangle_graph():
    g = Graph()
    g.add_edge("A", "B", weight=1.0)
    g.add_edge("B", "C", weight=1.0)
    g.add_edge("C", "A", weight=1.0)
    return g


@pytest.fixture
def line_graph():
    g = Graph()
    g.add_edge(1, 2, weight=1.0)
    g.add_edge(2, 3, weight=2.0)
    g.add_edge(3, 4, weight=3.0)
    g.add_edge(4, 5, weight=4.0)
    return g


@pytest.fixture
def complete_graph_k4():
    g = Graph()
    vertices = [1, 2, 3, 4]
    for v in vertices:
        g.add_vertex(v)
    for i in range(len(vertices)):
        for j in range(i + 1, len(vertices)):
            g.add_edge(vertices[i], vertices[j], weight=round(random.random() * 10, 2))
    return g


# ======================================================================
# Graph CRUD edge cases
# ======================================================================


class TestGraphCreationEdgeCases:
    def test_empty_graph_order(self, empty_graph):
        assert empty_graph.order() == 0
        assert empty_graph.edge_count() == 0
        assert empty_graph.is_empty()

    def test_single_vertex_properties(self, single_vertex_graph):
        assert single_vertex_graph.order() == 1
        assert single_vertex_graph.edge_count() == 0
        assert not single_vertex_graph.is_empty()
        assert single_vertex_graph.degree("A") == 0
        assert single_vertex_graph.get_neighbors("A") == []

    def test_none_vertex(self):
        g = Graph()
        g.add_vertex(None)
        assert g.has_vertex(None)
        assert g.order() == 1

    def test_int_vertices(self):
        g = Graph()
        g.add_edge(1, 2)
        g.add_edge(2, 3)
        assert g.has_edge(1, 2)
        assert g.has_edge(2, 1)
        assert g.degree(2) == 2

    def test_tuple_vertices(self):
        g = Graph()
        g.add_edge((1, 2), (3, 4))
        assert g.has_edge((1, 2), (3, 4))

    def test_float_vertices(self):
        g = Graph()
        g.add_edge(1.5, 2.5)
        assert g.has_edge(1.5, 2.5)

    def test_get_weight_nonexistent_vertex(self, empty_graph):
        with pytest.raises(VertexNotFoundError):
            empty_graph.get_weight("X", "Y")

    def test_set_weight_nonexistent_edge(self, single_vertex_graph):
        with pytest.raises(EdgeNotFoundError):
            single_vertex_graph.set_weight("A", "B", 5.0)

    def test_set_weight_on_directed_edge(self):
        g = Graph(directed=True)
        g.add_edge("A", "B", weight=1.0)
        g.set_weight("A", "B", 3.0)
        assert g.get_weight("A", "B") == 3.0
        with pytest.raises(EdgeNotFoundError):
            g.get_weight("B", "A")

    def test_remove_vertex_removes_all_incident_edges(self):
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("A", "C")
        g.add_edge("A", "D")
        g.remove_vertex("A")
        assert g.edge_count() == 0
        assert sorted(g.get_vertices()) == ["B", "C", "D"]

    def test_remove_vertex_reduces_degree_of_neighbors(self):
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("A", "C")
        g.remove_vertex("A")
        assert g.degree("B") == 0

    def test_clear_empty_graph(self, empty_graph):
        empty_graph.clear()
        assert empty_graph.is_empty()

    def test_copy_independence(self):
        g = Graph()
        g.add_edge("A", "B", weight=2.0)
        g2 = g.copy()
        g2.set_weight("A", "B", 99.0)
        assert g.get_weight("A", "B") == 2.0

    def test_has_edge_both_directions_undirected(self):
        g = Graph()
        g.add_edge("A", "B")
        assert g.has_edge("A", "B")
        assert g.has_edge("B", "A")

    def test_has_edge_directed_only_one_way(self):
        g = Graph(directed=True)
        g.add_edge("A", "B")
        assert g.has_edge("A", "B")
        assert not g.has_edge("B", "A")

    def test_add_edge_auto_creates_vertices(self):
        g = Graph()
        g.add_edge("A", "B")
        assert g.has_vertex("A")
        assert g.has_vertex("B")

    def test_self_loop_undirected(self):
        g = Graph()
        g.add_edge("A", "A")
        assert g.has_edge("A", "A")
        assert g.edge_count() == 1
        assert g.degree("A") == 1

    def test_self_loop_directed(self):
        g = DirectedGraph()
        g.add_edge("A", "A")
        assert g.has_edge("A", "A")
        assert g.edge_count() == 1
        assert g.out_degree("A") == 1
        assert g.in_degree("A") == 1

    def test_self_loop_removal(self):
        g = Graph()
        g.add_edge("A", "A")
        g.remove_edge("A", "A")
        assert not g.has_edge("A", "A")
        assert g.edge_count() == 0

    def test_multiple_edges_same_vertices(self):
        g = Graph()
        g.add_edge("A", "B", weight=1.0)
        g.add_edge("A", "B", weight=2.0)
        assert g.get_weight("A", "B") == 2.0
        assert g.edge_count() == 1

    def test_remove_nonexistent_vertex_from_empty(self, empty_graph):
        with pytest.raises(VertexNotFoundError):
            empty_graph.remove_vertex("X")

    def test_repr_empty(self, empty_graph):
        r = repr(empty_graph)
        assert "Graph" in r

    def test_repr_with_edges(self, single_edge_graph):
        r = repr(single_edge_graph)
        assert "Graph" in r

    def test_iter_empty(self, empty_graph):
        assert list(iter(empty_graph)) == []

    def test_contains_empty(self, empty_graph):
        assert "A" not in empty_graph


# ======================================================================
# DirectedGraph edge cases
# ======================================================================


class TestDirectedGraphEdgeCases:
    def test_in_degree_nonexistent(self):
        dg = DirectedGraph()
        with pytest.raises(VertexNotFoundError):
            dg.in_degree("X")

    def test_out_degree_nonexistent(self):
        dg = DirectedGraph()
        with pytest.raises(VertexNotFoundError):
            dg.out_degree("X")

    def test_sources_multiple(self):
        dg = DirectedGraph()
        dg.add_edge("A", "C")
        dg.add_edge("B", "C")
        sources = dg.sources()
        assert sorted(sources) == ["A", "B"]

    def test_sources_cycle(self):
        dg = DirectedGraph()
        dg.add_edge("A", "B")
        dg.add_edge("B", "A")
        assert dg.sources() == []

    def test_sinks_multiple(self):
        dg = DirectedGraph()
        dg.add_edge("A", "B")
        dg.add_edge("A", "C")
        sinks = dg.sinks()
        assert sorted(sinks) == ["B", "C"]

    def test_sinks_cycle(self):
        dg = DirectedGraph()
        dg.add_edge("A", "B")
        dg.add_edge("B", "A")
        assert dg.sinks() == []

    def test_reverse_empty(self):
        dg = DirectedGraph()
        rev = dg.reverse()
        assert rev.is_directed()
        assert rev.order() == 0

    def test_reverse_preserves_vertices_without_edges(self):
        dg = DirectedGraph()
        dg.add_vertex("A")
        dg.add_vertex("B")
        rev = dg.reverse()
        assert rev.has_vertex("A")
        assert rev.has_vertex("B")

    def test_reverse_self_loop(self):
        dg = DirectedGraph()
        dg.add_edge("A", "A")
        rev = dg.reverse()
        assert rev.has_edge("A", "A")


# ======================================================================
# Traversal edge cases
# ======================================================================


class TestTraversalEdgeCases:
    def test_bfs_empty_graph(self, empty_graph):
        with pytest.raises(VertexNotFoundError):
            bfs(empty_graph, "A")

    def test_bfs_single_vertex(self, single_vertex_graph):
        assert bfs(single_vertex_graph, "A") == ["A"]

    def test_bfs_disconnected(self, disconnected_graph):
        result = bfs(disconnected_graph, "A")
        assert set(result) == {"A", "B"}

    def test_dfs_empty_graph(self, empty_graph):
        with pytest.raises(VertexNotFoundError):
            dfs(empty_graph, "A")

    def test_dfs_single_vertex(self, single_vertex_graph):
        assert dfs(single_vertex_graph, "A") == ["A"]

    def test_dfs_disconnected(self, disconnected_graph):
        result = dfs(disconnected_graph, "A")
        assert set(result) == {"A", "B"}

    def test_bfs_paths_no_path(self, disconnected_graph):
        result = list(bfs_paths(disconnected_graph, "A", "C"))
        assert result == []

    def test_bfs_paths_same_vertex(self, single_vertex_graph):
        result = list(bfs_paths(single_vertex_graph, "A", "A"))
        assert result == [["A"]]

    def test_bfs_paths_same_vertex_with_self_loop(self):
        g = Graph()
        g.add_edge("A", "A")
        paths = list(bfs_paths(g, "A", "A"))
        assert len(paths) >= 1

    def test_dfs_paths_no_path(self, disconnected_graph):
        result = list(dfs_paths(disconnected_graph, "A", "C"))
        assert result == []

    def test_bfs_paths_source_does_not_exist(self, empty_graph):
        with pytest.raises(VertexNotFoundError):
            list(bfs_paths(empty_graph, "X", "Y"))

    def test_dfs_paths_source_does_not_exist(self, empty_graph):
        with pytest.raises(VertexNotFoundError):
            list(dfs_paths(empty_graph, "X", "Y"))

    def test_bfs_paths_target_does_not_exist(self, single_vertex_graph):
        result = list(bfs_paths(single_vertex_graph, "A", "X"))
        assert result == []

    def test_dfs_paths_target_does_not_exist(self, single_vertex_graph):
        result = list(dfs_paths(single_vertex_graph, "A", "X"))
        assert result == []

    def test_bfs_paths_shortest_path_length(self):
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("B", "D")
        g.add_edge("A", "C")
        g.add_edge("C", "D")
        paths = list(bfs_paths(g, "A", "D"))
        assert all(len(p) == 3 for p in paths)

    def test_dfs_paths_on_line(self, line_graph):
        paths = list(dfs_paths(line_graph, 1, 5))
        assert all(p[0] == 1 for p in paths)
        assert all(p[-1] == 5 for p in paths)


# ======================================================================
# Shortest path edge cases + known bugs
# ======================================================================


class TestShortestPathEdgeCases:
    def test_dijkstra_single_vertex(self, single_vertex_graph):
        dist, pred = dijkstra(single_vertex_graph, "A")
        assert dist["A"] == 0.0
        assert pred["A"] is None

    def test_dijkstra_disconnected(self, disconnected_graph):
        dist, pred = dijkstra(disconnected_graph, "A")
        assert dist["C"] == math.inf
        assert dist["D"] == math.inf
        assert dist["E"] == math.inf

    def test_dijkstra_non_existent_start(self, empty_graph):
        with pytest.raises(VertexNotFoundError):
            dijkstra(empty_graph, "X")

    def test_bellman_ford_single_vertex(self, single_vertex_graph):
        dist, pred = bellman_ford(single_vertex_graph, "A")
        assert dist["A"] == 0.0

    def test_bellman_ford_non_existent_start(self, empty_graph):
        with pytest.raises(VertexNotFoundError):
            bellman_ford(empty_graph, "X")

    def test_bellman_ford_undirected_both_directions(self):
        g = Graph()
        g.add_edge("A", "B", weight=1.0)
        g.add_edge("B", "C", weight=2.0)
        dist, _ = bellman_ford(g, "A")
        assert dist["A"] == 0.0
        assert dist["B"] == 1.0
        assert dist["C"] == 3.0

    def test_floyd_warshall_single_vertex(self, single_vertex_graph):
        dist, _ = floyd_warshall(single_vertex_graph)
        assert dist["A"]["A"] == 0.0

    def test_floyd_warshall_empty(self, empty_graph):
        dist, _ = floyd_warshall(empty_graph)
        assert dist == {}

    def test_floyd_warshall_undirected_both_directions(self):
        g = Graph()
        g.add_edge("A", "B", weight=1.0)
        g.add_edge("B", "C", weight=2.0)
        dist, _ = floyd_warshall(g)
        assert dist["A"]["B"] == 1.0
        assert dist["B"]["A"] == 1.0
        assert dist["A"]["C"] == 3.0
        assert dist["C"]["A"] == 3.0

    def test_reconstruct_path_same_vertex(self):
        g = Graph()
        g.add_edge("A", "B")
        _, pred = dijkstra(g, "A")
        path = reconstruct_path(pred, "A", "A")
        assert path == ["A"]

    def test_reconstruct_path_no_path(self, disconnected_graph):
        _, pred = dijkstra(disconnected_graph, "A")
        with pytest.raises(NoPathError):
            reconstruct_path(pred, "A", "C")

    def test_reconstruct_path_target_not_in_pred(self):
        g = Graph()
        g.add_vertex("A")
        g.add_vertex("B")
        _, pred = dijkstra(g, "A")
        with pytest.raises(NoPathError):
            reconstruct_path(pred, "A", "B")

    def test_bellman_ford_negative_weights_no_cycle(self):
        g = Graph(directed=True)
        g.add_edge("A", "B", weight=5.0)
        g.add_edge("B", "C", weight=-3.0)
        g.add_edge("A", "C", weight=4.0)
        dist, _ = bellman_ford(g, "A")
        assert dist["C"] == 2.0

    def test_negative_edge_weight_dijkstra(self):
        g = Graph(directed=True)
        g.add_edge("A", "B", weight=1.0)
        g.add_edge("B", "C", weight=-2.0)
        g.add_edge("A", "C", weight=10.0)
        dist, _ = dijkstra(g, "A")
        assert dist["C"] == -1.0

    def test_bellman_ford_all_zero_weights(self):
        g = Graph(directed=True)
        g.add_edge("A", "B", weight=0.0)
        g.add_edge("B", "C", weight=0.0)
        g.add_edge("C", "D", weight=0.0)
        dist, _ = bellman_ford(g, "A")
        assert all(v == 0.0 for v in dist.values())

    def test_bellman_ford_isolated_vertex(self):
        g = Graph(directed=True)
        g.add_edge("A", "B", weight=1.0)
        g.add_vertex("C")
        dist, _ = bellman_ford(g, "A")
        assert dist["C"] == math.inf

    def test_floyd_warshall_negative_weights_no_cycle(self):
        g = Graph(directed=True)
        g.add_edge("A", "B", weight=1.0)
        g.add_edge("B", "C", weight=-2.0)
        g.add_edge("A", "C", weight=5.0)
        dist, _ = floyd_warshall(g)
        assert dist["A"]["C"] == -1.0

    def test_floyd_warshall_isolated_vertex_inf(self):
        g = Graph(directed=True)
        g.add_edge("A", "B", weight=1.0)
        g.add_vertex("C")
        dist, _ = floyd_warshall(g)
        assert dist["C"]["A"] == math.inf
        assert dist["A"]["C"] == math.inf
        assert dist["C"]["C"] == 0.0


# ======================================================================
# MST edge cases
# ======================================================================


class TestMSTEdgeCases:
    def test_kruskal_single_vertex(self, single_vertex_graph):
        mst = kruskal(single_vertex_graph)
        assert mst == []

    def test_prim_single_vertex(self, single_vertex_graph):
        mst = prim(single_vertex_graph)
        assert mst == []

    def test_kruskal_two_vertices(self):
        g = Graph()
        g.add_edge("A", "B", weight=5.0)
        mst = kruskal(g)
        assert len(mst) == 1
        assert sum(w for _, _, w in mst) == 5.0

    def test_prim_two_vertices(self):
        g = Graph()
        g.add_edge("A", "B", weight=5.0)
        mst = prim(g)
        assert len(mst) == 1
        assert sum(w for _, _, w in mst) == 5.0

    def test_kruskal_disconnected(self, disconnected_graph):
        mst = kruskal(disconnected_graph)
        assert len(mst) == 2

    def test_prim_disconnected(self, disconnected_graph):
        mst = prim(disconnected_graph)
        assert len(mst) == 1

    def test_kruskal_all_equal_weights(self):
        g = Graph()
        g.add_edge("A", "B", weight=1.0)
        g.add_edge("B", "C", weight=1.0)
        g.add_edge("C", "A", weight=1.0)
        mst = kruskal(g)
        assert len(mst) == 2
        assert sum(w for _, _, w in mst) == 2.0

    def test_prim_all_equal_weights(self):
        g = Graph()
        g.add_edge("A", "B", weight=1.0)
        g.add_edge("B", "C", weight=1.0)
        g.add_edge("C", "A", weight=1.0)
        mst = prim(g)
        assert len(mst) == 2
        assert abs(sum(w for _, _, w in mst) - 2.0) < 1e-9

    def test_kruskal_line(self, line_graph):
        mst = kruskal(line_graph)
        assert len(mst) == 4
        total = sum(w for _, _, w in mst)
        assert total == pytest.approx(1.0 + 2.0 + 3.0 + 4.0)

    def test_prim_line(self, line_graph):
        mst = prim(line_graph)
        assert len(mst) == 4
        total = sum(w for _, _, w in mst)
        assert total == pytest.approx(1.0 + 2.0 + 3.0 + 4.0)

    def test_kruskal_and_prim_agree(self, triangle_graph):
        k = kruskal(triangle_graph)
        p = prim(triangle_graph)
        assert len(k) == len(p)
        assert sum(w for _, _, w in k) == pytest.approx(sum(w for _, _, w in p))


# ======================================================================
# Connectivity edge cases
# ======================================================================


class TestConnectivityEdgeCases:
    def test_connected_components_empty(self, empty_graph):
        assert connected_components(empty_graph) == []

    def test_connected_components_single(self, single_vertex_graph):
        comps = connected_components(single_vertex_graph)
        assert len(comps) == 1
        assert comps[0] == ["A"]

    def test_is_connected_empty(self, empty_graph):
        assert is_connected(empty_graph)

    def test_is_connected_single(self, single_vertex_graph):
        assert is_connected(single_vertex_graph)

    def test_is_bipartite_empty(self, empty_graph):
        assert is_bipartite(empty_graph)

    def test_is_bipartite_single(self, single_vertex_graph):
        assert is_bipartite(single_vertex_graph)

    def test_is_bipartite_self_loop(self):
        g = Graph()
        g.add_edge("A", "A")
        assert not is_bipartite(g)

    def test_is_bipartite_line_even(self):
        g = Graph()
        g.add_edge(1, 2)
        g.add_edge(2, 3)
        g.add_edge(3, 4)
        assert is_bipartite(g)

    def test_is_bipartite_line_odd(self):
        g = Graph()
        g.add_edge(1, 2)
        g.add_edge(2, 3)
        assert is_bipartite(g)

    def test_has_cycle_empty(self, empty_graph):
        assert not has_cycle(empty_graph)

    def test_has_cycle_single(self, single_vertex_graph):
        assert not has_cycle(single_vertex_graph)

    def test_has_cycle_self_loop(self):
        g = Graph()
        g.add_edge("A", "A")
        assert has_cycle(g)

    def test_has_cycle_directed_empty(self, empty_graph):
        assert not has_cycle_directed(empty_graph)

    def test_has_cycle_directed_single(self, single_vertex_graph):
        assert not has_cycle_directed(single_vertex_graph)

    def test_has_cycle_directed_self_loop(self):
        g = Graph(directed=True)
        g.add_edge("A", "A")
        assert has_cycle_directed(g)

    def test_has_cycle_directed_two_vertices_no_cycle(self):
        g = Graph(directed=True)
        g.add_edge("A", "B")
        assert not has_cycle_directed(g)

    def test_has_cycle_directed_complex_dag(self):
        g = Graph(directed=True)
        g.add_edge("A", "B")
        g.add_edge("A", "C")
        g.add_edge("B", "D")
        g.add_edge("C", "D")
        assert not has_cycle_directed(g)


# ======================================================================
# Topological sort edge cases
# ======================================================================


class TestTopoSortEdgeCases:
    def test_kahn_empty(self, empty_graph):
        with pytest.raises(InvalidGraphOperationError):
            topological_sort_kahn(empty_graph)

    def test_kahn_single_vertex(self, single_vertex_graph):
        with pytest.raises(InvalidGraphOperationError):
            topological_sort_kahn(single_vertex_graph)

    def test_kahn_disconnected_dag(self):
        g = Graph(directed=True)
        g.add_edge("A", "B")
        g.add_edge("C", "D")
        order = topological_sort_kahn(g)
        assert order.index("A") < order.index("B")
        assert order.index("C") < order.index("D")

    def test_kahn_two_vertices(self):
        g = Graph(directed=True)
        g.add_edge("A", "B")
        order = topological_sort_kahn(g)
        assert order == ["A", "B"]

    def test_dfs_sort_empty(self, empty_graph):
        with pytest.raises(InvalidGraphOperationError):
            topological_sort_dfs(empty_graph)

    def test_dfs_sort_single_vertex(self, single_vertex_graph):
        with pytest.raises(InvalidGraphOperationError):
            topological_sort_dfs(single_vertex_graph)

    def test_kahn_and_dfs_agree(self):
        g = Graph(directed=True)
        g.add_edge("A", "B")
        g.add_edge("A", "C")
        g.add_edge("B", "D")
        g.add_edge("C", "D")
        g.add_edge("D", "E")
        kahn = topological_sort_kahn(g)
        dfs_order = topological_sort_dfs(g)
        assert len(kahn) == len(dfs_order)
        assert set(kahn) == set(dfs_order)

    def test_kahn_large_dag(self):
        n = 100
        g = Graph(directed=True)
        for i in range(n - 1):
            g.add_edge(i, i + 1)
        order = topological_sort_kahn(g)
        assert len(order) == n

    def test_dfs_large_dag(self):
        n = 100
        g = Graph(directed=True)
        for i in range(n - 1):
            g.add_edge(i, i + 1)
        order = topological_sort_dfs(g)
        assert len(order) == n


# ======================================================================
# SCC edge cases
# ======================================================================


class TestSCCEdgeCases:
    def test_kosaraju_empty(self, empty_graph):
        with pytest.raises(InvalidGraphOperationError):
            kosaraju(empty_graph)

    def test_kosaraju_single_vertex_no_cycle(self):
        dg = DirectedGraph()
        dg.add_vertex("A")
        sccs = kosaraju(dg)
        assert len(sccs) == 1

    def test_kosaraju_two_vertices_no_edge(self):
        dg = DirectedGraph()
        dg.add_vertex("A")
        dg.add_vertex("B")
        sccs = kosaraju(dg)
        assert len(sccs) == 2

    def test_kosaraju_dag(self):
        dg = DirectedGraph()
        dg.add_edge("A", "B")
        dg.add_edge("B", "C")
        sccs = kosaraju(dg)
        assert len(sccs) == 3

    def test_tarjan_empty(self, empty_graph):
        with pytest.raises(InvalidGraphOperationError):
            tarjan(empty_graph)

    def test_tarjan_single_vertex_no_cycle(self):
        dg = DirectedGraph()
        dg.add_vertex("A")
        sccs = tarjan(dg)
        assert len(sccs) == 1

    def test_tarjan_two_vertices_no_edge(self):
        dg = DirectedGraph()
        dg.add_vertex("A")
        dg.add_vertex("B")
        sccs = tarjan(dg)
        assert len(sccs) == 2

    def test_tarjan_dag(self):
        dg = DirectedGraph()
        dg.add_edge("A", "B")
        dg.add_edge("B", "C")
        sccs = tarjan(dg)
        assert len(sccs) == 3

    def test_kosaraju_and_tarjan_agree_simple(self):
        dg = DirectedGraph()
        dg.add_edge("A", "B")
        dg.add_edge("B", "A")
        dg.add_edge("C", "D")
        dg.add_edge("D", "E")
        dg.add_edge("E", "D")
        k = kosaraju(dg)
        t = tarjan(dg)
        assert len(k) == len(t)

    def test_kosaraju_larger_scc(self):
        dg = DirectedGraph()
        dg.add_edge(1, 2)
        dg.add_edge(2, 3)
        dg.add_edge(3, 1)
        dg.add_edge(3, 4)
        dg.add_edge(4, 5)
        dg.add_edge(5, 6)
        dg.add_edge(6, 4)
        sccs = kosaraju(dg)
        assert len(sccs) == 2


# ======================================================================
# Visualization edge cases
# ======================================================================


class TestVisualizationEdgeCases:
    def test_visualize_single_vertex(self, single_vertex_graph):
        result = visualize(single_vertex_graph)
        assert isinstance(result, str)
        assert "A" in result

    def test_visualize_directed(self):
        g = Graph(directed=True)
        g.add_edge("A", "B")
        result = visualize(g)
        assert "->" in result

    def test_adjacency_matrix_empty(self, empty_graph):
        result = adjacency_matrix(empty_graph)
        assert isinstance(result, str)

    def test_adjacency_matrix_single(self, single_vertex_graph):
        result = adjacency_matrix(single_vertex_graph)
        assert "A" in result

    def test_adjacency_matrix_directed(self):
        g = Graph(directed=True)
        g.add_edge("A", "B")
        g.add_edge("A", "C")
        result = adjacency_matrix(g)
        assert "A" in result
        assert "B" in result


# ======================================================================
# Property-based invariants
# ======================================================================


class TestInvariants:
    def test_handshaking_lemma_undirected(self):
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        g.add_edge("C", "D")
        g.add_edge("D", "A")
        total_degree = sum(g.degree(v) for v in g.get_vertices())
        assert total_degree == 2 * g.edge_count()

    def test_directed_degree_sum(self):
        g = DirectedGraph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        g.add_edge("A", "C")
        total_in = sum(g.in_degree(v) for v in g.get_vertices())
        total_out = sum(g.out_degree(v) for v in g.get_vertices())
        assert total_in == total_out
        assert total_in == g.edge_count()

    def test_mst_spanning_tree_property(self):
        g = Graph()
        n = 6
        for i in range(1, n):
            g.add_edge(i, i + 1, weight=float(i))
        g.add_edge(1, 3, weight=0.5)
        g.add_edge(3, 5, weight=0.5)
        mst = kruskal(g)
        assert len(mst) == n - 1

    def test_mst_cycle_property(self, triangle_graph):
        mst = kruskal(triangle_graph)
        edges_set = set()
        for u, v, w in mst:
            edges_set.add((u, v) if u <= v else (v, u))
        assert len(edges_set) == 2

    def test_shortest_path_triangle_inequality(self):
        g = Graph()
        g.add_edge("A", "B", weight=3.0)
        g.add_edge("B", "C", weight=4.0)
        g.add_edge("A", "C", weight=12.0)
        dist, _ = floyd_warshall(g)
        d_ab = dist["A"]["B"]
        d_bc = dist["B"]["C"]
        d_ac = dist["A"]["C"]
        assert d_ac <= d_ab + d_bc + 1e-9

    def test_bipartite_coloring(self):
        g = Graph()
        g.add_edge(1, 2)
        g.add_edge(2, 3)
        g.add_edge(3, 4)
        g.add_edge(4, 5)
        g.add_edge(5, 6)
        assert is_bipartite(g)

    def test_scc_decomposition_partition(self):
        dg = DirectedGraph()
        dg.add_edge(1, 2)
        dg.add_edge(2, 1)
        dg.add_edge(2, 3)
        dg.add_edge(3, 2)
        dg.add_edge(4, 5)
        sccs = kosaraju(dg)
        all_vertices = set()
        for comp in sccs:
            for v in comp:
                assert v not in all_vertices
                all_vertices.add(v)
        assert all_vertices == set(dg.get_vertices())

    def test_dijkstra_non_negative_invariant(self):
        g = Graph()
        g.add_edge("A", "B", weight=2.0)
        g.add_edge("B", "C", weight=3.0)
        g.add_edge("A", "C", weight=10.0)
        dist, _ = dijkstra(g, "A")
        for v, d in dist.items():
            if v == "A":
                assert d == 0.0
            else:
                assert d >= 0.0

    def test_connected_components_union(self):
        n = 10
        g = Graph()
        for i in range(n):
            g.add_vertex(i)
        for i in range(0, n - 1, 2):
            g.add_edge(i, i + 1)
        comps = connected_components(g)
        union = set()
        for c in comps:
            union.update(c)
        assert union == set(range(n))

    def test_topo_order_validity(self):
        g = Graph(directed=True)
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        g.add_edge("A", "D")
        g.add_edge("D", "C")
        order = topological_sort_kahn(g)
        pos = {v: i for i, v in enumerate(order)}
        assert pos["A"] < pos["B"]
        assert pos["B"] < pos["C"]
        assert pos["A"] < pos["D"]
        assert pos["D"] < pos["C"]

    def test_reverse_graph_edges_invariant(self):
        dg = DirectedGraph()
        dg.add_edge("A", "B")
        dg.add_edge("B", "C")
        dg.add_edge("C", "A")
        rev = dg.reverse()
        for u in dg.get_vertices():
            for v in dg.get_vertices():
                if u == v:
                    continue
                assert dg.has_edge(u, v) == rev.has_edge(v, u)

    def test_self_loop_degree_invariant(self):
        g = Graph()
        g.add_edge("A", "A")
        assert g.degree("A") == 1


# ======================================================================
# Stress tests
# ======================================================================


class TestStress:
    LARGE = 500
    MEDIUM = 200

    def test_bfs_large_graph(self):
        g = Graph()
        n = self.LARGE
        for i in range(n - 1):
            g.add_edge(i, i + 1)
        result = bfs(g, 0)
        assert len(result) == n

    def test_dfs_large_graph(self):
        g = Graph()
        n = self.LARGE
        for i in range(n - 1):
            g.add_edge(i, i + 1)
        result = dfs(g, 0)
        assert len(result) == n

    def test_dijkstra_large(self):
        g = Graph()
        n = self.MEDIUM
        for i in range(n - 1):
            g.add_edge(i, i + 1, weight=1.0)
        dist, _ = dijkstra(g, 0)
        assert dist[n - 1] == n - 1

    def test_bellman_ford_large(self):
        g = Graph(directed=True)
        n = self.MEDIUM
        for i in range(n - 1):
            g.add_edge(i, i + 1, weight=1.0)
        dist, _ = bellman_ford(g, 0)
        assert dist[n - 1] == n - 1

    def test_floyd_warshall_medium(self):
        g = Graph()
        n = 50
        for i in range(n - 1):
            g.add_edge(i, i + 1, weight=1.0)
        dist, _ = floyd_warshall(g)
        assert dist[0][n - 1] == n - 1

    def test_kruskal_large(self):
        g = Graph()
        n = self.MEDIUM
        for i in range(n - 1):
            g.add_edge(i, i + 1, weight=float(i % 10 + 1))
        mst = kruskal(g)
        assert len(mst) == n - 1

    def test_prim_large(self):
        g = Graph()
        n = self.MEDIUM
        for i in range(n - 1):
            g.add_edge(i, i + 1, weight=float(i % 10 + 1))
        mst = prim(g)
        assert len(mst) == n - 1

    def test_connected_components_large(self):
        g = Graph()
        n = self.LARGE
        for i in range(0, n, 2):
            if i + 1 < n:
                g.add_edge(i, i + 1)
        comps = connected_components(g)
        assert len(comps) <= n

    def test_kosaraju_large(self):
        dg = DirectedGraph()
        n = self.MEDIUM
        for i in range(n - 1):
            dg.add_edge(i, i + 1)
        sccs = kosaraju(dg)
        assert len(sccs) == n

    def test_tarjan_large(self):
        dg = DirectedGraph()
        n = self.MEDIUM
        for i in range(n - 1):
            dg.add_edge(i, i + 1)
        sccs = tarjan(dg)
        assert len(sccs) == n

    def test_dense_graph_copy(self):
        g = Graph()
        n = 100
        for i in range(n):
            for j in range(i + 1, n):
                g.add_edge(i, j, weight=1.0)
        g2 = g.copy()
        assert g2.order() == n
        assert g2.edge_count() == g.edge_count()

    def test_stress_self_loops(self):
        g = Graph()
        n = self.MEDIUM
        for i in range(n):
            g.add_edge(i, i)
        assert g.edge_count() == n
        for i in range(n):
            assert g.has_edge(i, i)
        for i in range(n):
            g.remove_edge(i, i)
        assert g.edge_count() == 0


# ======================================================================
# Thread-safety tests
# ======================================================================


class TestThreadSafety:
    def test_concurrent_reads(self):
        g = Graph()
        n = 100
        for i in range(n - 1):
            g.add_edge(i, i + 1, weight=1.0)

        def read_ops():
            for _ in range(50):
                _ = g.order()
                _ = g.edge_count()
                for v in range(n):
                    _ = g.degree(v)
                    _ = g.has_vertex(v)
                for v in range(n - 1):
                    _ = g.has_edge(v, v + 1)
                    _ = g.get_weight(v, v + 1)

        threads = [threading.Thread(target=read_ops) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    def test_concurrent_writes_same_vertex(self):
        g = Graph()

        def add_vertex(v):
            for _ in range(10):
                g.add_vertex(v)

        threads = [threading.Thread(target=add_vertex, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert g.order() == 10

    def test_concurrent_add_edge(self):
        g = Graph()
        n = 50

        def add_edges(start):
            for i in range(start, start + 10):
                for j in range(i + 1, n):
                    g.add_edge(i, j, weight=1.0)

        threads = [threading.Thread(target=add_edges, args=(i,)) for i in range(0, n, 10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    def test_concurrent_read_write(self):
        g = Graph()
        g.add_vertex("X")

        def writer():
            for i in range(100):
                g.add_vertex(i)
                g.add_edge(i, "X", weight=1.0)

        def reader():
            for _ in range(100):
                _ = g.has_vertex("X")
                _ = g.degree("X")

        threads = []
        for _ in range(4):
            threads.append(threading.Thread(target=writer))
            threads.append(threading.Thread(target=reader))
        for t in threads:
            t.start()
        for t in threads:
            t.join()


# ======================================================================
# Cross-validation between algorithms
# ======================================================================


class TestCrossValidation:
    def test_dijkstra_vs_bellman_ford(self):
        g = Graph()
        g.add_edge("A", "B", weight=2.0)
        g.add_edge("B", "C", weight=3.0)
        g.add_edge("A", "C", weight=6.0)
        d1, _ = dijkstra(g, "A")
        d2, _ = bellman_ford(g, "A")
        for v in g.get_vertices():
            assert d1[v] == pytest.approx(d2[v])

    def test_bellman_ford_vs_floyd_warshall(self):
        g = Graph(directed=True)
        g.add_edge("A", "B", weight=1.0)
        g.add_edge("B", "C", weight=2.0)
        g.add_edge("A", "C", weight=4.0)
        d1, _ = bellman_ford(g, "A")
        d2, _ = floyd_warshall(g)
        for v in g.get_vertices():
            assert d1[v] == pytest.approx(d2["A"][v])

    def test_kruskal_vs_prim_weight(self, triangle_graph):
        k = kruskal(triangle_graph)
        p = prim(triangle_graph)
        kw = sum(w for _, _, w in k)
        pw = sum(w for _, _, w in p)
        assert kw == pytest.approx(pw)

    def test_kosaraju_vs_tarjan_simple(self):
        dg = DirectedGraph()
        dg.add_edge(1, 2)
        dg.add_edge(2, 3)
        dg.add_edge(3, 1)
        dg.add_edge(3, 4)
        dg.add_edge(4, 5)
        dg.add_edge(5, 4)
        k = kosaraju(dg)
        t = tarjan(dg)
        assert len(k) == len(t)

    def test_bfs_shortest_path_unweighted(self):
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("B", "D")
        g.add_edge("A", "C")
        g.add_edge("C", "D")
        g.add_edge("D", "E")
        paths = list(bfs_paths(g, "A", "E"))
        min_len = min(len(p) for p in paths)
        assert min_len == 4

    def test_connected_components_self_loop(self):
        g = Graph()
        g.add_edge("A", "A")
        g.add_vertex("B")
        comps = connected_components(g)
        assert len(comps) == 2

    def test_connectivity_after_removal(self):
        g = Graph()
        g.add_edge("A", "B")
        g.add_edge("B", "C")
        g.add_edge("C", "D")
        assert is_connected(g)
        g.remove_vertex("B")
        assert not is_connected(g)

    def test_dijkstra_vs_bellman_ford_complex(self):
        g = Graph(directed=True)
        edges = [
            ("A", "B", 4.0),
            ("A", "C", 2.0),
            ("B", "C", 1.0),
            ("B", "D", 5.0),
            ("C", "D", 8.0),
            ("C", "E", 10.0),
            ("D", "E", 2.0),
            ("D", "F", 6.0),
            ("E", "F", 3.0),
        ]
        for u, v, w in edges:
            g.add_edge(u, v, w)
        d1, _ = dijkstra(g, "A")
        d2, _ = bellman_ford(g, "A")
        for v in g.get_vertices():
            assert d1[v] == pytest.approx(d2[v])


# ======================================================================
# Bug reproduction tests
# ======================================================================


class TestBugReproduction:
    def test_undirected_bellman_ford_symmetric_path(self):
        g = Graph()
        g.add_edge("A", "B", weight=1.0)
        g.add_edge("B", "C", weight=2.0)
        dist, _ = bellman_ford(g, "A")
        assert dist["C"] == 3.0

    def test_undirected_floyd_warshall_symmetric(self):
        g = Graph()
        g.add_edge("A", "B", weight=1.0)
        g.add_edge("B", "C", weight=2.0)
        dist, _ = floyd_warshall(g)
        assert dist["A"]["C"] == 3.0

    def test_dijkstra_negative_weight_no_crash(self):
        g = Graph(directed=True)
        g.add_edge("A", "B", weight=5.0)
        g.add_edge("B", "C", weight=-3.0)
        dist, _ = dijkstra(g, "A")
        assert dist["C"] == 2.0

    def test_prim_single_node_no_crash(self):
        g = Graph()
        g.add_vertex("A")
        mst = prim(g)
        assert mst == []

    def test_kruskal_single_node_no_crash(self):
        g = Graph()
        g.add_vertex("A")
        mst = kruskal(g)
        assert mst == []

    def test_get_edges_on_custom_vertex_types(self):
        class Custom:
            def __init__(self, name):
                self.name = name

            def __repr__(self):
                return self.name

            def __eq__(self, other):
                return isinstance(other, Custom) and self.name == other.name

            def __hash__(self):
                return hash(self.name)

        g = Graph()
        a = Custom("A")
        b = Custom("B")
        g.add_edge(a, b, weight=1.0)
        edges = g.get_edges()
        assert len(edges) == 1
        u, v, w = edges[0]
        assert w == 1.0
        assert (u is a and v is b) or (u is b and v is a)

    def test_dfs_paths_deep_graph(self):
        n = 200
        g = Graph()
        for i in range(n - 1):
            g.add_edge(i, i + 1)
        paths = list(dfs_paths(g, 0, n - 1))
        assert len(paths) >= 1

    def test_self_loop_connected_component(self):
        g = Graph()
        g.add_edge("A", "A")
        g.add_edge("A", "B")
        comps = connected_components(g)
        assert len(comps) == 1

    def test_directed_star_graph_bellman_ford(self):
        g = Graph(directed=True)
        g.add_edge("CENTER", "A", weight=1.0)
        g.add_edge("CENTER", "B", weight=2.0)
        g.add_edge("CENTER", "C", weight=3.0)
        g.add_edge("CENTER", "D", weight=4.0)
        dist, _ = bellman_ford(g, "CENTER")
        assert dist["A"] == 1.0
        assert dist["B"] == 2.0
        assert dist["C"] == 3.0
        assert dist["D"] == 4.0

    def test_large_negative_cycle_detection(self):
        g = Graph(directed=True)
        n = 50
        for i in range(n):
            g.add_edge(i, (i + 1) % n, weight=-1.0)
        with pytest.raises(NegativeCycleError):
            bellman_ford(g, 0)

    def test_negative_edge_bellman_ford_but_no_cycle(self):
        g = Graph(directed=True)
        g.add_edge("S", "A", weight=10.0)
        g.add_edge("S", "B", weight=5.0)
        g.add_edge("A", "C", weight=-8.0)
        g.add_edge("B", "C", weight=2.0)
        dist, _ = bellman_ford(g, "S")
        assert dist["C"] == 2.0

    def test_bellman_ford_undirected_negative_edge_cycle(self):
        g = Graph()
        g.add_edge("A", "B", weight=5.0)
        g.add_edge("B", "C", weight=-2.0)
        g.add_edge("A", "C", weight=10.0)
        with pytest.raises(NegativeCycleError):
            bellman_ford(g, "A")

    def test_floyd_warshall_undirected_negative_edge_cycle(self):
        g = Graph()
        g.add_edge("A", "B", weight=5.0)
        g.add_edge("B", "C", weight=-2.0)
        g.add_edge("A", "C", weight=10.0)
        with pytest.raises(NegativeCycleError):
            floyd_warshall(g)
