import numpy as np
import shapely.ops as ops
from shapely.geometry import *
from pycircuit.device import *


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
                 segment_clearance=None, via_diameter=None,
                 via_drill=None, via_clearance=None):
        self.parent = net_class
        self._segment_width = segment_width
        self._segment_clearance = segment_clearance
        self._via_diameter = via_diameter
        self._via_drill = via_drill
        self._via_clearance = via_clearance

    def __getattr__(self, attr):
        value = getattr(self, '_' + attr)
        if value is None:
            return getattr(self.parent, attr)
        return value


class Segment(object):
    def __init__(self, net, net_class, start, end, layer):
        self.net = net
        self.net_class = net_class

        self.start = start
        self.end = end
        self.layer = layer

        self.net.segments.append(self)
        self.layer.segments.append(self)

    def width(self):
        return self.net_class.segment_width

    def length(self):
        '''Returns the length of the segment.'''

        return Point(self.start[0:2]).distance(Point(self.end[0:2]))

    def __str__(self):
        return '%s %s' % (str(self.start), str(self.end))


class Via(object):
    def __init__(self, net, net_class, coord, layers):
        self.net = net
        self.net_class = net_class

        self.coord = coord
        self.layers = layers

        self.net.vias.append(self)
        for layer in layers:
            layer.vias.append(self)

    def diameter(self):
        return self.net_class.via_diameter

    def drill(self):
        return self.net_class.via_drill

    def layers(self):
        for layer in self.layers:
            yield layer


class PortAttributes(object):
    def __init__(self, port, pads):
        self.port = port
        self.pads = pads

    def iter_pads(self):
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

    def iter_pads(self):
        '''Iterator over all coordinates belonging to the net.'''

        for port in self.net.iter_ports():
            for location in port.iter_pads():
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

        self.footprint = fp
        for port in self.node.ports:
            pads = [x for x in self.footprint.pads_by_pin(port.pin)]
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


class Layer(object):
    Cu, Ag, Au = list(range(3))
    oz = 34.79

    def __init__(self, name, thickness, material=None):
        # Properties
        self.name = name
        self.thickness = thickness
        self.material = Layer.Cu if material is None else material
        # Stackup
        self.above = None
        self.below = None
        # Elements
        self.packages = []
        self.segments = []
        self.vias = []

    def __str__(self):
        return self.name


class Layers(object):

    def __init__(self, layers):
        for i, layer in enumerate(layers[0:-1]):
            layer.below = layers[i + 1]
        for i, layer in enumerate(layers[1:]):
            layer.above = layers[i]
        self.layers = layers

    def __getitem__(self, index):
        return self.layers[index]

    def __str__(self):
        return str([str(layer) for layer in self.layers])

    @classmethod
    def two_layer_board(cls, oz):
        return cls([
            Layer('top', Layer.oz * oz),
            Layer('bottom', Layer.oz * oz)
        ])

    @classmethod
    def four_layer_board(cls, oz_outer, oz_inner):
        return cls([
            Layer('top', Layer.oz * oz_outer),
            Layer('inner1', Layer.oz * oz_inner),
            Layer('inner2', Layer.oz * oz_inner),
            Layer('bottom', Layer.oz * oz_outer)
        ])


class Pcb(object):
    def __init__(self, circuit, layers, net_class, cost_cm2):
        self.circuit = circuit
        self.layers = layers
        self.net_class = net_class
        self.edge_clearance = net_class.segment_clearance
        self.cost_cm2 = cost_cm2

        for node in self.circuit.iter_nodes():
            node.attrs = NodeAttributes(node)

        for net in self.circuit.iter_nets():
            net.attrs = NetAttributes(net, self)

        # Current position, layer and net used when creating segments and vias.
        self.pos = np.array([0, 0, 1])
        self.layer = self.layers[0]
        self.net = None

    def finalize(self):
        self.courtyards = []
        for node in self.circuit.iter_nodes():
            self.courtyards.append(node.courtyard())
        self.multipolygon = MultiPolygon(self.courtyards)
        self.bounds = self.multipolygon.bounds
        self.width = self.bounds[2] - self.bounds[0]
        self.height = self.bounds[3] - self.bounds[1]
        self.area = self.multipolygon.area
        self.cost = self.area / 100 * self.cost_cm2

    def get_layer(self, name):
        for layer in self.layers:
            if layer.name == name:
                return layer

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
        layer_index = -1 if node.flipped else 0
        layer = self.layers[layer_index]
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

    def via(self, layer, dia=None, drill=None):
        # Move cursor to target layer
        self.layer = self.get_layer(layer)

        net_class = NetClass(self.net_class, via_diameter=dia, via_drill=drill)
        Via(self.net, net_class, self.pos, layers=self.layers)

    def segment(self, dx=0, dy=0, width=None):
        net_class = NetClass(self.net_class, segment_width=width)

        start = self.pos
        self.move(dx, dy)

        segment = Segment(self.net, net_class, start, self.pos, self.layer)

    def segment_to(self, node, pad, width=None):
        net_class = NetClass(self.net_class, segment_width=width)

        start = self.pos
        self.move_to(node, pad)

        Segment(self.net, net_class, start, self.pos, self.layer)

    @classmethod
    def oshpark_4layer(cls, circuit):
        '''
        track width: 5mil (0.127mm)
        track clearance: 5mil (0.127mm)
        drill: 10mil (0.254mm)
        annular ring: 4mil (0.102mm)

        via diameter: 2 * annular ring + drill = 18mil (0.457mm)
        via clearance: track clearance
        '''

        return cls(circuit, Layers.four_layer_board(oz_outer=1, oz_inner=0.5),
                   net_class=NetClass(
                       segment_width=0.15,
                       segment_clearance=0.15,
                       via_drill=0.25,
                       via_diameter=0.5,
                       via_clearance=0.15),
                   cost_cm2=1.5)

    @classmethod
    def oshpark_2layer(cls, circuit):
       '''
       track width: 6mil (0.152mm)
       track clearance: 6mil (0.152mm)
       drill: 10mil (0.254mm)
       annular ring: 5mil (0.127mm)

       via diameter: 2 * annular ring + drill = 20mil (0.508mm)
       via clearance: track clearance
       '''

       return cls(circuit, Layers.two_layer_board(oz=1),
                  net_class=NetClass(
                      segment_width=0.15,
                      segment_clearance=0.15,
                      via_drill=0.25,
                      via_diameter=0.5,
                      via_clearance=0.15),
                  cost_cm2=0.75)
