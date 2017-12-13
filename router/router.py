# The MIT License (MIT)
#
# Copyright (c) 2017, Sam Bayless
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from monosat import *
import argparse
from time import time
from collections import defaultdict
import pcrt
import itertools
from shapely.geometry import Point, LineString, MultiLineString
from shapely.ops import linemerge

# Helper functions
def ExactlyOne(vars):
    AssertOr(vars)
    AMO(vars)

at_most_one_builtin_size=20
def AMO(vars):
    if (len(vars) <= at_most_one_builtin_size):
        for a, b in itertools.combinations(vars, 2):
            # in every distinct pair of edges, at least one must be false
            AssertOr(~a, ~b)
    else:
        # use more expensive, but more scalable, built-in AMO theory
        AssertAtMostOne(vars)

def BVEQ(bva,bvb):
    if(len(bva) != len(bvb)):
        return false()
    same = true()
    for a,b in zip(bva,bvb):
        same = And(same, Xnor(a, b))
    return same

# There are many ways to perform circuit routing using MonoSAT.
# This approach uses multiple graphs, and uses a conjunction of MonoSAT's
# built-in reachability constraints across those graphs to ensure nets are
# routed, while using propositional constraints over the edges in the graph
# to prevent nets from intersecting.
# This function also supports a slightly more complex router, which combines
# reachability and maximum flow constraints.
# The maximum flow constraint is not powerful enough to ensure correct routing,
# but is a (safe) overapproximative constraint, that allows the solver to prune
# large parts of the search space early.
#
# The variation described here supports multi-terminal routing; if your instance
# only has 2-terminal nets, router.py is recommended, as it's encoding is more
# efficient.

