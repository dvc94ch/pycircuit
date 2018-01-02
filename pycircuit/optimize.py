import numpy as np
import scipy.signal
import ngspyce
from pycircuit.circuit import testbench
from pycircuit.build import Builder
from pycircuit.diffev import DiffEvolver


class Optimizer(object):
    def __init__(self, netlist, spec, nsamples=20, npop=50):
        self.netlist = netlist
        self.spec = spec

        # Find simulation parameters from specification
        self.nsamples = nsamples
        self.sim_params = self.find_sim_params()

        # Find all resistors and capacitors in netlist
        # to determine problem size
        self.resistors = []
        self.capacitors = []

        for inst in netlist.iter_insts():
            if inst.component.name == 'R':
                self.resistors.append(inst)
            elif inst.component.name == 'C':
                self.capacitors.append(inst)

        self.nparams = len(self.resistors) + len(self.capacitors)

        # Run simulation to find freqs
        self.freqs, _ = self.simulate()
        # Compute target values from specification
        _, self.target = scipy.signal.freqs(*self.spec, worN=2 * np.pi * self.freqs)

        # Initialize DiffEvolver
        lbound = scipy.zeros(self.nparams)
        ubound = scipy.ones(self.nparams)
        self.de = DiffEvolver.frombounds(self.cost, lbound, ubound, npop)
        self.de.set_boundaries(lbound, ubound, mode='mirror')

    def find_sim_params(self):
        w = scipy.signal.findfreqs(*self.spec, self.nsamples)
        fstart = w[0] / 2 / np.pi
        fstop = w[-1] / 2 / np.pi
        decades = np.log10(fstop) - np.log10(fstart)
        npoints = self.nsamples / decades
        return {
            'mode': 'dec',
            'npoints': npoints,
            'fstart': fstart,
            'fstop': fstop
        }

    def transform(self, vector):
        for ir, r in enumerate(self.resistors):
            value = 10 ** (vector[ir] * 3 + 3)  # 1K to 1M
            r.set_value(value)
        for ic, c in enumerate(self.capacitors):
            value = 10 ** (vector[ir + ic] * 6 - 9)  # 1nF to 1mF
            c.set_value(value)

    def simulate(self):
        self.netlist.to_spice('optimize.sp')
        ngspyce.source('optimize.sp')
        ngspyce.ac(**self.sim_params)
        fs = np.abs(ngspyce.vector('frequency'))
        vs = ngspyce.vector('vout')
        return fs, vs

    def _vector_to_values(self, vector):
        self.transform(vector)
        _, values = self.simulate()
        return values

    def cost(self, vector):
        values = self._vector_to_values(vector)
        return sum(abs(self.target - values))

    def plot_result(self):
        values = self._vector_to_values(self.de.best_vector)
        self.plot_freq_resp(values)

    def plot_freq_resp(self, values):
        from matplotlib import pyplot as plt

        fig, (ax1, ax2) = plt.subplots(2)
        fig.suptitle('Frequency response')

        ax1.semilogx(self.freqs, 20 * np.log10(abs(self.target)))
        ax1.semilogx(self.freqs, 20 * np.log10(abs(values)))
        ax1.set_xlabel('Frequency [Hz]')
        ax1.set_ylabel('Amplitude [dB]')
        ax1.grid(which='both', axis='both')

        ax2.semilogx(self.freqs, np.angle(self.target, True))
        ax2.semilogx(self.freqs, np.angle(values, True))
        ax2.set_xlabel('Frequency [Hz]')
        ax2.set_ylabel('Phase [degrees]')
        ax2.grid(which='both', axis='both')

        plt.show()

    def optimize(self, threshold=None):
        while True:
            self.de.solve()
            min_cost = self.cost(self.de.best_vector)

            if threshold is None or min_cost < threshold:
                return min_cost

    @classmethod
    def from_twoport(cls, two_port, spec):
        netlist = Builder(testbench(two_port)).get_netlist()
        return cls(netlist, spec)
