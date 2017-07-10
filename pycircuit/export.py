import os, sys
import xml.etree.cElementTree as xml
from graphviz import Graph
from pycircuit.circuit import *
from pycircuit.package import *
from pykicad.module import Module as kModule, Pad as kPad, Drill as kDrill
from pykicad.module import Line as kLine, Text as kText
from pykicad.pcb import Pcb as kPcb, Net as kNet
from pykicad.pcb import Segment as kSegment, Via as kVia
from shapely.ops import polygonize

def export(string, filename, extension):
    if filename is None:
        filename = os.path.basename(sys.argv[0])
        filename = os.path.splitext(filename)[0]

    if not filename.endswith(extension):
        filename += extension

    with open(filename, 'w+') as f:
        f.write(string)


def polygon_to_lines(polygon):
    coords = polygon.exterior.coords
    for i in range(len(coords) - 1):
        yield coords[i], coords[i + 1]


### Graphviz
def circuit_to_graph(circuit, graph):
    for node in circuit.nodes:
        if isinstance(node, Node):
            ports = []
            for i, port in enumerate(node.ports):
                ports.append('<p%d> %s' % (i, port.pin.name))

                graph.edge('node' + str(port.node.id) + ':p' + str(i),
                           'net' + str(port.net.id))
                graph.node('net' + str(port.net.id), port.net.name)

            graph.node('node' + str(node.id),
                       '{%s|%s}' % (node.name, '|'.join(ports)),
                       shape='record')
        else:
            sub = Graph(name='cluster' + str(node.id))
            sub.attr(label=node.name)
            graph.subgraph(circuit_to_graph(node.circuit, sub))

    return graph


def export_circuit_to_graphviz(circuit, filename=None):
    dot = circuit_to_graph(circuit, Graph())
    dot.attr(label=circuit.name)

    export(dot.source, filename, '.dot')


### KiCad
def package_from_module(kmodule):
    lines = []
    for elem in kmodule.courtyard():
        # Only Lines are supported in the courtyard at the moment
        assert isinstance(elem, kLine)
        start, end = (elem.start[0], elem.start[1]), (elem.end[0], elem.end[1])
        lines.append((start, end))

    polygons = list(polygonize(lines))
    assert len(polygons) == 1
    coords = list(polygons[0].exterior.coords)

    package = Package(kmodule.name, Courtyard(coords), [])
    for kpad in kmodule.pads:
        drill = None if kpad.drill is None else kpad.drill.size
        package.add_pad(Pad(kpad.name, kpad.at[0], kpad.at[1],
                            size=(kpad.size[0], kpad.size[1]),
                            drill=drill,
                            shape=kpad.shape))
    return package


def package_to_module(package):
    lines = []
    for start, end in polygon_to_lines(package.courtyard.polygon):
        lines.append(kLine(list(start), list(end),
                           layer='F.CrtYd', width=0.05))

    pads = []
    for pad in package.pads:
        pad_at = list(pad.location)
        pad_at[2] = pad.angle

        if pad.drill is None:
            pad_type = 'smd'
            pad_layers = ['F.Cu', 'F.Paste', 'F.Mask']
            drill = None
        else:
            pad_type = 'thru_hole'
            pad_layers = ['*.Cu', 'F.Mask', 'B.Mask']
            drill = kDrill(pad.drill)

        pads.append(kPad(pad.name, type=pad_type, shape=pad.shape,
                         size=list(pad.size), at=pad_at, drill=drill,
                         layers=pad_layers))

    text_radius = package.size()[1] / 2 + 0.5
    ref = kText(type='reference', layer='F.SilkS', thickness=0.15, size=[1, 1],
                text=package.name, at=[0, -text_radius - 0.35])
    value = kText(type='value', layer='F.Fab', thickness=0.15, size=[1, 1],
                  text=package.name, at=[0, text_radius + 0.25])

    return kModule(package.name, layer='F.Cu', attr='smd',
                   pads=pads, lines=lines, texts=[ref, value])


def node_to_module(node):
    kmodule = package_to_module(node.footprint.package)
    if node.flipped:
        kmodule.flip()
    if node.angle is not None:
        kmodule.rotate(node.angle)
    kmodule.place(node.x, node.y)
    kmodule.set_reference(node.name)
    kmodule.set_value(node.device.name)
    return kmodule


def pcb_to_kicad(pcb):
    kpcb = kPcb(title=pcb.circuit.name)

    for node in pcb.circuit.iter_nodes():
        node.kmodule = node_to_module(node)
        kpcb.modules.append(node.kmodule)


    for code, net in enumerate(pcb.circuit.iter_nets()):
        net_name = net.name if not net.name == '' else str(net.id)
        knet = kNet(net_name, code + 1)
        kpcb.nets.append(knet)

        for port in net.ports:
            for pad in port.pads:
                kpcb.module_by_reference(port.node.name).connect(pad.name, knet)

        for seg in net.segments:
            layer = 'F.Cu' if seg.layer == 1 else 'B.Cu'
            kseg = kSegment(start=list(seg.start)[0:2], end=list(seg.end)[0:2],
                            net=knet.code, width=seg.width(), layer=layer)
            kpcb.segments.append(kseg)

        for via in net.vias:
            kvia = kVia(at=list(via.coord)[0:2], net=knet.code,
                        size=via.diameter(), drill=via.drill())
            kpcb.vias.append(kvia)


    return kpcb

