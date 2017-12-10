from pycircuit.device import *
from pycircuit.circuit import *
from pycircuit.footprint import *
from pycircuit.package import *
from pycircuit.pcb import *
from pycircuit.formats import *
from pycircuit.library import *
from pykicad.module import Module
from pykicad.pcb import Zone

# Define some devices
Device('RGB', pins=[
    Pin('RED'),
    Pin('GREEN'),
    Pin('BLUE'),
    Pin('GND')
])

Device('QuadOP', pins=[
    Pin('V+'),
    Pin('V-'),
    Pin('-_1', Fun('OP1', 'OP', '-')),
    Pin('+_1', Fun('OP1', 'OP', '+')),
    Pin('OUT_1', Fun('OP1', 'OP', 'OUT')),
    Pin('-_2', Fun('OP2', 'OP', '-')),
    Pin('+_2', Fun('OP2', 'OP', '+')),
    Pin('OUT_2', Fun('OP2', 'OP', 'OUT')),
    Pin('-_3', Fun('OP3', 'OP', '-')),
    Pin('+_3', Fun('OP3', 'OP', '+')),
    Pin('OUT_3', Fun('OP3', 'OP', 'OUT')),
    Pin('-_4', Fun('OP4', 'OP', '-')),
    Pin('+_4', Fun('OP4', 'OP', '+')),
    Pin('OUT_4', Fun('OP4', 'OP', 'OUT'))
])


Device('MCU', pins=[
       Pin('GND'),
       Pin('VCC'),
       Pin('XTAL_XI', 'XTAL'),
       Pin('XTAL_XO', 'XTAL'),
       Pin('JTAG_TCK', Fun('JTAG:S', 'TCK')),
       Pin('JTAG_TDO', Fun('JTAG:S', 'TDO')),
       Pin('JTAG_TMS', Fun('JTAG:S', 'TMS')),
       Pin('JTAG_TDI', Fun('JTAG:S', 'TDI')),
       Pin('GPIO_1', 'GPIO', Fun('UART1', 'UART', 'TX')),
       Pin('GPIO_2', 'GPIO', Fun('UART1', 'UART', 'RX')),
       Pin('GPIO_3', 'GPIO'),
       Pin('GPIO_4', 'GPIO'),
       Pin('GPIO_5', 'GPIO', Fun('UART2', 'UART', 'TX')),
       Pin('GPIO_6', 'GPIO', Fun('UART2', 'UART', 'RX')),
       Pin('GPIO_7', 'GPIO')
])

# Define some footprints
Footprint('R0805', 'R', '0805',
          Map(1, '1'),
          Map(2, '2'))

Footprint('D0805', 'D', '0805',
          Map(1, 'A'),
          Map(2, 'K'))

for a, b, c in ['BCE', 'BEC', 'CBE', 'CEB', 'ECB', 'EBC']:
    Footprint('SOT23' + a + b + c, 'Q', 'SOT23',
              Map(1, a),
              Map(2, b),
              Map(3, c))

Footprint('BAT0805', 'BAT', '0805',
          Map(1, 'VCC'),
          Map(2, 'GND'))

Footprint('OSC0805', 'XTAL', '0805',
          Map(1, '1'),
          Map(2, '2'))

Footprint('MCUQFN16', 'MCU', 'QFN16',
          Map(1, 'GPIO_1'),
          Map(2, 'GPIO_2'),
          Map(3, 'GPIO_3'),
          Map(4, 'GPIO_4'),
          Map(5, 'VCC'),
          Map(6, 'GND'),
          Map(7, 'GPIO_5'),
          Map(8, 'GPIO_6'),
          Map(9, 'XTAL_XI'),
          Map(10, 'XTAL_XO'),
          Map(11, 'GPIO_7'),
          Map(12, 'JTAG_TCK'),
          Map(13, 'JTAG_TDO'),
          Map(14, 'JTAG_TMS'),
          Map(15, 'JTAG_TDI'),
          Map(17, 'GND'))

# Define some circuits
@circuit('LED')
def led():
    Node('Rs', 'R')
    Node('LED', 'D')

    Net('IN') + Ref('Rs')['~']
    Net('') + Ref('Rs')['~'] + Ref('LED')['A']
    Ref('LED')['K'] + Net('GND')


@circuit('OP')
def op():
    Node('QOP1', 'QOP')
    Node('OP1', 'OP')
    Ref('QOP1')['OP'] + Ref('OP1')['OP']


