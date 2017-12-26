import pykicad as ki
from pycircuit.package import Package, Courtyard, Pad
from pycircuit.pcb import Pcb, Via, Segment, InstAttributes, NetAttributes
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


@extends(InstAttributes)
def to_kicad(self):
    kmodule = self.inst.device.package.to_kicad()
    if self.flipped:
        kmodule.flip()
    if self.angle is not None:
        kmodule.rotate(self.angle)
    kmodule.place(self.x, self.y)
    kmodule.set_reference(self.inst.name)
    kmodule.set_value(self.inst.component.name)
    return kmodule


@extends(Pcb)
def to_kicad(self):
    kpcb = ki.pcb.Pcb(title=self.netlist.name)

    # Add kicad modules
    for inst in self.netlist.insts:
        kpcb.modules.append(inst.attributes.to_kicad())

    # Add kicad nets, segments and vias and connect modules
    for i, net in enumerate(self.netlist.nets):
        # Kicad nets need to have an id > 0
        knet_code = i + 1
        knet = ki.module.Net(net.name, knet_code)
        kpcb.nets.append(knet)

        for abspad in net.attributes.iter_pads():
            kpcb.module_by_reference(abspad.inst.name) \
                .connect(abspad.pad.name, knet)

        for seg in net.attributes.segments:
            layer = 'F.Cu' if seg.layer.name == 'top' else 'B.Cu'
            kseg = ki.pcb.Segment(start=list(seg.start)[0:2],
                                  end=list(seg.end)[0:2],
                                  net=knet_code, width=seg.width(),
                                  layer=layer)
            kpcb.segments.append(kseg)

        for via in net.attributes.vias:
            kvia  = ki.pcb.Via(at=list(via.coord)[0:2],
                               net=knet_code,
                               size=self.diameter(),
                               drill=self.drill())
            kpcb.vias.append(kvia)

    # Add a pcb outline
    left, top, right, bottom = self.boundary()
    outline = [(left, top), (right, top), (right, bottom), (left, bottom)]

    for start, end in polygon_to_lines(outline):
        kline = ki.pcb.Line(list(start), list(end), layer='Edge.Cuts', width=0.15)
        kpcb.lines.append(kline)

    return kpcb
