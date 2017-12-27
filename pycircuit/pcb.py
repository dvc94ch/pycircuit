import numpy as np
import shapely.ops as ops
from shapely.geometry import *
from pycircuit.circuit import Netlist
from pycircuit.device import Device


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

        self.net.attributes.segments.append(self)
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

        self.net.attributes.vias.append(self)
        for layer in layers:
            layer.vias.append(self)

    def diameter(self):
        return self.net_class.via_diameter

    def drill(self):
        return self.net_class.via_drill

    def layers(self):
        for layer in self.layers:
            yield layer


class AbsolutePad(object):
    def __init__(self, inst, pad, matrix):
        self.inst = inst
        self.pad = pad
        self.location = matrix.dot(pad.location)
        self.size = pad.size

    def __repr__(self):
        return 'pad %s %s' % (self.inst.name, self.pad.name)


class NetAttributes(object):
    def __init__(self, net, pcb):
        self.net = net
        self.net.attributes = self
        self.pcb = pcb

        self.net_class = NetClass(pcb.net_class)
        self.segments = []
        self.vias = []

    def iter_pads(self):
        '''Iterator over all coordinates belonging to the net.'''

        for assign in self.net.assigns:
            for pad in assign.inst.attributes.pads_by_pin(assign.pin):
                yield pad

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


class InstAttributes(object):
    def __init__(self, inst, pcb):
        assert isinstance(inst.device, Device)

        self.inst = inst
        self.inst.attributes = self
        self.pcb = pcb

        self.x = 0
        self.y = 0
        self.angle = 0
        self.flipped = False
        self.matrix = None

    def get_matrix(self):
        '''Returns the pad and courtyard transformation matrix.'''

        transform = np.identity(3)
        if self.flipped:
            transform = Matrix.flip()
        transform = Matrix.rotation(self.angle).dot(transform)
        return Matrix.translation(self.x, self.y).dot(transform)

    def iter_pads(self):
        matrix = self.get_matrix()
        for pad in self.inst.device.package.pads:
            yield AbsolutePad(self.inst, pad, matrix)

    def pad_by_name(self, name):
        matrix = self.get_matrix()
        pad = self.inst.device.package.pad_by_name(name)
        return AbsolutePad(self.inst, pad, matrix)

    def pads_by_pin(self, pin):
        matrix = self.get_matrix()
        for pad in self.inst.device.pads_by_pin(pin):
            yield AbsolutePad(self.inst, pad, matrix)

    def courtyard(self):
        matrix = self.get_matrix()
        crtyd = self.inst.device.package.courtyard.polygon
        return Matrix.transform(crtyd, matrix)

    def place(self, x, y, angle=0, flipped=False):
        '''Places the node.'''

        self.flip(flipped)
        self.rotate(angle)
        self.move(x, y)

    def move(self, x=None, y=None, dx=0, dy=0):
        '''Places the node at (x + dx, y + dy) or if x, y are None moves it
        by (dx, dy).  Invalidates the transformation matrix.'''

        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        self.x += dx
        self.y += dy

    def rotate(self, angle):
        '''Rotates the node by angle.  Invalidates the transformation matrix.'''

        self.angle += angle

    def flip(self, flipped=None):
        '''Flips the node across the y-axis.  Takes an optional flipped argument
        that sets the state explicitly.  Invalidates the transformation
        matrix.'''

        if isinstance(flipped, bool):
            self.flipped = flipped
        else:
            self.flipped = not self.flipped


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
    def __init__(self, netlist, layers, net_class, cost_cm2):
        self.netlist = netlist
        self.layers = layers
        self.net_class = net_class
        self.edge_clearance = net_class.segment_clearance
        self.cost_cm2 = cost_cm2

        for inst in self.netlist.insts:
            inst.attrs = InstAttributes(inst, self)

        for net in self.netlist.nets:
            net.attrs = NetAttributes(net, self)

    def boundary(self):
        courtyards = []
        for inst in self.netlist.insts:
            courtyards.append(inst.attributes.courtyard())
        bounds = MultiPolygon(courtyards).bounds
        left = bounds[0] - self.edge_clearance
        top = bounds[1] - self.edge_clearance
        right = bounds[2] + self.edge_clearance
        bottom = bounds[3] + self.edge_clearance
        return left, top, right, bottom

    def size(self):
        bounds = self.boundary()
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        return width, height

    def area(self):
        size = self.size()
        return size[0] * size[1]

    def cost(self):
        return self.area() / 100 * self.cost_cm2

    def get_layer(self, name):
        for layer in self.layers:
            if layer.name == name:
                return layer
