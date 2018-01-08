from pycircuit.circuit import *
from pycircuit.library import *


Device('V0805', 'V', '0805',
       Map('1', '+'),
       Map('2', '-'))

Package('TDK ACT45B', RectCrtyd(5.9, 3.4), DualPads(4, 2.5, radius=2.275),
        package_size=(5.9, 3.4), pad_size=(0.9, 1.35))

Device('TDK ACT45B', 'Transformer_1P_1S', 'TDK ACT45B',
       Map('1', 'L1.1'), Map('2', 'L2.1'), Map('3', 'L2.2'), Map('4', 'L1.2'))


@circuit('Joule Thief', 'gnd', 'vin', 'vout')
def joule_thief(self, gnd, vin, vout):
    nb, nr = nets('nb nr')

    with Inst('Transformer_1P_1S', '1mH') as tr1:
        tr1['L1.1', 'L1.2'] = nr, nb
        tr1['L2.2', 'L2.1'] = vin, vout

    Inst('R', '1k 0805')['~', '~'] = vin, nr
    Inst('Q', 'npn sot23')['B', 'C', 'E'] = nb, vout, gnd
    Inst('D', 'led white 0805')['+', '-'] = vout, gnd


@circuit('Top')
def top(self):
    vcc, gnd, vout = nets('vcc gnd vout')

    SubInst(joule_thief())['vin', 'vout', 'gnd'] = vcc, vout, gnd
    Inst('V', '1.5V')['+', '-'] = vcc, gnd
    Inst('TP')['TP'] = vout


'''
def test_bench():
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

if __name__ == '__main__':
    from pycircuit.formats import *
    from pycircuit.build import Builder

    Builder(joule_thief()).compile()
    Builder(top()).compile()
