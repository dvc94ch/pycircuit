class Fun(object):
    def __init__(self, function):
        self.id = None
        self.bus_id = None
        self.pin = None

        self.function = function

    def __str__(self):
        return self.function


class BusFun(Fun):
    def __init__(self, bus, function):
        super().__init__(function)

        self.bus = bus

    def __str__(self):
        return '%s %s' % (self.bus, self.function)


class Pin(object):
    def __init__(self, name, *funs, **kwargs):
        self.id = None
        self.device = None
        self.name = name
        self.funs = funs

        self.optional = True
        if 'optional' in kwargs:
            self.optional = kwargs['optional']

        self.description = ''
        if 'description' in kwargs:
            self.description = kwargs['description']

    def __str__(self):
        '''Return a string "Component.Pin".'''

        return '%s.%s' % (self.component.name, self.name)

    def __repr__(self):
        '''Return a string "Pin (Functions)".'''

        text = '%s(%s)' % (self.__class__.__name__, self.name)
        return '%-15s (%s)' % (text, ' | '.join([str(fun) for fun in self.funs]))


class Component(object):
    components = []

    def __init__(self, name, description, *pins):
        Component.components.append(self)

        self.name = name
        self.description = description

        self.pins = []
        self.funs = []
        self.busses = []

        for pin in pins:
            self.add_pin(pin)

    def add_pin(self, pin):
        assert self.pin_by_name(pin.name) is None

        pin.id = len(self.pins)
        pin.component = self
        self.pins.append(pin)

        for fun in pin.funs:
            fun.id = len(self.funs)
            fun.pin = pin
            self.funs.append(fun)

            # Assign bus_id
            if isinstance(fun, BusFun):
                for i, bus in enumerate(self.busses):
                    if fun.bus == bus:
                        fun.bus_id = i
                        break
                else:
                    fun.bus_id = len(self.busses)
                    self.busses.append(fun.bus)
            else:
                fun.bus_id = -fun.id

    def funs_by_name(self, function):
        for fun in self.funs:
            if fun.function == function:
                yield fun

    def pin_by_name(self, name):
        for pin in self.pins:
            if pin.name == name:
                return name

    def __str__(self):
        '''Return the name of the device.'''

        return self.name

    def __repr__(self):
        '''Return a string representing the device's bus types,
        busses and pins.'''

        pin_string = '\n'.join([2 * ' ' + repr(pin) for pin in self.pins])

        return '%s\n%s' % (self.name, pin_string)

    @classmethod
    def component_by_name(cls, name):
        '''Returns the Component called `name` from registered components.'''

        for c in cls.components:
            if c.name == name:
                return c

        raise IndexError('No Component with name ' + name)

    @classmethod
    def register_component(cls, component):
        '''Register a Component.'''

        try:
            cls.component_by_name(component.name)
            raise Exception('Component with name %s exists' % component.name)
        except IndexError:
            cls.components.append(component)


class Io(Pin):
    '''Single function bidirectional signal pin.'''

    def __init__(self, name, *funs, **kwargs):
        super().__init__(name, *funs, **kwargs)

class Pwr(Io):
    '''Single function bidirectional power pin.'''

    def __init__(self, name, *funs, **kwargs):
        super().__init__(name, *funs, **kwargs)

class In(Pin):
    '''Single function input signal pin.'''

    def __init__(self, name, *funs, **kwargs):
        super().__init__(name, *funs, **kwargs)

class PwrIn(In):
    '''Single function input power pin.'''

    def __init__(self, name, *funs, **kwargs):
        super().__init__(name, *funs, **kwargs)

class Out(Pin):
    '''Single function output signal pin.'''

    def __init__(self, name, *funs, **kwargs):
        super().__init__(name, *funs, **kwargs)

class PwrOut(Out):
    '''Single function output power pin.'''

    def __init__(self, name, *funs, **kwargs):
        super().__init__(name, *funs, **kwargs)
