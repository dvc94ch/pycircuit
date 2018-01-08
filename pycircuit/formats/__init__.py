import os
import sys


def extends(klass):
    def decorator(func):
        setattr(klass, func.__name__, func)
        return func
    return decorator


def export(string, filename, extension):
    if filename is None:
        filename = os.path.basename(sys.argv[0])
        filename = os.path.splitext(filename)[0]

    if not filename.endswith(extension):
        filename += extension

    with open(filename, 'w+') as f:
        f.write(string)


def polygon_to_lines(coords):
    coords.append(coords[0])
    for i in range(len(coords) - 1):
        yield coords[i], coords[i + 1]


__all__ = ['netlist', 'yosys', 'graphviz', 'spice',
           'place', 'route', 'svg', 'kicad']
