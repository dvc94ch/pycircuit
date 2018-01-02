from pycircuit.component import *
from pycircuit.package import *


class Map(object):
    '''Represents the a map from a Pad to a Pin.'''

    def __init__(self, pad, pin):
        '''A Map has a pad name, a pin name and a Footprint.'''
        assert not (pad is None and pin is None)
        self.pad = pad
        self.pin = pin
        self.device = None

    def __str__(self):
        '''Returns the name of the pad.'''

        return self.pad

    def __repr__(self):
        '''Returns a string "pad <> pin".'''

        return '%4s <> %s' % (self.pad, self.pin)


class Device(object):
    '''Represents a mapping from a Component to a Package.'''

    devices = []

    def __init__(self, name, component, package, *maps):
        '''A Device with name that maps the pads of a Package to the pins
        of a Component.'''

        self.name = name
        self.component = Component.component_by_name(component)
        self.package = Package.package_by_name(package)
        self.maps = []

        for map in maps:
            self.add_map(map)

        self.check_device()
        self.register_device(self)

    def add_map(self, map):
        '''Adds a map to Device.'''

        pin = map.pin
        pad = map.pad

        if pin is not None:
            pin = self.component.pin_by_name(pin)
            if pin is None:
                print('Warn: Device %s: Pin %s not in component %s'
                      % (self.name, map.pin, self.component.name))
        if pad is not None:
            pad = self.package.pad_by_name(pad)
            if pad is None:
                print('Warn: Device %s: Pad %s not in package %s'
                      % (self.name, map.pad, self.package.name))

        if pad is None:
            assert pin.optional

        map.pin = pin
        map.pad = pad
        map.device = self
        self.maps.append(map)

    def check_device(self):
        '''Checks that every Pin and every Pad has a Map.'''

        for pin in self.component.pins:
            for map in self.maps:
                if map.pin == pin:
                    break
            else:
                raise AssertionError('No map for component %s pin %s in device %s' \
                                     % (self.component.name, pin.name, self.name))
        for pad in self.package.pads:
            for map in self.maps:
                if map.pad == pad:
                    break
            else:
                raise AssertionError('No map for package %s pad %s in device %s' \
                                     % (self.package.name, pad.name, self.name))

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
        '''Returns the name of the Device.'''

        return self.name

    def __repr__(self):
        '''Returns a string representation of a Device.'''

        return '%s (%s <> %s)\n%s\n' % (self.name, self.component, self.package,
                                        '\n'.join([repr(map) for map in self.maps]))

    @classmethod
    def device_by_name(cls, name):
        '''Returns the Device with name from registered devices.'''

        for dev in cls.devices:
            if dev.name == name:
                return dev

        raise IndexError('No Device with name ' + name)

    @classmethod
    def devices_by_component(cls, component):
        '''Returns the available Devices for Component.'''

        for dev in cls.devices:
            if dev.component == component:
                yield dev

    @classmethod
    def register_device(cls, device):
        '''Register a Device.'''

        try:
            cls.device_by_name(device.name)
            raise Exception('Device with name %s already exists' % device.name)
        except IndexError:
            cls.devices.append(device)
