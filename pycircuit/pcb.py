import numpy as np
import shapely.ops as ops
from shapely.geometry import *
from pycircuit.circuit import Netlist
from pycircuit.device import Device
from pycircuit.outline import Outline
from pycircuit.traces import NetClass


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

    def to_object(self):
        top = self.pcb.attributes.layers.top
        bottom = self.pcb.attributes.layers.bottom
        return {
            self.inst.name: {
                'x': self.x,
                'y': self.y,
                'angle': self.angle,
                'flipped': self.flipped,
                'layer': bottom.name if self.flipped else top.name,
                'package': self.inst.device.package.name,
            }
        }


class PcbAttributes(object):
    def __init__(self, layers, outline_design_rules, trace_design_rules,
                 cost_cm2):
        self.layers = layers
        self.outline_design_rules = outline_design_rules
        self.trace_design_rules = trace_design_rules
        self.cost_cm2 = cost_cm2


class Pcb(object):
    def __init__(self, netlist, outline, attributes):
        assert isinstance(netlist, Netlist)
        assert isinstance(outline, Outline)
        assert isinstance(attributes, PcbAttributes)

        self.netlist = netlist
        self.outline = outline
        self.attributes = attributes
        self.net_class = attributes.trace_design_rules.to_netclass()

        for inst in self.netlist.insts:
            inst.attrs = InstAttributes(inst, self)

        for net in self.netlist.nets:
            net.attrs = NetAttributes(net, self)

    def size(self):
        bounds = self.outline.exterior.bounds
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        return width, height

    def area(self):
        return self.outline.exterior.area - self.outline.interior.area

    def cost(self):
        return self.outline.exterior.area / 100 * self.attributes.cost_cm2

    def get_layer_by_name(self, name):
        for layer in self.layers:
            if layer.name == name:
                return layer

    def to_object(self):
        packages = {}
        insts = {}
        for inst in self.netlist.insts:
            pck = inst.device.package
            packages.update(pck.to_object())
            insts.update(inst.attributes.to_object())

        return {
            'outline': self.outline.to_object(),
            'layers': self.attributes.layers.to_object(),
            'packages': packages,
            'insts': insts,
        }
