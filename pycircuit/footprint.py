from pycircuit.device import *
from pycircuit.package import *


class Map(object):
    '''Represents the a map from a Pad to a Pin.'''

    def __init__(self, pad, pin):
        '''A Map has a pad name, a pin name and a Footprint.'''

        self.pad = str(pad)
        self.pin = pin
        self.footprint = None

    def __str__(self):
        '''Returns the name of the pad.'''

        return self.pad

    def __repr__(self):
        '''Returns a string "pad <> pin".'''

        return '%4s <> %s' % (self.pad, self.pin)


class Footprint(object):
    '''Represents a collection a complete map from a device to a package.'''

    footprints = []

    def __init__(self, name, device, package, *maps):
        '''A Footprint with name that maps the pads of a package to the pins
        of a device.'''

        self.name = name
        self.device = Device.device_by_name(device)
        self.package = Package.package_by_name(package)
        self.maps = []

        for map in maps:
            self.add_map(map)

        self.register_footprint(self)

    def add_map(self, map):
        '''Adds a map to footprint.'''

        pin = self.device.pin_by_name(map.pin)
        pad = self.package.pad_by_name(map.pad)
        assert not pin is None and not pad is None

        map.pin = pin
        map.pad = pad
        map.footprint = self
        self.maps.append(map)

    def pin_by_pad(self, pad):
        '''Returns the pin mapped to pad.'''

        for map in self.maps:
            if map.pad == pad:
                return map.pin

    def pads_by_pin(self, pin):
        '''Returns a list of pads mapped to pin.'''

        for map in self.maps:
            if map.pin == pin:
                yield map.pad

    def __str__(self):
        '''Returns the name of a Footprint.'''

        return self.name

    def __repr__(self):
        '''Returns a string representation of a Footprint.'''

        return '%s (%s <> %s)\n%s\n' % (self.name, self.device, self.package,
                                        '\n'.join([repr(map) for map in self.maps]))

    @classmethod
    def footprint_by_name(cls, name):
        '''Returns the Footprint with name from registered footprints.'''

        for fp in cls.footprints:
            if fp.name == name:
                return fp

        raise IndexError('No Footprint with name ' + name)

    @classmethod
    def footprints_by_device(cls, device):
        '''Returns the available Footprints for device.'''

        for fp in cls.footprints:
            if fp.device == device:
                yield fp

    @classmethod
    def register_footprint(cls, footprint):
        '''Register a Footprint.'''

        try:
            cls.footprint_by_name(footprint.name)
            raise Exception('Footprint with name %s already exists' % footprint.name)
        except IndexError:
            cls.footprints.append(footprint)
