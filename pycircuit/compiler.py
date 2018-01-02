from pycircuit.circuit import Circuit, Netlist
from pycircuit.device import Device
from pycircuit.formats import *
from pycircuit.pinassign import *


class Compiler(object):
    def check_circuit(self, circuit):
        for net in circuit.iter_nets():
            if len(net.assigns) < 2:
                print('Warn: Only one assignment to net %s' % net.name)
        for port in circuit.iter_ports():
            if len(port.assigns) < 1:
                print('Warn: Unused port %s' % port.name)

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
            while not assign.is_final():
                for subinst_assign in circuit.iter_subinst_assigns():
                    if assign.to == subinst_assign.port:
                        assign.to = subinst_assign.to
                        break
            assigns.append(assign)

        return Netlist(circuit.name, insts=insts, nets=nets, assigns=assigns)

    def assign_pins(self, inst):
        # Convert CircuitAssign to Assign
        assigns = {}
        for assign in inst.assigns:
            if not assign.guid in assigns:
                assigns[assign.guid] = BusAssign()
            assigns[assign.guid].add_assign(Assign(assign.function, assign))
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
                    if assign.pin == pin:
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
