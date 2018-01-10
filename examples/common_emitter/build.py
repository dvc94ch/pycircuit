import ngspyce as ng
import numpy as np
from matplotlib import pyplot as plt
from pycircuit.formats import *
from pycircuit.build import Builder
from pycircuit.circuit import testbench

from common_emitter import common_emitter_amplifer


def sim():
    tb = testbench(common_emitter_amplifer())
    circuit = Builder(tb).compile()
    circuit.to_spice('common_emitter_amplifier.sp')
    ng.source('common_emitter_amplifier.sp')
    ng.cmd('tran 50us 10ms')

    print('\n'.join(ng.vector_names()))
    time, tp1 = map(ng.vector, ['time', 'V(VOUT)'])
    plt.plot(time, tp1, label='VOUT')
    plt.legend()
    plt.show()


if __name__ == '__main__':
    sim()
