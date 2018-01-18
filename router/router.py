import itertools
from shapely.geometry import Point, LineString, MultiLineString
from shapely.ops import linemerge
from pycircuit.pcb import Pcb
from pycircuit.traces import Segment
from router.monosat import route_multi


class Router(object):
    def __init__(self, grid_size=0.05, allow_45=False,
                 monosat_args=[], amo_builtin_size=20, heuristic_edge_weights=0,
                 graph_separation_enforcement=2, maxflow_enforcement_level=0,
                 flowgraph_separation_enforcement=0):
        '''Initialize Router with settings.

        Keyword arguments:
        amo-builtin-size -- (default 20)
            The largest at-most-one constraint size to manually build instead of
            using builtin AMO solver.

        heuristic-edge-weights -- (default 0) (choices range(0, 2))
            This enables a heuristic which sets assigned edges to unit weight,
            to encourage edge-reuse in solutions in the solver.

        graph-separation-enforcement -- (default 2) (choices range(1, 4))
            This controls the type of constraint that prevents nets from
            intersecting. All three are reasonable choices.

        maxflow-enforcement-level -- (default 0) (choices range(0, 5))
            Set to >= 1 to enable redundant, over-approximative maximum flow
            constraints, which can help the solver prune bad solutions early.
            Options 2, 3, 4 control heuristic interactions between the flow
            constraints and the routing constraints in the solver.

        flowgraph-separation-enforcement -- (default 0) (choices range(0, 4))
            This controls the type of constraint used to prevent nets from
            intersecting with each other in the maximum flow constraint, IF
            maxflow constraints are used.
        '''

        self.grid_size = grid_size
        self.allow_45 = allow_45

        # default argument for MonoSAT; enables the heuristics described in
        # "Routing Under Constraints", FMCAD 2016, A. Nadel
        monosat_args.append('-ruc')

        assert heuristic_edge_weights in range(0, 2)
        assert graph_separation_enforcement in range(1, 4)
        assert maxflow_enforcement_level in range(0, 5)
        assert flowgraph_separation_enforcement in range(0, 4)

        self.monosat_args = monosat_args
        self.amo_builtin_size = amo_builtin_size
        self.heuristic_edge_weights = heuristic_edge_weights
        self.graph_separation_enforcement = graph_separation_enforcement
        self.maxflow_enforcement_level = maxflow_enforcement_level
        self.flowgraph_separation_enforcement = flowgraph_separation_enforcement

    def route(self, filein, fileout):
        pcb = Pcb.from_file(filein)

        width, height, bounds = *pcb.size(), pcb.outline.polygon.exterior.bounds
        grid_width, grid_height = int(width / self.grid_size + 1), \
                                  int(height / self.grid_size + 1)

        def pos_to_grid(x, y):
            return (
                int((x - bounds[0]) / self.grid_size),
                int((y - bounds[1]) / self.grid_size)
            )

        def grid_to_pos(x, y):
            return (
                x * self.grid_size + bounds[0],
                y * self.grid_size + bounds[1]
            )


        nets = []
        for net in pcb.netlist.nets:
            nets.append([])
            for pad in net.attributes.iter_pads():
                nets[-1].append(pos_to_grid(*pad.location[0:2]))
        #for inst in self.netlist.insts:
        #    for pad in inst.attributes.iter_pads():
        #        loc = grid(pad.location[0] - pad.size[0] / 2,
        #                   pad.location[1] - pad.size[1] / 2)
        #        width = int(math.ceil(pad.size[0] / grid_size))
        #        height = int(math.ceil(pad.size[1] / grid_size))
        #        vids = []
        #        for x in range(width):
        #            for y in range(height):
        #                vids.append(vid(x + loc[0], y + loc[1]))
                #print('C', ' '.join(vids), file=f)

        ## ROUTE ##
        nets = route_multi(self, grid_width, grid_height, nets)



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



        net_segments = []
        for i, coords in enumerate(nets):
            net_segments.append([])

            lines = []
            for a, b in itertools.combinations(coords, 2):
                if Point(a).distance(Point(b)) == 1:
                    lines.append(LineString([a, b]))
            mls = linemerge(MultiLineString(lines))
            if not isinstance(mls, MultiLineString):
                line = reduce_linestring(mls).coords
                net_segments[-1].append(line)
            else:
                for line in mls:
                    line = reduce_linestring(line).coords
                    net_segments[-1].append(line)

        for segments, net in zip(net_segments, pcb.netlist.nets):
            for seg in segments:
                for i, coord in enumerate(seg[1:]):
                    start = grid_to_pos(*seg[i])
                    end = grid_to_pos(*coord)
                    Segment(net, start, end, pcb.attributes.layers.routing_layers[0])

        pcb.to_file(fileout)


if __name__ == '__main__':
    import sys

    monosat_args = ['-ruc']

    parser = argparse.ArgumentParser(description='SAT-based, constrained multi-terminal routing')


    parser.add_argument('--amo-builtin-size', default=20, type=int, help=
                        '''The largest at-most-one constraint size to manually
                        build instead of using builtin AMO solver''')
    parser.add_argument('--heuristic-edge-weights', default=0, type=int,
                        choices=range(0,2), help='''This enables a heuristic
                        which sets assigned edges to unit weight, to encourage
                        edge-reuse in solutions in the solver.''')
    parser.add_argument('--graph-separation-enforcement', default=2, type=int,
                        choices=range(1,4), help='''This controls the type of
                        constraint that prevents nets from intersecting. All
                        three are reasonable choices.''')
    parser.add_argument('--maxflow-enforcement-level', default=0, type=int,
                        choices=range(0,5), help='''Set to >= 1 to enable
                        redundant, over-approximative maximum flow constraints,
                        which can help the solver prune bad solutions early.
                        Options 2,3,4 control heuristic interactions between the
                        flow constraints and the routing constraints in the
                        solver.''')
    parser.add_argument('--flowgraph-separation-enforcement', default=0, type=int,
                        choices=range(0,4), help='''This controls the type of
                        constraint used to prevent nets from intersecting with
                        each other in the maximum flow constraint, IF maxflow
                        constraints are used.''')

    parser.add_argument('filein', type=str)
    parser.add_argument('fileout', type=str)

    args, unknown = parser.parse_known_args()

    if len(unknown) > 0:
        print("Passing unrecognized arguments to monosat: " + str(unknown))
        monosat_args = unknown

    router = Router(monosat_args,
                    amo_builtin_size=amo_builtin_size,
                    heuristic_edge_weights=heuristic_edge_weights,
                    graph_separation_enforcement=graph_separation_enforcement,
                    maxflow_enforcement_level=maxflow_enforcement_level,
                    flowgraph_separation_enforcement=flowgraph_separation_enforcement)

    router.route(args.filein, args.fileout)
