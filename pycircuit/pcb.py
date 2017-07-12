import numpy as np
import shapely.ops as ops
from shapely.geometry import *
from pycircuit.footprint import *
from pycircuit.rbs import *


class Matrix(object):
    '''A collection of functions for generating transformation
    matrices with numpy and applying them to shapely geometry.'''

    @staticmethod
    def translation(x, y):
        '''Returns a translation matrix.'''

        return np.array([[1, 0, x],
                         [0, 1, y],
                         [0, 0, 1]])

    @staticmethod
    def rotation(angle):
        '''Returns a rotation matrix for a coordinate system with an inverted
        y-axis [oo, -oo].  The unit of angle is degrees.'''

        theta = (-angle / 180) * np.pi
        return np.array([[np.cos(theta), -np.sin(theta), 0],
                         [np.sin(theta),  np.cos(theta), 0],
                         [0, 0, 1]])

    @staticmethod
    def flip():
        '''Returns a matrix that mirrors accross the y-axis.'''

        return np.array([[1, 0, 0],
                         [0, -1, 0],
                         [0, 0, 1]])

    @staticmethod
    def transform(geometry, matrix):
        '''Returns a new shapely geometry transformed with matrix.'''

        def apply_matrix(xs, ys):
            res_xs, res_ys = [], []
            for x, y in zip(xs, ys):
                vec = np.array([x, y, 1])
                res = matrix.dot(np.array([x, y, 1]))
                res_xs.append(res[0])
                res_ys.append(res[1])
            return (res_xs, res_ys)

        return ops.transform(apply_matrix, geometry)


class NetClass(object):
    def __init__(self, net_class=None, segment_width=None,
                 via_diameter=None, via_drill=None):
        self.parent = net_class
        self._segment_width = segment_width
        self._via_diameter = via_diameter
        self._via_drill = via_drill

    def segment_width(self):
        if self._segment_width is None:
            return self.parent.segment_width()
        return self._segment_width

    def via_diameter(self):
        if self._via_diameter is None:
            return self.parent.via_diameter()
        return self._via_diameter

    def via_drill(self):
        if self._via_drill is None:
            return self.parent.via_drill()
        return self._via_drill


class Segment(object):
    def __init__(self, net, net_class, start, end, layer):
        self.net = net
        self.net_class = net_class

        self.start = start
        self.end = end
        self.layer = layer

    def width(self):
        return self.net_class.segment_width()

    def length(self):
        '''Returns the length of the segment.'''

        return Point(self.start[0:2]).distance(Point(self.end[0:2]))


class Via(object):
    def __init__(self, net, net_class, coord, layer1=1, layer2=-1):
        self.net = net
        self.net_class = net_class

        self.coord = coord
        self.layer1 = layer1
        self.layer2 = layer2

    def diameter(self):
        return self.net_class.via_diameter()

    def drill(self):
        return self.net_class.via_drill()


class PortAttributes(object):
    def __init__(self, port, pads):
        self.port = port
        self.pads = pads

    def pad_locations(self):
        '''Returns an iterator over the ports coordinates.'''

        for pad in self.pads:
            yield self.port.node.pad_location(pad)


class NetAttributes(object):
    def __init__(self, net, pcb):
        self.net = net
        self.pcb = pcb

        # topological information
        self.routes = []
        # geometric information
        self.net_class = NetClass(pcb.net_class)
        self.segments = []
        self.vias = []

    def pad_locations(self):
        '''Iterator over all coordinates belonging to the net.'''

        for port in self.net.ports:
            for location in port.pad_locations():
                yield location

    def bounds(self):
        '''Returns a tuple (min_x, min_y, max_x, max_y) of all the coordinates
        connected by the net.  Useful for placement algorithms.'''

        return asMultiPoint(list(self.pad_locations())).bounds

    def size(self):
        '''Returns a tuple (width, height) of the net.  Useful for placement
        algorithms.'''

        min_x, min_y, max_x, max_y = self.bounds()
        return max_x - min_x, max_y - min_y

    def half_perimeter_length(self):
        '''Returns an estimation of the wire length from the boundary
        of it's coordinates.  Useful for placement algorithms.'''

        return sum(self.size())

    def length(self):
        '''Returns the geometric length of the net by summing
        the length of it's segments.'''

        length = 0
        for segment in self.segments:
            length += segment.length()
        return length


