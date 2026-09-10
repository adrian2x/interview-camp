"""
algorithmlib.graphs - single-shot graph algorithms.

"Functional" graphs in the sense used throughout this package: you hand the
function a graph description and it returns the answer (shortest distances,
an ordering, ...). No graph object is built that you then query and update -
that would be a data structure, which this package deliberately leaves out.

Graph representation (shared by all functions here):

    A graph is a Mapping from node label to a sequence of (neighbour, weight)
    edges. Node labels are any hashable values - ints, strings, tuples, ...
    Weights are numbers; do not write float("inf") for an absent edge - just
    leave it out of the adjacency list.

    graph = {
        "A": [("B", 4), ("C", 2)],
        "B": [("C", 1)],
        "C": [],
    }

    The adjacency lists need not be sorted, and nodes with no outgoing edges
    may be present with an empty list (all functions also cope with nodes
    that appear only as a neighbour of someone else).

The algorithms, cheapest to most expensive:

    bellman_ford      shortest paths from one source; tolerates *negative*
                      weights and detects negative cycles. O(V * E).
    dijkstra          shortest paths from one source; requires non-negative
                      weights, much faster in practice. O(E log V).
    floyd_warshall    shortest paths between *every* pair of nodes, in one
                      shot. O(V^3). Detects negative cycles too.
    topological_sort  a linear ordering where every edge points forward,
                      for directed acyclic graphs. O(V + E).

    kruskal_mst       minimum spanning tree by sorting edges and unioning
                      their endpoints (Kruskal's algorithm).
    prim_mst          minimum spanning tree grown from a start node with a
                      priority queue of frontier edges (Prim's algorithm).
    is_bipartite      check whether a graph is 2-colorable and return a
                      valid coloring (BFS).
    strongly_connected_components  partition of a digraph into mutually
                      reachable groups (Kosaraju's two-pass DFS).
    edmonds_karp      maximum s-t flow in a capacitated digraph (BFS
                      augmenting paths).

Two input flavors are used, and each function's docstring states which:

* weighted: Mapping[Node, Sequence[(neighbour, weight)]] edges - used by
  shortest paths and the MST functions (undirected there: every edge must
  appear in both directions).
* unweighted: Mapping[Node, Sequence[neighbour]] - used by topological_sort,
  is_bipartite and strongly_connected_components.
* capacities: Mapping[Node, Sequence[(neighbour, capacity)]] for flows.

Each function returns a fresh result and does not mutate its input graph.
"""

from collections import defaultdict, deque
from collections.abc import Mapping, Sequence
from heapq import heappop, heappush
from typing import Dict, Hashable, List, Optional, Tuple, TypeVar

Node = TypeVar("Node", bound=Hashable)
Number = TypeVar("Number", int, float)  # a numeric edge weight


def _expand(
    graph: Mapping[Node, Sequence[Tuple[Node, Number]]]
) -> Dict[Node, List[Tuple[Node, Number]]]:
    """
    Normalize the input graph into an adjacency dict whose keys include every
    node mentioned anywhere (sources *and* targets). Targets with no outgoing
    edges get an empty list, so distance dicts can promise an entry for every
    node and negative-cycle checks cannot miss an edge into an otherwise
    silent node.
    """
    adj: Dict[Node, List[Tuple[Node, Number]]] = defaultdict(list)
    for node, edges in graph.items():
        adj[node].extend(edges)  # keep the caller's edges as-is
        for neighbour, _weight in edges:
            adj.setdefault(neighbour, [])  # ensure the target is a key too
    return adj


