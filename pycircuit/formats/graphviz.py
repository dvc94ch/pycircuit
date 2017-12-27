from graphviz import Graph
from pycircuit.circuit import Netlist, Inst
from pycircuit.formats import extends


@extends(Inst)
def to_graphviz(self):
    graph = Graph()
    assigns = ['<%s> %s' % (str(assign.uid), str(assign)) for assign in self.assigns]
    graph.node(str(self.uid), '{%s | %s}' % (self.name, '|'.join(assigns)), shape='record')
    return graph


@extends(Netlist)
def to_graphviz(self, filename):
    graph = Graph()
    graph.format = 'svg'
    for inst in self.insts:
        graph.subgraph(inst.to_graphviz())
    for net in self.nets:
        graph.node(str(net.uid), str(net))
    for assign in self.assigns:
        _from = '%s:%s' % (str(assign.inst.uid), str(assign.uid))
        graph.edge(_from, str(assign.to.uid))
    graph.render(filename)
