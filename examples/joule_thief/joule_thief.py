from pycircuit.circuit import *
from pycircuit.library import *


Device('BAT0805', 'BAT', '0805',
       Map('1', '+'),
       Map('2', '-'))

Package('TDK ACT45B', RectCrtyd(5.9, 3.4), DualPads(4, 2.5, radius=2.275),
        package_size=(5.9, 3.4), pad_size=(0.9, 1.35))

Device('TDK ACT45B', 'Transformer_1P_1S', 'TDK ACT45B',
       Map('1', 'L1.1'), Map('2', 'L2.1'), Map('3', 'L2.2'), Map('4', 'L1.2'))


@circuit('TOP')
def top():
    vcc, gnd, n1, n2, n3 = nets('VCC GND n1 n2 n3')

    with Inst('TR1', 'Transformer_1P_1S') as tr1:
        tr1['L1', 'L1'] = n1, n2
        tr1['L2', 'L2'] = vcc, n3

    Inst('BAT1', 'BAT')['+', '-'] = vcc, gnd
    Inst('R1', 'R', '10k 0805')['~', '~'] = vcc, n1
    Inst('Q1', 'Q', 'npn sot23')['B', 'C', 'E'] = n2, n3, gnd
    Inst('LED1', 'D', 'led red 0805')['A', 'C'] = n3, gnd
