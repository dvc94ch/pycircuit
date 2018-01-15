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


class NetClass(object):

    def __init__(self, net_class=None, segment_width=None,
                 segment_clearance=None, via_diameter=None,
                 via_drill=None, via_clearance=None,
                 blind_vias=True, burried_vias=True):
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
