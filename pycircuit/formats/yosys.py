import json
from pycircuit.component import Pin
from pycircuit.circuit import *
from pycircuit.formats import extends


def match_skin(inst):
    lookup = {
        'R': 'resistor',
        'C': 'capacitor',
        'L': 'inductor',
        'XTAL': 'crystal',
    }

    cname = inst.component.name
    value = '' if inst.value is None else inst.value
    suffix = '' if inst.horizontal else '_rot90'

    if cname in lookup:
        return lookup[cname] + suffix

    if cname == 'D':
        if 'led' in value:
            return 'led' + suffix
        if 'sk' in value:
            return 'diode_schottky' + suffix
        return 'diode' + suffix

    if cname == 'Q':
        if 'pnp' in value:
            return 'transistor_pnp'
        return 'BC846'

    return cname


def gnd(name, conn):
    return {
        'type': 'ground',
        'connections': {
            'GND': [conn]
        },
        'attributes': {
            'value': name,
        }
    }


def vcc(name, conn):
    return {
        'type': 'power',
        'connections': {
            'VCC': [conn]
        },
        'attributes': {
            'value': name,
        }
    }


def vee(name, conn):
    return {
        'type': 'power',
        'connections': {
            'VCC': [conn]
        },
        'attributes': {
            'value': name,
        }
    }


@extends(Circuit)
def to_yosys(self):
    cells = {}
    for inst in self.insts:
        connections = {}
        port_directions = {}
        for assign in inst.assigns:
            uid = UID.uid()
            net_name = assign.net.name
            net_type = assign.net.type
            if net_type == NetType.GND:
                cells['gnd' + str(uid)] = gnd(net_name, uid)
                connections[assign.pin.name] = [uid]
            elif net_type == NetType.VCC:
                cells['vcc' + str(uid)] = vcc(net_name, uid)
                connections[assign.pin.name] = [uid]
            elif net_type == NetType.VEE:
                cells['vee' + str(uid)] = vee(net_name, uid)
                connections[assign.pin.name] = [uid]
            else:
                connections[assign.pin.name] = [assign.net.uid]


            if assign.erc_type == ERCType.INPUT:
                port_directions[assign.pin.name] = 'input'
            elif assign.erc_type == ERCType.OUTPUT:
                port_directions[assign.pin.name] = 'output'
            else:
                print('Guessing pin direction')
                port_directions[assign.pin.name] = 'output'


            skin = match_skin(inst)
            value = inst.value or ' '

            cells[inst.name] = {
                'type': match_skin(inst),
                'port_directions': port_directions,
                'connections': connections,
                'attributes': {
                    'value': value,
                }
            }

    ports = {}
    for port in self.external_ports():
        if port.type == PortType.IN:
            direction = 'input'
        elif port.type == PortType.OUT:
            direction = 'output'
        else:
            continue

        ports[port.name] = {
            'direction': direction,
            'bits': [port.internal_net().uid]
        }

    return {
        'modules': {
            self.name: {
                'ports': ports,
                'cells': cells
            }
        }
    }


@extends(Circuit)
def to_yosys_file(self, path):
    with open(path, 'w+') as f:
        f.write(json.dumps(self.to_yosys(), sort_keys=True,
                           indent=2, separators=(',', ': ')))
