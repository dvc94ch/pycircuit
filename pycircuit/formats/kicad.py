import pykicad as ki
from pycircuit.circuit import Node, Net
from pycircuit.package import Package, Courtyard, Pad
from pycircuit.pcb import Pcb, Via, Segment
from pycircuit.formats import extends, polygon_to_lines
from shapely.ops import polygonize


@staticmethod
@extends(Package)
def from_kicad(kmodule):
    lines = []
    for elem in kmodule.courtyard():
        # Only Lines are supported in the courtyard at the moment
        assert isinstance(elem, ki.module.Line)
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


@extends(Package)
def to_kicad(package):
    kmod = ki.module.Module(package.name, layer='F.Cu', attr='smd')

    for start, end in polygon_to_lines(package.courtyard.coords):
        kline = ki.module.Line(list(start), list(end), layer='F.CrtYd',
                               width=0.05)
        kmod.lines.append(kline)

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
            drill = ki.module.Drill(pad.drill)

        kpad = ki.module.Pad(pad.name, type=pad_type, shape=pad.shape,
                             size=list(pad.size), at=pad_at, drill=drill,
                             layers=pad_layers)
        kmod.pads.append(kpad)

    text_radius = package.size()[1] / 2 + 0.5
    ref = ki.module.Text(type='reference', layer='F.SilkS', thickness=0.15,
                         size=[1, 1], text=package.name,
                         at=[0, -text_radius - 0.35])
    value = ki.module.Text(type='value', layer='F.Fab', thickness=0.15,
                           size=[1, 1], text=package.name,
                           at=[0, text_radius + 0.25])
    kmod.texts = [ref, value]

    return kmod


@extends(Node)
def to_kicad(self):
    kmodule = self.footprint.package.to_kicad()
    if self.flipped:
        kmodule.flip()
    if self.angle is not None:
        kmodule.rotate(self.angle)
    kmodule.place(self.x, self.y)
    kmodule.set_reference(self.name)
    kmodule.set_value(self.device.name)
    return kmodule


@extends(Via)
def to_kicad(self):
    return ki.pcb.Via(at=list(self.coord)[0:2], net=self.net.id,
                      size=self.diameter(), drill=self.drill())


@extends(Segment)
def to_kicad(self):
    layer = 'F.Cu' if self.layer.name == 'top' else 'B.Cu'
    return ki.pcb.Segment(start=list(self.start)[0:2],
                          end=list(self.end)[0:2],
                          net=self.net.id, width=self.width(),
                          layer=layer)

@extends(Net)
def to_kicad(self):
    return ki.module.Net(str(self), self.id)


@extends(Pcb)
def to_kicad(pcb):
    kpcb = ki.pcb.Pcb(title=pcb.circuit.name)

    for node in pcb.circuit.iter_nodes():
        kpcb.modules.append(node.to_kicad())


    for net in pcb.circuit.iter_nets():
        knet = net.to_kicad()
        kpcb.nets.append(knet)

        for port in net.iter_ports():
            for pad in port.pads:
                kpcb.module_by_reference(port.node.name).connect(pad.name, knet)

        for seg in net.segments:
            kpcb.segments.append(seg.to_kicad())

        for via in net.vias:
            kpcb.vias.append(via.to_kicad())

    left, top, right, bottom = pcb.outline()
    outline = [(left, top), (right, top), (right, bottom), (left, bottom)]

    for start, end in polygon_to_lines(outline):
        kline = ki.pcb.Line(list(start), list(end), layer='Edge.Cuts', width=0.15)
        kpcb.lines.append(kline)

    return kpcb
