from collections import defaultdict

from graph import AdjacencyMap, Graph


def test_nodes_is_kv_defaultdict_shape():
    g = Graph(n=3, edges=[(0, 1), (1, 2)], directed=True)

    assert isinstance(g.nodes, (AdjacencyMap, defaultdict))
    assert g.size == 3
    assert g.nodes[0] == [1]
    assert g.nodes[1] == [2]
    # get(cur) returns neighbors without requiring a default arg
    assert g.nodes.get(0) == [1]
    assert g.nodes.get(2) == []
    assert g.nodes.get(99) == []
    # get must not insert missing keys (unlike nodes[cur])
    assert 99 not in g.nodes
    assert g.size == 3


def test_cfs_style_access_pattern():
    """Mirror the tweet's loop: for next in g.nodes[cur]."""
    g = Graph(n=4, edges=[(0, 1), (0, 2), (2, 3)], directed=True)
    cur = 0
    neighbors = []
    for nxt in g.nodes[cur]:
        neighbors.append(nxt)
    assert neighbors == [1, 2]
    assert g.size == 4


def test_undirected_edges():
    g = Graph(edges=[("a", "b"), ("b", "c")], directed=False)
    assert g.size == 3
    assert "b" in g.nodes["a"]
    assert "a" in g.nodes["b"]
    assert g.nodes.get("c") == ["b"]


def test_add_node_and_edge():
    g = Graph(directed=True)
    g.add_node("s")
    g.add_edge("s", "t")
    assert g.size == 2
    assert g.nodes["s"] == ["t"]
    assert g.neighbors("t") == []


if __name__ == "__main__":
    test_nodes_is_kv_defaultdict_shape()
    test_cfs_style_access_pattern()
    test_undirected_edges()
    test_add_node_and_edge()
    print("graph tests passed")
