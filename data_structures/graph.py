"""Graph implementation with a KV adjacency map."""

from collections import defaultdict
from typing import Hashable, Iterable, Iterator, List, Optional, Tuple


_MISSING = object()


class AdjacencyMap(defaultdict):
    """Dict-like adjacency store: ``nodes[cur]`` / ``nodes.get(cur)`` → neighbors.

    Like ``defaultdict(list)``, missing keys materialize an empty neighbor list
    on ``[]`` access. ``get(cur)`` with no default returns an empty list without
    inserting the key. An explicit ``default`` (including ``None``) is honored,
    matching the stdlib ``dict.get`` contract.
    """

    def __init__(self):
        super().__init__(list)

    def get(self, key, default=_MISSING):
        if key in self:
            return self[key]
        if default is _MISSING:
            return self.default_factory()
        return default


class Graph:
    """General-purpose adjacency-list graph.

    - ``g.size`` — number of vertices
    - ``g.nodes[cur]`` — neighbors of ``cur``
    - ``g.nodes.get(cur)`` — same lookup with a safe empty default

    ``nodes`` is a key→neighbors map (``cur: [neighbors...]``), backed by a
    defaultdict-style ``AdjacencyMap``.
    """

    def __init__(
        self,
        n: Optional[int] = None,
        edges: Optional[Iterable[Tuple[Hashable, Hashable]]] = None,
        *,
        directed: bool = True,
    ):
        self.nodes: AdjacencyMap = AdjacencyMap()
        self.directed = directed
        self._size = 0

        if n is not None:
            if n < 0:
                raise ValueError("n must be non-negative")
            for i in range(n):
                # Pre-register integer vertices 0..n-1.
                _ = self.nodes[i]
            self._size = n

        if edges is not None:
            for u, v in edges:
                self.add_edge(u, v)

    @property
    def size(self) -> int:
        "Number of vertices in the graph."
        return self._size

    def add_node(self, node: Hashable) -> None:
        "Ensure ``node`` exists in the adjacency map."
        if node not in self.nodes:
            self.nodes[node] = []
            self._size += 1

    def add_edge(self, start: Hashable, end: Hashable) -> None:
        "Add an edge ``start → end`` (and the reverse when undirected)."
        self.add_node(start)
        self.add_node(end)
        self.nodes[start].append(end)
        if not self.directed:
            self.nodes[end].append(start)

    def neighbors(self, node: Hashable) -> List[Hashable]:
        "Return the neighbor list for ``node`` (empty if unknown)."
        return self.nodes.get(node)

    def __contains__(self, node: Hashable) -> bool:
        return node in self.nodes

    def __len__(self) -> int:
        return self.size

    def __iter__(self) -> Iterator[Hashable]:
        return iter(self.nodes)

    def __repr__(self) -> str:
        kind = "directed" if self.directed else "undirected"
        return f"Graph({kind}, size={self.size}, nodes={dict(self.nodes)})"
