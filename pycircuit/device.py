from pycircuit.component import *
from pycircuit.package import *


class Map(object):
    '''Represents the a map from a Pad to a Pin.'''

    def __init__(self, pad, pin):
        '''A Map has a pad name, a pin name and a Footprint.'''

        self.pad = str(pad)
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

        pin = self.component.pin_by_name(map.pin)
        pad = self.package.pad_by_name(map.pad)
        assert not pin is None or not pad is None

        map.pin = pin
        map.pad = pad
        map.device = self
        self.maps.append(map)

    def check_device(self):
        '''Checks that every Pin and every Pad has a Map.'''

        for pin in self.component.pins:
            maps = list(self._maps_by_pin(pin))
            if len(maps) > 1:
                # No pad can be None
                for map in maps:
                    assert not map.pad is None
            elif len(maps) > 0:
                # If pin is required pad can't be None
                if pin.required:
                    assert not maps[0].pad is None
            else:
                # At least one Map per Pin
                assert True

        for pad in self.package.pads:
            maps = list(self._maps_by_pad(pad))
            # At least one Map per Pad
            assert len(maps) > 0

    def _maps_by_pad(self, pad):
        '''Returns the map with pad.'''

        for map in self.maps:
            if map.pad == pad:
                yield map

    def _maps_by_pin(self, pin):
        '''Returns the maps with pin.'''

        for map in self.maps:
            if map.pin == pin:
                yield map

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
