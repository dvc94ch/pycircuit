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
            print('Warn: Randomly assigning device %s to %s'
                  % (inst.name, inst.device.name))
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
    def find_paths(start):
        '''Returns an iterator of Path's from start.
        path    := (port_ext | pin) - subpath
        subpath := net
                 | net2 - (port_ext | pin)
                 | net2 - inst2 - subpath
                 | net2 - port_int - subpath
        '''

        def inst2(inst, assign):
            if inst.assigns[0] == assign:
                return inst.assigns[1]
            return inst.assigns[0]

        def net2(net, assign):
            if net.assigns[0] == assign:
                return net.assigns[1]
            return net.assigns[0]

        def port_int(port, assign):
            if port.external == assign:
                return port.internal
            return port.external

        def net(net, assign):
            for nassign in net.assigns:
                if not nassign == assign:
                    yield nassign

        def subpath(path, split_net=False):
            assign = path[-1]
            while True:
                if not split_net:
                    if not len(assign.net.assigns) == 2:
                        # subpath = net
                        return path

                    # subpath = net2
                    assign = net2(assign.net, assign)
                    path.next(assign)

                if isinstance(assign, PortAssign):
                    if assign.port.is_external():
                        # subpath = net2 - port_ext
                        return path
                    else:
                        # subpath = net2 - port_int
                        assign = port_int(assign.port, assign)
                        if path.next(assign) is None:
                            return path
                        else:
                            split_net = False
                            continue

                if not len(assign.inst.assigns) == 2:
                    # subpath = net2 - pin
                    return path

                # subpath = net2 - inst2
                assign = inst2(assign.inst, assign)
                path.next(assign)

                split_net = False
                continue


        split_net = False
        path = Path()

        if path.next(start) is None:
            return iter([])

        if isinstance(start, PortAssign):
            for assign in start.net.assigns:
                if not start == assign:
                    path = Path().next(start).next(assign)
                    if path is not None:
                        yield subpath(path, split_net=True)
        else:
            yield subpath(path)


    @staticmethod
    def circuit_paths(circuit):
        for port in circuit.external_ports():
            for path in Compiler.find_paths(port.internal):
                yield path

        skipped_insts = []
        for inst in circuit.insts:
            if len(inst.assigns) == 2:
                skipped_insts.append(inst)
                continue
            for assign in inst.assigns:
                for path in Compiler.find_paths(assign):
                    yield path
        for inst in skipped_insts:
            for assign in inst.assigns:
                for path in Compiler.find_paths(assign):
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
                assign1.erc_type, assign2.erc_type = ERCType.diff(assign1.erc_type, assign2.erc_type)
            except AssertionError:
                print('ERC Error:',
                      assign_to_string(assign1),
                      '<>',
                      assign_to_string(assign2))

        for i, assign in enumerate(path.assigns[1:]):
            check_assign(assign, path.assigns[i])
        for i, assign in enumerate(path.assigns[0:-1]):
            check_assign(assign, path.assigns[i + 1])

    @staticmethod
    def port_swap(direction, assign1, assign2):
        def swap(assign1, assign2):
            if assign1.pin.id > assign2.pin.id:
                pin1 = assign2.pin
                assign2.pin = assign1.pin
                assign1.pin = pin1

        if assign1.inst == assign2.inst and \
           assign1.function == assign2.function:
            if direction > 0:
                assign = assign1
                assign1 = assign2
                assign2 = assign
            swap(assign1, assign2)

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

        # Detect POWER and GND Net's
        for net in circuit.iter_nets():
            net.set_net_type()

        # Find paths
        paths = []
        for path in Compiler.circuit_paths(circuit):
            Compiler.analyze_path(path)

            direction, horizontal = path.flow()
            # Set orientation
            for assign in path:
                if isinstance(assign, InstAssign):
                    assign.inst.horizontal = horizontal

            # Swap ports
            for i, assign in enumerate(path[1:]):
                if isinstance(assign, InstAssign) and \
                   isinstance(path[i], InstAssign):
                    Compiler.port_swap(direction, assign, path[i])

            paths.append(path)

        # Remove unneeded ports and nets
        ports = []
        for port in circuit.iter_ports():
            if port.is_external():
                ports.append(port)
            else:
                assigns = []
                for assign in port.internal.net.assigns:
                    if isinstance(assign, PortAssign) and assign.port == port:
                        continue
                    assigns.append(assign)
                for assign in port.external.net.assigns:
                    if isinstance(assign, PortAssign) and assign.port == port:
                        continue
                    assigns.append(assign)
                for assign in assigns:
                    assign.net = port.external.net
                port.external.net.assigns = assigns
                port.internal.net.assigns = []
        circuit.ports = ports
        circuit.nets = list(circuit.assigned_nets())

        circuit.to_file(net_out)
        return circuit


class Path(object):
    assigns = set()

    def __init__(self):
        self.assigns = []

    def next(self, assign):
        assert isinstance(assign, Assign)
        if not assign in Path.assigns:
            if isinstance(assign, InstAssign) or \
               not assign.port.is_external():
                Path.assigns.add(assign)

            self.assigns.append(assign)
            return self

    def flow(self):
        '''Returns the flow direction of the path, and if it's
        a SIGNAL to SIGNAL path.'''
        start = self.assigns[0]
        end = self.assigns[-1]
        snet_type = start.net.type
        enet_type = end.net.type

        if snet_type == NetType.VCC or enet_type == NetType.VEE:
            return 1, False
        if enet_type == NetType.VCC or snet_type == NetType.VEE:
            return -1, False
        # Neither snet_type nor enet_type are VCC or VEE
        if snet_type == NetType.GND:
            return -1, False
        if enet_type == NetType.GND:
            return 1, False

        # Both net_types are SIGNAL
        erc_type = start.erc_type
        # If is a PortAssign, invert to determine flow
        if isinstance(start, PortAssign):
            erc_type = erc_type.invert()

        if erc_type == ERCType.INPUT:
            return 1, True
        if erc_type == ERCType.OUTPUT:
            return -1, True

        print('Warn: Guessing flow direction. start: %s, end: %s'
              % (repr(start), repr(end)))
        return 1, True

    def __getitem__(self, index):
        return self.assigns[index]

    def __len__(self):
        return len(self.assigns)

    def __iter__(self):
        return iter(self.assigns)

    def __repr__(self):
        def assign_to_string(assign):
            return '%s %s %s' % (str(assign), str(assign.type), str(assign.erc_type))
        return ' - '.join([assign_to_string(assign) for assign in self.assigns])
