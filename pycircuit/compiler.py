from pycircuit.circuit import Netlist
from pycircuit.formats import *
from pycircuit.pinassign import *


class Compiler(object):
    def __init__(self, circuit):
        self.netlist = circuit.to_netlist()

        for inst in self.netlist.insts:
            # Convert CircuitAssign to Assign
            assigns = []
            for assign in inst.assigns:
                assigns.append(Assign(assign.terminal.function, assign))
            problem = AssignmentProblem(inst.component, assigns)
            try:
                problem.solve()
                assert problem.check_solution() is None
            except:
                print('Failed to pinassign', str(inst))
                raise

            for assign in assigns:
                assign.meta.terminal.pin = assign.pin

        self.netlist.to_graphviz().render('net.dot')

        # TODO
        # Check that all non optional pins are connected
        # Check that all nets have at least to assignments
        # Check during elaboration that all ports are connected internally
        # Check during elaboration that all ports are connected externally
