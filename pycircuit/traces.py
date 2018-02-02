from pycircuit.circuit import UID


class TraceDesignRules(object):
    def __init__(self, min_width, min_clearance,
                 min_annular_ring, min_drill,
                 blind_vias_allowed, burried_vias_allowed,
                 min_edge_clearance):
        self.min_width = min_width
        self.min_clearance = min_clearance
        self.min_annular_ring = min_annular_ring
        self.min_drill = min_drill
        self.blind_vias_allowed = blind_vias_allowed
        self.burried_vias_allowed = burried_vias_allowed
        self.min_edge_clearance = min_edge_clearance

    def to_netclass(self):
        return NetClass(segment_width=self.min_width,
                        segment_clearance=self.min_clearance,
                        via_drill=self.min_drill,
                        via_diameter=self.min_annular_ring * 2 + self.min_drill,
                        via_clearance=self.min_clearance,
                        blind_vias=self.blind_vias_allowed,
                        burried_vias=self.burried_vias_allowed)

    def to_object(self):
        return {
            'min_width': self.min_width,
            'min_clearance': self.min_clearance,
            'min_annular_ring': self.min_annular_ring,
            'min_drill': self.min_drill,
            'blind_vias_allowed': self.blind_vias_allowed,
            'burried_vias_allowed': self.burried_vias_allowed,
            'min_edge_clearance': self.min_edge_clearance,
        }

    @classmethod
    def from_object(cls, obj):
        return cls(obj['min_width'], obj['min_clearance'], obj['min_annular_ring'],
                   obj['min_drill'], obj['blind_vias_allowed'],
                   obj['burried_vias_allowed'], obj['min_edge_clearance'])


class TraceDesignRuleError(Exception):
    pass


class NetClass(object):
    def __init__(self, net_class=None, segment_width=None,
                 segment_clearance=None, via_diameter=None,
                 via_drill=None, via_clearance=None,
                 blind_vias=None, burried_vias=None,
                 length_match=None, uid=None):
        self.uid = uid
        if uid is None:
            self.uid = UID.uid()
        self.parent = net_class
        self._segment_width = segment_width
        self._segment_clearance = segment_clearance
        self._via_diameter = via_diameter
        self._via_drill = via_drill
        self._via_clearance = via_clearance
        self._blind_vias = blind_vias
        self._burried_vias = burried_vias

    def __getattr__(self, attr):
        value = getattr(self, '_' + attr)
        if value is None:
            return getattr(self.parent, attr)
        return value

    def to_object(self):
        obj = {'uid': self.uid}
        if self.parent is not None:
            obj['net_class'] = self.parent.uid
        if self._segment_width is not None:
            obj['segment_width'] = self._segment_width
        if self._segment_clearance is not None:
            obj['segment_clearance'] = self._segment_clearance
        if self._via_diameter is not None:
            obj['via_diameter'] = self._via_diameter
        if self._via_drill is not None:
            obj['via_drill'] = self._via_drill
        if self._via_clearance is not None:
            obj['via_clearance'] = self._via_clearance
        if self._blind_vias is not None:
            obj['blind_vias'] = self._blind_vias
        if self._burried_vias is not None:
            obj['burried_vias'] = self._burried_vias
        return obj

    @classmethod
    def from_object(cls, obj, pcb):
        if 'net_class' in obj:
            obj['net_class'] = pcb.net_class_by_uid(obj['net_class'])
        return cls(**obj)


class Segment(object):
    def __init__(self, net, start, end, routable_layer):
        self.net = net

        self.start = start
        self.end = end
        self.layer = routable_layer

        self.net.attributes.segments.append(self)
        self.layer.segments.append(self)

    def __getattr__(self, attr):
        if attr == 'width':
            return self.net.attributes.net_class.segment_width
        elif attr == 'length':
            return Point(self.start[0:2]).distance(Point(self.end[0:2]))

    def __str__(self):
        return '%s %s' % (str(self.start), str(self.end))

    def check(self, design_rules):
        # TODO: check clearance and edge_clearance
        if self.width < design_rules.min_width:
            raise TraceDesignRuleError('Trace width needs to be larger than %d'
                                       % design_rules.min_width)

    def to_object(self):
        return {
            'net': self.net.uid,
            'start': self.start,
            'end': self.end,
            'layer': self.layer.layer.name,
        }

    @classmethod
    def from_object(cls, obj, pcb):
        net = pcb.netlist.net_by_uid(obj['net'])
        rlayer = pcb.attributes.layers.rlayer_by_name(obj['layer'])
        return cls(net, obj['start'], obj['end'], rlayer)


class Via(object):
    def __init__(self, net, position, routable_layers):
        self.net = net

        self.position = position

        self.is_blind = False
        self.is_burried = False

        self.net.attributes.vias.append(self)
        for layer in layers:
            layer.vias.append(self)

    def __getattr__(self, attr):
        if attr == 'drill':
            return self.net.attributes.net_class.via_drill
        elif attr == 'diameter':
            return self.net.attributes.net_class.via_diameter

    def iter_layers(self):
        for layer in self.layers:
            yield layer

    def check(self, design_rules):
        # TODO: check clearance and edge_clearance
        if self.drill < design_rules.min_drill:
            raise TraceDesignRuleError('Via drill needs to be larger than %d'
                                       % design_rules.min_drill)
        min_diameter = design_rules.min_drill + 2 * design_rules.min_annular_ring
        if self.diameter < min_diameter:
            raise TraceDesignRuleError('Via diameter needs to be larger than %d'
                                       % min_diameter)
        if self.is_blind and not design_rules.blind_vias_allowed:
            raise TraceDesignRuleError('No blind vias allowed')
        if self.is_burried and not design_rules.burried_vias_allowed:
            raise TraceDesignRuleError('No burried vias allowed')

    def to_object(self):
        return {
            'net': self.net.uid,
            'x': float(self.position[0]),
            'y': float(self.position[1]),
            'layers': [layer.layer.name for layer in self.layers],
        }

    @classmethod
    def from_object(cls, obj, pcb):
        net = pcb.netlist.net_by_uid(obj['net'])
        net_class = pcb.net_class_by_uid(obj['net_class'])
        layers = [pcb.attributes.layers.rlayer_by_name(name)
                  for layer in obj['layers']]
        return cls(net, net_class, np.array(obj['x'], obj['y']), rlayers)
