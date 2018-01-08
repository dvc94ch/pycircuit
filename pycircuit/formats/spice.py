from pycircuit.circuit import Inst, Netlist, UID
from pycircuit.formats import extends


class SpiceInst(object):
    def __init__(self, ty, ref, nodes, value=None, model=None):
        self.ty = ty
        self.ref = ref
        self.nodes = nodes
        self.value = value
        self.model = model

        if not ref.startswith(self.ty):
            self.ref = self.ty + self.ref

    def __str__(self):
        nodes = ' '.join([str(n) for n in self.nodes])
        value = '' if self.value is None else str(self.value)
        model = '' if self.model is None else self.model.mname
        return '%s %s %s %s' % (self.ref, nodes, value, model)


class SpiceModel(object):
    def __init__(self, ty, params):
        self.mname = 'mod' + str(UID.uid())
        self.ty = ty
        self.params = params

    def __str__(self):
        params = ' '.join(['%s=%s' % (k, str(v)) for k, v in self.params.items()])
        return '.model %s %s (%s)' % (self.mname, self.ty, params)


class SpiceProbe(object):
    def __init__(self, ty, ref, node):
        self.ty = ty
        self.ref = ref
        self.node = node

    def __str__(self):
        return '.probe %s(%s) %s' % (self.ty, self.ref, str(self.node))


@extends(Inst)
def to_spice(self):
    def nodes_from_assigns(*pin_names):
        nodes = []
        for name in pin_names:
            if name == '0':
                nodes.append('0')
            else:
                assign = self.assign_by_pin_name(name)
                if assign is None:
                    continue
                if assign.to.name.lower() == 'gnd':
                    nodes.append('0')
                else:
                    nodes.append(assign.to.name)
        return nodes

    models = []

    if self.component.name == 'R':
        nodes = nodes_from_assigns('1', '2')
        models.append(SpiceInst('R', self.name, nodes, self.value))
    elif self.component.name == 'C':
        nodes = nodes_from_assigns('1', '2')
        models.append(SpiceInst('C', self.name, nodes, self.value))
    elif self.component.name == 'L':
        nodes = [assign.to.name for assign in self.assigns]
        models.append(SpiceInst('C', self.name, nodes, self.value))
    elif self.component.name == 'V':
        nodes = nodes_from_assigns('+', '-')
        net = 'n' + str(UID.uid())
        models.append(SpiceInst('V', self.name, (net, nodes[1]), self.value))
        models.append(SpiceInst('R', self.name, (net, nodes[0]), 30))
    elif self.component.name == 'OP':
        nodes = nodes_from_assigns('OUT', '0', '+', '-')
        models.append(SpiceInst('E', self.name, nodes, 100000))
    elif self.component.name == 'D':
        nodes = nodes_from_assigns('A', 'C')
        if 'led' in self.value.split(' '):
            model = SpiceModel('D', {'is': '1a', 'rs': 3.3, 'n': 1.8})
        else:
            raise Exception('D value needs to contain led')
        models.append(model)
        models.append(SpiceInst('D', self.name, nodes, model=model))
    elif self.component.name == 'Q':
        nodes = nodes_from_assigns('C', 'B', 'E', 'SUBSTRATE')
        if 'npn' in self.value.split(' '):
            model = SpiceModel('npn', {'is': 1e-15})
        elif 'pnp' in self.value.split(' '):
            model = SpiceModel('pnp', {'is': 1e-15})
        else:
            raise Exception('Q value needs to contain npn or pnp')
        models.append(model)
        models.append(SpiceInst('Q', self.name, nodes, model=model))
    elif self.component.name == 'M':
        nodes = nodes_from_assigns('D', 'G', 'S', 'SUBSTRATE')
        if 'nmos' in self.value.split(' '):
            model = SpiceModel('nmos')
        elif 'pmos' in self.value.split(' '):
            model = SpiceModel('pmos')
        else:
            raise Exception('M value needs to contain nmos or pmos')
        models.append(model)
        models.append(SpiceModel('M', self.name, nodes, model=model))
    elif self.component.name == 'Transformer_1P_1S':
        inductors = 'L1' + self.name, 'L2' + self.name
        nodes = nodes_from_assigns('L1.1', 'L1.2')
        models.append(SpiceInst('L', inductors[0], nodes, self.value))
        nodes = nodes_from_assigns('L2.1', 'L2.2')
        models.append(SpiceInst('L', inductors[1], nodes, self.value))
        models.append(SpiceInst('K', self.name, inductors, 1))
    elif self.component.name == 'TP':
        node = nodes_from_assigns('TP')
        models.append(SpiceProbe('v', self.name, *node))
    else:
        raise Exception("Component %s doesn't have a spice model"
                        % self.component.name)

    return models


@extends(Netlist)
def to_spice(self, filename):
    with open(filename, 'w+') as f:
        # Emit title
        print('.title', filename, file=f)

        for inst in self.insts:
            for model in inst.to_spice():
                print(str(model), file=f)

        # Emit end
        print('.end', file=f)
