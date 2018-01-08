import unittest
from pycircuit.circuit import *


class ParserTests(unittest.TestCase):
    def setUp(self):
        self.circuit = Circuit('ParserTests')
        Circuit.active_circuit = self.circuit

    def test_parse_busses(self):
        ns = nets('')
        assert ns is None

        n0 = nets('n0')
        assert n0.name == 'n0'

        n1, n2, n3 = nets('n1 n2 n3')
        assert n1.name == 'n1'
        assert n2.name == 'n2'
        assert n3.name == 'n3'
        assert not n1.guid == n2.guid
        assert not n2.guid == n3.guid
        assert not n1.guid == n3.guid

        uart = nets('uart[2]')
        assert len(uart) == 2
        assert uart[0].name == 'uart[0]'
        assert uart[1].name == 'uart[1]'
        assert uart[0].guid == uart[1].guid

        gpio, uart = nets('gpio[3] usart[2]')
        assert len(gpio) == 3
        assert len(uart) == 2
        assert not gpio[0].guid == uart[0].guid

    def test_parse_power_net(self):
        assert parse_power_net('GND') == 0
        assert parse_power_net('gnd') == 0

        assert parse_power_net('0') == 0
        assert parse_power_net('0V') == 0
        assert parse_power_net('V0') == 0

        assert parse_power_net('3.3') == 3.3
        assert parse_power_net('3.3V') == 3.3
        assert parse_power_net('V3.3') == 3.3
        assert parse_power_net('3V3') == 3.3
