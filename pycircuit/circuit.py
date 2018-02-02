import math
import re
from enum import Enum
from pycircuit.component import Component, Pin, PinType
from pycircuit.device import Device


class UID(object):
    '''Deterministic unique ID generator.'''
    _uid = 0

    @classmethod
    def uid(cls):
        _uid = cls._uid
        cls._uid += 1
        return _uid


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


class NetType(Enum):
    SIGNAL, VCC, VEE, GND = range(4)

    def __str__(self):
        return self.name.lower()


class Net(CircuitElement):
    def __init__(self, name, _parent=None, _uid=None, _guid=None):
        super().__init__(name, _parent, _uid, _guid)
        self.type = NetType.SIGNAL

    def set_net_type(self):
        for assign in self.assigns:
            v = assign.node_voltage()
            if v is None:
                continue
            if v == 0:
                self.type = NetType.GND
            elif v > 0:
                self.type = NetType.VCC
            else:
                self.type = NetType.VEE
            break

    def __repr__(self):
        return '%s %s' % (str(self.type), self.name)


class PortType(Enum):
    POWER, GND, IN, OUT = range(4)

    def invert(self):
        if self is PortType.IN:
            return PortType.OUT
        if self is PortType.OUT:
            return PortType.IN
        # See ERCType for this to make sense
        if self is PortType.GND:
            return PortType.IN
        if self is PortType.POWER:
            return PortType.OUT
        return self

    def __str__(self):
        return self.name.lower()

    @classmethod
    def from_string(cls, string):
        if string == 'power':
            return PortType.POWER
        if string == 'gnd':
            return PortType.GND
        if string == 'in':
            return PortType.IN
        if string == 'out':
            return PortType.OUT


class Port(CircuitElement):
    def __init__(self, name, type, _parent=None, _uid=None, _guid=None):
        super().__init__(name, _parent, _uid, _guid)
        self.type = type

        self.internal = None
        self.external = None

    def internal_net(self):
        '''Returns the internal net of a Port.'''

        if self.internal is None:
            self.internal = PortAssign(self, Net(self.name))
        return self.internal.net

    def is_external(self):
        # No connection has been made externally
        return self.external is None

    def __repr__(self):
        return '%s %s' % (str(self.type), self.name)

    def to_object(self):
        obj = super().to_object()
        obj['type'] = str(self.type)
        if self.internal is not None:
            obj['internal'] = self.internal.to_object()
        if self.external is not None:
            obj['external'] = self.external.to_object()
        return obj

    @classmethod
    def from_object(cls, obj, parent):
        port_type = PortType.from_string(obj['type'])
        port = cls(obj['name'], port_type,
                   _parent=parent, _uid=obj['uid'], _guid=obj['guid'])
        if 'internal' in obj:
            port.internal = PortAssign.from_object(
                obj['internal'], parent, port)
        if 'external' in obj:
            port.external = PortAssign.from_object(
                obj['external'], parent, port, external=True)
        return port


class Inst(CircuitElement):
    def __init__(self, component, value=None,
                 _parent=None, _uid=None, _guid=None):
        self.set_component(component)
        self.set_value(value)
        self.device = None
        super().__init__(self.component.name, _parent, _uid, _guid)

    def set_component(self, component):
        self.component = Component.component_by_name(component)

    def set_value(self, value):
        self.value = str(value) if value is not None else None

    def assign_by_pin_name(self, pin_name):
        pin = self.component.pin_by_name(pin_name)
        for assign in self.assigns:
            if assign.pin == pin:
                return assign

    def __setitem__(self, function, to):
        if isinstance(function, tuple):
            guid = UID.uid()
            for function, to in zip(function, to):
                self.assign(function, to, guid=guid)
        else:
            self.assign(function, to)

    def assign(self, function, to, guid=None):
        assert self.component.has_function(function)
        if not self.component.is_busfun(function):
            guid = None
        if isinstance(to, Port):
            to = to.internal_net()
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
        obj = super().to_object()
        obj['component'] = self.component.name
        obj['value'] = self.value
        obj['assigns'] = [assign.to_object() for assign in self.assigns]
        if self.device is not None:
            obj['device'] = self.device.name
        return obj

    @classmethod
    def from_object(cls, obj, parent):
        inst = cls(obj['component'], obj['value'],
                   _parent=parent, _uid=obj['uid'], _guid=obj['guid'])
        inst.name = obj['name']
        if 'device' in obj:
            inst.device = Device.device_by_name(obj['device'])
        for assign in obj['assigns']:
            InstAssign.from_object(assign, parent, inst)
        return inst


