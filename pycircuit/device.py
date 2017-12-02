from collections import defaultdict


class Fun(object):
    '''Function represents a function of a Pin.'''

    BIDIR, INPUT, OUTPUT = range(3)

    def __init__(self, bus_or_name, bus_type_or_dir=None, func=None):
        '''A Function has a name, a direction and optionally belongs to a Bus.

        Examples:
        Fun('GPIO')
        Fun('VCC', Fun.INPUT)
        Fun('UART0', 'UART', 'TX')
        Fun('JTAG', 'TDO')
        '''

        self.pin = None

        if not isinstance(bus_type_or_dir, str):
            self.bus_name = None
            self.bus = None
            self.bus_func = None
            self.name = bus_or_name
            self.dir = Fun.BIDIR if bus_type_or_dir is None else bus_type_or_dir
        else:
            if func is not None:
                self.bus_name = bus_or_name
                self.bus_func = func
                self.bus = Bus.bus_by_type(bus_type_or_dir)
            else:
                self.bus_name = bus_or_name
                self.bus_func = bus_type_or_dir
                self.bus = Bus.bus_by_type(bus_or_name)
            self.name = self.bus.type + '_' + self.bus_func
            self.dir = self.bus.function_by_name(self.bus_func).dir


    def __str__(self):
        '''Returns the name (NAME or BUSTYPE_NAME)'''

        return self.name

    def __repr__(self):
        '''Returns a string representation (BUSNAME__DIR_NAME__PIN)'''

        dir = 'io'
        if self.dir == Fun.INPUT:
            dir = 'i'
        elif self.dir == Fun.OUTPUT:
            dir = 'o'

        if self.bus is None:
            bus = ''
        else:
            bus = self.bus_name + '__'

        if self.pin is None:
            pin = ''
        else:
            pin = '__' + self.pin.name

        return '%s%s_%s%s' % (bus, dir, str(self), pin)


class Bus(object):
    '''Bus represents a collection of functions.'''

    busses = []

    def __init__(self, type, *functions):
        '''A Bus has a name a type and a list of functions. The constructor
        takes a name and a function or a name a type and a function.

        Examples:
        # Create a JTAG Bus
        Bus('JTAG', Fun('TCK', Fun.INPUT), Fun('TDO', Fun.OUTPUT),
                    Fun('TMS', Fun.INPUT), Fun('TDI', Fun.INPUT))
        # Create a UART Bus
        Bus('UART', Fun('RX', Fun.INPUT), Fun('TX', Fun.OUTPUT))
        '''

        self.type = type
        self.functions = functions
        self.register_bus(self)

    def add_function(self, function):
        '''Adds a function to bus.'''

        func = Function(function)
        func.bus = self
        func.dir = self.bus_types[self.type][self.name]
        self.functions.append(func)

    def function_by_name(self, name):
        '''Return a function with name.'''

        for func in self.functions:
            if func.name == name:
                return func

    def __str__(self):
        '''Returns the type of the Bus.'''

        return self.type

    def __repr__(self):
        '''Returns a string representation of the Bus.'''

        functions = [func.name for func in self.functions]
        functions.sort()

        return '%-20s (%s)' % (self.type, ' '.join(functions))

    @classmethod
    def bus_by_type(cls, type):
        '''Returns the Bus with type from registered busses.'''

        for bus in cls.busses:
            if bus.type == type:
                return bus

        raise IndexError('No Bus with type ' + type)

    @classmethod
    def register_bus(cls, bus):
        '''Register a Bus.'''

        try:
            cls.bus_by_type(bus.type)
            raise Exception('Bus with name %s exists' % bus.type)
        except IndexError:
            cls.busses.append(bus)


class Pin(object):
    '''Pin represents a port of a device.'''

    POWER, SIGNAL = range(2)

    def __init__(self, name, *functions, descr=''):
        '''A Pin has a name and a list of functions. If no functions listed
        the Pin only supports a single Function which is named the same as the
        Pin. A Function is either a String or a Bus.'''

        self.name = name
        self.descr = descr
        self.functions = []
        self.domain = Pin.SIGNAL

        if len(functions) < 1:
            self.add_function(Fun(name))
        else:
            for func in functions:
                if isinstance(func, str):
                    func = Fun(func)
                self.add_function(func)

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


class Io(Pin):
    '''Single function bidirectional signal pin.'''

    def __init__(self, name, descr=''):
        super().__init__(name, descr=descr)

class Pwr(Io):
    '''Single function bidirectional power pin.'''

    def __init__(self, name, descr=''):
        super().__init__(name, descr=descr)
        self.domain = Pin.POWER

class In(Pin):
    '''Single function input signal pin.'''

    def __init__(self, name, descr=''):
        super().__init__(name, descr=descr)
        self.functions[0].dir = Fun.INPUT

class PwrIn(In):
    '''Single function input power pin.'''

    def __init__(self, name, descr=''):
        super().__init__(name, descr=descr)
        self.domain = Pin.POWER

class Out(Pin):
    '''Single function output signal pin.'''

    def __init__(self, name, descr=''):
        super().__init__(name, descr=descr)
        self.functions[0].dir = Fun.OUTPUT

class PwrOut(Out):
    '''Single function output power pin.'''

    def __init__(self, name, descr=''):
        super().__init__(name, descr=descr)
        self.domain = Pin.POWER


class Device(object):
    '''Device represents an electrical interface. Devices are created in the
    library module and register themselves to the devices list when imported.
    Common devices like resistors are defined in pycircuit.library.__init__.py'''

    devices = []

    def __init__(self, name, descr='', pins=()):
        '''A Device has a name and a list of pins and busses. Busses are
        extracted from Pin functions and merged by name.'''

        self.name = name
        self.descr = descr
        self.pins = []
        # A bus is a list of pins.
        self.busses = defaultdict(list)

        for pin in pins:
            for func in pin.functions:
                if func.bus_name is not None:
                    self.busses[func.bus_name].append(func)

            self.pins.append(pin)

        self.register_device(self)

    def bus_types(self):
        '''Returns a list of supported bus types.'''

        types = set()
        for pin in self.pins:
            for fun in pin.functions:
                if fun.bus is not None:
                    if not fun.bus.type in types:
                        types.add(fun.bus.type)
        return types

    def bus_by_name(self, name):
        '''Returns a bus [Pin] with name or [].'''

        return self.busses[name]

    def busses_by_type(self, type):
        '''Returns a list of busses matching type.'''

        bus_names = list(self.busses.keys())
        bus_names.sort()

        busses = []
        for name in bus_names:
            if self.busses[name][0].bus.type == type:
                busses.append(self.busses[name])
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
                     '\n'.join([4 * ' ' + bus_name + ' ' +
                                ' '.join([f.bus_func for f in funcs])
                                for bus_name, funcs in self.busses.items()])

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
