import joule_thief
from pycircuit.build import Builder
from pycircuit.library.design_rules import oshpark_4layer
from pycircuit.library.outlines import sick_of_beige
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
    router = Router(maxflow_enforcement_level=2)
    router.route(filein, fileout)


def post_process(pcb, kpcb):
    coords = list(pcb.outline.polygon.interiors[0].coords)

    zone = Zone(net_name='gnd', layer='F.Cu',
                polygon=coords, clearance=0.3)

    kpcb.zones.append(zone)
    return kpcb


if __name__ == '__main__':
    pcb_attributes = oshpark_4layer()
    # Only allow placement on top layer
    pcb_attributes.layers.placement_layers.pop()

    Builder(joule_thief.top(), outline=sick_of_beige('DP5031'),
            pcb_attributes=pcb_attributes, place=place,
            # route=route,
            post_process=post_process).build()