class Assign(CircuitElement):
    def __init__(self, net, _parent=None, _uid=None, _guid=None):
        super().__init__(None, _parent, _uid, _guid)
        assert isinstance(net, Net)
        self.net = net
        self.net.assigns.append(self)
        self.erc_type = None

    def to_object(self):
        obj = super().to_object()
        obj['net'] = self.net.uid
        obj['erc_type'] = str(self.erc_type)
        return obj


class InstAssign(Assign):
    def __init__(self, inst, function, net,
                 _parent=None, _uid=None, _guid=None):
        assert isinstance(inst, Inst)
        super().__init__(net, _parent, _uid, _guid)
        self.inst = inst
        self.inst.assigns.append(self)
        self.function = function
        self.pin = None
        self.type = None

    def node_voltage(self):
        if self.pin.type == PinType.POWER:
            return parse_power_net(self.pin.name)
        elif self.pin.type == PinType.GND:
            return 0

    def __str__(self):
        return self.inst.name

    def __repr__(self):
        return '%s = %s' % (self.function, str(self.net))

    def to_object(self):
        obj = super().to_object()
        obj['function'] = self.function
        if self.pin is not None:
            obj['pin'] = self.pin.name
        if self.type is not None:
            obj['type'] = str(self.type)
        return obj

    @classmethod
    def from_object(cls, obj, parent, inst):
        net = inst.parent.net_by_uid(obj['net'])
        inst_assign = cls(inst, obj['function'], net,
                          _parent=parent, _uid=obj['uid'], _guid=obj['guid'])
        if 'pin' in obj:
            inst_assign.pin = inst.component.pin_by_name(obj['pin'])
        if 'type' in obj:
            inst_assign.type = PinType.from_string(obj['type'])
        return inst_assign


class PortAssign(Assign):
    def __init__(self, port, net, external=False,
                 _parent=None, _uid=None, _guid=None):
        assert isinstance(port, Port)
        super().__init__(net, _parent, _uid, _guid)
        self.port = port
        self.port.assigns.append(self)
        self.type = self.port.type
        if not external:
            self.type = self.type.invert()

    def node_voltage(self):
        if self.port.type == PortType.POWER:
            return parse_power_net(self.port.name)
        elif self.port.type == PortType.GND:
            return 0

    def __str__(self):
        return self.port.name

    def __repr__(self):
        return '%s = %s' % (self.port.name, str(self.net))

    def to_object(self):
        return super().to_object()

    @classmethod
    def from_object(cls, obj, parent, port, external=False):
        net = parent.net_by_uid(obj['net'])
        return cls(port, net, external=external,
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
        inst.parent = self
        self.insts.append(inst)

    def add_net(self, net):
        net.parent = self
        self.nets.append(net)

    def add_assign(self, assign):
        assign.parent = self
        self.assigns.append(assign)

    def inst_by_uid(self, uid):
        for inst in self.iter_insts():
            if inst.uid == uid:
                return inst

    def net_by_uid(self, uid):
        for net in self.iter_nets():
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
        }

    @classmethod
    def from_object(cls, obj):
        netlist = cls(obj['name'])
        for net in obj['nets']:
            Net.from_object(net, netlist)
        for inst in obj['insts']:
            Inst.from_object(inst, netlist)
        return netlist


