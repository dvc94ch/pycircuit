from collections import defaultdict
from enum import Enum
from pycircuit.circuit import *
from pycircuit.device import Device
from pycircuit.formats import *
from pycircuit.pinassign import *


class Compiler(object):

    @staticmethod
    def assign_pins(inst):
        '''Find a valid Pin assignment for an Inst.

        Converts all Assign's in Inst to Z3Assign's and Z3BusAssign's and uses
        Z3 to find a valid Pin assignment.
        '''
        assigns = {}
        for assign in inst.assigns:
            if not assign.guid in assigns:
                assigns[assign.guid] = Z3BusAssign()
            assigns[assign.guid].add_assign(Z3Assign(assign.function, assign))
            problem = AssignmentProblem(inst.component, assigns.values())
            try:
                problem.solve()
                assert problem.check_solution() is None
            except:
                print('Failed to assign pins', str(inst))
                raise

            for bus_assign in assigns.values():
                for assign in bus_assign:
                    assign.meta.pin = assign.pin
                    assign.meta.type = assign.pin.type

    @staticmethod
    def check_required_pins(inst):
        '''Checks that all Pin's in inst that are not optional
        are assigned.
        '''
        for pin in inst.component.pins:
            if not pin.optional:
                for assign in inst.assigns:
                    if assign.pin == pin:
                        break
                else:
                    print('Error: Unconnected non-optional pin: %s %s %s'
                          % (inst.name, inst.component.name, pin.name))

    @staticmethod
    def match_device(inst):
        '''Finds a Device for an Inst.'''
        devices = list(Device.devices_by_component(inst.component))
        if len(devices) < 1:
            print('Error: No devices for component %s in scope.'
                  % (inst.component.name))
            return

        if inst.value is None:
            inst.device = devices[0]
            #print('Warn: Randomly assigning device %s to %s'
            #      % (inst.name, inst.device.name))
            return

        value_parts = inst.value.lower().split(' ')
        for device in devices:
            inst.device = device
            for part in value_parts:
                if device.name.lower() == part:
                    return
                if device.package.name.lower() == part:
                    return
        print('Error: No device matched for value %s, randomly assigning %s'
              % (inst.value, inst.device.name))

    @staticmethod
    def rename(iterator):
        '''Takes an iterator of strings and returns an
        iterator of unique strings, by postfixing numbers.'''
        names = {}
        for item in iterator:
            if not item.name in names:
                names[item.name] = []
            names[item.name].append(item)
        for name, items in names.items():
            if len(items) == 1:
                yield items[0]
            else:
                for i, item in enumerate(items):
                    item.name += str(i + 1)
                    yield item

    @staticmethod
    def find_path(circuit, start):
        '''Returns a Path from start in an elaborated Circuit.
        path    := (port_ext | pin) - subpath
        subpath := net
                 | net2 - (port_ext | pin)
                 | net2 - inst2 - subpath
                 | net2 - port_int - subpath
        '''

        def next_assign(assigns, assign):
            if len(assigns) == 2:
                if assigns[0] == assign:
                    return assigns[1]
                return assigns[0]

        path = Path(start)
        assign = start

        while True:
            assign = next_assign(assign.net.assigns, assign)

            if assign is None:
                # subpath = net
                return path

            # subpath = net2
            if not path.next(assign):
                return path

            if isinstance(assign, PortAssign):
                assign = next_assign(assign.port.assigns, assign)
                if assign is None:
                    # subpath = net2 - port_ext
                    return path

                # subpath = net2 - port_int
                if not path.next(assign.port.internal):
                    return path

                continue

            assign = next_assign(assign.inst.assigns, assign)
            if assign is None:
                # subpath = net2 - pin
                return path

            # subpath = net2 - inst2
            if not path.next(assign):
                return path

            continue

    @staticmethod
    def find_paths(circuit):
        for port in circuit.ports:
            if len(port.assigns) == 1:
                path = Compiler.find_path(circuit, port.internal)
                if not path.is_empty():
                    yield path

        for inst in circuit.insts:
            for assign in inst.assigns:
                path = Compiler.find_path(circuit, assign)
                if not path.is_empty():
                    yield path

    @staticmethod
    def analyze_path(path):
        def assign_to_string(assign):
            if isinstance(assign, InstAssign):
                return "%s.%s :%s" % \
                    (assign.inst.name, assign.pin.name,
                     str(assign.type))
            if isinstance(assign, PortAssign):
                return "%s :%s" % \
                    (assign.port.name, str(assign.type))

        def check_assign(assign1, assign2):
            try:
                if isinstance(assign1, InstAssign) and \
                   isinstance(assign2, InstAssign):
                    # When both assigns are InstAssign's
                    # one has to be an input and the other
                    # an output
                    assign1.erc_type, assign2.erc_type = ERCType.diff(assign1.erc_type, assign2.erc_type)
                else:
                    assign1.erc_type, assign2.erc_type = ERCType.same(assign1.erc_type, assign2.erc_type)
            except AssertionError:
                print('ERC Error:',
                      assign_to_string(assign1),
                      '<>',
                      assign_to_string(assign2))
                raise AssertionError()

        for i, assign in enumerate(path.assigns[1:]):
            check_assign(assign, path.assigns[i])
        for i, assign in enumerate(path.assigns[0:-1]):
            check_assign(assign, path.assigns[i + 1])
        #print(path)

        # Join nets through ports
        for assign in path.assigns:
            if isinstance(assign, PortAssign) and len(assign.port.assigns) == 2:
                assign.port.external.net.assigns += assign.port.internal.net.assigns
                for net_assign in assign.port.external.net.assigns:
                    net_assign.net = assign.port.external.net

    def compile(self, net_in, net_out):
        circuit = Circuit.from_file(net_in)

        # Check insts
        for inst in Compiler.rename(circuit.iter_insts()):
            Compiler.assign_pins(inst)
            Compiler.check_required_pins(inst)
            Compiler.match_device(inst)

        # Set ERC types on all assigns
        for assign in circuit.iter_assigns():
            assign.erc_type = ERCType.from_type(assign.type)
        for port_assign in circuit.iter_port_assigns():
            port_assign.erc_type = ERCType.from_type(port_assign.type)


        # Find paths
        paths = []
        for path in Compiler.find_paths(circuit):
            Compiler.analyze_path(path)
            paths.append(path)


        # Detect POWER and GND Net's
        for net in circuit.iter_nets():
            for assign in net.assigns:
                if assign.type.is_power():
                    net.type = NetType.POWER
                    break
                if assign.type.is_gnd():
                    net.type = NetType.GND
                    break

        # Check path type
        for path in paths:
            print(path.type())


        # Remove unneeded ports
        ports = []
        for port in circuit.ports:
            if len(port.assigns) == 1:
                ports.append(port)
        circuit.ports = ports


        circuit.to_file(net_out)
        return circuit


class Path(object):
    assigns = set()

    def __init__(self, start):
        assert isinstance(start, Assign)
        self.assigns = []
        self.next(start)

    def next(self, assign):
        assert isinstance(assign, Assign)
        if assign in Path.assigns:
            return False
        Path.assigns.add(assign)
        self.assigns.append(assign)
        return True

    def is_empty(self):
        return len(self.assigns) == 0

    def type(self):
        return str(self.assigns[0].net.type) + ' - ' + str(self.assigns[-1].net.type)

    def __repr__(self):
        def assign_to_string(assign):
            return '%s %s %s' % (str(assign), str(assign.type), str(assign.erc_type))
        return ' - '.join([assign_to_string(assign) for assign in self.assigns])
