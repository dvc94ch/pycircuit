import unittest
from pytest import approx
from pycircuit.units import *


class ValueTests(unittest.TestCase):

    def setUp(self):
        Value.default_series_by_unit[''] = Value.E12

    def test_from_string(self):
        assert Value.from_string('1').value == 1.0
        assert Value.from_string('1.0').value == 1.0
        assert Value.from_string('1K').value == 1e3
        assert Value.from_string('1M').value == 1e6
        assert Value.from_string('2.2uF').value == 2.2e-6
        assert Value.from_string('33mH').value == 33e-3

    def test_to_string(self):
        assert str(Value(1)) == '1'
        assert str(Value(1e3)) == '1K'
        assert str(Value(2.2e-6)) == '2.2u'
        assert str(Value(33e-3)) == '33m'
        assert str(Value(1.123)) == '1.2'
        assert str(Value(2.2345e-6)) == '2.2u'
        assert str(Value(2.25e-6)) == '2.2u'
        assert str(Value(33.1e-3)) == '33m'

    def test_e_values(self):
        assert len(Value.E3) == 3
        assert len(Value.E6) == 6
        assert len(Value.E12) == 12
        assert len(Value.E24) == 24

    def test_select_value(self):
        assert Value(1).value_from_series() == approx(1.0)
        assert Value(10).value_from_series() == approx(10.0)
        assert Value(100).value_from_series() == approx(100.0)
        assert Value(0.1).value_from_series() == approx(0.1)
        assert Value(0.01).value_from_series() == approx(0.01)
        assert Value(2).value_from_series() == approx(2.2)
        assert Value(0.2).value_from_series() == approx(0.22)
        assert Value(20).value_from_series() == approx(22)
