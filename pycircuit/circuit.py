from collections import defaultdict
from pycircuit.device import *


class Vec(list):
    '''Vec class extends a list allows addition of vecs of equal length.'''

    def __add__(self, other):
        assert len(self) == len(other)
        return Vec([x + y for x, y in zip(self, other)])

    def __getitem__(self, funcs):
        def find_port(func):
            for port in self:
                if port.func.bus_func == func or port.pin.name == func:
                    return port

        if isinstance(funcs, tuple):
            ports = Vec()
            for fun in funcs:
                ports.append(find_port(fun))
            return ports

        return find_port(funcs)


class Net(object):

    counter = 1

    def __new__(cls, name=''):
        # Return existing net
        if not name == '':
            for net in Circuit.active_circuit.nets:
                if net.name == name:
                    return net
        # Create new net
        net = super().__new__(cls)
        net.id = Net.counter
        Net.counter += 1
        Circuit.active_circuit.add_net(net)

        # Initialize new net
        net.name = name
        net.ports = []
        net.nets = []
        net.parent_net = None

        return net

    def set_id(self, id):
        self.id = id
        for net in self.nets:
            net.set_id(id)

    def root_net(self):
        if self.parent_net is None:
            return self
        return self.parent_net.root_net()

    def add_port(self, port):
        assert port.net is None
        if not port in self.ports:
            port.net = self
            self.ports.append(port)

    def add_net(self, net):
        if not net in self.nets:
            net.set_id(self.id)
            net.parent_net = self
            self.nets.append(net)

    def iter_ports(self):
        ports = set()
        for port in self.ports:
            if not port in ports:
                ports.add(port)
                yield port
        for net in self.iter_nets():
            for port in net.iter_ports():
                if not port in ports:
                    ports.add(port)
                    yield port

    def iter_nets(self):
        for net in self.nets:
            yield net
            for net in net.iter_nets():
                yield net

    def __len__(self):
        return len(list(self.iter_ports()))

    def connect(self, other):
        if isinstance(other, Vec):
            for elem in other:
                self.connect(elem)
        elif isinstance(other, Net):
            self.add_net(other)
        else:
            self.add_port(other)
        return self

    __add__ = connect

    def iter_all_subs(self):
        subs = set()
        subs.add(self.parent.parent)
        for port in self.iter_ports():
            sub = port.node
            while True:
                sub = sub.parent.parent
                if sub in subs:
                    break
                subs.add(sub)
                yield sub

    def iter_subs(self):
        for sub in self.parent.subs:
            yield sub

    def __str__(self):
        if self.name == '':
            return str(self.id)
        return self.name

    def __repr__(self):
        ports = ' '.join(['(%s)' % repr(port) for port in self.ports])
        subnets = []
        for net in self.nets:
            subnets += repr(net).split('\n')
        subnets = '\n    '.join(subnets)
        string = '%s %s' % (str(self), ports)
        if not subnets == '':
            string += '\n    ' + subnets
        return string

    def __getattr__(self, attr):
        """Net is expected to be extended with
        self.attrs = NetAttributes(self). Is done
        when Pcb(circuit) is called."""

        return getattr(self.attrs, attr)

class Port(object):

    def __init__(self, node, id, func, pin):
        self.node = node
        self.id = id
        self.func = func
        self.pin = pin
        self.net = None

    def connect(self, other):
        if isinstance(other, Vec):
            return other.append(self)
        if isinstance(other, Net):
            return other.connect(self)
        if not self.net is None:
            return self.net.connect(other)
        if not other.net is None:
            return other.net.connect(self)
        return Vec([self, other])

    __add__ = connect

    def to_vec(self, width):
        iter = self.node.ports_by_func(self.func.name)
        return Vec([next(iter) for i in range(width)])

    def __repr__(self):
        return '%s %s %s' % (self.node.name, self.func, self.pin.name)

    def __getattr__(self, attr):
        """Port is expected to be extended with
        self.attrs = PortAttributes(self). Is done
        when node.set_footprint() is called."""

        return getattr(self.attrs, attr)


