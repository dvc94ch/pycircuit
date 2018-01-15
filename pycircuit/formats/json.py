from pycircuit.circuit import Circuit, Netlist
from pycircuit.pcb import Pcb
from pycircuit.formats import extends, _to_file, _to_json, _from_file


@extends(Circuit)
def to_file(self, path):
    _to_file(path, _to_json(self.to_object()))

@staticmethod
@extends(Circuit)
def from_file(path):
    return Circuit.from_object(_from_file(path))


@extends(Netlist)
def to_file(self, path):
    _to_file(path, _to_json(self.to_object()))

@staticmethod
@extends(Netlist)
def from_file(path):
    return Netlist.from_object(_from_file(path))


@extends(Pcb)
def to_file(self, path):
    _to_file(path, _to_json(self.to_object()))