def route_multi(filename, monosat_args, maxflow_enforcement_level,
                flowgraph_separation_enforcement_style=0,
                graph_separation_enforcement_style=1,
                heuristicEdgeWeights=False):
    (width, height), diagonals, nets, constraints, disabled = pcrt.read(filename)
    print(filename)
    print("Width = %d, Height = %d, %d nets, %d constraints" %
          (width, height, len(nets), len(constraints)))
    if diagonals:
        print("45-degree routing enabled. Warning: 45-degree routing is untested, and may be buggy.")
    else:
        print("90-degree routing")

    if (len(monosat_args) > 0):
        args = " ".join(monosat_args)
        print("Monosat args: " + args)
        Monosat().init(args)

    graphs = []
    all_graphs=[]
    for _ in nets:
        # for each net to be routed, created a separate symbolic graph.
        # later we will add constraints to force each edge to be enabled in at
        # most one of these graphs
        graphs.append(Graph())

        if heuristicEdgeWeights:
            # this enables a heuristic on these graphs, from the RUC paper,
            # which sets assigned edges to zero weight, to encourage edge-reuse
            # in solutions
            graphs[-1].assignWeightsTo(1)

        all_graphs.append(graphs[-1])

    flow_graph=None
    flow_graph_edges = dict()
    flow_grap_edge_list = collections.defaultdict(list)
    if maxflow_enforcement_level>=1:
        # if flow constraints are used, create a separate graph which will
        # contain the union of all the edges enabled in the above graphs
        flow_graph = Graph()
        all_graphs.append(flow_graph)


    print("Building grid")
    out_grid = dict()
    in_grid = dict()
    vertex_grid = dict()
    vertices=dict()
    fromGrid = dict()
    for g in all_graphs:
        out_grid[g] = dict()
        in_grid[g] = dict()
        vertex_grid[g] = dict()

    for x in range(width):
        for y in range(height):
            vertices[(x, y)] = []
            for g in all_graphs:
                out_node = g.addNode("%d_%d" % (x, y))
                out_grid[g][(x, y)] = out_node
                fromGrid[out_node] = (x, y)

                in_node = g.addNode("in_%d_%d" % (x, y))
                in_grid[g][(x, y)] = in_node
                fromGrid[in_node] = (x, y)

                if(g != flow_graph):
                    # a large-enough weight, only relevant if
                    # heuristicEdgeWeights > 0
                    weight = 1 if not heuristicEdgeWeights else 1000
                    edge = g.addEdge(in_node, out_node, weight)
                else:
                    # add an edge with constant capacity of 1
                    edge = g.addEdge(in_node, out_node, 1)
                vertex_grid[g][(x, y)] = edge

                if(g != flow_graph):
                    vertices[(x, y)].append(edge)

    print("Adding edges")
    disabled_nodes = set(disabled)
    undirected_edges = dict()
    start_nodes = set()
    end_nodes = set()
    net_nodes = set()
    for net in nets:
        start_nodes.add(net[0])
        # you can pick any of the terminals in the net to be the starting node
        # for the routing constraints; it might be a good idea to randomize this
        # choice
        for n in net[1:]:
            end_nodes.add(n)
        for (x, y) in net:
            net_nodes.add((x, y))


    # create undirected edges between neighbouring nodes
    def addEdge(n, r, diagonal_edge=False):
        e = None
        if n not in disabled_nodes and r not in disabled_nodes:
            if n in net_nodes or r in net_nodes:
                allow_out = True
                allow_in = True
                if n in start_nodes or r in end_nodes:
                    allow_in = False
                if n in end_nodes or r in start_nodes:
                    allow_out = False
                assert (not (allow_in and allow_out))
                if allow_out:
                    # for each net's symbolic graph (g), create an edge
                    edges = []
                    for g in graphs:
                        # add a _directed_ edge from n to r
                        eg = (g.addEdge(out_grid[g][n], in_grid[g][r]))
                        if e is None:
                            e = eg
                        undirected_edges[eg] = e
                        edges.append(eg)
                        if not diagonal_edge:
                            Assert(eg)


                    if flow_graph is not None:
                        # create the same edge in the flow graph
                        # add a _directed_ edge from n to r
                        ef = (flow_graph.addEdge(out_grid[flow_graph][n],
                                                 in_grid[flow_graph][r]))

                        if flowgraph_separation_enforcement_style > 0:
                            flow_graph_edges[(n, r)] = ef
                            flow_graph_edges[(r, n)] = ef
                            flow_grap_edge_list[n].append(ef)
                            flow_grap_edge_list[r].append(ef)
                        else:
                            if not diagonal_edge:
                                Assert(ef)
                        edges.append(ef)
                    if (diagonal_edge):
                        AssertEq(*edges)
                elif allow_in:
                    # for each net's symbolic graph (g), create an edge
                    edges = []
                    for g in graphs:
                        # add a _directed_ edge from n to r
                        eg = (g.addEdge(out_grid[g][r], in_grid[g][n]))
                        if e is None:
                            e = eg
                        undirected_edges[eg]=e
                        edges.append(eg)
                        if not diagonal_edge:
                            Assert(eg)

                    if flow_graph is not None:
                        # create the same edge in the flow graph
                        # add a _directed_ edge from n to r
                        ef = (flow_graph.addEdge(out_grid[flow_graph][r],
                                                 in_grid[flow_graph][n]))

                        if flowgraph_separation_enforcement_style > 0:
                            flow_graph_edges[(n, r)] = ef
                            flow_graph_edges[(r, n)] = ef
                            flow_grap_edge_list[n].append(ef)
                            flow_grap_edge_list[r].append(ef)
                        else:
                            if not diagonal_edge:
                                Assert(ef)
                        edges.append(ef)
                    if (diagonal_edge):
                        AssertEq(*edges)

                else:
                    e = None
            else:
                edges = []
                # for each net's symbolic graph (g), create an edge in both
                # directions
                for g in graphs:
                    # add a _directed_ edge from n to r
                    eg = (g.addEdge(out_grid[g][n], in_grid[g][r]))
                    if e is None:
                        e = eg
                    undirected_edges[eg]=e
                    if not diagonal_edge:
                        Assert(eg)
                    eg2 = (g.addEdge(out_grid[g][r], in_grid[g][n]))
                    if not diagonal_edge:
                        Assert(eg2)
                    else:
                        AssertEq(eg, eg2)
                    undirected_edges[eg2] = e # map e2 to e
                    edges.append(eg)
                if flow_graph is not None:
                    # add a _directed_ edge from n to r
                    ef = (flow_graph.addEdge(out_grid[flow_graph][r],
                                             in_grid[flow_graph][n]))
                    # add a _directed_ edge from r to n
                    ef2 = (flow_graph.addEdge(out_grid[flow_graph][n],
                                              in_grid[flow_graph][r]))
                    edges.append(ef)
                    if flowgraph_separation_enforcement_style > 0:
                        AssertEq(ef,ef2)
                        flow_grap_edge_list[n].append(ef)
                        flow_grap_edge_list[r].append(ef)
                        flow_graph_edges[(n, r)] = ef
                        flow_graph_edges[(r, n)] = ef
                    else:
                        if not diagonal_edge:
                            Assert(ef)
                            Assert(ef2)
                    if (diagonal_edge):
                        AssertEq(*edges)

        return e

    # create all the symbolic edges.
    for x in range(width):
        for y in range(height):
            n = (x, y)
            if n in disabled_nodes:
                continue
            if x < width - 1:
                r = (x + 1, y)
                e = addEdge(n, r)

            if y < height - 1:
                r = (x, y + 1)
                e = addEdge(n, r)

            if diagonals:
                # if 45 degree routing is enabled, create diagonal edges here
                diag_up = None
                diag_down = None
                if x < width - 1 and y < height - 1:
                    r = (x + 1, y + 1)
                    e = addEdge(n, r, True)
                    diag_down = e

                if x > 0 and y < height - 1 and False:
                    r = (x - 1, y + 1)
                    e = addEdge(n, r, True)
                    diag_up = e

                if diag_up and diag_down:
                    AssertNand(diag_up, diag_down) #cannot route both diagonals

    vertex_used=None

    # enforce constraints from the .pcrt file
    if len(constraints) > 0:
        print("Enforcing constraints")
        vertex_used = dict()
        for x in range(width):
            for y in range(height):
                # A vertex is used exactly if one of its edges is enabled
                vertex_used[(x, y)] = Or(vertices[(x, y)])

        for constraint in constraints:
            # a constraint is a list of vertices of which at most one can be used
            vertex_used_list = []
            for node in constraint:
                vertex_used_list.append(vertex_used[node])
            AMO(vertex_used_list)

    uses_bv = (flow_graph and flowgraph_separation_enforcement_style >= 2) or \
              (graph_separation_enforcement_style >= 2)

    print("Enforcing separation")
    #force each vertex to be in at most one graph.
    for x in range(width):
        for y in range(height):
            n = (x, y)
            if n not in net_nodes:
                if graph_separation_enforcement_style <= 1:
                    # use at-most-one constraint to force each edge to be
                    # assigned to at most on net
                    AMO(vertices[n])
                else:
                    # rely on the uniqueness bv encoding below to force at most
                    # one graph assign per vertex
                    assert(uses_bv)

                if flow_graph is not None or uses_bv:

                    if vertex_used is None:
                        # only create this lazily, if needed
                        vertex_used = dict()
                        for x in range(width):
                            for y in range(height):
                                # A vertex is used exactly if one of its edges
                                # is enabled
                                vertex_used[(x, y)] = Or(vertices[(x, y)])
                    if flow_graph is not None:
                        # Assert that iff this vertex is in _any_ graph, it must
                        # be in the flow graph
                        AssertEq(vertex_used[(x, y)], vertex_grid[flow_graph][n])

    if uses_bv:
        # Optionally, use a bitvector encoding to determine which graph each
        # edge belongs to (following the RUC paper).
        vertices_bv = dict()
        bvwidth = math.ceil(math.log(len(nets) + 1, 2))
        print("Building BV (width = %d)" % (bvwidth))

        # bv 0 means unused
        for x in range(width):
            for y in range(height):
                # netbv = BitVector(bvwidth)
                netbv = [Var() for _ in range(bvwidth)]
                # this is just for error checking this script
                seen_bit = [False] * bvwidth
                for b in range(bvwidth):
                    # if the vertex is not used, set the bv to 0
                    AssertImplies(~vertex_used[(x, y)], ~netbv[b])

                for i in range(len(nets)):
                    net_n = i + 1
                    seen_any_bits = False
                    for b in range(bvwidth):
                        bit = net_n & (1 << b)
                        if(bit):
                            AssertImplies(vertices[(x, y)][i], netbv[b])
                            seen_bit[b] = True
                            seen_any_bits = True
                        else:
                            AssertImplies(vertices[(x, y)][i], ~netbv[b])
                    # AssertImplies(vertices[(x,y)][i],(netbv.eq(net_n)))
                    assert (seen_any_bits)
                if graph_separation_enforcement_style < 3:
                    # rely on the above constraint
                    # AssertImplies(~vertex_used[(x, y)], ~netbv[b])
                    # to ensure that illegal values of netbv are disallowed
                    pass
                elif graph_separation_enforcement_style == 3:
                    # directly rule out disallowed bit patterns
                    # len(nets)+1, because 1 is added to each net id for the
                    # above calculation (so that 0 can be reserved for no net)
                    for i in range(len(nets) + 1, (1 << bvwidth)):
                        bits = []
                        for b in range(bvwidth):
                            bit = i & (1 << b)
                            if bit > 0:
                                bits.append(netbv[b])
                            else:
                                bits.append(~netbv[b])
                        # at least one of these bits cannot be assigned this way
                        AssertNand(bits)

                # all bits must have been set to 1 at some point, else the above
                # constraints are buggy
                assert(all(seen_bit))
                vertices_bv[(x, y)] = netbv


    # the following constraints are only relevant if maximum flow constraints
    # are being used. These constraints ensure that in the maximum flow graph,
    # edges are not connected between different nets.
    if flow_graph and flowgraph_separation_enforcement_style == 1:
        print("Enforcing (redundant) flow separation")
        # if two neighbouring nodes belong to different graphs, then
        # disable the edge between them.
        for x in range(width):
            for y in range(height):
                n = (x, y)

                if x < width - 1:
                    r = (x + 1, y)
                    if (n, r) in flow_graph_edges:
                        # if either end point is not is disabled, disable this
                        # edge... this is not technically required (since flow
                        # already cannot pass through unused vertices), but
                        # cheap to enforce and slightly reduces the search
                        # space.
                        AssertImplies(Or(Not(vertex_used[n]), Not(vertex_used[r])),
                                      Not(flow_graph_edges[(n, r)]))
                        any_same=false()
                        for i in range(len(vertices[n])):
                            # Enable this edge if both vertices belong to the
                            # same graph
                            same_graph = And(vertices[n][i], vertices[r][i])
                            AssertImplies(same_graph, flow_graph_edges[(n,r)])
                            any_same = Or(any_same, same_graph)
                            # Assert that if vertices[n] != vertices[r], then
                            # flow_graph_edges[(n, r)] = false
                            for j in range(i + 1,len(vertices[r])):
                                # if the end points of this edge belong to
                                # different graphs, disable them.
                                AssertImplies(And(vertices[n][i], vertices[r][j]),
                                              Not(flow_graph_edges[(n, r)]))
                        AssertEq(flow_graph_edges[(n, r)], any_same)


                if y < height - 1:
                    r = (x, y + 1)
                    if (n, r) in flow_graph_edges:
                        # if either end point is not is disabled, disable this
                        # edge... this is not technically required (since flow
                        # already cannot pass through unused vertices), but
                        # cheap to enforce and slightly reduces the search space.
                        AssertImplies(Or(Not(vertex_used[n]), Not(vertex_used[r])),
                                      Not(flow_graph_edges[(n, r)]))
                        any_same = false()
                        for i in range(len(vertices[n])):
                            # Enable this edge if both vertices belong to the
                            # same graph
                            same_graph = And(vertices[n][i], vertices[r][i])
                            AssertImplies(same_graph, flow_graph_edges[(n, r)])
                            any_same = Or(any_same, same_graph)

                            # Assert that if vertices[n] != vertices[r], then
                            # flow_graph_edges[(n,r)] = false
                            for j in range(i + 1, len(vertices[r])):
                                # if the end points of this edge belong to
                                # different graphs, disable them.
                                AssertImplies(And(vertices[n][i], vertices[r][j]),
                                              Not(flow_graph_edges[(n, r)]))
                        AssertEq(flow_graph_edges[(n, r)], any_same)

    elif flow_graph and flowgraph_separation_enforcement_style == 2:
        print("Enforcing (redundant) BV flow separation")
        for x in range(width):
            for y in range(height):
                n = (x, y)

                if x < width - 1:
                    r = (x + 1, y)
                    if (n, r) in flow_graph_edges:
                        # if either end point is not is disabled, disable this
                        # edge... this is not technically required (since flow
                        # already cannot pass through unused vertices), but
                        # cheap to enforce and slightly reduces the search space.
                        # AssertImplies(Or(Not(vertex_used[n]),Not(vertex_used[r])),
                        # Not(flow_graph_edges[(n, r)]))

                        # And(vertices[n][i], vertices[r][i])
                        same_graph = BVEQ(vertices_bv[n], vertices_bv[r])
                        AssertEq(And(vertex_used[n], same_graph),
                                 flow_graph_edges[(n, r)])

                if y < height - 1:
                    r = (x, y + 1)
                    if (n, r) in flow_graph_edges:
                        # if either end point is not is disabled, disable this
                        # edge... this is not technically required (since flow
                        # already cannot pass through unused vertices),
                        # but cheap to enforce and slightly reduces the search
                        # space.
                        # AssertImplies(Or(Not(vertex_used[n]), Not(vertex_used[r])),
                        # Not(flow_graph_edges[(n, r)]))

                        # And(vertices[n][i], vertices[r][i])
                        same_graph = BVEQ(vertices_bv[n], vertices_bv[r])
                        AssertEq(And(vertex_used[n], same_graph),
                                 flow_graph_edges[(n, r)])

    for i, net in enumerate(nets):
        for n in net:
            # terminal nodes must be assigned to this graph
            Assert(vertices[n][i])
            if(flow_graph):
                # force the terminal nodes to be enabled in the flow graph
                Assert(vertex_grid[flow_graph][n])


    print("Enforcing reachability")
    reachset = dict()
    # In each net's corresponding symbolic graph, enforce that the first
    # terminal of the net reaches each other terminal of the net.
    for i, net in enumerate(nets):
        reachset[i] = dict()
        n1 = net[0]
        # It is a good idea for all reachability constraints to have a common
        # source as that allows monosat to compute their paths simultaneously,
        # cheaply. Any of the terminals could be chosen to be that source; we
        # use net[0], arbitrarily.
        for n2 in net[1:]:
            g = graphs[i]
            r = g.reaches(in_grid[g][n1], out_grid[g][n2])
            reachset[i][n2] = r
            Assert(r)

            # decide reachability before considering regular variable decisions.
            r.setDecisionPriority(1);
            # That prioritization is required for the RUC heuristics to take
            # effect.



    if maxflow_enforcement_level >= 1:
        print("Enforcing flow constraints")

        # This adds an (optional) redundant maximum flow constraint. While the
        # flow constraint is not by itself powerful enough to enforce a correct
        # routing (and so must be used in conjunction with the routing
        # constraints above), it can allow the solver to prune parts of the
        # search space earlier than the routing constraints alone.

        # add a source and dest node, with 1 capacity from source to each net
        # start vertex, and 1 capacity from each net end vertex to dest
        g = flow_graph
        source = g.addNode()
        dest = g.addNode()
        for net in nets:
            Assert(g.addEdge(source, in_grid[g][net[0]], 1)) # directed edges!
            Assert(g.addEdge(out_grid[g][net[1]], dest, 1))  # directed edges!
        # create a maximum flow constraint
        m = g.maxFlowGreaterOrEqualTo(source, dest, len(nets))
        Assert(m) # assert the maximum flow constraint

        # These settings control how the maximum flow constraints interact
        # heuristically with the routing constraints.
        if maxflow_enforcement_level == 3:
            # sometimes make decisions on the maxflow predicate.
            m.setDecisionPriority(1);
        elif maxflow_enforcement_level == 4:
            # always make decisions on the maxflow predicate.
            m.setDecisionPriority(2);
        else:
            # never make decisions on the maxflow predicate.
            m.setDecisionPriority(-1);

    print("Solving...")

    if Solve():

        def vid(x, y):
            return str(int(y) * width + int(x))

        def reduce_linestring(linestring):
            if len(linestring.coords) < 3:
                return linestring
            coords = [linestring.coords[0]]
            for i, end in enumerate(linestring.coords[2:]):
                start = linestring.coords[i]
                test = linestring.coords[i + 1]
                if not LineString([start, end]).contains(Point(test)):
                    coords.append(test)
            coords.append(linestring.coords[-1])
            return LineString(coords)

        print("Solved!")

        filename = filename.split('.')
        filename[-1] = 'out.pcrt'
        filename = '.'.join(filename)

        nets_coords = []
        for i, net in enumerate(nets):
            nets_coords.append(set())
            for n2 in net[1:]:
                r = reachset[i][n2]
                g = graphs[i]
                path = g.getPath(r)
                for n in path:
                    nets_coords[-1].add(fromGrid[n])

        nets_lines = []
        for i, net_coord in enumerate(nets_coords):
            #print('net_coord:', [vid(x, y) for x, y in net_coord])
            nets_lines.append([])

            lines = []
            for a, b in itertools.combinations(net_coord, 2):
                if Point(a).distance(Point(b)) == 1:
                    lines.append(LineString([a, b]))
            mls = linemerge(MultiLineString(lines))
            if not isinstance(mls, MultiLineString):
                line = reduce_linestring(mls).coords
                #print('line:', [vid(x, y) for x, y in line])
                nets_lines[-1].append(line)
            else:
                for line in mls:
                    line = reduce_linestring(line).coords
                    #print('line:', [vid(x, y) for x, y in line])
                    nets_lines[-1].append(line)

        nets = nets_lines
        with open(filename, 'w') as f:
            print('G', width, height, file=f)
            for net in nets:
                segs = [','.join([vid(x, y) for x, y in net_seg]) for net_seg in net]
                print('N', *segs, file=f)

        print("s SATISFIABLE")
    else:
        print("s UNSATISFIABLE")
        sys.exit(1)

