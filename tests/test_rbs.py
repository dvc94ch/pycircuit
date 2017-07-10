import unittest
from pycircuit.rbs import *


class GraphTests(unittest.TestCase):
    def test_shortest_path(self):
        g = Graph()

        g.add_node(0)
        g.add_node(1)
        g.add_node(2)
        g.add_edge(0, 1, 1)
        g.add_edge(0, 2, 1)
        g.add_edge(1, 2, 2)
        distance, path = dijkstra(g, 0)
        assert distance[2] == 1
        assert path[2] == 0

        g.add_node(3)
        g.add_edge(1, 3, 2)
        distance, path = dijkstra(g, 0)
        assert distance[3] == 3
        assert path[3] == 1
        assert path[1] == 0

        g.add_edge(2, 3, 1)
        distance, path = dijkstra(g, 0)
        assert distance[3] == 2
        assert path[3] == 2
        assert path[2] == 0

        g.add_node(4)
        g.add_edge(3, 4, 1)
        distance, path = dijkstra(g, 0)
        assert distance[4] == 3
        assert path[4] == 3
        assert path[3] == 2
        assert path[2] == 0


class RubberBandSketchTests(unittest.TestCase):

    def test_triangulate(self):
        rbs = RubberBandSketch()

        for x, y, pad in [(0, 0, '0'), (1, 0, '1'), (0, 1, '2'), (1, 2, '3'), (1, 3, '4')]:
            rbs.add_feature(RBSFeature(x, y, None, None, pad))

        rbs.triangulate()
        route = rbs.shortest_route(0, 4)
        assert len(route) == 3
        assert route.features[0].pad == '4'
        assert route.features[1].pad == '2'
        assert route.features[2].pad == '0'
