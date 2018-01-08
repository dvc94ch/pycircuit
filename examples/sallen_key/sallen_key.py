from pycircuit.circuit import *
from pycircuit.library import *


@circuit('Sallen Key', '+12V -12V gnd', 'vin', 'vout')
def sallen_key(self, vcc, vee, gnd, vin, vout):
    n1, n2 = nets('n1 n2')

    Inst('R')['~', '~'] = vin, n1
    Inst('R')['~', '~'] = n1, n2
    Inst('C')['~', '~'] = n1, vout
    Inst('C')['~', '~'] = n2, gnd

    with Inst('OP', 'OP') as op:
        op['+', '-', 'OUT'] = n2, vout, vout
        op['VCC', 'VEE'] = vcc, vee


Device('V0805', 'V', '0805',
       Map('1', '+'),
       Map('2', '-'))

Device('OPDIP', 'OP', 'DIP8',
       Map('1', 'VCC'),
       Map('2', 'VEE'),
       Map('3', '+'),
       Map('4', 'OUT'),
       Map('5', '-'),
       Map('6', None),
       Map('7', None),
       Map('8', None))

@circuit('Sallen Key Top')
def top(self):
    vcc, vee, gnd, vin, vout = nets('+12V -12V gnd vin vout')
    # VCC
    Inst('V')['+', '-'] = vcc, gnd
    # VEE
    Inst('V')['+', '-'] = gnd, vee
    # Vin
    Inst('V')['+', '-'] = vin, gnd
    # Vout
    Inst('V')['+', '-'] = vout, gnd

    with SubInst(sallen_key()) as sk:
        sk['+12V', '-12V', 'gnd', 'vin', 'vout'] = vcc, vee, gnd, vin, vout


'''
def optimize():
    import numpy as np
    import scipy.signal as sig
    from pycircuit.optimize import Optimizer

    spec = sig.butter(2, 2 * np.pi * 100, btype='low', analog=True)
    problem = Optimizer.from_twoport(sallen_key(), spec)
    cost = problem.optimize()
    print(cost)
    problem.plot_result()
    print(repr(problem.netlist))
'''

if __name__ == '__main__':
    from pycircuit.formats import *
    from pycircuit.build import Builder

    Builder(sallen_key()).compile()
    Builder(top()).compile()
