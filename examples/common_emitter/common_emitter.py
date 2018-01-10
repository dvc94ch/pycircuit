from pycircuit.circuit import *
from pycircuit.library import *


@circuit('Common Emitter', 'gnd', '12V', 'vin', 'vout')
def common_emitter_amplifer(self, gnd, vcc, vin, vout):
    nb, ne = nets('nb ne')
    Inst('Q', 'npn sot23')['B', 'C', 'E'] = nb, vout, ne

    # Current limiting resistor
    Inst('R', '1.2k')['~', '~'] = vcc, vout

    # Thermal stabilization (leads to a gain reduction)
    Inst('R', '220')['~', '~'] = ne, gnd
    # Shorts Re for AC signal (increases gain)
    Inst('C', '10uF')['~', '~'] = ne, gnd

    # Biasing resistors
    Inst('R', '20k')['~', '~'] = vcc, nb
    Inst('R', '3.6k')['~', '~'] = nb, gnd
    # Decoupling capacitor
    Inst('C', '10uF')['~', '~'] = vin, nb


if __name__ == '__main__':
    from pycircuit.formats import *
    from pycircuit.build import Builder

    Builder(common_emitter_amplifer()).compile()
