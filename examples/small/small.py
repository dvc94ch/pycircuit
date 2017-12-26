from pycircuit.circuit import *
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
       Map('1', 'GPIO_1'),
       Map('2', 'GPIO_2'),
       Map('3', 'GPIO_3'),
       Map('4', 'GPIO_4'),
       Map('5', 'VCC'),
       Map('6', 'GND'),
       Map('7', 'GPIO_5'),
       Map('8', 'GPIO_6'),
       Map('9', 'XTAL_XI'),
       Map('10', 'XTAL_XO'),
       Map('11', 'GPIO_7'),
       Map('12', 'JTAG_TCK'),
       Map('13', 'JTAG_TDO'),
       Map('14', 'JTAG_TMS'),
       Map('15', 'JTAG_TDI'),
       Map('16', None),
       Map('17', 'GND'))

Device('BAT0805', 'BAT', '0805',
       Map('1', '+'),
       Map('2', '-'))

Device('OSC0805', 'XTAL', '0805',
       Map('1', '1'),
       Map('2', '2'))


@circuit('LED')
def led():
    _in, gnd = ports('IN GND')
    n = Net('n1')

    Inst('Rs', 'R')['~', '~'] = _in, n
    Inst('LED', 'D')['A', 'C'] = n, gnd


@circuit('RGB')
def rgb():
    gnd = Port('GND')
    for port in ports('RED GREEN BLUE'):
        SubInst(port.name, led())['IN', 'GND'] = port, gnd


@circuit('TOP')
def top():
    power = nets('VCC GND')
    clk = nets('XTAL_XI XTAL_XO')
    gpio = nets('RED GREEN BLUE')
    uart = bus('UART', 2)

    Inst('BAT1', 'BAT')['+', '-'] = power
    Inst('OSC1', 'XTAL')['~', '~'] = clk

    with SubInst('RBG1', rgb()) as rgb1:
        rgb1['RED', 'GREEN', 'BLUE'] = gpio
        rgb1['GND'] = power[1]

    with Inst('MCU1', 'MCU') as mcu:
        mcu['VCC', 'GND'] = power
        mcu['XTAL_XI', 'XTAL_XO'] = clk
        mcu['GPIO', 'GPIO', 'GPIO'] = gpio
        mcu['UART_TX', 'UART_RX'] = uart
        mcu['UART_TX', 'UART_RX'] = uart