class Circuit(Netlist):
    # Used in circuit decorator and CircuitElement.__init__
    active_circuit = None

    def __init__(self, name, _parent=None):
        self.parent = _parent
        super().__init__(name)

        self.uid = UID.uid()
        self.subinsts = []
        self.ports = []
        self.port_assigns = []

    def add_circuit_element(self, elem):
        if isinstance(elem, SubInst):
            self.add_subinst(elem)
        elif isinstance(elem, Port):
            self.add_port(elem)
        elif isinstance(elem, PortAssign):
            self.add_port_assign(elem)
        else:
            super().add_circuit_element(elem)

    def add_subinst(self, subinst):
        subinst.parent = self
        self.subinsts.append(subinst)

    def add_port(self, port):
        port.parent = self
        self.ports.append(port)

    def add_port_assign(self, port_assign):
        port_assign.parent = self
        self.port_assigns.append(port_assign)

    def subinst_by_uid(self, uid):
        for subinst in self.subinsts:
            if subinst.uid == uid:
                return subinst

    def port_by_uid(self, uid):
        for port in self.iter_ports():
            if port.uid == uid:
                return port

    def port_by_name(self, name):
        for port in self.ports:
            if port.name == name:
                return port

    def external_ports(self):
        for port in self.iter_ports():
            if port.is_external():
                yield port

    def ports_by_guid(self, guid):
        for port in self.ports:
            if port.guid == guid:
                yield port

    def port_guids(self):
        guids = set()
        for port in self.ports:
            if not port.guid in guids:
                guids.add(port.guid)
                yield port.guid

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

    def assigned_nets(self):
        for net in self.iter_nets():
            if len(net.assigns) > 0:
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

    def iter_port_assigns(self):
        for assign in self.port_assigns:
            yield assign
        for subinst in self.iter_subinsts():
            for assign in subinst.circuit.port_assigns:
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
            'nets': [net.to_object() for net in self.iter_nets()],
            'insts': [inst.to_object() for inst in self.iter_insts()],
            'ports': [port.to_object() for port in self.iter_ports()]
        }

    @classmethod
    def from_object(cls, obj, parent=None):
        circuit = cls(obj['name'], _parent=parent)

        for net in obj['nets']:
            Net.from_object(net, circuit)
        for inst in obj['insts']:
            Inst.from_object(inst, circuit)
        for port in obj['ports']:
            Port.from_object(port, circuit)

        return circuit


class ERCType(Enum):
    INPUT, OUTPUT, UNKNOWN = range(3)

    def invert(self):
        if self is ERCType.INPUT:
            return ERCType.OUTPUT
        if self is ERCType.OUTPUT:
            return ERCType.INPUT
        return ERCType.UNKNOWN

    def __str__(self):
        return self.name.lower()

    @staticmethod
    def diff(erc_type1, erc_type2):
        if erc_type1 == ERCType.INPUT:
            if erc_type2 == ERCType.INPUT:
                raise AssertionError()
            return ERCType.INPUT, ERCType.OUTPUT
        elif erc_type1 == ERCType.OUTPUT:
            if erc_type2 == ERCType.OUTPUT:
                raise AssertionError()
            return ERCType.OUTPUT, ERCType.INPUT
        else:
            if erc_type2 == ERCType.INPUT:
                return ERCType.OUTPUT, ERCType.INPUT
            elif erc_type2 == ERCType.OUTPUT:
                return ERCType.INPUT, ERCType.OUTPUT
            else:
                return ERCType.UNKNOWN, ERCType.UNKNOWN

    @staticmethod
    def from_type(ty):
        if isinstance(ty, PortType):
            if ty == PortType.OUT or ty == PortType.GND:
                return ERCType.OUTPUT
            else:
                return ERCType.INPUT
        elif isinstance(ty, PinType):
            if ty == PinType.UNKNOWN or ty == PinType.INOUT:
                return ERCType.UNKNOWN
            elif ty == PinType.OUT or ty == PinType.GND:
                return ERCType.OUTPUT
            else:
                return ERCType.INPUT
        else:
            raise TypeError(type(ty))


class SubInst(CircuitElement):
    def __init__(self, circuit, _parent=None, _uid=None, _guid=None):
        super().__init__(None, _parent, _uid, _guid)
        self.name = circuit.name
        self.circuit = circuit
        circuit.parent = self.parent

    def __setitem__(self, port_name, to):
        if isinstance(port_name, tuple):
            for port_name, to in zip(port_name, to):
                self[port_name] = to
        else:
            self.assign(port_name, to)

    def assign(self, port_name, net):
        port = self.circuit.port_by_name(port_name)
        if port is None:
            raise Exception('No port named %s in circuit %s'
                            % (port_name, self.circuit.name))

        if isinstance(net, Port):
            net = net.internal_net()

        assign = PortAssign(port, net, external=True)
        port.external = assign

        self.assigns.append(assign)

    def __repr__(self):
        subinst = 'subinst %s of %s {\n' % (self.name, self.circuit.name)
        for assign in self.assigns:
            subinst += '  ' + repr(assign) + '\n'
        subinst += '}\n'
        return subinst


