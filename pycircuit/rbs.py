import numpy as np
from collections import defaultdict
from scipy.spatial import Delaunay
from shapely.geometry import Point


class Graph(object):
    def __init__(self):
        self.nodes = set()
        self.edges = defaultdict(list)
        self.distances = {}

    def add_node(self, node):
        self.nodes.add(node)

    def add_edge(self, from_node, to_node, distance):
        self.edges[from_node].append(to_node)
        self.edges[to_node].append(from_node)
        self.distances[(from_node, to_node)] = distance
        self.distances[(to_node, from_node)] = distance


def dijkstra(graph, initial):
    # Adapted from https://gist.github.com/econchick/4666413
    visited = {initial: 0}
    path = {}

    nodes = set(graph.nodes)

    while nodes:
        min_node = None
        for node in nodes:
            if node in visited:
                if min_node is None:
                    min_node = node
                elif visited[node] < visited[min_node]:
                    min_node = node

        if min_node is None:
            break

        nodes.remove(min_node)
        current_weight = visited[min_node]

        for edge in graph.edges[min_node]:
            weight = current_weight + graph.distances[(min_node, edge)]
            if edge not in visited or weight < visited[edge]:
                visited[edge] = weight
                path[edge] = min_node

    return visited, path


def find_neighbors(pindex, triang):
    # Adapted from https://stackoverflow.com/questions/12374781/how-to-find-all-neighbors-of-a-given-point-in-a-delaunay-triangulation-using-sci
    start = triang.vertex_neighbor_vertices[0][pindex]
    stop = triang.vertex_neighbor_vertices[0][pindex+1]
    return triang.vertex_neighbor_vertices[1][start:stop]


class RBSFeature(object):
    def __init__(self, x, y, net, node, pad):
        self.x = x
        self.y = y
        self.net = net

        self.node = node
        self.pad = pad


class Route(object):
    def __init__(self, feature):
        self.features = [feature]

    def add_feature(self, feature):
        self.features.append(feature)

    def __iter__(self):
        return iter(self.features)

    def __len__(self):
        return len(self.features)


class RubberBandSketch(object):
    def __init__(self):
        self.graph = Graph()
        self.features = []
        self.coords = []

    def add_feature(self, feature):
        self.graph.add_node(len(self.features))
        self.features.append(feature)
        self.coords.append([feature.x, feature.y])

    def triangulate(self):
        tri = Delaunay(np.array(self.coords))

        for i, feat in enumerate(self.features):
            for j in find_neighbors(i, tri):
                d = Point(self.coords[i]).distance(Point(self.coords[j]))
                self.graph.add_edge(i, j, d)

    def shortest_route(self, i, j):
        distance, path = dijkstra(self.graph, i)

        route = Route(self.features[j])
        while not j == i:
            j = path[j]
            route.add_feature(self.features[j])

        return route
