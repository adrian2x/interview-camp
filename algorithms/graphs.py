from typing import List
from collections import deque


class Edge:
    def __init__(self, start, end, cost) -> None:
        self.start = start
        self.end = end
        self.cost = cost


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
