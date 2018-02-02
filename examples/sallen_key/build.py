import numpy as np
import scipy.signal as sig
from pycircuit.build import Builder
from pycircuit.testbench import testbench
from pycircuit.optimize import Optimizer
from pycircuit.library.design_rules import oshpark_4layer

from sallen_key import lp_sallen_key, top


def lp_optimize():
    spec = sig.butter(2, 2 * np.pi * 100, btype='low', analog=True)
    tb = Builder(testbench(lp_sallen_key())).compile()
    problem = Optimizer(tb, spec)
    cost = problem.optimize()
    print(cost)
    problem.plot_result()
    print(repr(problem.netlist))


if __name__ == '__main__':
    lp_optimize()
    #Builder(top(), oshpark_4layer).build()