def bellman_ford(
    graph: Mapping[Node, Sequence[Tuple[Node, Number]]], source: Node
) -> Dict[Node, Number]:
    """
    Return the shortest distances from source to every node in graph, or raise
    ValueError if a negative cycle is reachable from source.

    Bellman-Ford is the general shortest-path algorithm: unlike Dijkstra it
    tolerates negative edge weights, which makes it the right tool whenever
    weights may go below zero (and the tool that detects the resulting
    negative cycles, which make "shortest path" meaningless).

    The idea is *relaxation*: repeatedly try to shorten each node's distance
    by routing through a neighbour:

        if dist[u] + weight(u, v) < dist[v]:  dist[v] = dist[u] + weight(u, v)

    The key theorem: after k full passes over every edge, dist[v] is the
    shortest path using at most k edges. Any shortest path uses at most V - 1
    edges (a path that repeats a node contains a cycle, and removing a
    positive cycle only shortens it). So V - 1 passes are enough - and if a
    V-th pass still improves something, that improvement can only come from a
    negative cycle, hence the final detection pass.

    Distances to nodes unreachable from source stay float("inf"). The passes
    stop early as soon as a full pass changes nothing, which makes easy
    graphs (few edges on shortest paths) much faster than the worst case.

    Time: O(V * E).  Space: O(V).

    Example:
        >>> bellman_ford({"A": [("B", 4)], "B": [("C", -2)]}, source="A")
        {'A': 0, 'B': 4, 'C': 2}
    """
    adj = _expand(graph)
    adj.setdefault(source, [])  # isolated source: distances to itself only
    dist: Dict[Node, Number] = {node: float("inf") for node in adj}
    dist[source] = 0

    # Collect every edge once; relaxing over this flat list is a full pass.
    edges = [
        (u, v, w) for u, neighbours in adj.items() for (v, w) in neighbours
    ]

    # V - 1 full passes: after pass k, distances are optimal for paths of at
    # most k edges, and any simple path has at most V - 1 edges.
    for _ in range(len(adj) - 1):
        changed = False
        for u, v, w in edges:
            if dist[u] != float("inf") and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                changed = True
        if not changed:
            break  # nothing moved: already optimal, skip remaining passes

    # One extra pass to *detect* negative cycles reachable from source: if an
    # edge can still be relaxed, its tail must be on (or reachable from) a
    # negative cycle, which keeps producing shorter and shorter paths.
    for u, v, w in edges:
        if dist[u] != float("inf") and dist[u] + w < dist[v]:
            raise ValueError(
                f"graph contains a negative cycle reachable from {source!r}"
            )
    return dist


def dijkstra(
    graph: Mapping[Node, Sequence[Tuple[Node, Number]]], source: Node
) -> Dict[Node, Number]:
    """
    Return the shortest distances from source to every node in graph, using
    Dijkstra's algorithm. Raises ValueError if any edge weight is negative.

    Dijkstra is Bellman-Ford's fast cousin for the (very common) case of
    non-negative weights. Instead of blindly relaxing every edge V - 1 times,
    it always settles the *closest unsettled* node next:

    * The priority queue hands out the node with the smallest tentative
      distance. Because no weight is negative, that distance can never be
      improved later (any detour through other unsettled nodes would only add
      non-negative length) - so the node is *finalized* the moment it is
      popped.
    * When a node is finalized, relaxing its outgoing edges may shorten the
      tentative distances of its neighbours, which are pushed back onto the
      queue. The `if d > dist[u]: continue` guard skips stale queue entries,
      keeping the heap small without ever deleting from it.

    The "why no negative weights?" interview answer: with a negative edge, a
    node popped as closest could later be improved by a path through a node
    that is still far away - breaking the finalization argument above.

    Complexity note: the binary heap used here gives O(E log V). A Fibonacci
    heap lowers it to O(E + V log V) - the textbook optimum, rarely worth the
    constant factors in practice.

    Distances to unreachable nodes stay float("inf").

    Time: O(E log V).  Space: O(V).

    Example:
        >>> dijkstra({"A": [("B", 4), ("C", 2)], "B": [("C", 1)]}, source="A")
        {'A': 0, 'B': 4, 'C': 2}
    """
    adj = _expand(graph)
    adj.setdefault(source, [])  # isolated source: distances to itself only
    dist: Dict[Node, Number] = {node: float("inf") for node in adj}
    dist[source] = 0

    # Heap entries are (distance, ticket, node). The ticket is a running
    # counter: when two distances tie, the heap falls back to comparing
    # tickets instead of node labels, so labels never need to be orderable.
    queue: List[Tuple[Number, int, Node]] = [(0, 0, source)]
    ticket = 0

    while queue:
        d, _ticket, u = heappop(queue)
        if d > dist[u]:
            continue  # stale entry: u was improved after this one was pushed

        for v, w in adj[u]:
            if w < 0:
                raise ValueError("Dijkstra requires non-negative edge weights")
            candidate = d + w
            if candidate < dist[v]:
                dist[v] = candidate  # a shorter route to v was found
                ticket += 1
                heappush(queue, (candidate, ticket, v))
    return dist


