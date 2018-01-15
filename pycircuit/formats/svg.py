import xml.etree.cElementTree as xml
from pycircuit.formats import extends
from pycircuit.layers import Layer
from pycircuit.package import Package
from pycircuit.pcb import Pcb, InstAttributes
from pycircuit.traces import Via, Segment


class SvgElement(object):
    tag = ''

    def __init__(self, attrs={}):
        self.element = xml.Element(self.tag)
        self.set_attrs(attrs)
        self.children = []

    def set_attrs(self, attrs):
        for k, v in attrs.items():
            if not isinstance(v, str):
                v = str(v)
            self.set_attr(k, v)
        return self

    def set_attr(self, key, value):
        self.element.attrib[key] = value

    def get_attr(self, key):
        return self.element.attrib[key]

    def add_class(self, klass):
        klasses = self.get_attr('class')
        klasses += " " + klass
        self.set_attr('class', klasses)

    def append(self, *children):
        for child in children:
            self.element.append(child.element)
            self.children.append(child)
        return self

    def transform(self, transform):
        if 'transform' in self.element.attrib:
            transform = self.element.attrib['transform'] + transform

        self.element.attrib['transform'] = transform
        return self

    def translate(self, x, y):
        return self.transform('translate(%f %f)' % (x, y))

    def rotate(self, angle):
        return self.transform('rotate(%f)' % angle)

    def scale(self, x, y):
        return self.transform('scale(%f %f)' % (x, y))

    def find(self, tag):
        def find_rec(node, tag):
            for child in node:
                if child.tag == tag:
                    yield child
                for found in find_rec(child, tag):
                    yield found
        return find_rec(self.element, tag)


class SvgRoot(SvgElement):
    tag = 'svg'

    def __init__(self, viewbox, attrs={}):
        attrs['xmlns'] = 'http://www.w3.org/2000/svg'
        attrs['width'] = '100%'
        attrs['height'] = '100%'
        super().__init__(attrs)
        self.viewbox(*viewbox)

    def viewbox(self, left, top, right, bottom):
        return self.set_attrs({
            'viewBox': '%f %f %f %f' % (left, top, right - left, bottom - top)
        })

    def save(self, filename):
        tree = xml.ElementTree(self.element)
        tree.write(filename)


class SvgGroup(SvgElement):
    tag = 'g'

    def __init__(self, klass, *children):
        super().__init__({'class': klass})
        self.append(*children)


class SvgLine(SvgElement):
    tag = 'line'

    def __init__(self, start, end, attrs={}):
        attrs['x1'] = start[0]
        attrs['y1'] = start[1]
        attrs['x2'] = end[0]
        attrs['y2'] = end[1]
        super().__init__(attrs)

class SvgCircle(SvgElement):
    tag = 'circle'

    def __init__(self, radius, attrs={}):
        if not 'cx' in attrs:
            attrs['cx'] = 0
        if not 'cy' in attrs:
            attrs['cy'] = 0
        attrs['r'] = radius
        super().__init__(attrs)


class SvgRect(SvgElement):
    tag = 'rect'

    def __init__(self, size, attrs={}):
        attrs['x'] = -size[0] / 2
        attrs['y'] = -size[1] / 2
        attrs['width'] = size[0]
        attrs['height'] = size[1]
        super().__init__(attrs)


class SvgText(SvgElement):
    tag = 'text'

    def __init__(self, text, attrs={}):
        if not 'x' in attrs:
            attrs['x'] = 0
        if not 'y' in attrs:
            attrs['y'] = 0
        if not 'text-anchor' in attrs:
            attrs['text-anchor'] = 'middle'
        super().__init__(attrs)
        self.element.text = text

    def set_text(self, text):
        self.element.text = text
        return self


class SvgPath(SvgElement):
    tag = 'path'

    def set_coords(self, coords):
        coords = ['{0},{1}'.format(*c) for c in coords]

        path = 'M {0} L {1} z'.format(coords[0], ' L '.join(coords[1:]))
        return self.set_attrs({'d': path})



@extends(Package)
def to_svg(self):
    # Courtyard
    svg_crtyd = SvgGroup('crtyd', SvgPath().set_coords(self.courtyard.coords))

    # Pads
    svg_pads = SvgGroup('pads')
    for pad in self.pads:
        if pad.shape == 'rect':
            svg_pad = SvgRect(pad.size).rotate(-pad.angle)
        elif pad.shape == 'circle':
            svg_pad = SvgCircle(pad.size[0])

        svg_pad.set_attrs({'class': 'pad'})
        svg_label = SvgText(pad.name, {'dy': '.4em'})
        svg_pad_group = SvgGroup('pad-group', svg_pad, svg_label) \
                                 .translate(*pad.location[0:2])

        svg_pads.append(svg_pad_group)

    # Reference
    text_radius = self.size()[1] / 2
    svg_ref = SvgText(self.name, {'y': -text_radius - 0.2})

    return SvgRoot(self.courtyard.bounds) \
        .append(svg_crtyd, svg_pads, svg_ref)


@extends(InstAttributes)
def to_svg(self):
    package = self.inst.device.package.to_svg()
    crtyd, pads, ref = package.children
    ref.set_text(self.inst.name)
    package = SvgGroup('package', crtyd, pads, ref)
    package.translate(self.x, self.y).rotate(-self.angle)
    if self.flipped:
        package.scale(1, -1)
        for text in package.find('text'):
            text.attrib['transform'] = 'scale(1, -1)'

    return package.set_attrs({
        'class': 'package bottom' if self.flipped else 'package top'
    })


@extends(Via)
def to_svg(self):
    return SvgGroup('via',
        SvgCircle(self.diameter() / 2, {
            'class': 'dia'
        }),
        SvgCircle(self.drill() / 2, {
            'class': 'drill'
        })
    ).translate(self.coord[0], self.coord[1])


@extends(Segment)
def to_svg(self):
    return SvgLine(self.start, self.end, {
        'class': 'segment',
        'stroke-width': self.width()
    })


@extends(Layer)
def to_svg(self):
    layer = SvgGroup('layer')
    layer.add_class(self.name)
    for via in self.vias:
        layer.append(via.to_svg())
    for seg in self.segments:
        layer.append(seg.to_svg())
    return layer


@extends(Pcb)
def to_svg(self, path):
    bounds = self.boundary()
    svg = SvgRoot(bounds)

    #graph = SvgGroup('graph')
    #for i, ij in self.rbs.graph.edges.items():
    #    for j in ij:
    #        n1, n2 = self.rbs.features[i], self.rbs.features[j]

    #        graph.append(SvgLine((n1.x, n1.y), (n2.x, n2.y)))
    #svg.append(graph)

    #grid = SvgGroup('grid')
    #grid_size = 0.05
    #grid_width = int(self.width / grid_size + 1)
    #grid_height = int(self.height / grid_size + 1)
    #for ix in range(grid_width):
    #    x = ix * grid_size + bounds[0]
    #    grid.append(SvgLine((x, bounds[1]), (x, bounds[3])))
    #for iy in range(grid_height):
    #    y = iy * grid_size + bounds[1]
    #    grid.append(SvgLine((bounds[0], y), (bounds[2], y)))
    #svg.append(grid)

    for inst in self.netlist.insts:
        svg.append(inst.attributes.to_svg())

    for layer in self.layers:
        svg.append(layer.to_svg())

    svg.save(path)
