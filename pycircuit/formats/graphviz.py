from graphviz import Digraph
from pycircuit.device import Fun
from pycircuit.circuit import Circuit, Node, Sub, Net, Port
from pycircuit.formats import extends, export


@extends(Port)
def to_graphviz(self):
    return 'node%d:port%d' % (self.node.id, self.id)


@extends(Net)
def to_graphviz(self):
    def get_dir(port):
        try:
            return port.func.dir
        except:
            return Fun.BIDIR

    def to_graphviz(port):
        # If port is a graph node return
        if isinstance(port, str):
            return port
        return port.to_graphviz()

    def edge(graph, port1, port2):
        port1_dir, port2_dir = get_dir(port1), get_dir(port2)
        port1_gv, port2_gv = to_graphviz(port1), to_graphviz(port2)

        if port1_dir == Fun.OUTPUT or port2_dir == Fun.INPUT:
            graph.edge(port1_gv, port2_gv)
        elif port1_dir == Fun.INPUT or port2_dir == Fun.OUTPUT:
            graph.edge(port2_gv, port1_gv)
        else:
            graph.edge(port1_gv, port2_gv, dir='none')

    def get_sub_id(self):
        # if circuit is not a sub return 0
        try:
            # self.circuit.sub.id
            return self.parent.parent.id
        except:
            return 0

    def get_node_id(sub_id, net_id):
        return 'sub%snet%s' % (str(sub_id), str(net_id))

    graph = Digraph()

    if self.parent_net is None and len(self.nets) == 0 and len(self.ports) == 2:
        edge(graph, *self.ports)
    else:
        # create graphnode for net in sub
        node_id = get_node_id(get_sub_id(self), self.id)
        graph.node(node_id, self.name)

        # internal connections
        for port in self.ports:
            edge(graph, port, node_id)

        # connect to subcircuits
        for sub in self.iter_subs():
            for net in sub.circuit.nets:
                if net.id == self.id:
                    edge(graph, node_id, get_node_id(sub.id, net.id))
    return graph


@extends(Node)
def to_graphviz(self):
    graph = Digraph(name='node' + str(self.id))
    graph.attr(label=self.name)

    node_name = self.name.split('.')[-1]
    node_id = 'node' + str(self.id)

    ports = ['<port%d> %s' % (port.id, port.pin.name) for port in self.ports]
    graph.node(node_id, '{%s | %s}' % (node_name, '|'.join(ports)),
               shape='record')

    return graph


@extends(Sub)
def to_graphviz(self):
    graph = Digraph(name='cluster' + str(self.id))
    label = self.name
    graph.attr(label=label)
    graph.subgraph(self.circuit.to_graphviz())
    return graph


@extends(Circuit)
def to_graphviz(self):
    graph = Digraph(name=self.name)
    for node in self.nodes:
        graph.subgraph(node.to_graphviz())
    for sub in self.subs:
        graph.subgraph(sub.to_graphviz())
    for net in self.nets:
        graph.subgraph(net.to_graphviz())

    return graph
