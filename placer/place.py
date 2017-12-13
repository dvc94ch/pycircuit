from z3 import *
from box import Z3Box
from bin import Z3Bin
from grid import Grid

def place(nodes):
    boxes = []
    min_area = 0

    for node in nodes:
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

        result = []
        for box in boxes:
            box.eval(model)
            print(str(box))
            result.append(box.to_dict())
            grid.add_box(box)

        print(str(grid))
        return result
    else:
        print('unsat')
        return []


if __name__ == '__main__':
    import argparse
    import json

    parser = argparse.ArgumentParser(description='SMT-based, constrained placement')

    parser.add_argument('filename', type=str)

    args, unknown = parser.parse_known_args()

    fileout = args.filename.split('.')
    fileout[-1] = 'out.pcpl'
    fileout = '.'.join(fileout)

    input = ""
    with open(args.filename) as f:
        input = json.loads(f.read())

    result = place(input)

    with open(fileout, 'w') as f:
        print(json.dumps(result), file=f)