class Node(object):

    counter = 1

    def __init__(self, name, device, value=None):
        self.id = Node.counter
        Node.counter += 1

        self.name = name
        self.device = Device.device_by_name(device)
        self.value = value

        self.ports = []
        Circuit.active_circuit.add_node(self)

    def add_port(self, func, pin):
        func = pin.function_by_name(func)
        port = Port(self, len(self.ports), func, pin)
        self.ports.append(port)
        return port

    def port_by_pin(self, pin):
        for port in self.ports:
            if port.pin == pin:
                return port

    def port_by_name(self, name):
        for port in self.ports:
            if port.pin.name == name:
                return port
        pin = self.device.pin_by_name(name)
        if not pin is None and len(pin.functions) == 1:
            return self.add_port(pin.functions[0].name, pin)

    def ports_by_func(self, func):
        for pin in self.device.pins_by_function(func):
            port = self.port_by_pin(pin)
            if port is None:
                yield self.add_port(func, pin)
            else:
                if port.net is None:
                    yield port
        raise Exception('No unconnected pin with function %s available' % func)

    def ports_by_bus(self, bus):
        vec = Vec()
        for func in self.device.bus_by_name(bus):
            port = self.port_by_name(func.pin.name)
            if not port is None:
                vec.append(port)
        return vec

    def __str__(self):
        return '%s : %s' % (self.name, self.device.name)

    def __getattr__(self, attr):
        """Node is expected to be extended with
        self.attrs = NodeAttributes(self)."""

        return getattr(self.attrs, attr)


class Sub(object):

    counter = 1

    def __init__(self, name, circuit):
        self.id = Sub.counter
        Sub.counter += 1

        # Allows referencing nodes as Ref('circuit_name.node_name')
        for node in circuit.nodes:
            node.name = name + '.' + node.name

        self.name = name
        self.circuit = circuit
        circuit.parent = self
        Circuit.active_circuit.add_sub(self)

    def net_by_name(self, name):
        return self.circuit.net_by_name(name)

    def __str__(self):
        return self.name


class Ref(object):

    def __init__(self, name):
        circuit = Circuit.active_circuit

        self.node = circuit.node_by_name(name)
        self.getitem = self.getitem_node

        if isinstance(self.node, Sub):
            self.getitem = self.getitem_sub

        self.iterator = {}

    def getitem_node(self, func):
        if func in self.node.device.bus_types():
            return self.node.ports_by_bus(func)

        port = self.node.port_by_name(func)
        if not port is None:
            return port
        iter = self.iterator.get(func, self.node.ports_by_func(func))
        self.iterator[func] = iter
        return next(iter)

    def getitem_sub(self, net):
        return self.node.net_by_name(net)

    def __getitem__(self, index):
        if isinstance(index, tuple):
            return Vec(list(map(self.getitem, index)))
        return self.getitem(index)

    def __str__(self):
        return '*' + str(self.node)


class Refs(object):

    def __init__(self, *nodes):
        self.refs = []
        for node in nodes:
            self.refs.append(Ref(node))

    def __getitem__(self, func):
        return Vec([ref[func] for ref in self.refs])


def Nets(*nets):
    vec = Vec()
    for net in nets:
        vec.append(Net(net))
    return vec


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


class Circuit(object):

    active_circuit = None

    def __init__(self, name):
        self.parent = None
        self.name = name
        self.nodes = []
        self.subs = []
        self.nets = []

    def add_node(self, node):
        node.parent = self
        self.nodes.append(node)

    def add_sub(self, sub):
        sub.parent = self
        self.subs.append(sub)

    def add_net(self, net):
        net.parent = self
        self.nets.append(net)

    def iter_nodes(self):
        for node in self.nodes:
            yield node
        for sub in self.subs:
            for node in sub.circuit.iter_nodes():
                yield node

    def iter_nets(self):
        visited = set()
        for node in self.iter_nodes():
            for port in node.ports:
                if not port.net is None and not port.net.id in visited:
                    visited.add(port.net.id)
                    yield port.net.root_net()

    def iter_subnets(self):
        for net in self.nets:
            yield net
            for net in net.iter_nets():
                yield net

    def node_by_id(self, id):
        for node in self.iter_nodes():
            if node.id == id:
                return node

    def node_by_name(self, name):
        for node in self.nodes:
            if node.name == name:
                return node
        for sub in self.subs:
            if sub.name == name:
                return sub
            if name.startswith(sub.name + '.'):
                return sub.circuit.node_by_name(name)

    def nodes_by_device(self, device):
        for node in self.iter_nodes():
            if node.device.name == device:
                yield node

    def net_by_name(self, name):
        assert not name == ''
        for net in self.nets:
            if net.name == name:
                return net

    def __str__(self):
        return self.name

    def __repr__(self):
        return '%s\n%s' % (str(self), '\n'.join([repr(net) for net in self.iter_nets()]))
