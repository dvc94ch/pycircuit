import os
import hashlib
import shutil
from pycircuit.circuit import Netlist, Circuit
from pycircuit.compiler import Compiler
from pycircuit.formats import *
from pycircuit.pcb import Pcb


pycircuitdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def get_node_module(name):
    return os.path.join(pycircuitdir, 'node_modules', name)


def netlistsvg(filein, fileout):
    module = get_node_module('netlistsvg')
    skin = os.path.join(pycircuitdir, 'qeda-default-skin.svg')
    netlistsvg = os.path.join(module, 'bin', 'netlistsvg.js')
    os.system('%s --skin %s %s -o %s' % (netlistsvg, skin, filein, fileout))


def qeda(cmd):
    module = get_node_module('qeda')
    qeda = os.path.join(module, 'bin', 'qeda')
    os.system('%s %s' % (qeda, cmd))


def default_compile(filein, fileout):
    compiler = Compiler()
    return compiler.compile(filein, fileout)


def default_place(filein, fileout):
    Pcb.from_file(filein).to_file(fileout)


def default_route(filein, fileout):
    Pcb.from_file(filein).to_file(fileout)


def default_post_process(pcb, kpcb):
    return kpcb


def string_to_filename(string):
    return string.lower().replace(' ', '_')


class Builder(object):
    def __init__(self, circuit,
                 outline=None,
                 pcb_attributes=None,
                 builddir='build',
                 compile=default_compile,
                 place=default_place,
                 route=default_route,
                 post_process=default_post_process):
        self.base_file_name = string_to_filename(circuit.name)
        self.builddir = builddir
        self.files = {
            'hash': self.base_file_name + '.hash',
            'net_in': self.base_file_name + '.net',
            'net_out': self.base_file_name + '.out.net',
            'place_in': self.base_file_name + '.place.pcb',
            'place_out': self.base_file_name + '.place.out.pcb',
            'route_in': self.base_file_name + '.place.out.pcb',
            'route_out': self.base_file_name + '.route.out.pcb',
            'spice': self.base_file_name + '.sp',
            'net_yosys': self.base_file_name + '.json',
            'net_svg': self.base_file_name + '.net.svg',
            'pcb_svg': self.base_file_name + '.pcb.svg',
            'kicad': self.base_file_name + '.kicad_pcb'
        }
        for tag, filename in self.files.items():
            self.files[tag] = os.path.join(self.builddir, filename)

        self.hashs = {}
        self.circuit = circuit
        self.outline = outline
        self.pcb_attributes = pcb_attributes

        self.compile_hook = compile
        self.place_hook = place
        self.route_hook = route
        self.post_process_hook = post_process

    def file_hash(self, path):
        try:
            with open(path) as f:
                return hashlib.sha256(f.read().encode('utf-8')).hexdigest()
        except FileNotFoundError:
            return None

    def write_hashfile(self):
        with open(self.files['hash'], 'w+') as f:
            for name, path in self.files.items():
                if name == 'hash':
                    continue
                print(path, self.file_hash(path), file=f)

    def read_hashfile(self):
        try:
            with open(self.files['hash']) as f:
                for line in f.read().split('\n'):
                    if line == '':
                        continue
                    path, digest = line.split(' ')
                    if digest == 'None':
                        digest = None
                    self.hashs[path] = digest
        except FileNotFoundError:
            if not os.path.exists(self.builddir):
                os.makedirs(self.builddir)
            self.write_hashfile()
            self.read_hashfile()

    def stored_hash(self, name):
        return self.hashs[self.files[name]]

    def current_hash(self, name):
        return self.file_hash(self.files[name])

    def load_pcb(self, place=False, route=False):
        file_name = self.files['place_in']
        if place:
            file_name = self.files['place_out']
        if route:
            file_name = self.files['route_out']
        return Pcb.from_file(file_name)

    def step(self, input, output, call):
        if not self.stored_hash(input) == self.current_hash(input) \
           or self.current_hash(output) is None:
            result = call(self.files[input], self.files[output])
            self.write_hashfile()
            return True, result
        else:
            return False, None

    def build(self):
        self.compile()
        self.place()
        self.route()
        self.post_process()

    def compile(self):
        self.read_hashfile()
        self.circuit.to_file(self.files['net_in'])

        run, circuit = self.step('net_in', 'net_out', self.compile_hook)
        if not run:
            circuit = Circuit.from_file(self.files['net_out'])

        self.step('net_out', 'net_yosys', lambda _,
                  x: circuit.to_yosys_file(x))
        self.step('net_yosys', 'net_svg', netlistsvg)
        return circuit

    def place(self):
        netlist = Netlist.from_file(self.files['net_out'])
        pcb = Pcb(netlist, self.outline, self.pcb_attributes)

        self.step('net_out', 'place_in', lambda _, x: pcb.to_file(x))
        self.step('place_in', 'place_out', self.place_hook)
        pcb = self.load_pcb(place=True)
        self.step('place_out', 'pcb_svg', lambda _, x: pcb.to_svg(x))

    def route(self):
        pcb = self.load_pcb(place=True)
        self.step('place_out', 'route_in', lambda _, x: pcb.to_file(x))
        self.step('route_in', 'route_out', self.route_hook)
        pcb = self.load_pcb(place=True, route=True)
        self.step('route_out', 'pcb_svg', lambda _, x: pcb.to_svg(x))

    def post_process(self):
        pcb = self.load_pcb(place=True, route=True)
        kpcb = self.post_process_hook(pcb, pcb.to_kicad())
        kpcb.to_file(self.files['kicad'])

    def clean(self):
        shutil.rmtree(self.builddir)
