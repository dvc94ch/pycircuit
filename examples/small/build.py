import small
from pycircuit.build import Builder
from pycircuit.compiler import Compiler
from pycircuit.library.design_rules import oshpark_4layer
from placer import Placer
from router import Router
from pykicad.pcb import Zone


def compile(filein, fileout):
    compiler = Compiler()
    compiler.compile(filein, fileout)


def place(filein, fileout):
    placer = Placer()
    placer.place(filein, fileout)


def route(filein, fileout):
    #router = Router()
    #router.route(filein, fileout)
    with open(fileout, 'w+') as f:
        f.write('G 10 10')


def post_process(pcb, kpcb):
    xmin, ymin, xmax, ymax = pcb.boundary()
    coords = [(xmin, ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin)]

    zone = Zone(net_name='GND', layer='F.Cu',
                polygon=coords, clearance=0.3)

    kpcb.zones.append(zone)
    return kpcb


if __name__ == '__main__':
    Builder('small', small.top, oshpark_4layer,
            compile, place, route, post_process).build()
