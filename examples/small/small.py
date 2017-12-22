from pycircuit.library import *


Component('MCU', 'Microcontroller',
          PwrIn('GND'),
          PwrIn('VCC'),
          Pin('XTAL_XI'),
          Pin('XTAL_XO'),
          Pin('JTAG_TCK'),
          Pin('JTAG_TDO'),
          Pin('JTAG_TMS'),
          Pin('JTAG_TDI'),
          Io('GPIO_1', Fun('GPIO'), BusFun('UART0', 'UART_TX')),
          Io('GPIO_2', Fun('GPIO'), BusFun('UART0', 'UART_RX')),
          Io('GPIO_3', Fun('GPIO')),
          Io('GPIO_4', Fun('GPIO')),
          Io('GPIO_5', Fun('GPIO'), BusFun('UART1', 'UART_TX')),
          Io('GPIO_6', Fun('GPIO'), BusFun('UART1', 'UART_RX')),
          Io('GPIO_7', Fun('GPIO')))

Device('MCUQFN16', 'MCU', 'QFN16',
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
       Map(16, None),
       Map(17, 'GND'))

Device('BAT0805', 'BAT', '0805',
       Map(1, 'VCC'),
       Map(2, 'GND'))

Device('OSC0805', 'XTAL', '0805',
       Map(1, '1'),
       Map(2, '2'))

'''
# Define some circuits
@circuit('LED')
def led():
    Node('Rs', 'R')
    Node('LED', 'D')

    Net('IN') + Ref('Rs')['~']
    Net('') + Ref('Rs')['~'] + Ref('LED')['A']
    Ref('LED')['K'] + Net('GND')


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
    try:
        pcb.from_pcpl('small.out.pcpl')
    except FileNotFoundError:
        print('No small.out.pcpl file.')

    pcb.finalize()

    pcb.to_pcrt('small.pcrt')
    try:
        pcb.from_pcrt('small.out.pcrt')
    except FileNotFoundError:
        print('No small.out.pcrt file.')

    graph = pcb.circuit.to_graphviz()
    graph.format = 'svg'
    graph.render('net.dot')

    pcb.to_svg().save('pcb.svg')
    pcb.to_kicad().to_file('small.kicad_pcb')
'''
