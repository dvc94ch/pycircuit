from pycircuit.circuit import *
from pycircuit.library import *


@circuit('Sallen Key')
def sallen_key(self):
    power, (vin, gnd), (vout, _) = i_two_port()
    n1, n2 = nets('n1 n2')

    Inst('Z1', 'R')['~', '~'] = vin, n1
    Inst('Z2', 'R')['~', '~'] = n1, n2
    Inst('Z3', 'C')['~', '~'] = n1, vout
    Inst('Z4', 'C')['~', '~'] = n2, gnd

    with Inst('OP', 'OP') as op:
        op['+', '-', 'OUT'] = n2, vout, vout
        op['V+', 'V-'] = power


Device('V0805', 'V', '0805',
       Map('1', '+'),
       Map('2', '-'))

Device('OPDIP', 'OP', 'DIP8',
       Map('1', 'V+'),
       Map('2', 'V-'),
       Map('3', '+'),
       Map('4', 'OUT'),
       Map('5', '-'),
       Map('6', None),
       Map('7', None),
       Map('8', None))

@circuit('Sallen Key Top')
def top(self):
    power, input, output = i_two_port(port=False)

    Inst('VCC', 'V')['+', '-'] = power[0], input[1]
    Inst('VEE', 'V')['+', '-'] = input[1], power[1]
    Inst('IN', 'V')['+', '-'] = input
    Inst('OUT', 'V')['+', '-'] = output

    with SubInst('FILTER', sallen_key()) as sk:
        sk['v+', 'v-', 'vin', 'gnd', 'vout'] = *power, *input, *output


if __name__ == '__main__':
    import numpy as np
    import scipy.signal as sig
    from pycircuit.optimize import Optimizer

    spec = sig.butter(2, 2 * np.pi * 100, btype='low', analog=True)
    problem = Optimizer.from_twoport(sallen_key(), spec)
    cost = problem.optimize()
    print(cost)
    problem.plot_result()
    print(repr(problem.netlist))
