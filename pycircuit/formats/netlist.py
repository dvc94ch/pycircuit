import json
from pycircuit.circuit import Circuit, Netlist
from pycircuit.formats import extends


@extends(Circuit)
def to_file(self, path):
    with open(path, 'w+') as f:
        f.write(json.dumps(self.to_object(), sort_keys=True,
                           indent=2, separators=(',', ': ')))

@staticmethod
@extends(Circuit)
def from_file(path):
    with open(path) as f:
        return Circuit.from_object(json.loads(f.read()), parent=None)


@extends(Netlist)
def to_file(self, path):
    with open(path, 'w+') as f:
        f.write(json.dumps(self.to_object(), sort_keys=True,
                           indent=2, separators=(',', ': ')))

@staticmethod
@extends(Netlist)
def from_file(path):
    with open(path) as f:
        return Netlist.from_object(json.loads(f.read()))
