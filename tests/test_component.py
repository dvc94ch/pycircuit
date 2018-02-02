import unittest
from pycircuit.component import *


class FunTests(unittest.TestCase):

    def test_name_only(self):
        f = Fun('GPIO')
        assert f.function == 'GPIO'

    def test_name_and_dir(self):
        f = Fun('VCC')
        assert f.function == 'VCC'

    def test_bus(self):
        f = BusFun('UART0', 'UART_TX')
        assert f.bus == 'UART0'
        assert f.function == 'UART_TX'


class PinTests(unittest.TestCase):

    def test_simple_pin(self):
        pin = Pin('GPIO')
        assert pin.name == 'GPIO'
        assert pin.description == ''
        assert len(pin.funs) == 1

    def test_pin_with_descr(self):
        pin = Pin('GPIO', description='A GPIO Pin')
        assert pin.description == 'A GPIO Pin'

    def test_pin_with_fun(self):
        pin = Pin('GPIO_1', Fun('GPIO'), BusFun(
            'UART0', 'UART_TX'), description='A GPIO Pin')
        assert pin.name == 'GPIO_1'
        assert pin.description == 'A GPIO Pin'
        assert len(pin.funs) == 2
        assert pin.funs[0].function == 'GPIO'
        assert pin.funs[1].function == 'UART_TX'

    def test_function_by_name(self):
        pin = Pin('GPIO_1', Fun('GPIO'))
        assert pin.has_function('GPIO') == True


class ComponentTests(unittest.TestCase):

    def test_component(self):
        cmp = Component('MCU', 'Microcontroller',
                        Pin('GND'),
                        Pin('VCC'),
                        Pin('XTAL_XI'),
                        Pin('XTAL_XO'),
                        Pin('JTAG_TCK'),
                        Pin('JTAG_TDO'),
                        Pin('JTAG_TMS'),
                        Pin('JTAG_TDI'),
                        Pin('GPIO_1', Fun('GPIO'), BusFun('UART0', 'UART_TX')),
                        Pin('GPIO_2', Fun('GPIO'), BusFun('UART0', 'UART_RX')),
                        Pin('GPIO_3', Fun('GPIO')),
                        Pin('GPIO_4', Fun('GPIO')),
                        Pin('GPIO_5', Fun('GPIO'), BusFun('UART1', 'UART_TX')),
                        Pin('GPIO_6', Fun('GPIO'), BusFun('UART1', 'UART_RX')))

        assert cmp.name == 'MCU'
        assert cmp.description == 'Microcontroller'
        assert len(cmp.pins) == 14
        assert len(cmp.busses) == 2

        gnd = cmp.pin_by_name('GND')
        assert len(gnd.funs) == 1

        gpio_1 = cmp.pin_by_name('GPIO_1')
        assert gpio_1.name == 'GPIO_1'
        assert len(gpio_1.funs) == 2
