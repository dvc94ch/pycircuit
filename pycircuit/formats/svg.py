import xml.etree.cElementTree as xml
from pycircuit.formats import extends
from pycircuit.layers import RoutingLayer, PlacementLayer
from pycircuit.package import Package
from pycircuit.outline import *
from pycircuit.pcb import Pcb


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

    def __init__(self, viewbox, attrs={}, style=''):
        attrs['xmlns'] = 'http://www.w3.org/2000/svg'
        attrs['width'] = '100%'
        attrs['height'] = '100%'
        super().__init__(attrs)
        self.viewbox(*viewbox)

        style_node = xml.Element('style')
        style_node.text = style
        self.element.append(style_node)

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
    svg_pad_labels = SvgGroup('pad-labels')

    for pad in self.pads:
        if pad.shape == 'rect':
            svg_pad = SvgRect(pad.size)
        elif pad.shape == 'circle':
            svg_pad = SvgCircle(pad.size[0] / 2)
        else:
            raise Exception('Unknown pad shape')

        svg_pad.set_attrs({'class': 'pad'})
        svg_pad.translate(*pad.location[0:2]).rotate(-pad.angle)
        svg_pads.append(svg_pad)

        svg_label = SvgText(pad.name, {'dy': '.4em'})
        svg_label.set_attrs({'class': 'pad-label'})
        svg_label.translate(*pad.location[0:2])
        svg_pad_labels.append(svg_label)

    # Reference
    text_radius = self.size()[1] / 2
    svg_ref = SvgText(self.name, {'class': 'ref', 'y': -text_radius - 0.2})

    return SvgRoot(self.courtyard.bounds) \
        .append(svg_crtyd, svg_pads, svg_pad_labels, svg_ref)


@extends(PlacementLayer)
def to_svg(self):
    def transform(elem, x, y, angle, no_flip=False):
        elem.translate(x, y).rotate(-angle)
        if not no_flip and self.flip:
            elem.scale(1, -1)
        return elem

    pads_layer = SvgGroup('pads_layer')
    pad_labels_layer = SvgGroup('pad_labels_layer')
    crtyd_layer = SvgGroup('crtyd_layer')
    ref_layer = SvgGroup('ref_layer')

    for inst in self.insts:
        package = inst.device.package.to_svg()
        crtyd, pads, pad_labels, ref = package.children
        ref.set_text(inst.name)

        x, y, angle = inst.attributes.x, inst.attributes.y, inst.attributes.angle

        pads_layer.append(transform(pads, x, y, angle))
        crtyd_layer.append(transform(crtyd, x, y, angle))
        ref_layer.append(transform(ref, x, y, angle, no_flip=True))
        pad_labels_layer.append(transform(pad_labels, x, y, angle, no_flip=True))

    layer = SvgGroup('layer')
    layer.add_class(self.layer.name)
    layer.append(pads_layer)
    layer.append(pad_labels_layer)
    layer.append(crtyd_layer)
    layer.append(ref_layer)

    return layer


@extends(RoutingLayer)
def to_svg(self):
    layer = SvgGroup('layer')
    layer.add_class(self.layer.name)

    for via in self.vias:
        svia = SvgGroup('via',
                        SvgCircle(via.diameter / 2, {
                            'class': 'dia'
                        }),
                        SvgCircle(via.drill / 2, {
                            'class': 'drill'
                        })
        ).translate(via.coord[0], via.coord[1])
        layer.append(svia)

    for seg in self.segments:
        sseg = SvgLine(seg.start, seg.end, {
            'class': 'seg',
            'stroke-width': seg.width
        })
        layer.append(sseg)

    return layer


@extends(Outline)
def to_svg(self):
    layer = SvgGroup('outline')
    layer.append(SvgPath().set_coords(self.polygon.exterior.coords))
    for f in self.features:
        if isinstance(f, Hole):
            f = SvgCircle(f.drill_size / 2, {
                'cx': f.position[0],
                'cy': f.position[1]
            })
        layer.append(f)
    return layer


@extends(Pcb)
def to_svg(self, path):
    bounds = self.outline.polygon.exterior.bounds
    with open('../../viewer/css/pcb.svg.css') as f:
        style = f.read()
    svg = SvgRoot(bounds, style=style)

    top = self.attributes.layers.placement_layers[0]
    bottom = self.attributes.layers.placement_layers[-1]

    svg.append(bottom.to_svg())

    for layer in reversed(self.attributes.layers.routing_layers):
        svg.append(layer.to_svg())

    svg.append(top.to_svg())

    svg.append(self.outline.to_svg())

    svg.save(path)
