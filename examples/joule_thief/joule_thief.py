from pycircuit.device import *
from pycircuit.circuit import *
from pycircuit.footprint import *
from pycircuit.package import *
from pycircuit.pcb import *
from pycircuit.formats import *
from pycircuit.library import *
from pycircuit.library.connectors import *
from pykicad.module import Module
from pykicad.pcb import Zone

Device('Choke', pins=(Pin('1'), Pin('2'), Pin('3'), Pin('4')))

Footprint('R0805', 'R', '0805',
          Map(1, '1'),
          Map(2, '2'))


Footprint('D0805', 'D', '0805',
          Map(1, 'A'),
          Map(2, 'K'))


Footprint('BAT0805', 'DCCONN', '0805',
          Map(1, 'V'),
          Map(2, 'GND'))

for a, b, c in ['BCE', 'BEC', 'CBE', 'CEB', 'ECB', 'EBC']:
    Footprint('SOT23' + a + b + c, 'Q', 'SOT23',
              Map(1, a),
              Map(2, b),
              Map(3, c))


Package('TDK:ACT45B', RectCrtyd(5.9, 3.4), DualPads(4, 2.5, radius=2.275),
        package_size=(5.9, 3.4), pad_size=(0.9, 1.35))


Footprint('TDK:ACT45B', 'Choke', 'TDK:ACT45B',
          Map(1, '1'), Map(2, '2'), Map(3, '4'), Map(4, '3'))


@circuit('TOP')
def top():
    Node('L1', 'Choke')
    Node('BAT1', 'DCCONN')
    Node('R1', 'R')
    Node('Q1', 'Q')
    Node('LED1', 'D')
    Ref('BAT1')['V']   + Net('VCC')       + Ref('R1')['1']
    Ref('BAT1')['GND'] + Net('GND')
    Ref('R1')['2']     + Ref('L1')['1']
    Net('VCC')         + Ref('L1')['2']
    Ref('L1')['3']     + Ref('Q1')['B']
    Ref('L1')['4']     + Net('n1')        + Ref('Q1')['C']
    Ref('Q1')['E']     + Net('GND')
    Net('n1')          + Ref('LED1')['A']
    Ref('LED1')['K']   + Net('GND')


if __name__ == '__main__':
    pcb = Pcb.oshpark_4layer(top())

    for node in pcb.circuit.iter_nodes():
        fps = list(Footprint.footprints_by_device(node.device))
        if len(fps) < 1:
            print('No footprint found for %s' % node.device.name)
        else:
            node.set_footprint(fps[0])

    pcb.to_pcpl('joule_thief.pcpl')
    try:
        pcb.from_pcpl('joule_thief.out.pcpl')
    except FileNotFoundError:
        print('No joule_thief.out.pcpl file.')

    pcb.finalize()

    pcb.to_pcrt('joule_thief.pcrt')
    try:
        pcb.from_pcrt('joule_thief.out.pcrt')
    except FileNotFoundError:
        print('No joule_thief.out.pcrt file.')

    graph = pcb.circuit.to_graphviz()
    graph.format = 'svg'
    graph.render('net.dot')

    pcb.to_svg().save('pcb.svg')
    pcb.to_kicad().to_file('joule_thief.kicad_pcb')
