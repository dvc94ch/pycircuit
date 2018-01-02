from pycircuit.component import Component, Pin
from pycircuit.device import Device


class UID(object):
    '''Deterministic unique ID generator.'''
    _uid = 0

    @classmethod
    def uid(cls):
        _uid = cls._uid
        cls._uid += 1
        return _uid


### Circuit elements ###
class CircuitElement(object):
    '''Abstract base class for circuit elements.'''

    def __init__(self, name, _parent=None, _uid=None, _guid=None):
        self.parent = _parent
        self.uid = _uid
        self.guid = _guid
        self.name = name
        self.assigns = []

        if self.uid is None:
            self.uid = UID.uid()
        if self.guid is None:
            self.guid = UID.uid()
        if self.parent is None:
            self.parent = Circuit.active_circuit

        self.parent.add_circuit_element(self)

    def __enter__(self):
        # Helps visually grouping assignments
        return self

    def __exit__(self, type, value, traceback):
        # Helps visually grouping assignments
        pass

    def __str__(self):
        return self.name

    def to_object(self):
        return {
            'uid': self.uid,
            'guid': self.guid,
            'name': self.name,
        }

    @classmethod
    def from_object(cls, obj, parent):
        return cls(obj['name'], _parent=parent, _uid=obj['uid'], _guid=obj['guid'])


class Net(CircuitElement):
    def __repr__(self):
        return 'net %s' % self.name


class Port(CircuitElement):
    def __repr__(self):
        return 'port %s' % self.name

class Inst(CircuitElement):
    def __init__(self, name, component, value=None,
                 _parent=None, _uid=None, _guid=None, _device=None):
        super().__init__(name, _parent, _uid, _guid)
        self.set_component(component)
        self.set_value(value)
        self.device = _device

    def __setitem__(self, function, to):
        if isinstance(function, tuple):
            guid = UID.uid()
            for function, to in zip(function, to):
                self.assign(function, to, guid=guid)
        else:
            self.assign(function, to)

    def set_component(self, component):
        self.component = Component.component_by_name(component)

    def set_value(self, value):
        self.value = str(value) if value is not None else None

    def assign(self, function, to, guid=None):
        assert self.component.has_function(function)
        if not self.component.is_busfun(function):
            guid = None
        InstAssign(self, function, to, _guid=guid)

    def __repr__(self):
        inst = 'inst %s of %s {\n' % (self.name, self.component.name)
        if self.value is not None:
            inst += 'attr %s\n' % self.value
        for assign in self.assigns:
            inst += '  ' + repr(assign) + '\n'
        inst += '}\n'
        return inst

    def to_object(self):
        return {
            'uid': self.uid,
            'guid': self.guid,
            'name': self.name,
            'component': self.component.name,
            'value': self.value,
            'device': self.device.name
            if isinstance(self.device, Device) else None,
        }

    def assign_by_pin_name(self, pin_name):
        pin = self.component.pin_by_name(pin_name)
        for assign in self.assigns:
            if assign.pin == pin:
                return assign

    @classmethod
    def from_object(cls, obj, parent):
        device = Device.device_by_name(obj['device']) \
                 if not obj['device'] is None else None
        return cls(obj['name'], obj['component'], obj['value'],
                   _parent=parent, _uid=obj['uid'], _guid=obj['guid'],
                   _device=device)


class SubInst(CircuitElement):
    def __init__(self, name, circuit, _parent=None, _uid=None, _guid=None):
        super().__init__(name, _parent, _uid, _guid)
        self.circuit = circuit
        circuit.parent = self.parent

    def __setitem__(self, port_name, to):
        if isinstance(port_name, tuple):
            for port_name, to in zip(port_name, to):
                self[port_name] = to
        else:
            self.assign(port_name, to)

    def assign(self, port_name, to):
        port = self.circuit.port_by_name(port_name)
        assert port is not None
        SubInstAssign(self, port, to)

    def __repr__(self):
        subinst = 'subinst %s of %s {\n' % (self.name, self.circuit.name)
        for assign in self.assigns:
            subinst += '  ' + repr(assign) + '\n'
        subinst += '}\n'
        return subinst

    def to_object(self):
        return {
            'uid': self.uid,
            'guid': self.guid,
            'name': self.name,
            'circuit': self.circuit.to_object()
        }

    @classmethod
    def from_object(cls, obj, parent):
        circuit = Circuit.from_object(obj['circuit'], parent)
        return cls(obj['name'], circuit,
                   _parent=parent, _uid=obj['uid'], _guid=obj['guid'])


class CircuitAssign(CircuitElement):
    def __init__(self, to, _parent=None, _uid=None, _guid=None):
        super().__init__(None, _parent, _uid, _guid)
        assert isinstance(to, Net) or isinstance(to, Port)
        self.to = to
        self.to.assigns.append(self)


