import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data_structures.graph import Graph
from algorithms.graphs import bfs


def test_bfs_reachability():
    g = Graph(n=5, edges=[(0, 1), (1, 2), (2, 3), (0, 4)], directed=True)

    assert bfs(g, 0, 3) is True
    assert bfs(g, 4, 3) is False
    assert bfs(g, 3, 0) is False
    assert bfs(g, 2, 2) is True


def test_bfs_string_nodes():
    g = Graph(edges=[("paper", "composition"), ("composition", "essay")], directed=False)
    assert g.nodes.get("paper") == ["composition"]
    assert bfs(g, "paper", "essay") is True


if __name__ == "__main__":
    test_bfs_reachability()
    test_bfs_string_nodes()
    print("bfs tests passed")
