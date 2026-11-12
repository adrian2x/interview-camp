from typing import Hashable, List
from collections import defaultdict, deque


class Edge:
    def __init__(self, start, end, cost) -> None:
        self.start = start
        self.end = end
        self.cost = cost


def bfs(graph, source: Hashable, target: Hashable) -> bool:
    """Example BFS reachability over a Graph with a KV ``nodes`` map.

    Expects ``graph.nodes[cur]`` (or ``graph.nodes.get(cur)``) to yield the
    neighbors of ``cur``.
    """
    if source == target:
        return True

    visited = {source}
    queue = deque([source])

    while queue:
        cur = queue.popleft()
        for nxt in graph.nodes[cur]:
            if nxt in visited:
                continue
            if nxt == target:
                return True
            visited.add(nxt)
            queue.append(nxt)

    return False


def bellman_ford(graph: List[Edge], nodes, source):
    "Returns the min path from a source node to all other nodes in graph and identify negative cycles"
    dist = [float("inf")] * nodes
    dist[source] = 0

    # Note this is O(N * E)
    for i in range(nodes):
        for edge in graph:
            # relax edge (update dist with shorter path)
            dist[edge.end] = min(dist[edge.end], dist[edge.start] + edge.cost)

    # run again to detect negative cycles
    # if there is a negative cycle, we would improve previous nodes
    for i in range(nodes):
        for edge in graph:
            if dist[edge.start] + edge.cost < dist[edge.end]:
                dist[edge.end] = float("-inf")

    return dist


def floyd_warshall(graph_matrix):
    N = len(graph_matrix)
    # setup distances and path matrix
    dist = [[float("inf")] * len(i) for i in range(N)]
    path = [[None] * len(i) for i in range(N)]
    for i in range(N):
        for j in range(N):
            dist[i][j] = graph_matrix[i][j]
            if graph_matrix[i][j] != None:
                path[i][j] = j

    # compute all pairs shortest path in O(N^3)
    for k in range(N):
        for i in range(N):
            for j in range(N):
                # check the distance from (i, k) + (k, j)
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    # update the path to (i, j) as going through (i, k)
                    path[i][j] = path[i][k]

    # run the loops again to check for negative cycles
    # for k in range(N):
    #     for i in range(N):
    #         for j in range(N):
    #             # if we can improve upon the already optimal cost
    #             # then it means we are reaching a negative cycle
    #             if dist[i][k] + dist[k][j] < dist[i][j]:
    #                 dist[i][j] = float('-inf')
    #                 path[i][j] = float('-inf')
    return dist, path


def topsort(vertices, edges):
    ordering = []
    # keep track of nodes in-degree
    inDegree = {i: 0 for i in range(vertices)}
    # initialize the adjacency matrix
    graph = [[] for i in range(vertices)]
    for edge in edges:
        start, end = edge[0], edge[1]
        graph[start].append(end)
        inDegree[end] += 1  # increment in-degree of end node

    # find sources (nodes with in-degree of zero)
    sources = deque()
    for key in inDegree:
        if inDegree[key] == 0:
            sources.append(key)

    while sources:
        # add sources to the ordering
        vertex = sources.popleft()
        ordering.append(vertex)
        # decrement neighbors in-degree
        for n in graph[vertex]:
            inDegree[n] -= 1
            # add to queue when in-degree is 0
            if inDegree[n] == 0:
                sources.append(n)

    # if nodes remain with in-degree > 0, there is a cycle
    # if len(ordering) != vertices: return None
    return ordering


def dfs_path(source, graph, visited, path=[], stack=set()):
    visited.add(source)
    stack.add(source)
    edges = graph.get(source)
    for dest in edges:
        if dest not in visited:
            dfs_path(dest, graph, visited, path, stack)
        elif dest in stack:
            raise ValueError("cycle found")
    path.append(source)
    stack.remove(source)
    return path


def clone_graph_recursive(node, clones={}):
    if clones.get(node):
        return clones[node]
    copy = Node(node.val)
    clones[node] = copy
    for n in node.neighbors:
        copy.neighbors.append(clone_graph_recursive(n, clones))
    return copy


def clone_graph_iter(node):
    # Start the queue
    queue = deque()
    queue.append(node)
    seen = {node}

    # Clone the start node
    clones = {}
    clones[node.val] = Node(node.val)

    while len(queue) > 0:
        source = queue.popleft()
        clone = clones[source.val]
        # clone the neighbors
        for dest in source.neighbors:
            dest_clone = clones.get(dest.val, Node(dest.val))
            clone.neighbors.append(dest_clone)
            clones[dest.val] = dest_clone
            if dest not in seen:
                seen.add(dest)
                queue.append(dest)

    return clones[node.val]


