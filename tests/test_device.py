import unittest
from pycircuit.device import *

class FunctionTests(unittest.TestCase):

    def test_simple_function(self):
        f = Function('UART_TX')
        assert f.name == 'UART_TX'
        assert str(f) == 'UART_TX'


class BusTests(unittest.TestCase):

    def test_bus_no_type(self):
        xtal = Bus('XTAL', 'XI')
        assert xtal.name == 'XTAL'
        assert xtal.type == 'XTAL'
        assert len(xtal.functions) == 1

    def test_bus_with_type(self):
        uart = Bus('UART1', 'UART', 'TX')
        assert uart.name == 'UART1'
        assert uart.type == 'UART'
        assert len(uart.functions) == 1

    def test_function_by_name(self):
        xtal = Bus('XTAL', 'XI')
        assert xtal.function_by_name('XI').name == 'XTAL_XI'


class DeviceTests(unittest.TestCase):

    def test_device(self):
        dev = Device('MCU',
                     Pin('GND'),
                     Pin('VCC'),
                     Pin('XTAL_XI', Bus('XTAL', 'XI')),
                     Pin('XTAL_XO', Bus('XTAL', 'XO')),
                     Pin('JTAG_TCK', Bus('JTAG', 'TCK')),
                     Pin('JTAG_TDO', Bus('JTAG', 'TDO')),
                     Pin('JTAG_TMS', Bus('JTAG', 'TMS')),
                     Pin('JTAG_TDI', Bus('JTAG', 'TDI')),
                     Pin('GPIO_1', 'GPIO', Bus('UART_1', 'UART', 'TX')),
                     Pin('GPIO_2', 'GPIO', Bus('UART_1', 'UART', 'RX')),
                     Pin('GPIO_3', 'GPIO'),
                     Pin('GPIO_4', 'GPIO'),
                     Pin('GPIO_5', 'GPIO', Bus('UART_2', 'UART', 'TX')),
                     Pin('GPIO_6', 'GPIO', Bus('UART_2', 'UART', 'RX')))

        assert dev.name == 'MCU'
        assert len(dev.pins) == 14
        assert len(dev.busses) == 4

        assert dev.bus_by_name('JTAG').name == 'JTAG'
        assert dev.bus_by_name('UART_1').name == 'UART_1'
        assert dev.busses_by_type('JTAG')[0].name == 'JTAG'
        assert dev.busses_by_type('UART')[1].name == 'UART_2'

        assert dev.pin_by_index(1).name == 'VCC'
        assert dev.pin_by_name('VCC').name == 'VCC'
        assert dev.pins_by_function('VCC')[0].name == 'VCC'

        assert len(dev.pins_by_function('UART_TX')) == 2
        assert len(dev.pins_by_function('GPIO')) == 6

        gnd = dev.pin_by_name('GND')
        assert len(gnd.functions) == 1
        assert gnd.functions[0].name == 'GND'

        xtal_xi = dev.pin_by_name('XTAL_XI')
        assert xtal_xi.name == 'XTAL_XI'
        assert len(xtal_xi.functions) == 1
        assert xtal_xi.function_by_name('XTAL_XI').name == 'XTAL_XI'

        gpio_1 = dev.pin_by_name('GPIO_1')
        assert gpio_1.name == 'GPIO_1'
        assert len(gpio_1.functions) == 2
        assert gpio_1.function_by_name('GPIO').name == 'GPIO'
        assert gpio_1.function_by_index(1).name == 'UART_TX'
