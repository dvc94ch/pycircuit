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
    pcb = Pcb.oshpark_4layer(top())

    for node in pcb.circuit.iter_nodes():
        fps = list(Footprint.footprints_by_device(node.device))
        if len(fps) < 1:
            print('No footprint found for %s' % node.device.name)
        else:
            node.set_footprint(fps[0])

    pcb.to_pcpl('small.pcpl')
    pcb.from_pcpl('small.out.pcpl')

    pcb.finalize()

    pcb.to_pcrt('small.pcrt')
    try:
        pcb.from_pcrt('small.out.pcrt')
    except:
        print('No small.out.pcrt file.')

    graph = pcb.circuit.to_graphviz()
    graph.format = 'svg'
    graph.render('net.dot')

    pcb.to_svg().save('pcb.svg')
    pcb.to_kicad().to_file('small.kicad_pcb')
