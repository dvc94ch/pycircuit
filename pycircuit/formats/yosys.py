import json
from pycircuit.component import Pin
from pycircuit.circuit import *
from pycircuit.formats import extends


def match_skin(inst):
    cname = inst.component.name
    value = '' if inst.value is None else inst.value
    suffix = '_h' if inst.horizontal else '_v'

    if cname == 'R' or cname == 'C' or cname == 'L':
        return cname.lower() + suffix

    if cname == 'D':
        if 'led' in value:
            return 'd_led' + suffix
        if 'sk' in value:
            return 'd_sk' + suffix
        return 'd' + suffix

    if cname == 'Q':
        if 'pnp' in value:
            return 'q_pnp'
        return 'q_npn'

    mapping = {
        'OP': 'op',
        'XTAL': 'xtal',
        'V': 'v',
        'I': 'i',
        'Transformer_1P_1S': 'transformer_1p_1s'
    }

    if cname in mapping:
        return mapping[cname]

    return cname


def match_port_direction(skin, assign):
    if skin.startswith('r_') or skin.startswith('c_') or skin.startswith('l_'):
        return {'A': 'input', 'B': 'output'}[assign.pin.name]
    if skin.startswith('d_'):
        return {'+': 'input', '-': 'output'}[assign.pin.name]
    if skin.startswith('q_'):
        return {'B': 'input', 'C': 'input', 'E': 'output'}[assign.pin.name]
    if skin == 'v' or skin == 'i':
        return {'+': 'input', '-': 'output'}[assign.pin.name]
    if skin == 'op':
        return {'VCC': 'input', 'VEE': 'output', '+': 'input', '-': 'input', 'OUT': 'output'}[assign.pin.name]
    if skin == 'xtal':
        return {'A': 'input', 'B': 'output'}[assign.pin.name]
    if skin == 'transformer_1p_1s':
        return {'L1.1': 'input', 'L1.2': 'input', 'L2.1': 'output', 'L2.2': 'output'}[assign.pin.name]
    if assign.erc_type == ERCType.INPUT:
        return 'input'
    elif assign.erc_type == ERCType.OUTPUT:
        return 'output'
    else:
        print('Warn: Pin %s has no direction!' % assign.pin.name)


def gnd(conn):
    return {
        'type': 'gnd',
        'port_directions': {
            'A': 'input'
        },
        'connections': {
            'A': [conn]
        }
    }


def vcc(conn):
    return {
        'type': 'vcc',
        'port_directions': {
            'A': 'output'
        },
        'connections': {
            'A': [conn]
        }
    }


def vee(conn):
    return {
        'type': 'vee',
        'port_directions': {
            'A': 'input'
        },
        'connections': {
            'A': [conn]
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
            net_type = assign.net.type
            if net_type == NetType.GND:
                cells['gnd' + str(uid)] = gnd(uid)
                connections[assign.pin.name] = [uid]
            elif net_type == NetType.VCC:
                cells['vcc' + str(uid)] = vcc(uid)
                connections[assign.pin.name] = [uid]
            elif net_type == NetType.VEE:
                cells['vee' + str(uid)] = vee(uid)
                connections[assign.pin.name] = [uid]
            else:
                connections[assign.pin.name] = [assign.net.uid]

            skin = match_skin(inst)
            port_directions[assign.pin.name] = match_port_direction(skin, assign)

            cells[inst.name] = {
                'type': match_skin(inst),
                'port_directions': port_directions,
                'connections': connections
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
