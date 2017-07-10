class Function(object):
    '''Function represents a function of a Pin.'''

    def __init__(self, name, bus=None):
        '''A Function has a name and optionally belongs to a Bus.'''

        self.pin = None
        self.name = name
        self.bus = bus

    def __str__(self):
        '''Returns the name of the Function.'''

        return self.name


class Bus(object):
    '''Bus represents a collection of functions.'''

    def __init__(self, name, type, function=None):
        '''A Bus has a name a type and a list of functions. The constructor
        takes a name and a function or a name a type and a function.'''

        if function is None:
            function = type
            type = name

        self.name = name
        self.type = type
        self.functions = []
        self.functions.append(Function(type + '_' + function, self))

    def add_function(self, func):
        '''Adds a function to bus.'''

        assert isinstance(func, Function)
        assert func.bus.name == self.name
        assert func.bus.type == self.type

        func.bus = self
        self.functions.append(func)

    def function_by_name(self, name):
        '''Return a function with name type_name.'''

        name = self.type + '_' + name

        for func in self.functions:
            if func.name == name:
                return func

    def __str__(self):
        '''Returns the name of the Bus.'''

        return self.name

    def __repr__(self):
        '''Returns a string representation of the Bus.'''

        functions = [ '_'.join(str(func).split('_')[1:])
                      for func in self.functions ]
        functions.sort()
        #string = '%-6s (%s)' % (self.name, self.type)

        return '%-20s (%s)' % (self.name, ' '.join(functions))


class Pin(object):
    '''Pin represents a port of a device.'''

    def __init__(self, name, *functions):
        '''A Pin has a name and a list of functions. If no functions listed
        the Pin only supports a single Function which is named the same as the
        Pin. A Function is either a String or a Bus.'''

        self.name = name
        self.functions = []

        if len(functions) < 1:
            self.functions.append(Function(name))
        else:
            for func in functions:
                if isinstance(func, str):
                    self.add_function(Function(func))
                elif isinstance(func, Bus):
                    self.add_function(func.functions[0])

    def add_function(self, function):
        '''Adds a Function to Pin.'''

        function.pin = self
        self.functions.append(function)

    def function_by_index(self, index):
        '''Return the function at index.'''

        return self.functions[index]

    def function_by_name(self, name):
        '''Return the function with name.'''

        for func in self.functions:
            if func.name == name:
                return func

    def __str__(self):
        '''Return a string "Pin (Functions)".'''

        return '%-20s (%s)' % (self.name,
                            ' | '.join([str(func) for func in self.functions]))

    def __repr__(self):
        '''Return a string "Device.Pin".'''

        return '%s.%s' % (self.device.name, self.name)


class Device(object):
    '''Device represents an electrical interface. Devices are created in the
    library module and register themselves to the devices list when imported.
    Common devices like resistors are defined in pycircuit.library.__init__.py'''

    devices = []

    def __init__(self, name, *pins):
        '''A Device has a name and a list of pins and busses. Busses are
        extracted from Pin functions and merged by name.'''

        self.name = name
        self.pins = []
        self.busses = []

        for pin in pins:
            for func in pin.functions:
                if func.bus is not None:
                    bus = self.bus_by_name(func.bus.name)
                    if bus is not None:
                        bus.add_function(func)
                    else:
                        self.busses.append(func.bus)

            self.pins.append(pin)

        self.register_device(self)

    def bus_types(self):
        '''Returns a list of supported bus types.'''

        bus_types = []
        for bus in self.busses:
            if not bus.type in bus_types:
                bus_types.append(bus.type)
        return bus_types

    def bus_by_name(self, name):
        '''Returns the Bus with name.'''

        for bus in self.busses:
            if bus.name == name:
                return bus

    def busses_by_type(self, type):
        '''Returns a list of busses matching type.'''

        busses = []
        for bus in self.busses:
            if bus.type == type:
                busses.append(bus)
        return busses

    def pin_by_index(self, index):
        '''Return the Pin at index.'''

        return self.pins[index]

    def pin_by_name(self, name):
        '''Return the Pin with name.'''

        for pin in self.pins:
            if pin.name == name:
                return pin

    def pins_by_function(self, func):
        '''Return a list of pins matching func.'''

        pins = []
        for pin in self.pins:
            if pin.function_by_name(func) is not None:
                pins.append(pin)
        return pins

    def __str__(self):
        '''Return the name of the device.'''

        return self.name

    def __repr__(self):
        '''Return a string representing the device's bus types,
        busses and pins.'''

        pin_string = 'Pins:\n%s\n' % \
                     '\n'.join([4 * ' ' + str(pin) for pin in self.pins])
        bus_string = 'Busses:\n%s\n' % \
                     '\n'.join([4 * ' ' + repr(bus) for bus in self.busses])

        details_string = pin_string
        if len(self.busses) > 0:
            details_string += bus_string

        string = self.name

        bus_types = self.bus_types()
        if len(bus_types) > 0:
            string += ' (%s)' % ' '.join(bus_types)

        return '%s\n%s' % (string, details_string)

    @classmethod
    def device_by_name(cls, name):
        '''Returns the Device with name from registered devices.'''

        for dev in cls.devices:
            if dev.name == name:
                return dev

        raise IndexError('No Device with name ' + name)

    @classmethod
    def register_device(cls, device):
        '''Register a Device.'''

        try:
            cls.device_by_name(device.name)
            raise Exception('Device with name %s exists' % device.name)
        except IndexError:
            cls.devices.append(device)
