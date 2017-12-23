from pycircuit.circuit import *
from pycircuit.compiler import *
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


@circuit('LED')
def led():
    _in, gnd = ports('IN GND')
    n1 = Net('n1')

    Inst('Rs', 'R')['~', '~'] = _in, n1
    Inst('LED', 'D')['A', 'C'] = n1, gnd


@circuit('RGB')
def rgb():
    gnd = Port('GND')
    for port in ports('RED GREEN BLUE'):
        SubInst(port.name, led())['IN', 'GND'] = port, gnd


@circuit('TOP')
def top():
    vcc, gnd = nets('VCC GND')
    xtal_xi, xtal_xo = nets('XTAL_XI XTAL_XO')
    red, green, blue = nets('RED GREEN BLUE')
    uart_tx, uart_rx = nets('UART_RX UART_TX')

    Inst('BAT1', 'BAT')['+', '-'] = vcc, gnd
    Inst('OSC1', 'XTAL')['~', '~'] = xtal_xi, xtal_xo

    with SubInst('RBG1', rgb()) as rgb1:
        rgb1['RED', 'GREEN', 'BLUE'] = red, green, blue
        rgb1['GND'] = gnd

    with Inst('MCU1', 'MCU') as mcu:
        mcu['VCC', 'GND'] = vcc, gnd
        mcu['XTAL_XI', 'XTAL_XO'] = xtal_xi, xtal_xo
        mcu['GPIO', 'GPIO', 'GPIO'] = red, green, blue
        mcu['UART_TX', 'UART_RX'] = uart_tx, uart_rx
        mcu['UART_TX', 'UART_RX'] = uart_rx, uart_tx


if __name__ == '__main__':
    Compiler(top())

    '''
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


    pcb.to_svg().save('pcb.svg')
    pcb.to_kicad().to_file('small.kicad_pcb')
'''