def floyd_warshall(
    matrix: Sequence[Sequence[Number]],
) -> List[List[Number]]:
    """
    Return a new matrix of shortest distances between every pair of nodes,
    computed by the Floyd-Warshall algorithm. Raises ValueError if the graph
    contains a negative cycle.

    Input: an n x n weight matrix where matrix[u][v] is the direct edge weight
    from u to v. Absent edges are float("inf") and the diagonal is 0 (a node
    reaches itself for free) unless a self-loop says otherwise. The input
    matrix is not mutated.

    The algorithm's elegance is its recurrence. Let d_k[u][v] be the shortest
    path from u to v whose *internal* nodes are drawn only from {0..k}. Then

        d_k[u][v] = min(d_{k-1}[u][v],          # avoid node k entirely
                         d_{k-1}[u][k] + d_{k-1}[k][v])  # or pass through k

    and since the in-place update never needs yesterday's d[k][*] after node k
    has been processed, the whole thing collapses into three nested loops
    over a single matrix. Running the recurrence for k = 0..n-1 allows every
    node as an intermediate, so the final matrix holds true shortest paths.

    A negative cycle reveals itself at the end: dist[i][i] < 0 for some i
    (the cycle keeps shortening its own round trip).

    Time: O(n^3).  Space: O(n^2) for the result copy.

    Example:
        >>> floyd_warshall([[0, 3, float("inf")], [float("inf"), 0, 1],
        ...                 [float("inf"), float("inf"), 0]])
        [[0, 3, 4], [inf, 0, 1], [inf, inf, 0]]
    """
    n = len(matrix)
    # Work on a copy so the caller's matrix is untouched.
    dist = [list(row) for row in matrix]

    for k in range(n):  # allow node k as an intermediate
        row_k = dist[k]
        for i in range(n):
            row_i = dist[i]
            best_i_k = row_i[k]
            # Optimization: if i cannot reach k yet, no path through k can
            # improve i's row - skip the whole inner loop. (This is the
            # standard "only relax reachable prefixes" shortcut; it also
            # avoids pointless inf + inf arithmetic.)
            if best_i_k == float("inf"):
                continue
            for j in range(n):
                via_k = best_i_k + row_k[j]
                if via_k < row_i[j]:
                    row_i[j] = via_k

    for i in range(n):
        if dist[i][i] < 0:
            raise ValueError("graph contains a negative cycle")
    return dist


