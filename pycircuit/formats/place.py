import json
from pycircuit.pcb import Pcb, InstAttributes
from pycircuit.formats import extends

@extends(InstAttributes)
def to_place(self):
    width, height = self.inst.device.package.size()
    return {
        'uid': self.inst.uid,
        'width': width,
        'height': height,
    }


@extends(Pcb)
def to_place(self, filename):
    insts = []
    for inst in self.netlist.insts:
        insts.append(inst.attributes.to_place())
    with open(filename, 'w') as f:
        f.write(json.dumps(insts, sort_keys=True,
                           indent=2, separators=(',', ': ')))


@extends(Pcb)
def from_place(self, filename):
    with open(filename) as f:
        for inst in json.loads(f.read()):
            self.netlist.inst_by_uid(inst['uid']) \
                        .attributes.place(inst['x'], inst['y'])
