from pycircuit.pcb import Pcb
from pycircuit.package import Courtyard
from pycircuit.formats import json

from z3 import *
from placer.box import Z3Box
from placer.bin import Z3Bin
from placer.grid import Grid

class Placer(object):
    def __init__(self, grid_size=Courtyard.IPC_GRID_SCALE, density=1.5):
        assert density > 1
        self.grid_size = grid_size
        self.density = density

    def place(self, filein, fileout):
        self.pcb = Pcb.from_file(filein)
        left, bottom, right, top = self.pcb.outline.polygon.interiors[0].bounds
        width, height = (right - left) / self.grid_size, (top - bottom) / self.grid_size
        print('width', width, 'height', height)

        boxes = []
        min_area = 0

        for inst in self.pcb.netlist.insts:
            box = Z3Box.from_inst(inst)
            min_area += box.area()
            boxes.append(box)

        pcb = Z3Bin()

        s = Solver()

        s.add(pcb.range_constraint())

        for i, box in enumerate(boxes):
            # Add rotation constraints
            s.add(box.rotation_constraint())
            # Constrain position to be on the pcb
            s.add(box.range_constraint(pcb))
            for j in range(i):
                # Add non overlapping constraint
                s.add(box.overlap_constraint(boxes[j]))

        # Project constraints:
        s.add(pcb.var_width <= width)
        s.add(pcb.var_height <= height)
        s.add(pcb.area_constraint(min_area * self.density))

        #s.add(boxes[0].fix_position_constraint(*pcb.var_center()))

        if s.check() == sat:
            model = s.model()

            pcb.eval(model)
            print(str(pcb))

            grid = Grid(*pcb.dim())

            for box in boxes:
                box.eval(model)
                print(str(box))
                grid.add_box(box)
                box.place_inst((left, top), self.grid_size)

            print(str(grid))

            self.pcb.to_file(fileout)
        else:
            print('unsat')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='SMT-based, constrained placement')

    parser.add_argument('filein', type=str)
    parser.add_argument('fileout', type=str)

    args, unknown = parser.parse_known_args()

    placer = Placer()
    placer.place(args.filein, args.fileout)
