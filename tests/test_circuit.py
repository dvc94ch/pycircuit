import pytest
import unittest
from pycircuit.circuit import *


class CircuitTests(unittest.TestCase):
    def setUp(self):
        self.circuit = Circuit('CircuitTests')
        Circuit.active_circuit = self.circuit

    def test_port(self):
        p1 = Port('p1')
        assert self.circuit.port_by_name('p1') == p1
        assert str(p1) == 'p1'
        assert repr(p1) == 'port p1'

    def test_net(self):
        n1 = Net('n1')
        assert self.circuit.net_by_name('n1') == n1
        assert str(n1) == 'n1'
        assert repr(n1) == 'net n1'

    def test_inst(self):
        r1 = Inst('R1', 'R')
        assert self.circuit.inst_by_name('R1') == r1
        assert str(r1) == 'R1'
        assert repr(r1) == 'inst R1 of R {\n}\n'

    def test_subinst(self):
        s1 = SubInst('S1', Circuit('SubCircuit'))
        assert self.circuit.subinst_by_name('S1') == s1
        assert str(s1) == 'S1'
        assert repr(s1) == 'subinst S1 of SubCircuit {\n}\n'

    def test_port_name_unique(self):
        with pytest.raises(Exception):
            p1 = Port('p1')
            p2 = Port('p1')

    def test_net_name_unique(self):
        with pytest.raises(Exception):
            n1 = Net('n1')
            n2 = Net('n1')

    def test_inst_name_unique(self):
        with pytest.raises(Exception):
            r1 = Inst('r1', 'R')
            r2 = Inst('r1', 'R')

    def test_subinst_name_unique(self):
        with pytest.raises(Exception):
            s1 = SubInst('s1', Circuit('SubCircuit'))
            s2 = SubInst('s1', Circuit('SubCircuit'))

    def test_assign_inst_to_net(self):
        n1 = Net('n1')
        r1 = Inst('R1', 'R')
        r1['~'] = n1
        assert len(r1.assigns) == 1
        assert len(n1.assigns) == 1
        assert repr(r1) == 'inst R1 of R {\n  ~ = n1\n}\n'

    def test_assign_inst_to_port(self):
        p1 = Port('p1')
        r1 = Inst('R1', 'R')
        r1['~'] = p1
        assert len(r1.assigns) == 1
        assert len(p1.assigns) == 1
        assert repr(r1) == 'inst R1 of R {\n  ~ = p1\n}\n'

    def test_assign_subinst_to_net(self):
        net = Net('n1')
        circuit = Circuit('SubCircuit')
        port_inner = Port('p', _parent=circuit)
        subinst = SubInst('s1', circuit)
        subinst['p'] = net
        assert len(subinst.assigns) == 1
        assert len(net.assigns) == 1
        assert repr(subinst) == 'subinst s1 of SubCircuit {\n  p = n1\n}\n'

    def test_assign_subinst_to_port(self):
        port = Port('p1')
        circuit = Circuit('SubCircuit')
        port_inner = Port('p', _parent=circuit)
        subinst = SubInst('s1', circuit)
        subinst['p'] = port
        assert len(subinst.assigns) == 1
        assert len(port.assigns) == 1
        assert repr(subinst) == 'subinst s1 of SubCircuit {\n  p = p1\n}\n'

    def test_port_to_object(self):
        p1 = Port('p1')
        obj = p1.to_object()
        assert isinstance(obj['uid'], int)
        assert isinstance(obj['guid'], int)
        assert obj['name'] == 'p1'

    def test_port_from_object(self):
        p1 = Port.from_object({'uid': 0, 'guid': 1, 'name': 'p1'}, self.circuit)
        assert p1.uid == 0
        assert p1.name == 'p1'

    def test_net_to_object(self):
        n1 = Net('n1')
        obj = n1.to_object()
        assert isinstance(obj['uid'], int)
        assert isinstance(obj['guid'], int)
        assert obj['name'] == 'n1'

    def test_net_from_object(self):
        n1 = Port.from_object({'uid': 0, 'guid': 1, 'name': 'n1'}, self.circuit)
        assert n1.uid == 0
        assert n1.name == 'n1'

    def test_inst_to_object(self):
        r1 = Inst('R1', 'R')
        obj = r1.to_object()
        assert isinstance(obj['uid'], int)
        assert isinstance(obj['guid'], int)
        assert obj['name'] == 'R1'
        assert obj['component'] == 'R'
        assert obj['device'] == None
        assert obj['value'] == None

    def test_inst_from_object(self):
        r1 = Inst.from_object({
            'uid': 0,
            'guid': 1,
            'name': 'R1',
            'component': 'R',
            'device': None,
            'value': None,
        }, self.circuit)
        assert r1.uid == 0
        assert r1.name == 'R1'
        assert isinstance(r1.component, Component)
        assert r1.component.name == 'R'
        assert r1.device is None
        assert r1.value is None

    def test_subinst_to_object(self):
        c1 = Circuit('SubCircuit')
        s1 = SubInst('s1', c1)
        obj = s1.to_object()
        assert isinstance(obj['uid'], int)
        assert isinstance(obj['guid'], int)
        assert obj['name'] == 's1'
        assert obj['circuit']['name'] == 'SubCircuit'

    def test_subinst_from_object(self):
        s1 = SubInst.from_object({
            'uid': 0,
            'guid': 1,
            'name': 's1',
            'circuit': {
                'name': 'SubCircuit',
                'ports': [],
                'nets': [],
                'insts': [],
                'subinsts': [],
                'assigns': [],
                'subinst_assigns': [],
            }
        }, self.circuit)
        assert s1.uid == 0
        assert s1.name == 's1'
        assert isinstance(s1.circuit, Circuit)
        assert s1.circuit.name == 'SubCircuit'

    def test_circuit_to_object(self):
        p1, n1, r1 = Port('p1'), Net('n1'), Inst('R1', 'R')
        obj = self.circuit.to_object()
        assert obj['name'] == 'CircuitTests'
        assert len(obj['ports']) == 1
        assert len(obj['nets']) == 1
        assert len(obj['insts']) == 1

    def test_circuit_from_object(self):
        c1 = Circuit.from_object({
            'name': 'SubCircuit',
            'ports': [{'uid': 0, 'guid': 2, 'name': 'p1'}],
            'nets': [{'uid': 1, 'guid': 3, 'name': 'n1'}],
            'insts': [{
                'uid': 4,
                'guid': 5,
                'name': 'R1',
                'component': 'R',
                'device': None,
                'value': None
            }],
            'subinsts': [],
            'assigns': [],
            'subinst_assigns': [],
        }, None)
        assert c1.name == 'SubCircuit'
        assert len(c1.ports) == 1
        assert isinstance(c1.ports[0], Port)
        assert len(c1.nets) == 1
        assert isinstance(c1.nets[0], Net)
        assert len(c1.insts) == 1
        assert isinstance(c1.insts[0], Inst)

    def test_inst_assign_to_object(self):
        inst = Inst('R1', 'R')
        function = '~'
        to = Net('n1')
        assign = InstAssign(inst, function, to)
        obj = assign.to_object()
        assert isinstance(obj['uid'], int)
        assert isinstance(obj['guid'], int)
        assert obj['inst'] == inst.uid
        assert obj['function'] == function
        assert obj['pin'] is None
        assert obj['to'] == to.uid

    def test_inst_assign_from_object(self):
        uid = UID.uid()
        guid = UID.uid()
        inst = Inst('R1', 'R')
        function = '~'
        to = Net('n1')
        assign = InstAssign.from_object({
            'uid': uid,
            'guid': guid,
            'inst': inst.uid,
            'function': function,
            'pin': None,
            'to': to.uid,
        }, self.circuit)
        assert assign.uid == uid
        assert assign.guid == guid
        assert assign.inst == inst
        assert assign.function == function
        assert assign.pin is None
        assert assign.to == to

    def test_subinst_assign_to_object(self):
        circuit = Circuit('sub')
        port = Port('p1', _parent=circuit)
        subinst = SubInst('s1', circuit)
        to = Net('n1')
        assign = SubInstAssign(subinst, port, to)
        obj = assign.to_object()
        assert isinstance(obj['uid'], int)
        assert isinstance(obj['guid'], int)
        assert obj['subinst'] == subinst.uid
        assert obj['port'] == port.uid
        assert obj['to'] == to.uid

    def test_subinst_assign_from_object(self):
        uid = UID.uid()
        guid = UID.uid()
        circuit = Circuit('sub')
        port = Port('p1', _parent=circuit)
        subinst = SubInst('s1', circuit)
        to = Net('n1')
        assign = SubInstAssign.from_object({
            'uid': uid,
            'guid': guid,
            'subinst': subinst.uid,
            'port': port.uid,
            'to': to.uid,
        }, self.circuit)
        assert assign.uid == uid
        assert assign.guid == guid
        assert assign.subinst == subinst
        assert assign.port == port
        assert assign.to == to
