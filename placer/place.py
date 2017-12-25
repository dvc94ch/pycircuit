import json
from z3 import *
from placer.box import Z3Box
from placer.bin import Z3Bin
from placer.grid import Grid

class Placer(object):
    def __init__(self):
        pass

    def from_file(self, path):
        with open(path) as f:
            self.nodes = json.loads(f.read())

    def to_file(self, path):
        with open(path, 'w+') as f:
            print(json.dumps(self.result), file=f)

    def place(self, filein, fileout):
        self.from_file(filein)

        boxes = []
        min_area = 0

        for node in self.nodes:
            box = Z3Box.from_dict(node)
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
        #s.add(pcb.var_width == 170)
        #s.add(pcb.var_height == 50)
        s.add(pcb.area_constraint(min_area * 1.5))

        #s.add(boxes[0].fix_position_constraint(*pcb.var_center()))

        if s.check() == sat:
            model = s.model()

            pcb.eval(model)
            print(str(pcb))

            grid = Grid(*pcb.dim())

            self.result = []
            for box in boxes:
                box.eval(model)
                print(str(box))
                self.result.append(box.to_dict())
                grid.add_box(box)

            print(str(grid))

            self.to_file(fileout)
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
