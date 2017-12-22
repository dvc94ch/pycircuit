from pycircuit.library import *


Device('BAT0805', 'BAT', '0805',
       Map(1, '+'),
       Map(2, '-'))

Package('TDK ACT45B', RectCrtyd(5.9, 3.4), DualPads(4, 2.5, radius=2.275),
        package_size=(5.9, 3.4), pad_size=(0.9, 1.35))

Device('TDK ACT45B', 'Transformer_1P_1S', 'TDK ACT45B',
       Map(1, 'L1.1'), Map(2, 'L2.1'), Map(3, 'L2.2'), Map(4, 'L1.2'))


'''
@circuit('TOP')
def top():
    vcc, gnd, n1, n2, n3 = nets('VCC GND n1 n2 n3')

    with Node('TR1', 'Transformer_1P_1S') as tr1:
        # Assign to individual pins
        tr1['L1.1'] += n1
        tr1['L1.2'] += n2
        # Assign to bus
        tr1['L2'] += (vcc, n3)

    with Node('BAT1', 'DCCONN') as bat1:
        bat1['+'] += vcc
        bat1['-'] += gnd

    with Node('R1', 'R') as r1:
        r1 += (vcc, n1)

    with Node('Q1', 'Q') as q1:
        # Assign multiple pins
        q1['B', 'C', 'E'] += (n2, n3, gnd)

    with Node('LED1', 'D') as led1:
        led1['A', 'C'] += (n3, gnd)


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
'''