@circuit('RGB')
def rgb():
    Sub('RED', led())
    Sub('GREEN', led())
    Sub('BLUE', led())

    for net in ['RED', 'GREEN', 'BLUE']:
        Net(net) + Ref(net)['IN']
        Net('GND') + Ref(net)['GND']


@circuit('TOP')
def top():
    Node('BAT1', 'BAT')
    Node('OSC1', 'XTAL')
    Node('MCU1', 'MCU')
    Sub('RGB1', rgb())

    Net('VCC') + Refs('BAT1', 'MCU1')['VCC']
    Net('GND') + Refs('BAT1', 'MCU1', 'RGB1')['GND']
    Nets('XTAL_XI', 'XTAL_XO') + Ref('MCU1')['XTAL_XI', 'XTAL_XO'] + \
        Ref('OSC1')['~'].to_vec(2)
    #Nets('UART_1', 'UART_2') + Ref('MCU1')['UART']['RX', 'TX'] + \
    #    Ref('MCU1')['UART']['TX', 'RX']
    Nets('RED', 'GREEN', 'BLUE') + \
        Ref('MCU1')['GPIO'].to_vec(3) + \
        Ref('RGB1')['RED', 'GREEN', 'BLUE']


if __name__ == '__main__':
    circuit = top()

    for node in circuit.iter_nodes():
        node.attrs = NodeAttributes(node)

    for node in circuit.iter_nodes():
        fps = list(Footprint.footprints_by_device(node.device))
        if len(fps) < 1:
            print('No footprint found for %s' % node.device.name)
        else:
            node.set_footprint(fps[0])

    # Place nodes
    #circuit.to_pcpl()

    i = 0
    for node in circuit.iter_nodes():
        if node.footprint.package.name == '0805':
            node.place(i * 5, 0, 90)
            i += 1

    mcu1 = circuit.node_by_name('MCU1')
    mcu1.place(10, 10)
    mcu1.flip()

    # Show some statistics
    bat = circuit.node_by_name('BAT1')
    print('MCU1 area:', mcu1.area())
    print('BAT1 area:', bat.area())
    print('MCU1 intersects itself:', mcu1.intersects(mcu1))
    print('MCU1 intersects BAT1:', mcu1.intersects(bat))

    mcu1.set_power(1.2)
    #mcu1.swap_pin('GPIO_5', 'GPIO_6')
    #mcu1.swap_bus('UART1', 'UART2')

    # Create a pcb
    pcb = Pcb.oshpark_4layer(circuit)
    pcb.move_to('BAT1', '1')
    dist = pcb.distance('MCU1', '5')
    pcb.segment(dy=dist[1])
    pcb.via('bottom')
    pcb.segment_to('MCU1', '5')

    # Print some more statistics
    print(
        'area:', pcb.area, 'mm2',
        'cost:', pcb.cost, '$',
        'traces:', pcb.net.length(), 'mm'
    )

    for net in circuit.iter_nets():
        #for loc in net.pad_locations():
        #pcb.rbs.shortest_route()
        print('net', net.name, net.half_perimeter_length())


    # Export circuit to graph
    graph = circuit.to_graphviz()
    graph.format = 'svg'
    graph.render('viewer/files/net')
    # Export pcb to svg
    pcb.to_svg().save('viewer/files/pcb.svg')

    # Convert pcb to kicad
    kpcb = pcb.to_kicad()

    left, top, right, bottom = pcb.outline()
    coords = [(left, top), (right, top), (right, bottom), (left, bottom)]
    gndplane_top = Zone(net_name='GND', layer='F.Cu', polygon=coords, clearance=0.3)
    gndplane_bottom = Zone(net_name='GND', layer='B.Cu', polygon=coords, clearance=0.3)
    kpcb.zones = [gndplane_top, gndplane_bottom]

    # Use pykicad to postprocess the pcb:
    # Add and place some floating packages
    r_0805 = Package.from_kicad(Module.from_library('Resistors_SMD', 'R_0805'))
    pkgs = [Package.package_by_name(pkg) for pkg in ['SOT23', 'DIP8', 'PBGA16_8x8']]
    xpos = 0
    for pkg in pkgs + [r_0805]:
        kmod = pkg.to_kicad()
        xpos += pkg.size()[0] / 2
        kmod.place(xpos, 25)
        xpos += pkg.size()[0] / 2
        xpos += 1
        kpcb.modules.append(kmod)
    # Save pcb to file
    kpcb.to_file('small.kicad_pcb')