# https://www.hackerrank.com/interview/preparation-kits/one-month-preparation-kit/one-month-week-four/challenges
def roadsAndLibraries(N, c_lib, c_road, cities):
    adjlist = defaultdict(list)

    for i, j in cities:
        adjlist[i].append(j)
        adjlist[j].append(i)

    def dfs(node, adjlist, seen=set(), path=[]):
        seen.add(node)
        for n in adjlist[node]:
            if n not in seen:
                dfs(n, adjlist, seen, path)
        path.append(node)
        return path

    components = []
    seen = set()
    for node in adjlist:
        if node not in seen:
            path = []
            path = dfs(node, adjlist, seen, path)
            components.append(path)

    total_comp = len(components) + (N - len(seen))
    components_cost = (
        sum([c_road * (len(p) - 1) for p in components]) + total_comp * c_lib
    )
    all_libraries_cost = N * c_lib
    return min(all_libraries_cost, components_cost)


print(roadsAndLibraries(5, 6, 1, [[1, 2], [1, 3], [1, 4]]))


'''
While grading papers as an assistant, you've noticed some of them are surprisingly similar. You've decided to write a simple plagiarism detector to try to combat this, including checking for swapped in synonyms.

You've found a list of synonyms online. These synonyms come in a list of pairs, and sometimes you may have to link together multiple pairs to see if the words are synonyms.

In this example, "paper", "composition" and "essay" are all synonyms:
synonyms1_1 = [
  ("paper", "composition"), 
  ("composition", "essay")
]
So these lines are considered equal:
line1_1 = "this |paper| is totally an original paper"
line1_2 = "this |composition| is totally an original |essay|"

similar(line1_1, line1_2, synonyms1_1) => True

Write a function that takes in two lines and a list of synonym pairs, and returns whether the two lines are considered equal.

Additional input data:
line2_1 = "the man in the blue shirt sat by the blue sea in a blue chair under the blue sky"
line2_2 = "the man in the teal shirt sat by the cerulean sea in a navy chair beneath the cyan sky"
synonyms2_1 = [("teal", "turquoise"), ("teal", "cyan"), ("cerulean", "navy"), ("blue", "navy"), ("navy", "teal"), ("under", "beneath")]
synonyms2_2 = [("teal", "turquoise"), ("teal", "cyan"), ("cerulean", "navy"), ("blue", "navy"), ("under", "beneath")]

Here is a diagram of how synonyms2_1 and synonyms2_2 connect together:

   ===synonyms2_1===            ===synonyms2_2===

   cerulean     blue            cerulean     blue      
           \    /                       \    /         
            navy                         navy          
              |                                       
            teal                         teal          
           /    \                       /    \         
    turquoise   cyan             turquoise   cyan
  
     under - beneath              under - beneath

With synonyms2_1, all of the instances of blue in the first sentence have synonyms in the second. However, without the (navy, teal) synonym, such as in synonyms2_2, blue would not be considered a synonym of teal, turquoise, and cyan, so with those synonyms we return False.

line3_1 = "also these sentences are not really related in any way"
line3_2 = "i like cats a lot but dogs are ok too"
synonyms3_1 = [("too", "also"), ("cats", "felines"), ("dogs", "canines")]

line4_1 = "it is important to play in spring"
line4_2 = "it is important to plow in spring"
synonyms4_1 = [("lay", "low"), ("spring", "springtime")]

Test Cases:
similar(line1_1, line1_2, synonyms1_1) => True
similar(line2_1, line2_2, synonyms2_1) => True
similar(line2_2, line2_1, synonyms2_1) => True
similar(line2_1, line2_2, synonyms2_2) => False
similar(line3_1, line3_2, synonyms3_1) => False
similar(line4_1, line4_2, synonyms4_1) => False

Complexity Variables:
N = length of the lines
S = number of synonym pairs

'''


line1_1 = "this paper is totally an original paper"
line1_2 = "this composition is totally an original essay"
synonyms1_1 = [
  ("paper", "composition"),
  ("composition", "essay")
]

line2_1 = "the man in the blue shirt sat by the blue sea in a blue chair under the blue sky"
line2_2 = "the man in the teal shirt sat by the cerulean sea in a navy chair beneath the cyan sky"
synonyms2_1 = [
  ("teal", "turquoise"),
  ("teal", "cyan"),
  ("cerulean", "navy"),
  ("blue", "navy"),
  ("navy", "teal"),
  ("under", "beneath")
]
synonyms2_2 = [
  ("teal", "turquoise"),
  ("teal", "cyan"),
  ("cerulean", "navy"),
  ("blue", "navy"),
  ("under", "beneath")
]

line3_1 = "also these sentences are not really related in any way"
line3_2 = "i like cats a lot but dogs are ok too"
synonyms3_1 = [
  ("too", "also"),
  ("cats", "felines"),
  ("dogs", "canines")
]

line4_1 = "it is important to play in spring"
line4_2 = "it is important to plow in spring"
synonyms4_1 = [
  ("lay", "low"), 
  ("spring", "springtime")
]
