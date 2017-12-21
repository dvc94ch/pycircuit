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
    def __init__(self, *funs):
        self.id = None
        self.device = None
        self.funs = funs


class Component(object):
    def __init__(self, pins):
        self.pins = []
        self.funs = []
        self.busses = []

        for pin in pins:
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
