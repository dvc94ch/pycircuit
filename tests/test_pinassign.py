import unittest
from pycircuit.component import *
from pycircuit.pinassign import *

Component('R', 'Resistor',
          Pin('1', Fun('~')),
          Pin('2', Fun('~'))
)

Component('MCU', 'Microcontroller',
          Pin('VCC'),
          Pin('GPIO0', Fun('GPIO'), BusFun('UART0', 'UART_TX')),
          Pin('GPIO1', Fun('GPIO'), BusFun('UART0', 'UART_RX')),
          Pin('GPIO2', Fun('GPIO'), BusFun('UART1', 'UART_TX')),
          Pin('GPIO3', Fun('GPIO'), BusFun('UART1', 'UART_RX'))
)

Component('3x0806', '2 Resistors and one Capacitor',
          Pin('P1.1', BusFun('P1', '~'), BusFun('P1', '+'), BusFun('P1', '-')),
          Pin('P1.2', BusFun('P1', '~'), BusFun('P1', '+'), BusFun('P1', '-')),
          Pin('P2.1', BusFun('P2', '~'), BusFun('P2', '+'), BusFun('P2', '-')),
          Pin('P2.2', BusFun('P2', '~'), BusFun('P2', '+'), BusFun('P2', '-')),
          Pin('P3.1', BusFun('P3', '~'), BusFun('P3', '+'), BusFun('P3', '-')),
          Pin('P3.2', BusFun('P3', '~'), BusFun('P3', '+'), BusFun('P3', '-')),
)


class PinAssignTests(unittest.TestCase):
    def test_obvious_assign(self):
        component = Component.component_by_name('R')
        problem = AssignmentProblem(component, (
            Z3Assign('~', 0),
            Z3Assign('~', 1),
        ))

        problem.solve()
        problem.print_solution()
        assert problem.check_solution() is None

    def test_simple_assign(self):
        component = Component.component_by_name('MCU')
        problem = AssignmentProblem(component, (
            Z3Assign('GPIO', 0),
            Z3Assign('GPIO', 1),
            Z3Assign('UART_TX', 2),
            Z3Assign('UART_RX', 3),
            Z3Assign('VCC', 4)
        ))

        problem.solve()
        problem.print_solution()
        assert problem.check_solution() is None

    def test_bus_assign(self):
        component = Component.component_by_name('MCU')
        problem = AssignmentProblem(component, (
            Z3Assign('GPIO', 0),
            Z3Assign('GPIO', 1),
            Z3BusAssign(
                Z3Assign('UART_TX', 2),
                Z3Assign('UART_RX', 3)
            ),
            Z3Assign('VCC', 4)
        ))

        problem.solve()
        problem.print_solution()
        assert problem.check_solution() is None

    def test_multiple_bus_assign(self):
        component = Component.component_by_name('3x0806')
        problem = AssignmentProblem(component, (
            Z3BusAssign(
                Z3Assign('~', 0),
                Z3Assign('~', 1)
            ),
            Z3BusAssign(
                Z3Assign('~', 2),
                Z3Assign('~', 3)
            ),
            Z3BusAssign(
                Z3Assign('+', 4),
                Z3Assign('-', 5)
            )
        ))

        problem.solve()
        problem.print_solution()
        assert problem.check_solution() is None
