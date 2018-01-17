import numpy as np
import shapely.ops as ops
from shapely.geometry import Point, Polygon
from pycircuit.circuit import Netlist
from pycircuit.device import Device
from pycircuit.outline import Outline, OutlineDesignRules
from pycircuit.layers import Layers
from pycircuit.traces import NetClass, TraceDesignRules


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

    @staticmethod
    def inst_matrix(x, y, angle, flip):
        if flip:
            flip = Matrix.flip()
        else:
            flip = np.identity(3)

        return Matrix.translation(x, y).dot(Matrix.rotation(angle)).dot(flip)



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

        self.layer = pcb.attributes.layers.placement_layers[0]
        self.x = 0
        self.y = 0
        self.angle = 0
        self.matrix = None

    def iter_pads(self):
        for pad in self.inst.device.package.pads:
            yield AbsolutePad(self.inst, pad, self.matrix)

    def pad_by_name(self, name):
        pad = self.inst.device.package.pad_by_name(name)
        return AbsolutePad(self.inst, pad, self.matrix)

    def pads_by_pin(self, pin):
        for pad in self.inst.device.pads_by_pin(pin):
            yield AbsolutePad(self.inst, pad, self.matrix)

    def courtyard(self):
        crtyd = self.inst.device.package.courtyard.polygon
        return Matrix.transform(crtyd, self.matrix)

    def place(self, layer, x, y, angle=0):
        '''Places the node.'''

        self.layer = layer
        self.angle = angle
        self.x = x
        self.y = y
        self.matrix = Matrix.inst_matrix(x, y, angle, layer.flip)

    def to_object(self):
        return {
            self.inst.name: {
                'x': self.x,
                'y': self.y,
                'angle': self.angle,
                'flip': self.layer.flip,
                'layer': self.layer.layer.name,
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

    def to_object(self):
        return {
            'layers': self.layers.to_object(),
            'outline_design_rules': self.outline_design_rules.to_object(),
            'trace_design_rules': self.trace_design_rules.to_object(),
            'cost_cm2': self.cost_cm2,
        }

    @classmethod
    def from_object(cls, obj):
        return cls(Layers.from_object(obj['layers']),
                   OutlineDesignRules.from_object(obj['outline_design_rules']),
                   TraceDesignRules.from_object(obj['trace_design_rules']),
                   obj['cost_cm2'])


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
        bounds = self.outline.polygon.exterior.bounds
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        return width, height

    def area(self):
        return self.outline.polygon.exterior.area

    def cost(self):
        return self.outline.polygon.exterior.area / 100 * self.attributes.cost_cm2

    def to_object(self):
        packages = {}
        insts = {}
        for inst in self.netlist.insts:
            pck = inst.device.package
            packages.update(pck.to_object())
            insts.update(inst.attributes.to_object())

        return {
            'netlist': self.netlist.to_object(),
            'outline': self.outline.to_object(),
            'attributes': self.attributes.to_object(),
            'packages': packages,
            'insts': insts,
        }

    @classmethod
    def from_object(cls, obj):
        pcb = cls(Netlist.from_object(obj['netlist']),
                  Outline.from_object(obj['outline']),
                  PcbAttributes.from_object(obj['attributes']))

        for inst in pcb.netlist.insts:
            inst_obj = obj['insts'][inst.name]
            players = pcb.attributes.layers.placement_layers
            for player in players:
                if player.layer.name == inst_obj['layer']:
                    break
            inst.attributes.place(player, inst_obj['x'], inst_obj['y'],
                                  inst_obj['angle'])

        return pcb
