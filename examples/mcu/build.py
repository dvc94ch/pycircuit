import small
from pycircuit.build import Builder
from pycircuit.library.design_rules import oshpark_4layer
from placer import Placer
from pykicad.pcb import Zone


def place(filein, fileout):
    placer = Placer()
    placer.place(filein, fileout)

def post_process(pcb, kpcb):
    xmin, ymin, xmax, ymax = pcb.boundary()
    coords = [(xmin, ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin)]

    zone = Zone(net_name='GND', layer='F.Cu',
                polygon=coords, clearance=0.3)

    kpcb.zones.append(zone)
    return kpcb


if __name__ == '__main__':
    Builder(small.top(), oshpark_4layer,
            place=place, post_process=post_process).build()
