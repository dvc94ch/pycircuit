from pycircuit.circuit import *
from pycircuit.library import *


def sallen_key(z1, z2, z3, z4, vcc, vee):

    @circuit('Sallen Key', 'gnd', '%s %s' % (vcc, vee), 'vin', 'vout')
    def sallen_key_topology(self, gnd, vcc, vee, vin, vout):
        n1, n2 = nets('n1 n2')

        Inst(z1)['~', '~'] = vin, n1
        Inst(z2)['~', '~'] = n1, n2
        Inst(z3)['~', '~'] = n1, vout
        Inst(z4)['~', '~'] = n2, gnd

        with Inst('OP', 'OP') as op:
            op['+', '-', 'OUT'] = n2, vout, vout
            op['VCC', 'VEE'] = vcc, vee

    return sallen_key_topology()


def lp_sallen_key(vcc='+12V', vee='-12V'):
    return sallen_key('R', 'R', 'C', 'C', vcc, vee)


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


@circuit('Sallen Key Top', 'gnd')
def top(self, gnd):
    vcc, vee, vin, vout = nets('+12V -12V vin vout')
    # VCC
    Inst('V')['+', '-'] = vcc, gnd
    # VEE
    Inst('V')['+', '-'] = gnd, vee
    # Vin
    Inst('V')['+', '-'] = vin, gnd

    Inst('TP')['TP'] = vout

    with SubInst(lp_sallen_key()) as sk:
        sk['+12V', '-12V', 'gnd', 'vin', 'vout'] = vcc, vee, gnd, vin, vout


if __name__ == '__main__':
    from pycircuit.formats import *
    from pycircuit.build import Builder

    Builder(lp_sallen_key()).compile()
    Builder(top()).compile()