def topological_sort(
    graph: Mapping[Node, Sequence[Node]],
) -> List[Node]:
    """
    Return the nodes of the directed acyclic graph in topological order: an
    ordering where every edge (u, v) has u before v. Raises ValueError if the
    graph contains a cycle (no such ordering exists then).

    Kahn's algorithm is the queue-based formulation. The observation: in a
    DAG there is always at least one node with no incoming edges (a *source*),
    and deleting it cannot create a cycle. So:

    1. Count every node's in-degree.
    2. Seed a queue with the in-degree-0 nodes - they are ready to emit, since
       nothing must come before them.
    3. Repeatedly emit a queued node and "delete" it by decrementing the
       in-degrees of its successors; any successor whose in-degree hits 0 has
       now had all its prerequisites emitted and joins the queue.

    If the queue runs dry before every node was emitted, the leftover nodes
    all have in-degree > 0 - each waits on another leftover, which is exactly
    what a cycle looks like - so we report it.

    This is the algorithm behind build systems (make, cargo, npm) ordering
    compilation units, and behind "course prerequisite" scheduling problems.
    (An alternative formulation - reverse DFS finish order - falls out of the
    strongly connected components algorithm below, which records exactly that
    order in its first pass.)

    Time: O(V + E).  Space: O(V).

    Example:
        >>> topological_sort({"a": ["b", "c"], "b": ["d"], "c": ["d"]})
        ['a', 'b', 'c', 'd']
    """
    # In-degrees for every node that appears anywhere (sources and targets).
    in_degree: Dict[Node, int] = defaultdict(int)
    for node in graph:
        in_degree.setdefault(node, 0)
        for neighbour in graph[node]:
            in_degree[neighbour] += 1

    ready = deque(node for node, deg in in_degree.items() if deg == 0)
    ordering: List[Node] = []

    while ready:
        node = ready.popleft()
        ordering.append(node)
        # "Deleting" node removes one incoming edge from each successor.
        for neighbour in graph.get(node, ()):
            in_degree[neighbour] -= 1
            if in_degree[neighbour] == 0:
                ready.append(neighbour)  # all prerequisites are now ordered

    if len(ordering) != len(in_degree):
        raise ValueError("graph contains a cycle; no topological order exists")
    return ordering


# ---------------------------------------------------------------------------
# Minimum spanning trees
# ---------------------------------------------------------------------------


class _DSU:
    """
    Disjoint-set (union-find) helper used inside kruskal_mst. Publicly this
    package avoids data structures, but an MST *algorithm* needs one to test
    "would this edge close a cycle?" in near-constant time - so it lives here
    as a private implementation detail.

    find() follows parent pointers to the root and flattens the path on the
    way up (path compression); union() attaches the smaller tree under the
    larger one (union by rank). Together they make each operation cost
    O(alpha(n)), i.e. effectively constant.
    """

    def __init__(self, nodes: Sequence[Node]):
        self.parent: Dict[Node, Node] = {node: node for node in nodes}
        self.rank: Dict[Node, int] = {node: 0 for node in nodes}

    def find(self, node: Node) -> Node:
        # Walk to the root...
        root = node
        while self.parent[root] != root:
            root = self.parent[root]
        # ...then point everything on the way at the root directly. This
        # "path compression" makes future finds (near-)constant time.
        while self.parent[node] != root:
            next_node = self.parent[node]
            self.parent[node] = root
            node = next_node
        return root

    def union(self, a: Node, b: Node) -> bool:
        """Join the trees of a and b. Returns True if they were separate."""
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False  # already connected: adding this edge would cycle
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


def kruskal_mst(
    graph: Mapping[Node, Sequence[Tuple[Node, Number]]]
) -> List[Tuple[Node, Node, Number]]:
    """
    Return the edges (u, v, weight) of a minimum spanning tree of the
    undirected weighted graph, using Kruskal's algorithm. Raises ValueError
    if the graph is disconnected (no spanning tree exists).

    Input: undirected adjacency - every undirected edge must appear in both
    directions. Self-loops are ignored; parallel edges between the same pair
    collapse to the lightest one.

    Kruskal's rule is delightfully simple: sort all edges by weight, then
    take each edge unless it would connect two nodes that are already
    connected (which would form a cycle). The union-find structure answers
    "already connected?" in near-constant time.

    Why it is optimal (cut property): consider the moment the algorithm takes
    edge e. The taken edges so far are all part of *some* MST, and e is the
    lightest edge crossing the cut between the two components it joins - so
    some MST contains e too. By induction the final tree is an MST.

    Time: O(E log E) - dominated by the sort.  Space: O(V).

    Example:
        >>> kruskal_mst({0: [(1, 4), (2, 3)], 1: [(0, 4), (2, 1)],
        ...              2: [(0, 3), (1, 1)]})
        [(1, 2, 1), (0, 2, 3)]
    """
    # Collect every node and every undirected edge exactly once; parallel
    # edges between the same pair collapse to the lightest one (an MST over
    # a multigraph never uses a heavier parallel edge).
    adj = _expand(graph)
    nodes = list(adj)
    if not nodes:
        return []

    best: Dict[frozenset, Tuple[Number, Node, Node]] = {}
    for u, neighbours in adj.items():
        for v, w in neighbours:
            if u == v:
                continue  # self-loops never help a spanning tree
            pair = frozenset((u, v))
            if pair not in best or w < best[pair][0]:
                best[pair] = (w, u, v)
    edges = sorted(best.values(), key=lambda edge: edge[0])

    dsu = _DSU(nodes)
    mst: List[Tuple[Node, Node, Number]] = []
    for w, u, v in edges:
        if dsu.union(u, v):
            mst.append((u, v, w))
            if len(mst) == len(nodes) - 1:
                break  # a tree on V nodes has exactly V - 1 edges

    if len(mst) != len(nodes) - 1:
        raise ValueError("graph is disconnected: no spanning tree exists")
    return mst


