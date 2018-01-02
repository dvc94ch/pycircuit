import electro_grammar as eg
from pycircuit.circuit import Inst, Netlist
from pycircuit.formats import extends


class SpiceModel(object):
    def __init__(self, model, ref, nodes, value=None):
        self.ref = ref
        self.nodes = nodes
        self.value = value if not value is None else ''

        if not ref.startswith(model):
            self.ref = model + self.ref

    def __str__(self):
        return '%s %s %s' % (self.ref, ' '.join([str(n) for n in self.nodes]), self.value)


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
        models.append(SpiceModel('R', self.name, nodes, self.value))
    elif self.component.name == 'C':
        nodes = nodes_from_assigns('1', '2')
        models.append(SpiceModel('C', self.name, nodes, self.value))
    elif self.component.name == 'L':
        nodes = [assign.to.name for assign in self.assigns]
        models.append(SpiceModel('C', self.name, nodes, self.value))
    elif self.component.name == 'V':
        nodes = nodes_from_assigns('+', '-')
        models.append(SpiceModel('V', self.name, nodes, self.value))
    elif self.component.name == 'OP':
        nodes = nodes_from_assigns('OUT', '0', '+', '-')
        models.append(SpiceModel('E', self.name, nodes, 100000))
    elif self.component.name == 'D':
        nodes = nodes_from_assigns('A', 'C')
        models.append(SpiceModel('D', self.name, nodes))
    elif self.component.name == 'Q':
        nodes = nodes_from_assigns('C', 'B', 'E', 'SUBSTRATE')
        models.append(SpiceModel('Q', self.name, nodes))
    elif self.component.name == 'M':
        nodes = nodes_from_assigns('D', 'G', 'S', 'SUBSTRATE')
        models.append(SpiceModel('M', self.name, nodes))
    elif self.component.name == 'Transformer_1P_1S':
        inductors = 'L1' + self.name, 'L2' + self.name
        nodes = nodes_from_assigns('L1.1', 'L1.2')
        models.append(SpiceModel(inductors[0], nodes, self.value))
        nodes = nodes_from_assigns('L2.1', 'L2.2')
        models.append(SpiceModel(inductors[1], nodes, self.value))
        models.append(SpiceModel('K', self.name, inductors))
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
