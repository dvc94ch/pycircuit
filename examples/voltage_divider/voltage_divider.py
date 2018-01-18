from pycircuit.circuit import *
from pycircuit.device import *
from pycircuit.library import *
from pycircuit.build import Builder
from placer.place import Placer
from router.router import Router


Component('Connector', 'A connector', Pin('vin'), Pin('vout'), Pin('gnd'))
Device('Connector', 'Connector', 'Pins_3x1',
       Map('A1', 'vin'),
       Map('A2', 'vout'),
       Map('A3', 'gnd')
)

@circuit('Voltage Divider', 'gnd', None, 'vin', 'vout')
def voltage_divider(self, gnd, vin, vout):
    Inst('R', '10k 0805')['~', '~'] = vin, vout
    Inst('R', '10k 0805')['~', '~'] = vout, gnd


@circuit('Top')
def top(self):
    vin, vout, gnd = nets('vin vout gnd')
    SubInst(voltage_divider())['vin', 'vout', 'gnd'] = vin, vout, gnd
    Inst('Connector', 'Pins_3x1')['vin', 'vout', 'gnd'] = vin, vout, gnd


def place(fin, fout):
    p = Placer()
    p.place(fin, fout)


def route(fin, fout):
    r = Router(grid_size=.5, maxflow_enforcement_level=3)
    r.route(fin, fout)


if __name__ == '__main__':
    outline = rectangle_with_mounting_holes(20, 10, inset=1, hole_shift=2, hole_dia=1)

    Builder(top(), outline=outline,
            pcb_attributes=oshpark_2layer(),
            place=place, route=route).build()
