from pycircuit.circuit import Netlist
from pycircuit.formats import *
from pycircuit.pinassign import *


class Compiler(object):
    def __init__(self, circuit):
        self.netlist = circuit.to_netlist()

        for inst in self.netlist.insts:
            # Convert CircuitAssign to Assign
            assigns = {}
            for assign in inst.assigns:
                if not assign.terminal.group in assigns:
                    assigns[assign.terminal.group] = BusAssign()
                assigns[assign.terminal.group].add_assign(Assign(assign.terminal.function, assign))
            problem = AssignmentProblem(inst.component, assigns.values())
            try:
                problem.solve()
                assert problem.check_solution() is None
            except:
                print('Failed to pinassign', str(inst))
                raise

            for bus_assign in assigns.values():
                for assign in bus_assign:
                    assign.meta.terminal.pin = assign.pin

        self.netlist.to_graphviz().render('net.dot')

        # TODO
        # Check that all non optional pins are connected
        # Check that all nets have at least to assignments
        # Check during elaboration that all ports are connected internally
        # Check during elaboration that all ports are connected externally
