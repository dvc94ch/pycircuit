import numpy as np
from shapely.geometry.polygon import Polygon
from pycircuit.outline import Hole, Outline


def rectangle_with_mounting_holes(width, height, inset, hole_shift, hole_drill):
    shift_matrix = np.array([[1, 1], [-1, 1], [-1, -1], [1, -1]])

    exterior_coords = np.array([[0, 0], [width, 0], [width, height], [0, height]])
    interior_coords = exterior_coords + shift_matrix * inset
    interior = Polygon(interior_coords)

    hole_coords = exterior_coords + shift_matrix * hole_shift
    holes = []
    for pos in hole_coords:
        holes.append(Hole(pos, hole_drill))
        hole_clearance = hole_drill / 2 + inset
        interior = interior.difference(Polygon(shift_matrix * hole_clearance + pos))

    outline = Polygon(exterior_coords, [interior.exterior.coords])
    return Outline(outline, *holes)


def sick_of_beige(name):
    '''http://dangerousprototypes.com/docs/Sick_of_Beige_standard_PCB_sizes_v1.0'''

    lookup = {
        'DP5031': (50, 31),
        'DP6037': (60, 37),
        'DP7043': (70, 43),
        'DP8049': (80, 49),
        'DP9056': (90, 56),
        'DP10062': (100, 62),
        'DP3030': (30, 30),
        'DP4040': (40, 40),
        'DP5050': (50, 50),
        'DP6060': (60, 60),
        'DP7070': (70, 70),
        'DP8080': (80, 80),
    }

    width, height = lookup[name]
    inset = 1.7
    hole_shift = 4
    hole_dia = 3.2

    return rectangle_with_mounting_holes(width=width, height=height, inset=inset,
                                         hole_shift=hole_shift, hole_dia=hole_dia)
