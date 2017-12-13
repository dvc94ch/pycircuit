import json
from pycircuit.circuit import Node
from pycircuit.pcb import Pcb
from pycircuit.formats import extends

@extends(Node)
def to_pcpl(self):
    assert(self.footprint)
    width, height = self.footprint.package.size()
    return {
        'id': self.id,
        'width': width,
        'height': height,
    }


@extends(Pcb)
def to_pcpl(self, filename):
    nodes = []
    for node in self.circuit.iter_nodes():
        nodes.append(node.to_pcpl())
    with open(filename, 'w') as f:
        print(json.dumps(nodes), file=f)


@extends(Pcb)
def from_pcpl(self, filename):
    with open(filename) as f:
        for node in json.loads(f.read()):
            self.circuit.node_by_id(node['id']).place(node['x'], node['y'])