def prim_mst(
    graph: Mapping[Node, Sequence[Tuple[Node, Number]]],
    start: Optional[Node] = None,
) -> List[Tuple[Node, Node, Number]]:
    """
    Return the edges (u, v, weight) of a minimum spanning tree of the
    undirected weighted graph, using Prim's algorithm. Raises ValueError if
    the graph is disconnected. The optional start node only affects which
    equal-weight tree is returned, never its total weight.

    Input: undirected adjacency (both directions per edge).

    Prim grows a single tree from one node. At every step it looks at the
    *frontier* - edges from a tree node to an outside node - and adds the
    lightest one, which pulls the next node into the tree. A priority queue
    keeps the frontier edges ordered; when an edge is popped whose far end is
    already in the tree, it is simply skipped (it became internal to the
    tree).

    Same cut-property proof as Kruskal: the lightest edge crossing the cut
    (tree, rest of the graph) belongs to some MST, so growing greedily stays
    optimal. Prim differs from Kruskal in shape (one growing blob vs merging
    components) and in cost (better on dense graphs with the right queue).

    Time: O(E log V).  Space: O(V).

    Example:
        >>> prim_mst({0: [(1, 4), (2, 3)], 1: [(0, 4), (2, 1)],
        ...           2: [(0, 3), (1, 1)]})
        [(0, 2, 3), (2, 1, 1)]
    """
    adj = _expand(graph)
    nodes = list(adj)
    if not nodes:
        return []
    if start is None:
        start = nodes[0]
    if start not in adj:
        raise ValueError(f"start node {start!r} is not in the graph")

    in_tree = {start}
    # Heap entries (weight, ticket, from_node, to_node); the ticket keeps
    # equal-weight entries from comparing node labels (see dijkstra).
    heap: List[Tuple[Number, int, Node, Node]] = []
    ticket = 0
    for neighbour, w in adj[start]:
        heappush(heap, (w, ticket, start, neighbour))
        ticket += 1

    mst: List[Tuple[Node, Node, Number]] = []
    while heap and len(in_tree) < len(nodes):
        w, _t, u, v = heappop(heap)
        if v in in_tree:
            continue  # v joined meanwhile: this edge is now internal
        in_tree.add(v)
        mst.append((u, v, w))
        for neighbour, w2 in adj[v]:
            if neighbour not in in_tree:
                heappush(heap, (w2, ticket, v, neighbour))
                ticket += 1

    if len(in_tree) != len(nodes):
        raise ValueError("graph is disconnected: no spanning tree exists")
    return mst


# ---------------------------------------------------------------------------
# Bipartiteness (2-coloring)
# ---------------------------------------------------------------------------


def _expand_unweighted(
    graph: Mapping[Node, Sequence[Node]]
) -> Dict[Node, List[Node]]:
    """
    Normalize an unweighted graph into an adjacency dict whose keys include
    every node mentioned anywhere (sources and targets), so traversals and
    colorings can promise an entry for every node.
    """
    adj: Dict[Node, List[Node]] = defaultdict(list)
    for node, neighbours in graph.items():
        adj[node].extend(neighbours)
        for neighbour in neighbours:
            adj.setdefault(neighbour, [])
    return adj


