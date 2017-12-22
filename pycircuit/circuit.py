import uuid
from pycircuit.component import *


# Abstract base class
class CircuitElement(object):
    def __init__(self, name):
        self.parent = None
        self.uuid = uuid.uuid4()
        self.name = name
        self.assigns = []
        Circuit.active_circuit.add_circuit_element(self)

    def __str__(self):
        return self.name


# Ports and Nets
def nets(string):
    return [Net(name) for name in string.split(' ')]


class Net(CircuitElement):
    def __repr__(self):
        return 'net %s' % self.name


def ports(string):
    return [Port(name) for name in string.split(' ')]


class Port(CircuitElement):
    def __repr__(self):
        return 'port %s' % self.name


# Assignments
class CircuitAssign(object):
    def __init__(self, terminal, to):
        assert isinstance(to, Port) or isinstance(to, Net)
        self.uuid = uuid.uuid4()
        self.terminal = terminal
        self.to = to

    def __str__(self):
        return '%s (%s)' % (str(self.terminal.pin), str(self.terminal.function))

    def __repr__(self):
        return '%s = %s' % (str(self.terminal), str(self.to))


# Terminals
class Terminal(object):
    pass

class InstTerminal(Terminal):
    def __init__(self, inst, function):
        self.inst = inst
        self.function = function
        self.pin = None

    def __str__(self):
        return self.function

    def __repr__(self):
        return '%s %s' % (repr(self.inst), self.function)

class SubInstTerminal(Terminal):
    def __init__(self, subinst, port):
        self.subinst = subinst
        self.port = port

    def __str__(self):
        return str(self.port)

    def __repr__(self):
        return '%s %s' % (repr(self.subinst), str(self.port))


# Insts and SubInsts
class Inst(CircuitElement):
    def __init__(self, name, component, value=None):
        super().__init__(name)

        self.component = Component.component_by_name(component)
        self.value = value

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def __setitem__(self, function, to):
        if isinstance(function, tuple):
            for function, to in zip(function, to):
                self[function] = to
        else:
            assert self.component.has_function(function)
            terminal = InstTerminal(self, function)
            self.parent.assign(terminal, to)

    def __repr__(self):
        inst = 'inst %s of %s {\n' % (self.name, self.component.name)
        for assign in self.assigns:
            inst += '  ' + repr(assign) + '\n'
        inst += '}\n'
        return inst


class SubInst(CircuitElement):
    def __init__(self, name, circuit):
        self.circuit = circuit
        super().__init__(name)
        # Is set in add_subinst
        circuit.parent = self.parent

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def __setitem__(self, port_name, to):
        if isinstance(port_name, tuple):
            for port_name, to in zip(port_name, to):
                self[port_name] = to
        else:
            port = self.circuit.port_by_name(port_name)
            assert port is not None
            terminal = SubInstTerminal(self, port)
            self.parent.assign(terminal, to)

    def __repr__(self):
        return 'subinst %s of %s' % (self.name, self.circuit.name)


# Circuit decorator
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


# Circuit
class Circuit(object):

    active_circuit = None

    def __init__(self, name):
        self.parent = None
        self.name = name

        self.insts = []
        self.subinsts = []
        self.nets = []
        self.ports = []
        self.assigns = []

        self.insts_elab = []
        self.nets_elab = []
        self.assigns_elab = []

    def add_circuit_element(self, elem):
        if isinstance(elem, Inst):
            self.add_inst(elem)
        elif isinstance(elem, SubInst):
            self.add_subinst(elem)
        elif isinstance(elem, Net):
            self.add_net(elem)
        elif isinstance(elem, Port):
            self.add_port(elem)
        else:
            raise AssertionError('Not a circuit element')

    def add_inst(self, inst):
        assert self.inst_by_name(inst.name) is None
        inst.parent = self
        self.insts.append(inst)
        self.insts_elab.append(inst)

    def add_subinst(self, subinst):
        assert self.subinst_by_name(subinst.name) is None
        subinst.parent = self
        self.subinsts.append(subinst)

        # Propagate insts and assigns
        self.insts_elab += subinst.circuit.insts_elab
        self.assigns_elab += subinst.circuit.assigns_elab

        # Propagate internal nets
        for assign in subinst.circuit.assigns_elab:
            if isinstance(assign.terminal, InstTerminal) and \
               isinstance(assign.to, Net):
                self.nets_elab.append(assign.to)


    def add_net(self, net):
        assert self.net_by_name(net.name) is None
        net.parent = self
        self.nets.append(net)
        self.nets_elab.append(net)

    def add_port(self, port):
        assert self.port_by_name(port.name) is None
        port.parent = self
        self.ports.append(port)

    def inst_by_name(self, name):
        for inst in self.insts:
            if inst.name == name:
                return inst

    def subinst_by_name(self, name):
        for subinst in self.subinsts:
            if subinst.name == name:
                return subinst

    def net_by_name(self, name):
        for net in self.nets:
            if net.name == name:
                return net

    def port_by_name(self, name):
        for port in self.ports:
            if port.name == name:
                return port

    def assign(self, terminal, to):
        assign = CircuitAssign(terminal, to)
        # Preserve unelaborated assigns (debug info)
        assign_copy = CircuitAssign(terminal, to)
        self.assigns.append(assign_copy)

        if isinstance(assign.terminal, InstTerminal):
            assign.terminal.inst.assigns.append(assign)
            self.assigns_elab.append(assign)
        elif isinstance(assign.terminal, SubInstTerminal):
            assign.terminal.subinst.assigns.append(assign)

            assigns_elab = []
            for assign2 in self.assigns_elab:
                if assign2.to.uuid == assign.terminal.port.uuid:
                    assign2.to = assign.to
                assigns_elab.append(assign2)
            self.assigns_elab = assigns_elab
        else:
            raise AssertionError('Invalid terminal')

    def to_netlist(self):
        # Check that it is a top level circuit (no ports)
        assert len(self.ports) == 0
        return Netlist(self.insts_elab, self.assigns_elab, self.nets_elab)

    def __str__(self):
        return self.name

    def __repr__(self):
        subdesign = 'subdesign {\n'
        for port in self.ports:
            subdesign += '  ' + repr(port) + '\n'
        for net in self.nets:
            subdesign += '  ' + repr(net) + '\n'
        for inst in self.insts:
            for line in repr(inst).split('\n'):
                subdesign += '\n  ' + line
        subdesign += '\n}\n'
        return subdesign


class Netlist(object):
    def __init__(self, insts, assigns, nets):
        self.insts = insts
        self.assigns = assigns
        self.nets = nets

    def __repr__(self):
        return '\n'.join([repr(assign) for assign in self.assigns])
