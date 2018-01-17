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
                 blind_vias=True, burried_vias=True,
                 length_match=False):
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


class Segment(object):
    def __init__(self, net, net_class, start, end, routable_layer):
        self.net = net
        self.net_class = net_class

        self.start = start
        self.end = end
        self.layer = routable_layer

        self.net.attributes.segments.append(self)
        self.layer.segments.append(self)

    def __getattr__(self, attr):
        if attr == 'width':
            return self.net_class.segment_width
        elif attr == 'length':
            return Point(self.start[0:2]).distance(Point(self.end[0:2]))

    def __str__(self):
        return '%s %s' % (str(self.start), str(self.end))

    def check(self, design_rules):
        # TODO: check clearance and edge_clearance
        if self.width < design_rules.min_width:
            raise TraceDesignRuleError('Trace width needs to be larger than %d'
                                       % design_rules.min_width)


class Via(object):
    def __init__(self, net, net_class, position, routable_layers):
        self.parent = None
        self.net = net
        self.net_class = net_class

        self.position = position
        self.start_layer = start_layer
        self.end_layer = end_layer

        self.is_blind = False
        self.is_burried = False

        self.net.attributes.vias.append(self)
        for layer in layers:
            layer.vias.append(self)

    def __getattr__(self, attr):
        if attr == 'drill':
            return self.net_class.via_drill
        elif attr == 'diameter':
            return self.net_class.via_diameter

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