def is_bipartite(graph: Mapping[Node, Sequence[Node]]) -> Optional[Dict[Node, int]]:
    """
    Return a valid 2-coloring of the undirected graph as {node: 0 or 1}, or
    None if the graph is not bipartite (no such coloring exists).

    Input: unweighted adjacency Mapping[Node, Sequence[neighbour]].

    The characterization that makes this easy: a graph is bipartite exactly
    when it contains no odd cycle. Coloring by BFS tests this directly - paint
    the start node 0, paint every neighbour the opposite color, and the first
    time a neighbour already has the *same* color as its parent, an odd cycle
    has been found and the graph is not bipartite. When the BFS finishes
    cleanly, the coloring is valid by construction.

    Bipartite graphs are exactly the 2-colorable ones - the graphs behind
    matching problems (jobs to workers), alternating paths, and constraint
    graphs where two colors must alternate (checkerboards, scheduling with
    two shifts).

    Time: O(V + E).  Space: O(V).

    Example:
        >>> is_bipartite({0: [1], 1: [0, 2], 2: [1]})   # a path
        {0: 0, 1: 1, 2: 0}
        >>> is_bipartite({0: [1], 1: [0, 2], 2: [1, 0]}) is None  # triangle
        True
    """
    color: Dict[Node, int] = {}
    # Iterate over every node so disconnected components are handled too.
    for start in _expand_unweighted(graph):
        if start in color:
            continue
        color[start] = 0
        queue = deque([start])
        while queue:
            u = queue.popleft()
            for v in graph.get(u, ()):
                if v not in color:
                    color[v] = 1 - color[u]  # neighbour takes the other color
                    queue.append(v)
                elif color[v] == color[u]:
                    return None  # same-colored neighbours: an odd cycle
    return color


# ---------------------------------------------------------------------------
# Strongly connected components (Kosaraju's algorithm)
# ---------------------------------------------------------------------------


def strongly_connected_components(
    graph: Mapping[Node, Sequence[Node]]
) -> List[List[Node]]:
    """
    Return the strongly connected components of the directed graph: a list of
    node groups, where every node in a group can reach every other node in
    that group (and the groups are maximal). Computed with Kosaraju's
    two-pass DFS.

    Input: unweighted adjacency Mapping[Node, Sequence[neighbour]].

    The two-pass structure is the beautiful part:

    Pass 1 (original graph): record nodes in order of DFS *finish time*.
    Pass 2 (reversed graph): process the nodes in reverse finish order; each
    DFS tree grown in the reversed graph is exactly one SCC.

    Why it works: the finish order of pass 1 lists the SCCs of the
    *condensation* (the DAG of components) in reverse topological order.
    Running DFS on the reversed graph in that order means each search is
    confined to one component - the reversed edges inside a component still
    reach everywhere in it, while edges between components now point the
    wrong way to escape.

    Time: O(V + E).  Space: O(V).

    Example:
        >>> strongly_connected_components({0: [1], 1: [2], 2: [0, 3],
        ...                                3: [4], 4: []})
        [[0, 2, 1], [3], [4]]
    """
    adj = _expand_unweighted(graph)  # every mentioned node is now a key
    reverse: Dict[Node, List[Node]] = {node: [] for node in adj}
    for u, neighbours in adj.items():
        for v in neighbours:
            reverse[v].append(u)

    # Pass 1: finish times on the original graph (iterative DFS so deep
    # graphs cannot overflow the call stack).
    visited = set()
    finish_order: List[Node] = []
    for start in adj:
        if start in visited:
            continue
        stack = [(start, False)]  # (node, exiting?)
        while stack:
            node, exiting = stack.pop()
            if exiting:
                finish_order.append(node)
                continue
            if node in visited:
                continue
            visited.add(node)
            stack.append((node, True))  # re-visit to record finish time
            for neighbour in adj[node]:
                if neighbour not in visited:
                    stack.append((neighbour, False))

    # Pass 2: DFS on the reversed graph in reverse finish order.
    seen = set()
    components: List[List[Node]] = []
    for start in reversed(finish_order):
        if start in seen:
            continue
        component: List[Node] = []
        stack = [start]
        seen.add(start)
        while stack:
            node = stack.pop()
            component.append(node)
            for neighbour in reverse[node]:
                if neighbour not in seen:
                    seen.add(neighbour)
                    stack.append(neighbour)
        components.append(component)
    return components


