import unittest
from pycircuit.circuit import *
from pycircuit.library import *

class MockPort(object):
    def __init__(self, name):
        self.name = name
        self.net = None

    def __str__(self):
        return self.name

    def __add__(self, other):
        return Port.connect(self, other)


class CircuitTestCase(unittest.TestCase):

    def setUp(self):
        Circuit.active_circuit = Circuit('')


class VecTests(unittest.TestCase):

    def test_vec(self):
        v1 = Vec([1, 2, 3, 4])
        v2 = Vec([4, 3, 2, 1])
        assert v1 + v2 == Vec([5, 5, 5, 5])

class NetTests(unittest.TestCase):

    def setUp(self):
        Net.counter = 1
        self.circuit = Circuit('')
        Circuit.active_circuit = self.circuit

    def test_id(self):
        n = Net('net')
        assert n.name == 'net'
        assert n.id == 1
        assert Net.counter == 2

    def test_new_net(self):
        gnd = Net('GND')
        assert len(self.circuit.nets) == 1
        assert self.circuit.nets[0].name == 'GND'

    def test_existing_net(self):
        gnd = Net('GND')
        gnd2 = Net('GND')
        assert gnd == gnd2

    def test_add_port(self):
        gnd = Net('GND') + MockPort('a')
        assert len(gnd.ports) == 1
        assert gnd.ports[0].name == 'a'
        assert gnd.ports[0].net == gnd

    def test_add_vec(self):
        vec = MockPort('a') + MockPort('b')
        assert isinstance(vec, Vec)
        assert len(vec) == 2
        gnd = Net('GND') + vec
        assert len(gnd.ports) == 2
        assert gnd.ports[0].name == 'a'
        assert gnd.ports[0].net == gnd
        assert gnd.ports[1].name == 'b'
        assert gnd.ports[1].net == gnd

    def test_add_net(self):
        agnd = Net('AGND') + MockPort('a') + MockPort('b')
        gnd = Net('GND') + agnd
        assert len(gnd) == 2
        assert len(gnd.ports) == 0
        assert len(gnd.nets) == 1
        assert gnd.nets[0].name == 'AGND'
        assert len(gnd.nets[0].ports) == 2


@circuit('a')
def a():
    Node('R', 'R')
    Ref('R')['1', '2'] + (Net('VDD'), Net('GND'))


class RefTests(CircuitTestCase):

    def test_node_ref(self):
        Node('R', 'R')
        assert isinstance(Ref('R')['1'], Port)
        assert isinstance(Ref('R')['~'], Port)
        assert isinstance(Ref('R')['1', '2'], Vec)
        vec = Ref('R')['~', '~']
        assert isinstance(vec, Vec)
        assert isinstance(vec['1'], Port)
        assert isinstance(vec['2'], Port)

    def test_sub_ref(self):
        Sub('a', a())
        assert isinstance(Ref('a')['VDD'], Net)
        assert isinstance(Ref('a')['VDD', 'GND'], Vec)


class RefsTests(CircuitTestCase):

    def test_node_refs(self):
        Node('R1', 'R')
        Node('R2', 'R')
        assert isinstance(Refs('R1', 'R2')['1'], Vec)
        assert isinstance(Refs('R1', 'R2')['~'], Vec)
        assert isinstance(Refs('R1', 'R2')['1', '2'], Vec)
        vec = Refs('R1', 'R2')['~', '~']
        assert isinstance(vec, Vec)
        assert len(vec) == 2
        for v in vec:
            assert len(v) == 2
            assert isinstance(v, Vec)

    def test_sub_refs(self):
        Sub('a1', a())
        Sub('a2', a())
        assert isinstance(Refs('a1', 'a2')['VDD'], Vec)
        assert isinstance(Refs('a1', 'a2')['VDD', 'GND'], Vec)


class NetsTests(CircuitTestCase):

    def test_nets(self):
        gnd, agnd, gnd2 = Nets('GND', 'AGND', 'GND')
        assert isinstance(gnd, Net)
        assert isinstance(agnd, Net)
        assert isinstance(gnd2, Net)
        assert gnd == gnd2

    def test_connect_nets_to_refs(self):
        Node('C1', 'C')
        Node('C2', 'C')
        Nets('VDD', 'GND') + Refs('C1', 'C2')['~', '~']
        assert len(Net('VDD').ports) == 2
        assert len(Net('GND').ports) == 2

'''
@circuit('b')
def b():
    Sub('a1', a())
    Sub('a2', a())
    Net('1') + Ref('a1.R')['~'] + Ref('a2.R')['~']
    Net('2') + Ref('a1.R')['~'] + Ref('a2.R')['~']

@circuit('c')
def c():
    Node('TP1', 'TP')
    Sub('b1', b())
    Sub('b2', b())
    Ref('b1')['1'] + Ref('b2')['1']
    Ref('b1')['2'] + Ref('b2')['2']
    Ref('b1')['1'] + Ref('TP1')['TP']


class CircuitTests(unittest.TestCase):

    def setUp(self):
        Circuit.active_circuit = Circuit('')

    def test_ports_by_circuit(self):
        cir = b()
        for net in cir.iter_nets():
            ports_by_circuit = net.ports_by_circuit()
            assert len(ports_by_circuit) == 3
            assert 'a1' in ports_by_circuit
            assert 'a2' in ports_by_circuit
            assert len(ports_by_circuit['a1']['.']) == 1
            assert len(ports_by_circuit['a2']['.']) == 1

    def test_ports_by_circuit_nested(self):
        cir = c()
        for net in cir.iter_nets():
            ports_by_circuit = net.ports_by_circuit()
            #assert len(ports_by_circuit) == 3
            assert 'b1' in ports_by_circuit
            assert 'b2' in ports_by_circuit
            assert len(ports_by_circuit['b1']['a1']['.']) == 1
            assert len(ports_by_circuit['b2']['a2']['.']) == 1
'''
