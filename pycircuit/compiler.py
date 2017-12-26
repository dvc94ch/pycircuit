from pycircuit.circuit import Circuit, Netlist, SubInstTerminal
from pycircuit.device import Device
from pycircuit.formats import *
from pycircuit.pinassign import *


class Compiler(object):
    def check_circuit(self, circuit):
        for net in circuit.iter_nets():
            # At least two assignments to a net
            assert len(net.assigns) > 1
        for port in circuit.iter_ports():
            # At least one internal connection from a port
            assert len(port.assigns) > 0

    def rename(self, iterator):
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

    def elaborate_circuit(self, circuit):
        assert len(circuit.ports) == 0

        insts = list(self.rename(circuit.iter_insts()))
        nets = list(self.rename(circuit.iter_nets()))

        assigns = []
        for assign in circuit.iter_assigns():
            if isinstance(assign.terminal, SubInstTerminal):
                continue
            while not assign.is_final():
                for other_assign in circuit.iter_assigns():
                    if assign.is_next(other_assign):
                        assign.next(other_assign)
                        break
            assigns.append(assign)

        return Netlist(circuit.name, insts=insts, nets=nets, assigns=assigns)

    def assign_pins(self, inst):
        # Convert CircuitAssign to Assign
        assigns = {}
        for assign in inst.assigns:
            if not assign.terminal.group in assigns:
                assigns[assign.terminal.group] = BusAssign()
            assigns[assign.terminal.group].add_assign(Assign(assign.terminal.function, assign))
            problem = AssignmentProblem(inst.component, assigns.values())
            try:
                problem.solve()
                assert problem.check_solution() is None
            except:
                print('Failed to assign pins', str(inst))
                raise

            for bus_assign in assigns.values():
                for assign in bus_assign:
                    assign.meta.terminal.pin = assign.pin

    def match_device(self, inst):
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

    def check_required_pins(self, inst):
        for pin in inst.component.pins:
            if not pin.optional:
                for assign in inst.assigns:
                    if assign.terminal.pin == pin:
                        break
                else:
                    print('Error: Unconnected non-optional pin: %s %s %s'
                          % (inst.name, inst.component.name, pin.name))

    def compile(self, net_in, net_out):
        circuit = Circuit.from_file(net_in)

        self.check_circuit(circuit)
        netlist = self.elaborate_circuit(circuit)

        for inst in netlist.insts:
            self.assign_pins(inst)
            self.check_required_pins(inst)
            self.match_device(inst)

        netlist.to_file(net_out)
