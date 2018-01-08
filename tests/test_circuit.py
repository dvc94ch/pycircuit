import pytest
import unittest
from pycircuit.circuit import *


class CircuitTests(unittest.TestCase):
    def setUp(self):
        self.circuit = Circuit('CircuitTests')
        Circuit.active_circuit = self.circuit

    def test_port(self):
        p1 = Port('p1', PortType.IN)
        assert self.circuit.port_by_name('p1') == p1
        assert self.circuit.port_by_uid(p1.uid) == p1
        assert str(p1) == 'p1'
        assert repr(p1) == 'in p1'

    def test_net(self):
        n1 = Net('n1')
        assert self.circuit.net_by_uid(n1.uid) == n1
        assert str(n1) == 'n1'
        assert repr(n1) == 'signal n1'

    def test_inst(self):
        r1 = Inst('R')
        assert self.circuit.inst_by_uid(r1.uid) == r1
        assert str(r1) == 'R'
        assert repr(r1) == 'inst R of R {\n}\n'

    def test_subinst(self):
        s1 = SubInst(Circuit('SubCircuit'))
        assert self.circuit.subinst_by_uid(s1.uid) == s1
        assert str(s1) == 'SubCircuit'
        assert repr(s1) == 'subinst SubCircuit of SubCircuit {\n}\n'

    def test_assign_inst_to_net(self):
        n1 = Net('n1')
        r1 = Inst('R')
        r1['~'] = n1
        assert len(r1.assigns) == 1
        assert len(n1.assigns) == 1
        assert repr(r1) == 'inst R of R {\n  ~ = n1\n}\n'

    def test_assign_inst_to_port(self):
        p1 = Port('p1', PortType.IN)
        r1 = Inst('R')
        r1['~'] = p1
        assert len(r1.assigns) == 1
        assert len(p1.assigns) == 1
        assert repr(r1) == 'inst R of R {\n  ~ = p1\n}\n'

    def test_assign_subinst_to_net(self):
        net = Net('n1')
        circuit = Circuit('SubCircuit')
        port_inner = Port('p', PortType.IN, _parent=circuit)
        subinst = SubInst(circuit)
        subinst['p'] = net
        assert len(subinst.assigns) == 1
        assert len(net.assigns) == 1
        assert repr(subinst) == 'subinst SubCircuit of SubCircuit {\n  p = n1\n}\n'

    def test_assign_subinst_to_port(self):
        port = Port('p1', PortType.IN)
        circuit = Circuit('SubCircuit')
        port_inner = Port('p', PortType.IN, _parent=circuit)
        subinst = SubInst(circuit)
        subinst['p'] = port
        assert len(subinst.assigns) == 1
        assert len(port.assigns) == 1
        assert len(port_inner.assigns) == 1
        assert port.assigns[0].net == port_inner.assigns[0].net
        assert repr(subinst) == 'subinst SubCircuit of SubCircuit {\n  p = p1\n}\n'

    def test_port_to_object(self):
        p1 = Port('p1', PortType.IN)
        obj = p1.to_object()
        assert isinstance(obj['uid'], int)
        assert isinstance(obj['guid'], int)
        assert obj['name'] == 'p1'

    def test_port_from_object(self):
        p1 = Port.from_object({'uid': 0, 'guid': 1, 'name': 'p1', 'type': 0}, self.circuit)
        assert p1.uid == 0
        assert p1.name == 'p1'

    def test_net_to_object(self):
        n1 = Net('n1')
        obj = n1.to_object()
        assert isinstance(obj['uid'], int)
        assert isinstance(obj['guid'], int)
        assert obj['name'] == 'n1'

    def test_net_from_object(self):
        n1 = Port.from_object({'uid': 0, 'guid': 1, 'name': 'n1', 'type': 0}, self.circuit)
        assert n1.uid == 0
        assert n1.name == 'n1'

    def test_inst_to_object(self):
        r1 = Inst('R')
        obj = r1.to_object()
        assert isinstance(obj['uid'], int)
        assert isinstance(obj['guid'], int)
        assert obj['name'] == 'R'
        assert obj['component'] == 'R'
        assert obj['value'] == None
        assert obj['assigns'] == []

    def test_inst_from_object(self):
        r1 = Inst.from_object({
            'uid': 0,
            'guid': 1,
            'name': 'R1',
            'component': 'R',
            'value': None,
            'assigns': []
        }, self.circuit)
        assert r1.uid == 0
        assert r1.name == 'R1'
        assert isinstance(r1.component, Component)
        assert r1.component.name == 'R'
        assert r1.device is None
        assert r1.value is None

    def test_circuit_to_object(self):
        p1, n1, r1 = Port('p1', PortType.IN), Net('n1'), Inst('R')
        obj = self.circuit.to_object()
        assert obj['name'] == 'CircuitTests'
        assert len(obj['ports']) == 1
        assert len(obj['nets']) == 1
        assert len(obj['insts']) == 1

    def test_circuit_from_object(self):
        c1 = Circuit.from_object({
            'name': 'SubCircuit',
            'ports': [{'uid': 0, 'guid': 2, 'name': 'p1', 'type': 0}],
            'nets': [{'uid': 1, 'guid': 3, 'name': 'n1'}],
            'insts': [{
                'uid': 4,
                'guid': 5,
                'name': 'R1',
                'component': 'R',
                'value': None,
                'assigns': []
            }],
        }, None)
        assert c1.name == 'SubCircuit'
        assert len(c1.ports) == 1
        assert isinstance(c1.ports[0], Port)
        assert len(c1.nets) == 1
        assert isinstance(c1.nets[0], Net)
        assert len(c1.insts) == 1
        assert isinstance(c1.insts[0], Inst)

    def test_inst_assign_to_object(self):
        inst = Inst('R')
        function = '~'
        net = Net('n1')
        assign = InstAssign(inst, function, net)
        obj = assign.to_object()
        assert isinstance(obj['uid'], int)
        assert isinstance(obj['guid'], int)
        assert obj['function'] == function
        assert obj['net'] == net.uid

    def test_inst_assign_from_object(self):
        uid = UID.uid()
        guid = UID.uid()
        inst = Inst('R')
        function = '~'
        net = Net('n1')
        assign = InstAssign.from_object({
            'uid': uid,
            'guid': guid,
            'function': function,
            'pin': None,
            'type': None,
            'net': net.uid,
        }, self.circuit, inst)
        assert assign.uid == uid
        assert assign.guid == guid
        assert assign.inst == inst
        assert assign.function == function
        assert assign.pin is None
        assert assign.type is None
        assert assign.net == net

    def test_port_assign_to_object(self):
        circuit = Circuit('sub')
        port = Port('p1', PortType.IN, _parent=circuit)
        subinst = SubInst(circuit)
        net = Net('n1')
        assign = PortAssign(port, net)
        obj = assign.to_object()
        assert isinstance(obj['uid'], int)
        assert isinstance(obj['guid'], int)
        assert obj['net'] == net.uid

    def test_port_assign_from_object(self):
        uid = UID.uid()
        guid = UID.uid()
        circuit = Circuit('sub')
        port = Port('p1', PortType.IN, _parent=circuit)
        subinst = SubInst(circuit)
        net = Net('n1')
        assign = PortAssign.from_object({
            'uid': uid,
            'guid': guid,
            'net': net.uid,
        }, self.circuit, port)
        assert assign.uid == uid
        assert assign.guid == guid
        assert assign.port == port
        assert assign.net == net
