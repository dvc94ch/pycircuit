import pytest
import unittest
from pycircuit.device import Device, Map
from pycircuit.library import *


class DeviceTests(unittest.TestCase):
    def setUp(self):
        Device.devices = []

    def test_works(self):
        Device('R0805', 'R', '0805',
               Map('1', 'A'),
               Map('2', 'B'))

    def test_none_none_map(self):
        with pytest.raises(Exception):
            Map(None, None)

    def test_component_doesnt_exist(self):
        with pytest.raises(Exception):
            Device('R0805', 'R1', '0805',
                   Map('1', 'A'),
                   Map('2', 'B'))

    def test_package_doesnt_exist(self):
        with pytest.raises(Exception):
            Device('R0805', 'R', 'R0805',
                   Map('1', 'A'),
                   Map('2', 'B'))

    def test_pin_doesnt_exist(self):
        with pytest.raises(Exception):
            Device('R0805', 'R', '0805',
                   Map('1', 'A'),
                   Map('2', 'C'))

    def test_pad_doesnt_exist(self):
        with pytest.raises(Exception):
            Device('R0805', 'R', '0805',
                   Map('1', 'A'),
                   Map('3', 'B'))

    def test_works2(self):
        Device('SOT23BCE', 'Q', 'SOT23',
               Map('1', 'B'),
               Map('2', 'C'),
               Map('3', 'E'),
               Map(None, 'SUBSTRATE'))

    def test_pin_unmapped(self):
        with pytest.raises(Exception):
            Device('SOT23BCE', 'Q', 'SOT23',
                   Map('1', 'B'),
                   Map('2', 'C'),
                   Map('3', 'E'))

    def test_pin_required(self):
        with pytest.raises(Exception):
            Device('SOT23BCE', 'Q', 'SOT23',
                   Map('1', 'B'),
                   Map('2', 'C'),
                   Map('3', 'SUBSTRATE'),
                   Map(None, 'E'))

    def pad_mapped_multiple(self):
        with pytest.raises(Exception):
            Device('SOT23BCE', 'Q', 'SOT23',
                   Map('1', 'B'),
                   Map('2', 'C'),
                   Map('3', 'E'),
                   Map('3', 'SUBSTRATE'))

    def test_works3(self):
        Device('RSOT23', 'R', 'SOT23',
               Map('1', 'A'),
               Map('2', 'B'),
               Map('3', None))

    def test_pad_unmapped(self):
        with pytest.raises(Exception):
            Device('RSOT23', 'R', 'SOT23',
                   Map('1', 'A'),
                   Map('2', 'B'))