def export_pcb(kpcb, filename=None):
    export(str(kpcb), filename, '.kicad_pcb')


# SVG
def package_to_svg(package, ref='', flipped=False):
    trans = 'translate(%f %f)'
    rot = 'rotate(%f)'

    # Package
    package_group = xml.Element('g')

    # Courtyard
    courtyard_group = xml.SubElement(package_group, 'g')
    courtyard = xml.fromstring(package.courtyard.polygon.svg())
    courtyard.attrib['stroke-width'] = '0.05'
    courtyard.attrib['fill-opacity'] = '0'
    courtyard_group.append(courtyard)

    # Pads
    pads_group = xml.SubElement(package_group, 'g')
    for pad in package.pads:
        pad_group = xml.SubElement(pads_group, 'g')
        pad_trans = 'translate(%f %f)' % (pad.location[0], pad.location[1])
        pad_group.attrib['transform'] = pad_trans

        pad_color = 'green' if flipped else 'red'
        if pad.shape == 'rect':
            rect = xml.SubElement(pad_group, 'rect', x='0', y='0', fill=pad_color,
                                  width=str(pad.size[0]), height=str(pad.size[1]))
            rect.attrib['transform'] = rot % -pad.angle + \
                                       trans % (-pad.size[0] / 2, -pad.size[1] / 2)
        elif pad.shape == 'circle':
            circle = xml.SubElement(pad_group, 'circle', cx='0', cy='0',
                                    fill=pad_color, r=str(pad.size[0]))

        pad_label = xml.SubElement(pad_group, 'text', x='0', y='0',
                                   fill='white', dy='.4em')
        pad_label.text = pad.name
        pad_label.attrib['font-size'] = '.2'
        pad_label.attrib['font-family'] = 'Verdana'
        pad_label.attrib['text-anchor'] = 'middle'
        pad_label.attrib['transform'] = int(flipped) * 'scale(1 -1)'

    # Reference
    ref = package.name if ref == '' else ref
    text_radius = package.size()[1] / 2
    text = xml.SubElement(package_group, 'text', x='0', y=str(-text_radius - 0.2))
    text.attrib['font-size'] = '.8'
    text.attrib['font-family'] = 'Verdana'
    text.attrib['text-anchor'] = 'middle'
    text.attrib['transform'] = int(flipped) * 'scale(1 -1)'
    text.text = ref

    return package_group


def export_package_to_svg(package):
    viewbox = (package.courtyard.bounds[0], package.courtyard.bounds[1],
               package.courtyard.width, package.courtyard.height)
    svg = xml.Element('svg', width='100%', height='100%',
                      viewBox='%f %f %f %f' % viewbox,
                      xmlns='http://www.w3.org/2000/svg')

    svg.append(package_to_svg(package))

    tree = xml.ElementTree(svg)
    string = xml.tostring(tree.getroot()).decode('utf-8')
    export(string, package.name, '.svg')


def export_pcb_to_svg(pcb, filename=None):
    trans = 'translate(%f %f)'
    rot = 'rotate(%f)'

    svg = xml.Element('svg', width='100%', height='100%',
                      viewBox='%f %f %f %f' % (pcb.bounds[0] - 1, pcb.bounds[1] - 1,
                                               pcb.width + 2, pcb.height + 2),
                      xmlns='http://www.w3.org/2000/svg')

    for i, ij in pcb.rbs.graph.edges.items():
        for j in ij:
            n1, n2 = pcb.rbs.features[i], pcb.rbs.features[j]
            line = xml.SubElement(svg, 'line', stroke='black',
                                  x1=str(n1.x), y1=str(n1.y),
                                  x2=str(n2.x), y2=str(n2.y))
            line.attrib['stroke-width'] = str(0.02)

    for node in pcb.circuit.iter_nodes():
        package = package_to_svg(node.footprint.package, ref=node.name,
                                 flipped=node.flipped)
        package.attrib['transform'] = trans % (node.x, node.y) + \
                                      rot % -node.angle + \
                                      int(node.flipped) * 'scale(1 -1)'
        svg.append(package)

    for net in pcb.circuit.iter_nets():
        for seg in net.segments:
            if seg.layer == 1:
                layer_color = 'red'
            elif seg.layer == -1:
                layer_color = 'green'

            line = xml.SubElement(svg, 'line', stroke=layer_color,
                                  x1=str(seg.start[0]), y1=str(seg.start[1]),
                                  x2=str(seg.end[0]), y2=str(seg.end[1]))
            line.attrib['stroke-width'] = str(seg.width())

        for via in net.vias:
            xml.SubElement(svg, 'circle', fill='black', r=str(via.diameter() / 2),
                           cx=str(via.coord[0]), cy=str(via.coord[1]))
            xml.SubElement(svg, 'circle', fill='white', r=str(via.drill() / 2),
                           cx=str(via.coord[0]), cy=str(via.coord[1]))


    tree = xml.ElementTree(svg)
    string = xml.tostring(tree.getroot()).decode('utf-8')
    export(string, filename, '.svg')