# ---------------------------------------------------------------------------
# Maximum flow (Edmonds-Karp)
# ---------------------------------------------------------------------------


def edmonds_karp(
    graph: Mapping[Node, Sequence[Tuple[Node, Number]]],
    source: Node,
    sink: Node,
) -> Number:
    """
    Return the value of the maximum flow from source to sink in the directed
    capacitated graph (edges are (neighbour, capacity) pairs, capacities
    non-negative), using the Edmonds-Karp algorithm. Raises ValueError if
    source or sink is not in the graph or a capacity is negative.

    The family: Ford-Fulkerson repeatedly finds *any* path from source to
    sink in the residual graph - the graph of remaining capacity, where every
    used edge also gets a reverse edge of equal capacity so flow can be
    "undone" - and pushes as much as the path's bottleneck allows. Edmonds-
    Karp is the instance that always picks the *shortest* residual path (BFS
    instead of DFS), which guarantees O(V * E^2) time regardless of the
    capacities - important because plain Ford-Fulkerson can crawl when
    capacities are irrational or huge.

    The residual reverse edges are the conceptual heart: augmenting along
    u -> v creates capacity v -> u, which is how later augmenting paths can
    reroute flow that was assigned poorly. The algorithm terminates when no
    residual path remains, and the max-flow min-cut theorem certifies that
    the accumulated flow is then maximal.

    Why BFS (not any path)? Each augmenting path found by BFS is a *shortest*
    one, and after each augmentation at least one residual edge is saturated.
    That bounds the number of augmentations by O(V * E), which is what turns
    Ford-Fulkerson's capacity-dependent runtime into the guaranteed
    O(V * E^2) below.

    Time: O(V * E^2).  Space: O(V + E) for the residual graph.

    Example:
        >>> graph = {0: [(1, 3), (2, 2)], 1: [(2, 1), (3, 2)],
        ...          2: [(3, 3)], 3: []}
        >>> edmonds_karp(graph, source=0, sink=3)
        5
    """
    if source == sink:
        return 0  # nothing needs to travel; and this must not run the BFS

    # Build the residual graph: forward capacities from the input, and every
    # reverse edge present with capacity 0 (it gains capacity as flow is
    # pushed through its forward edge).
    adj = _expand(graph)
    if source not in adj or sink not in adj:
        raise ValueError("source and sink must be nodes of the graph")
    residual: Dict[Node, Dict[Node, Number]] = {
        node: {} for node in adj
    }
    for u, neighbours in adj.items():
        for v, capacity in neighbours:
            if capacity < 0:
                raise ValueError("capacities must be non-negative")
            residual[u][v] = residual[u].get(v, 0) + capacity
            residual[v].setdefault(u, 0)

    total: Number = 0
    while True:
        # BFS for a shortest augmenting path in the residual graph.
        parent: Dict[Node, Optional[Node]] = {source: None}
        queue = deque([source])
        while queue and sink not in parent:
            u = queue.popleft()
            for v, capacity in residual[u].items():
                if v not in parent and capacity > 0:
                    parent[v] = u
                    queue.append(v)
        if sink not in parent:
            break  # no residual path: flow is maximal

        # Find the bottleneck: the smallest residual capacity on the path.
        # Node equality is by value (!=, not `is`): the stored keys come from
        # the caller's graph, so value semantics is what must terminate the
        # walk back at the source.
        bottleneck = float("inf")
        node = sink
        while node != source:
            prev = parent[node]
            bottleneck = min(bottleneck, residual[prev][node])
            node = prev

        # Augment: consume capacity forward, refund it backward.
        node = sink
        while node != source:
            prev = parent[node]
            residual[prev][node] -= bottleneck
            residual[node][prev] = residual[node].get(prev, 0) + bottleneck
            node = prev
        total += bottleneck
    return total
