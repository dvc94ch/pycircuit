import numpy as np
from shapely import affinity
from shapely.geometry import Point, Polygon


class Pad(object):

    def __init__(self, name, x, y, angle=0, size=None, shape=None, drill=None):
        self.name = name
        self.angle = angle

        point = affinity.rotate(Point(x, y), angle, origin=Point(0, 0))
        self.location = np.array([point.coords[0][0], point.coords[0][1], 1])

        # Optional properties for pcb export
        self.size = size
        self.shape = shape
        self.drill = drill

    def __repr__(self):
        return '%s (%s, %s)' % (self.name, self.location[0], self.location[1])


class PadArray(object):
    def __init__(self, length, pitch, radius, angle, prefix='', offset=0):
        self.length = length
        self.pitch = pitch
        self.angle = angle
        self.array_radius = (length - 1) * pitch / 2
        self.radius = radius
        # Pad name is %s%s % prefix, (index + offset)
        self.prefix = prefix
        self.offset = offset

    def __getitem__(self, index):
        pad_name = self.prefix + str(index + self.offset)
        pad_x = (index - 1) * self.pitch - self.array_radius
        return Pad(pad_name, pad_x, self.radius, self.angle)

    def __len__(self):
        return self.length

    def __iter__(self):
        self.counter = 0
        return self

    def __next__(self):
        if self.counter < self.length:
            self.counter += 1
            return self[self.counter]
        raise StopIteration()


class TwoPads(object):
    def __init__(self, distance):
        self.distance = distance

    def __iter__(self):
        for i, angle in enumerate([90, -90]):
            for pad in PadArray(1, 0, self.distance / 2, angle, offset=i):
                yield pad


class Sot23Pads(object):
    def __init__(self, c, e):
        self.c = c
        self.e = e

    def __iter__(self):
        for pad in PadArray(2, self.e * 2, self.c / 2, 0):
            yield pad
        for pad in PadArray(1, 0, self.c / 2, 180, offset=2):
            yield pad


class DualPads(object):
    def __init__(self, num, pitch, radius):
        assert num % 2 == 0
        self.num = num
        self.pitch = pitch
        self.radius = radius

    def __iter__(self):
        pad_array_length = int(self.num / 2)
        for i, angle in enumerate([90, -90]):
            for pad in PadArray(pad_array_length, self.pitch, self.radius, angle,
                                offset=pad_array_length * i):
                yield pad


class QuadPads(object):
    def __init__(self, num, pitch, radius, thermal_pad=False):
        assert num % 4 == 0
        self.num = num
        self.pitch = pitch
        self.radius = radius
        self.thermal_pad = thermal_pad

    def __iter__(self):
        pad_array_length = int(self.num / 4)
        for i, angle in enumerate([90, 0, -90, 180]):
            for pad in PadArray(pad_array_length, self.pitch, self.radius, angle,
                                offset=pad_array_length * i):
                yield pad
        if self.thermal_pad:
            yield Pad(str(self.num + 1), 0, 0,
                      size=(self.thermal_pad, self.thermal_pad))


class GridPads(object):
    def __init__(self, num, pitch):
        self.num = num
        self.pitch = pitch

    def __iter__(self):
        grid_radius = (self.num - 1) * self.pitch / 2
        for row in range(self.num):
            prefix = ''
            for i in range(int(row / 26) + 1):
                prefix += chr(row % 26 + ord('A'))
            radius = row * self.pitch - grid_radius
            for pad in PadArray(self.num, self.pitch, radius, 0, prefix):
                yield pad


class StaggeredGridPads(object):
    pass


class PerimeterPads(object):
    def __init__(self, num, perimeter, inner=0):
        self.num = num
        self.perimeter = perimeter
        self.inner = inner


class Courtyard(object):
    def __init__(self, coords):
        self.coords = coords
        self.polygon = Polygon(coords)
        self.bounds = self.polygon.bounds
        self.width = self.bounds[2] - self.bounds[0]
        self.height = self.bounds[3] - self.bounds[1]

    def __repr__(self):
        return repr(self.coords)


class RectCrtyd(Courtyard):
    def __init__(self, xlen, ylen):
        self.xlen = xlen
        self.ylen = ylen

        x, y = xlen / 2, ylen / 2
        super().__init__([(-x, y), (x, y), (x, -y), (-x, -y)])


class IPCGrid(RectCrtyd):

    # IPC grid element is 0.5mm * 0.5mm
    IPC_GRID_SCALE = 0.5

    def __init__(self, ipc_x, ipc_z):
        super().__init__(ipc_z * self.IPC_GRID_SCALE,
                         ipc_x * self.IPC_GRID_SCALE)

        # X is the ylen axis
        self.ipc_x = ipc_x
        # Z is the xlen axis
        self.ipc_z = ipc_z


class Package(object):
    '''Package represents a IC package. Packages are registered when imported
    from library.'''

    packages = []

    def __init__(self, name, courtyard, pads,
                 package_size=(5, 5), pad_size=(1, 1),
                 pad_shape='rect', pad_drill=None):
        self.name = name
        self.courtyard = courtyard
        self.pads = []
        self.package_size = package_size
        self.pad_size = pad_size
        self.pad_shape = pad_shape
        self.pad_drill = pad_drill

        for pad in pads:
            self.add_pad(pad)

        self.register_package(self)

    def add_pad(self, pad):
        pad.package = self
        if pad.size is None:
            pad.size = self.pad_size
        if pad.shape is None:
            pad.shape = self.pad_shape
        if pad.drill is None:
            pad.drill = self.pad_drill

        self.pads.append(pad)

    def pad_by_name(self, name):
        for pad in self.pads:
            if pad.name == name:
                return pad

    def size(self):
        bounds = self.courtyard.polygon.bounds
        return (bounds[2] - bounds[0], bounds[3] - bounds[1])

    def __str__(self):
        '''Returns the name of the Package.'''

        return self.name

    def __repr__(self):
        '''Returns the representation of a Package.'''

        pad_string = '\n'.join([4 * ' ' + repr(pad) for pad in self.pads])
        return '%s\nCourtyard:\n%s\nPads:\n%s\n' \
            % (self.name, str(self.courtyard), pad_string)

    @classmethod
    def package_by_name(cls, name):
        '''Returns the Package with name from registered packages.'''

        for pkg in cls.packages:
            if pkg.name == name:
                return pkg

        raise IndexError('No Package with name ' + name)

    @classmethod
    def register_package(cls, package):
        '''Register a Package.'''

        try:
            cls.package_by_name(package.name)
            raise Exception('Package with name %s already exists' % package.name)
        except IndexError:
            cls.packages.append(package)