class InstAssign(CircuitAssign):
    def __init__(self, inst, function, to,
                 _parent=None, _uid=None, _guid=None, _pin=None):
        super().__init__(to, _parent, _uid, _guid)
        self.inst = inst
        self.function = function
        self.pin = _pin
        self.inst.assigns.append(self)

    def __str__(self):
        return '%s (%s)' % (str(self.pin), str(self.function))

    def __repr__(self):
        return '%s = %s' % (self.function, str(self.to))

    def is_final(self):
        return isinstance(self.to, Net)

    def to_object(self):
        return {
            'uid': self.uid,
            'guid': self.guid,
            'inst': self.inst.uid,
            'function': self.function,
            'pin': self.pin.name
            if isinstance(self.pin, Pin) else None,
            'to': self.to.uid,
        }

    @classmethod
    def from_object(cls, obj, parent):
        inst = parent.inst_by_uid(obj['inst'])
        to = parent.net_by_uid(obj['to'])
        if to is None:
            to = parent.port_by_uid(obj['to'])
        pin = inst.component.pin_by_name(obj['pin'])
        return cls(inst, obj['function'], to, _pin=pin,
                   _parent=parent, _uid=obj['uid'], _guid=obj['guid'])


class SubInstAssign(CircuitAssign):
    def __init__(self, subinst, port, to,
                 _parent=None, _uid=None, _guid=None):
        super().__init__(to, _parent, _uid, _guid)
        self.subinst = subinst
        self.port = port
        self.subinst.assigns.append(self)

    def __str__(self):
        return self.port.name

    def __repr__(self):
        return '%s = %s' % (self.port.name, str(self.to))

    def to_object(self):
        return {
            'uid': self.uid,
            'guid': self.guid,
            'subinst': self.subinst.uid,
            'port': self.port.uid,
            'to': self.to.uid
        }

    @classmethod
    def from_object(cls, obj, parent):
        subinst = parent.subinst_by_uid(obj['subinst'])
        port = subinst.circuit.port_by_uid(obj['port'])
        to = parent.net_by_uid(obj['to'])
        if to is None:
            to = parent.port_by_uid(obj['to'])
        return cls(subinst, port, to,
                   _parent=parent, _uid=obj['uid'], _guid=obj['guid'])


class Netlist(object):
    def __init__(self, name):
        self.name = name
        self.insts = []
        self.nets = []
        self.assigns = []

    def add_circuit_element(self, elem):
        if isinstance(elem, Inst):
            self.add_inst(elem)
        if isinstance(elem, Net):
            self.add_net(elem)
        if isinstance(elem, InstAssign):
            self.add_assign(elem)

    def set_values(self, values):
        for inst, value in values.items():
            self.inst_by_name(inst).set_value(value)

    def add_inst(self, inst):
        assert self.inst_by_name(inst.name) is None
        self.insts.append(inst)

    def add_net(self, net):
        assert self.net_by_name(net.name) is None
        self.nets.append(net)

    def add_assign(self, assign):
        self.assigns.append(assign)

    def inst_by_name(self, name):
        for inst in self.insts:
            if inst.name == name:
                return inst

    def net_by_name(self, name):
        for net in self.nets:
            if net.name == name:
                return net

    def inst_by_uid(self, uid):
        for inst in self.insts:
            if inst.uid == uid:
                return inst

    def net_by_uid(self, uid):
        for net in self.nets:
            if net.uid == uid:
                return net

    def iter_insts(self):
        return iter(self.insts)

    def iter_nets(self):
        return iter(self.nets)

    def iter_assigns(self):
        return iter(self.assigns)

    def __str__(self):
        return self.name

    def __repr__(self):
        design = 'design {\n'
        for net in self.nets:
            design += '  ' + repr(net) + '\n'
        for inst in self.insts:
            for line in repr(inst).split('\n'):
                design += '\n  ' + line
        design += '\n}\n'
        return design

    def to_object(self):
        return {
            'name': self.name,
            'nets': [net.to_object() for net in self.nets],
            'insts': [inst.to_object() for inst in self.insts],
            'assigns': [assign.to_object() for assign in self.assigns],
        }

    @classmethod
    def from_object(cls, obj):
        netlist = cls(obj['name'])
        for net in obj['nets']:
            Net.from_object(net, netlist)
        for inst in obj['insts']:
            Inst.from_object(inst, netlist)
        for assign in obj['assigns']:
            InstAssign.from_object(assign, netlist)
        return netlist


