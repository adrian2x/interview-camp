import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data_structures.graph import Graph
from algorithms.graphs import bfs, cfs, dfs
from collections import deque


def test_bfs_and_dfs_reachability():
    # 0 → 1 → 2 → 3, plus a dead branch 0 → 4
    g = Graph(n=5, edges=[(0, 1), (1, 2), (2, 3), (0, 4)], directed=True)

    assert bfs(g, 0, 3) is True
    assert dfs(g, 0, 3) is True
    assert bfs(g, 4, 3) is False
    assert dfs(g, 3, 0) is False
    assert bfs(g, 2, 2) is True


def test_cfs_container_choice():
    g = Graph(n=3, edges=[(0, 1), (1, 2)], directed=True)
    assert cfs(g, 0, 2, deque()) is True
    assert cfs(g, 0, 2, []) is True
    assert cfs(g, 2, 0, deque()) is False


def test_string_node_keys():
    g = Graph(edges=[("paper", "composition"), ("composition", "essay")], directed=False)
    assert g.nodes.get("paper") == ["composition"]
    assert bfs(g, "paper", "essay") is True
    assert dfs(g, "essay", "paper") is True


if __name__ == "__main__":
    test_bfs_and_dfs_reachability()
    test_cfs_container_choice()
    test_string_node_keys()
    print("cfs tests passed")