#### Helpers to make defining circuits, nets and ports more ergonomic ###
def parse_busses(string, cons, **kwargs):
    if len(string) < 1:
        return None

    regex = re.compile('([^\[\]]*)(\[([1-9][0-9]*)\])?$')
    busses = []
    for bus in string.split(' '):
        guid = UID.uid()
        m = regex.match(bus)
        if m is None:
            raise Exception('Invalid bus name %s' % bus)
        name, _, size = m.groups()
        if size is None:
            busses.append(cons(name, _guid=guid, **kwargs))
        else:
            bus = []
            for i in range(int(size)):
                bus.append(cons('%s[%d]' % (name, i), _guid=guid, **kwargs))
            busses.append(bus)

    if len(busses) == 1:
        return busses[0]
    return busses


def parse_power_net(string):
    lstr = string.lower()
    if lstr == 'vcc':
        return math.inf
    elif lstr == 'vee':
        return -math.inf

    if 'gnd' in lstr:
        return 0

    lstr = lstr.replace('v', '.')
    if lstr.startswith('.'):
        lstr = lstr[1:]
    if lstr.endswith('.'):
        lstr = lstr[0:-1]
    return float(lstr)


def nets(string):
    return parse_busses(string, Net)


def circuit(name, gnd=None, power=None, inputs=None, outputs=None):
    def closure(function):
        def wrapper(**kwargs):
            # Save active circuit
            parent = Circuit.active_circuit
            # Create new circuit
            active = Circuit(name)
            # Set active circuit
            Circuit.active_circuit = active

            # Add ports to circuit
            if gnd is not None:
                parse_busses(gnd, Port, type=PortType.GND)
            if power is not None:
                parse_busses(power, Port, type=PortType.POWER)

            # Check that gnd and power nets have valid names
            for port in active.ports:
                try:
                    v = parse_power_net(port.name)
                    if v == 0:
                        assert port.type == PortType.GND
                except AssertionError:
                    raise Exception('Err: Port %s is not a gnd port.'
                                    % port.name)
                except Exception:
                    raise Exception('Err: %s is an invalid name for gnd or power port.'
                                    % port.name)

            if inputs is not None:
                parse_busses(inputs, Port, type=PortType.IN)
            if outputs is not None:
                parse_busses(outputs, Port, type=PortType.OUT)

            # Check that port names are unique
            port_names = set()
            for port in active.ports:
                if port.name in port_names:
                    raise Exception('Port names must be unique.')
                port_names.add(port.name)

            function(active, *active.ports, **kwargs)

            # Check circuit
            for port in active.ports:
                if len(port.assigns) < 1:
                    print('Warn: Unused port %s' % port.name)

            for subinst in active.subinsts:
                for port in subinst.circuit.ports:
                    if len(port.assigns) < 2:
                        print('Warn: Not unconnected port %s in subinst %s'
                              % (subinst.name, port.name))

            for net in active.nets:
                if len(net.assigns) < 2:
                    print('Warn: Only one assignment to net %s' % net.name)

            # Reset active circuit
            Circuit.active_circuit = parent
            return active
        return wrapper
    return closure


def testbench(circuit):
    tb = Circuit(circuit.name + '_testbench')
    Circuit.active_circuit = tb

    dut = SubInst(circuit, _parent=tb)
    gnd = Net('gnd', _parent=tb)
    nets = []

    for port in dut.circuit.external_ports():
        if port.type == PortType.GND:
            dut[port.name] = gnd
        else:
            nets.append(Net(port.name, _parent=tb))
            dut[port.name] = nets[-1]

            if port.type == PortType.POWER:
                Inst('V', 'dc %d' % parse_power_net(port.name),
                     _parent=tb)['+', '-'] = nets[-1], gnd
            elif port.type == PortType.IN:
                Inst('V', 'sin(0, 0.1, 1K) ac 1', _parent=tb)[
                    '+', '-'] = nets[-1], gnd
            elif port.type == PortType.OUT:
                Inst('TP', _parent=tb)['TP'] = nets[-1]

    return tb