if __name__ == '__main__':
    import sys

    # default argument for MonoSAT; enables the heuristics described in
    # "Routing Under Constraints", FMCAD 2016, A. Nadel
    monosat_args = ['-ruc']

    parser = argparse.ArgumentParser(description='SAT-based, constrained multi-terminal routing')

    parser.add_argument('--use-maxflow', default=0, type=int,
                        choices=range(0,5), help='''Set to >= 1 to enable
                        redundant, over-approximative maximum flow constraints,
                        which can help the solver prune bad solutions early.
                        Options 2,3,4 control heuristic interactions between the
                        flow constraints and the routing constraints in the
                        solver.''')
    parser.add_argument('--separate-graphs', default=2, type=int,
                        choices=range(1,4), help='''This controls the type of
                        constraint that prevents nets from intersecting. All
                        three are reasonable choices.''')
    parser.add_argument('--enforce-separate', default=0, type=int,
                        choices=range(0,4), help='''This controls the type of
                        constraint used to prevent nets from intersecting with
                        each other in the maximum flow constraint, IF maxflow
                        constraints are used.''')
    parser.add_argument('--amo-builtin-size', default=20, type=int, help=
                        '''The largest at-most-one constraint size to manually
                        build instead of using builtin AMO solver''')
    parser.add_argument('--heuristic-edge-weights', default=0, type=int,
                        choices=range(0,2), help='''This enables a heuristic
                        which sets assigned edges to unit weight, to encourage
                        edge-reuse in solutions in the solver.''')

    parser.add_argument('filename', type=str)

    args, unknown = parser.parse_known_args()

    at_most_one_builtin_size=args.amo_builtin_size

    if len(unknown) > 0:
        print("Passing unrecognized arguments to monosat: " + str(unknown))
        monosat_args = unknown

    route_multi(args.filename, monosat_args, args.use_maxflow,
                args.enforce_separate, args.separate_graphs,
                args.heuristic_edge_weights > 0)
