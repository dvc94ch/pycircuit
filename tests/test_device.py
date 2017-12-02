import unittest
from pycircuit.device import *


class FunTests(unittest.TestCase):

    def setUp(self):
        Bus.busses = []
        Bus('UART',
            Fun('TX', Fun.OUTPUT),
            Fun('RX', Fun.INPUT))

    def test_name_only(self):
        f = Fun('GPIO')
        assert f.name == 'GPIO'
        assert f.bus is None
        assert f.dir == Fun.BIDIR
        assert str(f) == 'GPIO'
        assert repr(f) == 'io_GPIO'

    def test_name_and_dir(self):
        f = Fun('VCC', Fun.INPUT)
        assert f.name == 'VCC'
        assert f.bus is None
        assert f.dir == Fun.INPUT
        assert str(f) == 'VCC'
        assert repr(f) == 'i_VCC'

    def test_bus(self):
        f = Fun('UART0', 'UART', 'TX')
        assert f.bus_name == 'UART0'
        assert f.bus_func == 'TX'
        assert f.name == 'UART_TX'
        assert f.bus.type == 'UART'
        assert str(f) == 'UART_TX'
        assert repr(f) == 'UART0__o_UART_TX'

    def test_bus_no_name(self):
        f = Fun('UART', 'TX')
        assert f.bus_name == 'UART'
        assert f.bus_func == 'TX'
        assert f.name == 'UART_TX'
        assert f.bus.type == 'UART'


class BusTests(unittest.TestCase):

    def setUp(self):
        Bus.busses = []

    def test_register_bus(self):
        bus = Bus('UART',
                  Fun('TX', Fun.OUTPUT),
                  Fun('RX', Fun.INPUT))
        assert Bus.bus_by_type('UART') == bus
        assert bus.type == 'UART'
        assert len(bus.functions) == 2
        assert str(bus) == 'UART'
        assert repr(bus) == 'UART                 (RX TX)'

    def test_function_by_name(self):
        xtal = Bus('XTAL', Fun('XI', Fun.INPUT), Fun('XO', Fun.OUTPUT))
        assert xtal.type == 'XTAL'
        assert len(xtal.functions) == 2
        assert xtal.function_by_name('XI').name == 'XI'


class PinTests(unittest.TestCase):

    def test_simple_pin(self):
        pin = Pin('GPIO')
        assert pin.name == 'GPIO'
        assert pin.descr == ''
        assert pin.domain == Pin.SIGNAL
        assert len(pin.functions) == 1
        assert isinstance(pin.functions[0], Fun)
        assert pin.functions[0].name == 'GPIO'
        assert pin.functions[0].dir == Fun.BIDIR

    def test_pin_with_descr(self):
        pin = Pin('GPIO', descr='A GPIO Pin')
        assert pin.descr == 'A GPIO Pin'

    def test_pin_with_fun(self):
        pin = Pin('GPIO_1', 'GPIO', Fun('UART_1', 'UART', 'TX'), descr='A GPIO Pin')
        assert pin.name == 'GPIO_1'
        assert pin.descr == 'A GPIO Pin'
        assert pin.domain == Pin.SIGNAL
        assert len(pin.functions) == 2
        assert pin.functions[0].name == 'GPIO'
        assert pin.functions[1].name == 'UART_TX'

    def test_function_by_name(self):
        pin = Pin('GPIO_1', 'GPIO')
        assert isinstance(pin.function_by_name('GPIO'), Fun)


class DeviceTests(unittest.TestCase):

    def setUp(self):
        Bus.busses = []
        Bus('JTAG', Fun('TCK', Fun.INPUT), Fun('TDO', Fun.OUTPUT),
                    Fun('TMS', Fun.INPUT), Fun('TDI', Fun.INPUT))
        Bus('UART', Fun('RX', Fun.INPUT), Fun('TX', Fun.OUTPUT))

    def test_device(self):
        dev = Device('MCU', pins=[
            Pin('GND'),
            Pin('VCC'),
            Pin('XTAL_XI'),
            Pin('XTAL_XO'),
            Pin('JTAG_TCK', Fun('JTAG', 'TCK')),
            Pin('JTAG_TDO', Fun('JTAG', 'TDO')),
            Pin('JTAG_TMS', Fun('JTAG', 'TMS')),
            Pin('JTAG_TDI', Fun('JTAG', 'TDI')),
            Pin('GPIO_1', 'GPIO', Fun('UART_1', 'UART', 'TX')),
            Pin('GPIO_2', 'GPIO', Fun('UART_1', 'UART', 'RX')),
            Pin('GPIO_3', 'GPIO'),
            Pin('GPIO_4', 'GPIO'),
            Pin('GPIO_5', 'GPIO', Fun('UART_2', 'UART', 'TX')),
            Pin('GPIO_6', 'GPIO', Fun('UART_2', 'UART', 'RX'))
        ])

        assert dev.name == 'MCU'
        assert len(dev.pins) == 14
        assert len(dev.busses) == 3

        assert dev.bus_by_name('JTAG')[0].bus_name == 'JTAG'
        assert dev.bus_by_name('UART_1')[0].bus_name == 'UART_1'
        assert dev.busses_by_type('JTAG')[0][0].bus_name == 'JTAG'
        assert dev.busses_by_type('UART')[1][0].bus_name == 'UART_2'

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
