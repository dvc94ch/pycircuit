from pycircuit.circuit import *
from pycircuit.library import *


Device('V0805', 'V', '0805',
       Map('1', '+'),
       Map('2', '-'))

Package('TDK ACT45B', RectCrtyd(5.9, 3.4), DualPads(4, 2.5, radius=2.275),
        package_size=(5.9, 3.4), pad_size=(0.9, 1.35))

Device('TDK ACT45B', 'Transformer_1P_1S', 'TDK ACT45B',
       Map('1', 'L1.1'), Map('2', 'L2.1'), Map('3', 'L2.2'), Map('4', 'L1.2'))


@circuit('Joule Thief')
def joule_thief(self):
    vin, vout, gnd = ports('VIN VOUT GND')
    nb, nr = nets('nb nr')

    with Inst('TR1', 'Transformer_1P_1S', '1mH') as tr1:
        tr1['L1.1', 'L1.2'] = nr, nb
        tr1['L2.2', 'L2.1'] = vin, vout

    Inst('R1', 'R', '1k 0805')['~', '~'] = vin, nr
    Inst('Q1', 'Q', 'npn sot23')['B', 'C', 'E'] = nb, vout, gnd
    Inst('LED1', 'D', 'led white 0805')['A', 'C'] = vout, gnd


@circuit('Top')
def top(self):
    vcc, gnd, vout = nets('VCC GND VOUT')

    SubInst('JT', joule_thief())['VIN', 'VOUT', 'GND'] = vcc, vout, gnd
    Inst('V1', 'V', '1.5V')['+', '-'] = vcc, gnd
    Inst('TP1', 'TP')['TP'] = vout


def test_bench():
    netlist = Netlist.from_file('joule_thief.out.net')
    netlist.to_spice('joule_thief.sp')
    ng.source('joule_thief.sp')
    ng.cmd('tran 1ms 20ms')

    print('\n'.join(ng.vector_names()))
    time, tp1 = map(ng.vector, ['time', 'V(VOUT)'])
    plt.plot(time, tp1, label='VOUT')
    plt.legend()
    plt.show()


if __name__ == '__main__':
    import ngspyce as ng
    import numpy as np
    from matplotlib import pyplot as plt
    from pycircuit.formats import *

    test_bench()
