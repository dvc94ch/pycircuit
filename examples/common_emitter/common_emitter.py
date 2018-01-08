from pycircuit.circuit import *
from pycircuit.library import *


@circuit('Common Emitter Amplifer', '12V gnd', 'vin', 'vout')
def common_emitter_amplifer(self, vcc, gnd, vin, vout):
    nb, ne = nets('nb ne')
    Inst('Q', 'npn sot23')['B', 'C', 'E'] = nb, vout, ne

    # Current limiting resistor
    Inst('R')['~', '~'] = vcc, vout

    # Thermal stabilization (leads to a gain reduction)
    Inst('R')['~', '~'] = ne, gnd
    # Shorts Re for AC signal (increases gain)
    Inst('C')['~', '~'] = ne, gnd

    # Biasing resistors
    Inst('R')['~', '~'] = vcc, nb
    Inst('R')['~', '~'] = nb, gnd
    # Decoupling capacitor
    Inst('C')['~', '~'] = vin, nb


'''def sim():
    import ngspyce as ng
    import numpy as np
    from matplotlib import pyplot as plt
    from pycircuit.formats import *
    from pycircuit.build import Builder

    testbench = test_bench(common_emitter_amplifer())
    netlist = Builder.build(testbench).get_netlist()

    netlist.to_spice('common_emitter_amplifier.sp')
    ng.source('common_emitter_amplifier.sp')
    ng.cmd('tran 1us 500us')

    print('\n'.join(ng.vector_names()))
    time, tp1 = map(ng.vector, ['time', 'V(VOUT)'])
    plt.plot(time, tp1, label='VOUT')
    plt.legend()
    plt.show()'''


if __name__ == '__main__':
    from pycircuit.formats import *
    from pycircuit.build import Builder

    Builder(common_emitter_amplifer()).compile()
