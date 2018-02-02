from pycircuit.circuit import *


@circuit('Pierce oscillator')
def pierce_oscillator(freq, cap, res=False):
    Node('Y', 'XTAL', freq)
    Node('C1', 'C', cap)
    Node('C2', 'C', cap)

    xi = Net('XTAL_XI') + Ref('Y')['~'] + Ref('C1')['~']
    xo = Net('XTAL_XO') + Ref('Y')['~'] + Ref('C2')['~']
    Net('GND') + Ref('C1')['~'] + Ref('C2')['~']

    if res:
        Node('R', 'R', res)
        xi + Ref('R')['~']
        xo + Ref('R')['~']


@circuit('Level shifter')
def level_shifter(r_low=False, r_high='10K'):
    Node('R_HIGH', 'R', r_high)
    Node('Q', 'M')

    vdd_low = Net('VDD_LOW') + Ref('Q')['G']
    low = Net('LOW') + Ref('Q')['S']

    if r_low:
        Node('R_LOW', 'R', r_low)
        vdd_low + Ref('R_LOW')['~']
        low + Ref('R_LOW')['~']

    Net('VDD_HIGH') + Ref('R_HIGH')['~']
    Net('HIGH') + Ref('Q')['D'] + Ref('R_HIGH')['~']


@circuit('Button')
def button(pullup='100K', esd_protection=True):
    Node('BTN', 'BTN')
    Node('PULLUP', 'R', pullup)
    Net('VDD') + Ref('PULLUP')['~']
    inp = Net('IN') + Ref('PULLUP')['~'] + Ref('BTN')['~']
    gnd = Net('GND') + Ref('BTN')['~']

    if esd_protection:
        Node('TVS', 'DD')
        inp + Ref('TVS')['~']
        gnd + Ref('TVS')['~']


@circuit('Decoupling')
def decoupling_capacitors(*args):
    vdd, vss = Net('VDD'), Net('VSS')
    for i, c in enumerate(args):
        name = 'C' + str(i + 1)
        Node(name, 'C', c)
        vdd + Ref(name)['~']
        vss + Ref(name)['~']

#@circuit('Debouncer')
# def debouncer(r1='470', r2='10K', c='10nF', diode=True):
#    Node('R1', 'R', r1)
#    Node('R2', 'R', r2)
#    Node('C', 'C', c)


@circuit('RGB')
def rgb(r='330'):
    Node('RGB', 'RGB_A')

    def led(color):
        Node('R' + color[0], 'R', r)
        Net(color) + Ref('R' + color[0])['~']
        Net() + Ref('R' + color[0])['~'] + Ref('RGB')[color[0]]

    led('RED')
    led('GREEN')
    led('BLUE')
    Net('VDD') + Ref('RGB')['A']
