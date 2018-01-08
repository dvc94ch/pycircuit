import os
import hashlib
import shutil
from pycircuit.circuit import Netlist, Circuit
from pycircuit.compiler import Compiler
from pycircuit.formats import *
from pycircuit.pcb import Pcb


def netlistsvg(filein, fileout):
    skin = '~/repos/netlistsvg/lib/analog.svg'
    os.system('netlistsvg --skin %s %s -o %s' % (skin, filein, fileout))


def default_compile(filein, fileout):
    compiler = Compiler()
    return compiler.compile(filein, fileout)


def default_place(filein, fileout):
    with open(fileout, 'w+') as f:
        f.write('{}')


def default_route(filein, fileout):
    with open(fileout, 'w+') as f:
        f.write('G 10 10')


def default_post_process(pcb, kpcb):
    return kpcb


def string_to_filename(string):
    return string.lower().replace(' ', '_')


class Builder(object):
    def __init__(self, circuit, design_rules=None,
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
            'place_in': self.base_file_name + '.place',
            'place_out': self.base_file_name + '.out.place',
            'route_in': self.base_file_name + '.route',
            'route_out': self.base_file_name + '.out.route',
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
        self.design_rules = design_rules

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

    def new_pcb(self, netlist, placement=None, routes=None):
        netlist = Netlist.from_file(netlist)
        pcb = Pcb(netlist, *self.design_rules())
        if not placement is None:
            pcb.from_place(placement)
        if not routes is None:
            pcb.from_route(routes)
        return pcb

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

    def compile(self):
        self.read_hashfile()
        self.circuit.to_file(self.files['net_in'])

        run, circuit = self.step('net_in', 'net_out', self.compile_hook)
        if not run:
            circuit = Circuit.from_file(self.files['net_out'])

        self.step('net_out', 'net_yosys', lambda _, x: circuit.to_yosys_file(x))
        self.step('net_yosys', 'net_svg', netlistsvg)
        return circuit

    def place(self):
        if not self.stored_hash('place_in') == self.current_hash('place_in') \
           or self.stored_hash('place_out') is None:

            print('Placing')
            self.place_hook(self.files['place_in'], self.files['place_out'])

            self.new_pcb(self.files['net_out'],
                         self.files['place_out']) \
                .to_svg(self.files['pcb_svg'])

            self.new_pcb(self.files['net_out'],
                         self.files['place_out']) \
                .to_route(self.files['route_in'])

            self.write_hashfile()
        else:
            print('Skipping place')

    def route(self):
        if not self.stored_hash('route_in') == self.current_hash('route_in') \
           or self.stored_hash('route_out') is None:

            print('Routing')
            self.route_hook(self.files['route_in'], self.files['route_out'])

            self.new_pcb(self.files['net_out'],
                         self.files['place_out'],
                         self.files['route_out']) \
                .to_svg(self.files['pcb_svg'])

            self.write_hashfile()
        else:
            print('Skipping route')

    def post_process(self):
        print('Post processing')
        pcb = self.new_pcb(self.files['net_out'],
                           self.files['place_out'],
                           self.files['route_out'])

        kpcb = self.post_process_hook(pcb, pcb.to_kicad())

        kpcb.to_file(self.files['kicad'])

        self.write_hashfile()

    def clean(self):
        shutil.rmtree(self.builddir)