class Circuit(Netlist):
    # Used in circuit decorator and CircuitElement.__init__
    active_circuit = None

    def __init__(self, name, _parent=None):
        self.parent = _parent
        super().__init__(name)

        self.subinsts = []
        self.ports = []
        self.subinst_assigns = []

    def add_circuit_element(self, elem):
        if isinstance(elem, SubInst):
            self.add_subinst(elem)
        elif isinstance(elem, Port):
            self.add_port(elem)
        elif isinstance(elem, SubInstAssign):
            self.add_subinst_assign(elem)
        else:
            super().add_circuit_element(elem)

    def add_subinst(self, subinst):
        assert self.subinst_by_name(subinst.name) is None
        self.subinsts.append(subinst)

    def add_port(self, port):
        assert self.port_by_name(port.name) is None
        self.ports.append(port)

    def add_subinst_assign(self, subinst_assign):
        self.subinst_assigns.append(subinst_assign)

    def subinst_by_name(self, name):
        for subinst in self.subinsts:
            if subinst.name == name:
                return subinst

    def port_by_name(self, name):
        for port in self.ports:
            if port.name == name:
                return port

    def subinst_by_uid(self, uid):
        for subinst in self.subinsts:
            if subinst.uid == uid:
                return subinst

    def port_by_uid(self, uid):
        for port in self.ports:
            if port.uid == uid:
                return port

    def iter_insts(self):
        for inst in self.insts:
            yield inst
        for subinst in self.iter_subinsts():
            for inst in subinst.circuit.insts:
                yield inst

    def iter_subinsts(self):
        for subinst in self.subinsts:
            yield subinst
            for subinst in subinst.circuit.iter_subinsts():
                yield subinst

    def iter_nets(self):
        for net in self.nets:
            yield net
        for subinst in self.iter_subinsts():
            for net in subinst.circuit.nets:
                yield net

    def iter_ports(self):
        for port in self.ports:
            yield port
        for subinst in self.iter_subinsts():
            for port in subinst.circuit.ports:
                yield port

    def iter_assigns(self):
        for assign in self.assigns:
            yield assign
        for subinst in self.iter_subinsts():
            for assign in subinst.circuit.assigns:
                yield assign

    def iter_subinst_assigns(self):
        for assign in self.subinst_assigns:
            yield assign
        for subinst in self.iter_subinsts():
            for assign in subinst.circuit.subinst_assigns:
                yield assign

    def __repr__(self):
        subdesign = 'subdesign {\n'
        for port in self.ports:
            subdesign += '  ' + repr(port) + '\n'
        for net in self.nets:
            subdesign += '  ' + repr(net) + '\n'
        for inst in self.insts:
            for line in repr(inst).split('\n'):
                subdesign += '\n  ' + line
        for subinst in self.subinsts:
            for line in repr(subinst).split('\n'):
                subdesign += '\n ' + line
        subdesign += '\n}\n'
        return subdesign

    def to_object(self):
        return {
            'name': self.name,
            'ports': [port.to_object() for port in self.ports],
            'nets': [net.to_object() for net in self.nets],
            'insts': [inst.to_object() for inst in self.insts],
            'subinsts': [subinst.to_object() for subinst in self.subinsts],
            'assigns': [assign.to_object() for assign in self.assigns],
            'subinst_assigns': [assign.to_object() for assign in self.subinst_assigns],
        }

    @classmethod
    def from_object(cls, obj, parent):
        circuit = cls(obj['name'], _parent=parent)
        for port in obj['ports']:
            Port.from_object(port, circuit)
        for net in obj['nets']:
            Net.from_object(net, circuit)
        for inst in obj['insts']:
            Inst.from_object(inst, circuit)
        for subinst in obj['subinsts']:
            SubInst.from_object(subinst, circuit)
        for assign in obj['assigns']:
            InstAssign.from_object(assign, circuit)
        for subinst_assign in obj['subinst_assigns']:
            SubInstAssign.from_object(subinst_assign, circuit)
        return circuit


#### Helpers to make defining circuits, nets and ports more ergonomic ###
def nets(string):
    return [Net(name) for name in string.split(' ')]

def ports(string):
    return [Port(name) for name in string.split(' ')]

def bus(name, size, port=False):
    cls = Port if port else Net
    return [cls('%s_%d' % (name, i)) for i in range(size)]

def i_two_port(port=True):
    '''Two port interface.'''

    gen = ports if port else nets
    power = gen('v+ v-')
    vin, vout, gnd = gen('vin vout gnd')
    return power, (vin, gnd), (vout, gnd)

def circuit(name):
    def closure(function):
        def wrapper(*args, **kwargs):
            # Save active circuit
            parent = Circuit.active_circuit
            # Create new circuit
            circuit = Circuit(name)
            # Set active circuit
            Circuit.active_circuit = circuit
            function(*args, **kwargs)
            # Reset active circuit
            Circuit.active_circuit = parent
            return circuit
        return wrapper
    return closure
