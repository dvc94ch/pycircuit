from pycircuit.device import *
from pycircuit.pcb import NodeAttributes

class Net(object):

    counter = 1

    def __init__(self, name=''):
        self.id = Net.counter
        Net.counter += 1

        self.name = name
        self.ports = []
        self.attrs = {}

    def add_port(self, port):
        if not port in self.ports:
            port.net = self
            self.ports.append(port)

    def connect(self, other):
        if isinstance(other, Port):
            self.connect(other.net)
        elif isinstance(other, Net):
            if self.name == '':
                self.name = other.name
            for port in other.ports:
                self.add_port(port)

    def __getattr__(self, attr):
        return getattr(self.attrs, attr)

    def __str__(self):
        if self.name == '':
            return '(unnamed)'
        return self.name

    def __repr__(self):
        return '%s %s' % (str(self),
                          ' '.join(['(%s)' % repr(port) for port in self.ports]))

    def __add__(self, other):
        self.connect(other)
        return self


class Vector(object):

    def __init__(self, vector):
        self.vector = vector

    def __getitem__(self, index):
        return self.vector[index]

    def __len__(self):
        return len(self.vector)

    def connect(self, other):
        if not isinstance(other, Vector):
            other = other.to_vector(len(self.vector))
        assert len(self) == len(other)
        for i in range(len(self.vector)):
            self.vector[i].connect(other.vector[i])

    __add__ = connect


class Port(object):

    def __init__(self, node, func, pin):
        self.node = node
        self.func = func
        self.pin = pin
        self.net = Net('')
        self.attrs = {}
        self.net.add_port(self)

    def connect(self, other):
        if isinstance(other, Vector):
            return other.connect(self)
        return self.net.connect(other)

    def to_vector(self, width):
        ports = [self.node.allocate_function(self.func) for i in range(width - 1)]
        ports.append(self)
        return Vector(ports)

    def __getattr__(self, attr):
        return getattr(self.attrs, attr)

    def __repr__(self):
        return '%s %s %s' % (self.node.name, self.func, self.pin.name)

    __add__ = connect


class BusPort(object):

    def __init__(self, node, bus_type, bus):
        self.node = node
        self.bus_type = bus_type
        self.bus = bus
        self.ports = []

        for func in bus.functions:
            self.ports.append(Port(node, func.name, func.pin))

    def port_by_function(self, func):
        for port in self.ports:
            if port.func == func:
                return port

    def connect(self, other):
        assert isinstance(other, BusPort)
        assert self.bus_type == other.bus_type
        for port in self.ports:
            port.connect(other.port_by_function(port.func))

    def __getitem__(self, funcs):
        ports = []
        for func in funcs:
            ports.append(self.port_by_function(self.bus_type + '_' + func))
        return Vector(ports)

    __add__ = connect


class Node(object):

    counter = 1

    def __init__(self, name, device):
        self.id = Node.counter
        Node.counter += 1

        self.name = name
        self.device = Device.device_by_name(device)
        self.ports = []
        self.attrs = NodeAttributes(self)
        Circuit.active_circuit.add_node(self)

    def port_by_pin(self, pin):
        for port in self.ports:
            if port.pin == pin:
                return port

    def unconnected_pin_by_func(self, func):
        for pin in self.device.pins_by_function(func):
            if self.port_by_pin(pin) is None:
                return pin
        raise Exception('No unconnected pin with function %s available' % func)

    def unconnected_bus_by_type(self, bus):
        for bus in self.device.busses_by_type(bus):
            for func in bus.functions:
                if self.port_by_pin(func.pin) is not None:
                    break
            else:
                return bus
        raise Exception('No unconnected bus with type %s available' % bus)

    def allocate_function(self, func):
        port = Port(self, func, self.unconnected_pin_by_func(func))
        self.ports.append(port)
        return port

    def allocate_bus(self, bus):
        bus_port = BusPort(self, bus, self.unconnected_bus_by_type(bus))
        self.ports += bus_port.ports
        return bus_port

    def __getattr__(self, attr):
        return getattr(self.attrs, attr)

    def __str__(self):
        return '%s : %s' % (self.name, self.device.name)


class Sub(object):

    counter = 1

    def __init__(self, name, circuit):
        self.id = Sub.counter
        Sub.counter += 1

        self.name = name
        self.circuit = circuit
        for node in circuit.nodes:
            node.name = name + '.' + node.name
        Circuit.active_circuit.add_node(self)

    def net_by_name(self, name):
        return self.circuit.net_by_name(name)

    def __str__(self):
        return self.name


class Ref(object):

    def __init__(self, node):
        self.node = Circuit.active_circuit.node_by_name(node)

    def getitem_device(self, func):
        if func in self.node.device.bus_types():
            return self.node.allocate_bus(func)
        return self.node.allocate_function(func)

    def getitem_circuit(self, net):
        return self.node.net_by_name(net)

    def __getitem__(self, index):
        if isinstance(self.node, Node):
            getitem = self.getitem_device
        elif isinstance(self.node, Sub):
            getitem = self.getitem_circuit

        if isinstance(index, tuple):
            return Vector(list(map(getitem, index)))
        return getitem(index)

    def __str__(self):
        return '*' + str(self.node)


class Refs(object):

    def __init__(self):
        self.nodes = Circuit.active_circuit.nodes

    def __getitem__(self, func):
        net = Net('')
        for node in self.nodes:
            if isinstance(node, Node):
                try:
                    net.connect(node.allocate_function(func))
                except:
                    pass
            elif isinstance(node, Sub):
                net.connect(node.net_by_name(func))
        return net


def circuit(name):

    def closure(function):

        def wrapper():
            # Save active circuit
            parent = Circuit.active_circuit

            # Create new circuit
            circuit = Circuit(name)

            # Set active circuit
            Circuit.active_circuit = circuit

            function()

            # Reset active circuit
            Circuit.active_circuit = parent

            return circuit

        return wrapper

    return closure


class Circuit(object):

    active_circuit = None

    def __init__(self, name):
        self.name = name
        self.nodes = []

    def add_node(self, node):
        self.nodes.append(node)

    def iter_nodes(self):
        for node in self.nodes:
            if isinstance(node, Node):
                yield node
            elif isinstance(node, Sub):
                for node in node.circuit.iter_nodes():
                    yield node

    def iter_nets(self):
        visited = set()
        for node in self.iter_nodes():
            for port in node.ports:
                if not port.net.id in visited:
                    visited.add(port.net.id)
                    yield port.net

    def node_by_name(self, name):
        for node in self.nodes:
            if node.name == name:
                return node
            if isinstance(node, Sub) and \
               name.startswith(node.name + '.'):
                return node.circuit.node_by_name(name)

    def nodes_by_device(self, device):
        for node in self.iter_nodes():
            if node.device.name == device:
                yield node

    def net_by_name(self, name):
        assert not name == ''
        for net in self.iter_nets():
            if net.name == name:
                return net

    def __str__(self):
        return self.name

    def __repr__(self):
        return '%s\n%s' % (str(self), '\n'.join([repr(net) for net in self.all_nets()]))
