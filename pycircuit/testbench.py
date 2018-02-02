from pycircuit.circuit import *


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
