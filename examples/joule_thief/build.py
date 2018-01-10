import joule_thief
from pycircuit.build import Builder
from pycircuit.library.design_rules import oshpark_4layer
from placer import Placer
from router import Router
from pykicad.pcb import Zone


'''
def sim():
    import ngspyce as ng
    import numpy as np
    from matplotlib import pyplot as plt
    netlist = Builder(top()).get_netlist()
    netlist.to_spice('joule_thief.sp')
    ng.source('joule_thief.sp')
    ng.cmd('tran 1us 500us')

    print('\n'.join(ng.vector_names()))
    time, tp1 = map(ng.vector, ['time', 'V(VOUT)'])
    plt.plot(time, tp1, label='VOUT')
    plt.legend()
    plt.show()
'''

def place(filein, fileout):
    placer = Placer()
    placer.place(filein, fileout)


def route(filein, fileout):
    router = Router()
    router.route(filein, fileout)


def post_process(pcb, kpcb):
    xmin, ymin, xmax, ymax = pcb.boundary()
    coords = [(xmin, ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin)]

    zone = Zone(net_name='GND', layer='F.Cu',
                polygon=coords, clearance=0.3)

    kpcb.zones.append(zone)
    return kpcb


if __name__ == '__main__':
    Builder(joule_thief.top(), oshpark_4layer,
            place=place, post_process=post_process).build()