class NodeAttributes(object):
    def __init__(self, node):
        self.node = node
        self.x = 0
        self.y = 0
        self.angle = 0
        self.flipped = False
        self.matrix = None

        self.footprint = None
        self.power = 0

    def set_footprint(self, fp):
        '''Sets the footprint of a node and assigns pads to all ports.'''

        self.footprint = Footprint.footprint_by_name(fp)
        for port in self.node.ports:
            pads = self.footprint.pads_by_pin(port.pin)
            port.attrs = PortAttributes(self.node, pads)

    def set_power(self, power):
        '''Sets the maximum power dissipated by the node.  Useful for placement
        algorithms.'''

        self.power = power

    def pad_by_name(self, pad):
        '''Finds a pad by it's name.'''

        return self.footprint.package.pad_by_name(pad)

    def pad_location(self, pad):
        '''Computes the location of a pad using the transformation matrix.'''

        if self.matrix is None:
            self.update_matrix()
        return self.matrix.dot(pad.location)

    def place(self, x, y, angle=0, flipped=False):
        '''Places the node.'''

        self.flip(flipped)
        self.rotate(angle)
        self.move(x, y)

    def move(self, x=None, y=None, dx=0, dy=0):
        '''Places the node at (x + dx, y + dy) or if x, y are None moves it
        by (dx, dy).  Invalidates the transformation matrix.'''

        self.matrix = None
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        self.x += dx
        self.y += dy

    def rotate(self, angle):
        '''Rotates the node by angle.  Invalidates the transformation matrix.'''

        self.matrix = None
        self.angle += angle

    def flip(self, flipped=None):
        '''Flips the node across the y-axis.  Takes an optional flipped argument
        that sets the state explicitly.  Invalidates the transformation
        matrix.'''

        self.matrix = None
        if isinstance(flipped, bool):
            self.flipped = flipped
        else:
            self.flipped = not self.flipped

    def update_matrix(self):
        '''Updates the transformation matrix.'''

        transform = np.identity(3)
        if self.flipped:
            transform = Matrix.flip()
        transform = Matrix.rotation(self.angle).dot(transform)
        self.matrix = Matrix.translation(self.x, self.y).dot(transform)

    def area(self):
        '''Returns the area of the courtyard.'''

        return self.footprint.package.courtyard.polygon.area

    def courtyard(self):
        '''Returns a Polygon of the courtyard after applying the transformation
        matrix.'''

        if self.matrix is None:
            self.update_matrix()
        crtyd = self.footprint.package.courtyard.polygon
        return Matrix.transform(crtyd, self.matrix)

    def intersection(self, node):
        '''Returns a Polygon of the intersection of the courtyard with a
        node.'''

        return self.courtyard().intersection(node.courtyard())

    def intersects(self, node):
        '''Returns True when the courtyard intersects with a node.'''

        return not self.intersection(node).is_empty


class Pcb(object):
    def __init__(self, circuit):
        self.circuit = circuit
        self.net_class = NetClass(segment_width=0.25, via_diameter=0.8, via_drill=0.6)
        self.layers = 1
        self.edge_clearance = 2

        # Current position, layer and net used when creating segments and vias.
        self.pos = np.array([0, 0, 1])
        self.layer = 1
        self.net = None

        # Topological representation
        self.rbs = RubberBandSketch()

        self.courtyards = []

        for node in self.circuit.iter_nodes():
            self.courtyards.append(node.courtyard())

            for pad in node.footprint.package.pads:
                loc = node.pad_location(pad)
                pin = node.footprint.pin_by_pad(pad)
                port = node.port_by_pin(pin)
                net = None if port is None else port.net

                self.rbs.add_feature(RBSFeature(loc[0], loc[1], net, node, pad))

        for net in self.circuit.iter_nets():
            net.attrs = NetAttributes(net, self)

        self.multipolygon = MultiPolygon(self.courtyards)
        self.bounds = self.multipolygon.bounds
        self.width = self.bounds[2] - self.bounds[0]
        self.height = self.bounds[3] - self.bounds[1]

        self.rbs.triangulate()

    def outline(self):
        left = self.bounds[0] - self.edge_clearance
        top = self.bounds[1] - self.edge_clearance
        right = self.bounds[2] + self.edge_clearance
        bottom = self.bounds[3] + self.edge_clearance
        return left, top, right, bottom

    def resolve_pad(self, node, pad):
        node = self.circuit.node_by_name(node)
        pad = node.pad_by_name(pad)
        pin = node.footprint.pin_by_pad(pad)
        net = node.port_by_pin(pin).net
        layer = -1 if node.flipped else 1
        location = node.pad_location(pad)
        return {
            'node': node,
            'pad': pad,
            'pin': pin,
            'net': net,
            'layer': layer,
            'location': location
        }

    def distance(self, node, pad):
        x, y, z = self.resolve_pad(node, pad)['location']
        return np.array([x, y, 0]) - self.pos

    def move_to(self, node, pad):
        pad_info = self.resolve_pad(node, pad)
        self.pos = pad_info['location']
        self.layer = pad_info['layer']
        self.net = pad_info['net']

    def move(self, dx=0, dy=0):
        # Avoid in place updating
        self.pos = self.pos + np.array([dx, dy, 1])

    def via(self, dia=None, drill=None, layer=None):
        if layer is None:
            layer = self.layer * -1
        assert abs(layer) > 0
        self.layers = max(abs(layer), self.layers, 2)

        net_class = NetClass(self.net_class, via_diameter=dia, via_drill=drill)
        via = Via(self.net, net_class, self.pos,
                  layer1=self.layer, layer2=layer)
        self.net.vias.append(via)
        self.layer = layer

    def segment(self, dx=0, dy=0, width=None):
        net_class = NetClass(self.net_class, segment_width=width)

        start = self.pos
        self.move(dx, dy)

        segment = Segment(self.net, net_class, start, self.pos, self.layer)
        self.net.segments.append(segment)

    def segment_to(self, node, pad, width=None):
        net_class = NetClass(self.net_class, segment_width=width)

        start = self.pos
        self.move_to(node, pad)

        segment = Segment(self.net, net_class, start, self.pos, self.layer)
        self.net.segments.append(segment)
