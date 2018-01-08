import uuid
from z3 import And, Or, Implies, Int, Distinct, Solver, sat


class Z3Assign(object):
    def __init__(self, function, meta):
        self.function = function
        self.meta = meta

        self.constraints = []

        _uuid = uuid.uuid4()
        self.z3_fun = Int(str(_uuid) + '_fun')
        self.z3_pin = Int(str(_uuid) + '_pin')
        self.z3_bus = Int(str(_uuid) + '_bus')


    def component_constraint(self, component):
        self.component = component

        fun_constraints = []
        for fun in component.funs_by_function(self.function):
            assert(fun.id >= 0)
            assert(fun.bus_id is not None)

            # Constraint z3_fun to pin functions
            fun_constraints.append(self.z3_fun == fun.id)

            # z3_fun implies z3_pin and z3_bus
            self.constraints.append(Implies(self.z3_fun == fun.id,
                                            And(self.z3_bus == fun.bus_id,
                                                self.z3_pin == fun.pin.id)))
        self.constraints.append(Or(fun_constraints))

    def eval(self, model):
        self.fun = self.component.funs[model[self.z3_fun].as_long()]
        self.pin = self.component.pins[model[self.z3_pin].as_long()]
        self.bus = model[self.z3_bus].as_long()

    def __iter__(self):
        yield self

    def __repr__(self):
        return self.function


class Z3BusAssign(object):
    def __init__(self, *assigns):
        _uuid = uuid.uuid4()
        self.z3_bus = Int(str(_uuid) + '_bus')

        self.assigns = []
        self.constraints = []

        for assign in assigns:
            self.add_assign(assign)

    def add_assign(self, assign):
        # All assignments in a BusAssign need to have a the same bus
        self.assigns.append(assign)
        self.constraints.append(self.z3_bus == assign.z3_bus)

    def eval(self, model):
        self.bus = model[self.z3_bus].as_long()

    def __iter__(self):
        for assig in self.assigns:
            yield assig


class AssignmentProblem(object):
    def __init__(self, component, assigns):
        self.component = component
        self.assigns = []
        self.bus_assigns = []
        self.constraints = []

        for bus_assign in assigns:
            if isinstance(bus_assign, Z3Assign):
                bus_assign = Z3BusAssign(bus_assign)

            self.constraints += bus_assign.constraints
            self.bus_assigns.append(bus_assign)

            for assign in bus_assign:
                assign.component_constraint(component)
                self.constraints += assign.constraints
                self.assigns.append(assign)

        # Each assignment needs a different Fun
        self.constraints.append(Distinct([assign.z3_fun for assign in self.assigns]))

        # Each assignment needs a different Pin
        self.constraints.append(Distinct([assign.z3_pin for assign in self.assigns]))

        # Each BusFun needs a different bus
        self.constraints.append(Distinct([bus_assign.z3_bus for bus_assign in self.bus_assigns]))

    def solve(self):
        s = Solver()

        s.add(And(self.constraints))

        if not s.check() == sat:
            print('Problem:')
            self.print_problem()
            print('Constraints:')
            for constraint in self.constraints:
                print(constraint)
            raise Exception('unsat')

        model = s.model()

        for assign in self.assigns:
            assign.eval(model)

        for bus_assign in self.bus_assigns:
            bus_assign.eval(model)

    def check_solution(self):
        pins = set()
        funs = set()
        busses = set()

        for assign in self.assigns:
            if assign.fun in funs:
                return 'Fun assigned multiple times'
            else:
                funs.add(assign.fun)

            if assign.pin in pins:
                return 'Pin assigned multiple times'
            else:
                pins.add(assign.pin)

        for bus_assign in self.bus_assigns:
            if bus_assign.bus in busses:
                return 'BusAssign needs unique bus'
            busses.add(bus_assign.bus)

            for assign in bus_assign:
                if not assign.bus == bus_assign.bus:
                    return 'BusAssign Assigns need the same bus'

    def print_problem(self):
        print(self.assigns)

    def print_solution(self):
        for i, assign in enumerate(self.assigns):
            print('pin: %s func: %s assign: %s' %
                  (assign.fun.pin.id, str(assign.fun), str(i)))
