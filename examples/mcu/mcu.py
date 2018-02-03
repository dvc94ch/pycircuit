from pycircuit.circuit import *
from pycircuit.library import *


Component('MCU', 'Microcontroller',
          Gnd('GND'),
          Pwr('5V'),
          In('XTAL_XI'),
          Out('XTAL_XO'),
          In('JTAG_TCK'),
          In('JTAG_TMS'),
          In('JTAG_TDI'),
          Out('JTAG_TDO'),
          Io('GPIO_1', BusFun('UART0', 'UART_TX')),
          Io('GPIO_2', BusFun('UART0', 'UART_RX')),
          Io('GPIO_3'),
          Io('GPIO_4'),
          Io('GPIO_5', BusFun('UART1', 'UART_TX')),
          Io('GPIO_6', BusFun('UART1', 'UART_RX')),
          Io('GPIO_7'))

Device('MCUQFN16', 'MCU', 'QFN16',
       Map('1', 'GPIO_1'),
       Map('2', 'GPIO_2'),
       Map('3', 'GPIO_3'),
       Map('4', 'GPIO_4'),
       Map('5', '5V'),
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

Device('V0805', 'V', '0805',
       Map('1', '+'),
       Map('2', '-'))

Device('OSC0805', 'XTAL', '0805',
       Map('1', 'L'),
       Map('2', 'R'))


@circuit('LED', 'gnd', None, 'vin')
def led(self, gnd, vin):
    n1 = nets('n1')

    Inst('R')['~', '~'] = vin, n1
    Inst('D', 'led')['A', 'C'] = n1, gnd


@circuit('RGB', 'gnd', None, 'red green blue')
def rgb(self, gnd, *inputs):
    for port in inputs:
        SubInst(led())['vin', 'gnd'] = port, gnd


@circuit('MCU')
def mcu(self):
    vcc, gnd, clk, gpio, uart = nets('5V GND clk[2] gpio[3] uart[2]')

    Inst('V')['+', '-'] = vcc, gnd
    Inst('XTAL')['~', '~'] = clk
    SubInst(rgb())['red', 'green', 'blue', 'gnd'] = *gpio, gnd

    with Inst('MCU') as mcu:
        mcu['5V', 'GND'] = vcc, gnd
        mcu['XTAL_XI', 'XTAL_XO'] = clk
        mcu['GPIO', 'GPIO', 'GPIO'] = gpio
        mcu['UART_TX', 'UART_RX'] = uart
        mcu['UART_RX', 'UART_TX'] = uart


if __name__ == '__main__':
    from pycircuit.formats import *
    from pycircuit.build import Builder

    Builder(led()).compile()
    Builder(rgb()).compile()
    Builder(mcu()).compile()
