from pycircuit.device import *
from pycircuit.footprint import *
from pycircuit.circuit import *


Device('TPS6213x', descr='''3V to 17V, 3A Step-Down Converter''', pins=[
    PwrOut('SW', descr='''Switch node, which is connected to the internal
    MOSFET switches.  Connect inductor between SW and output capacitor.'''),

    Out('PG', descr='''Output power good (High = Vout ready, Low = Vout below
    nominal regulation) ; open drain (requires pull-up resistor).'''),

    Pwr('AGND', descr='''Analog Ground.  Must be connected directly to the
    Exposed Thermal Pad and common ground plane.'''),

    In('FB', descr='''Voltage feedback of adjustable version.  Connect
    resistive voltage divider to this pin.  It is recommended to connect FB
    to AGND on fixed output voltage versions for improved thermal
    performance.'''),

    In('FSW', descr='''Switching Frequency Slect (Low ~2.5MHz, High ~1.25MHz
    [0] for typical operation) [0] Connect FSW to Vout or PG in this case.'''),

    In('DEF', descr='''Output Voltage Scaling (Low = nominal,
    High = nominal +5%)'''),

    In('SS/TR', descr='''Soft-Start / Tracking Pin.  An external capacitor
    connected to this pin sets the internal voltage reference rise time.  It
    can be used for tracking and sequencing.'''),

    PwrIn('AVIN', descr='''Supply voltage for control circuitry.  Connect to
    same source as PVIN.'''),

    PwrIn('PVIN', descr='''Supply voltage for power stage.  Connect to same
    source as AVIN.'''),

    In('EN', descr='''Enable input (High = enabled, Low = disabled)'''),

    In('VOS', descr='''Output voltage sense pin and connection for the
    control loop circuitry.'''),

    Pwr('PGND', descr='''Power Ground.  Must be connected directly to the
    Exposed Thermal Pad and common ground plane.'''),

    Pwr('EP', descr='''Must be connected to AGND, PGND and common ground
    plane.  Must be soldered to achieve appropriate power dissipation and
    mechanical reliablility.''')
])


#Device('TPS62130', 'TPS62130x', adjustable=True)
# Device('TPS62130A', 'TPS62130x', adjustable=True) # Power Good logic level low
#Device('TPS62131', 'TPS62130x', vout=1.8, adjustable=False)
#Device('TPS62132', 'TPS62130x', vout=3.3, adjustable=False)
#Device('TPS62133', 'TPS62130x', vout=5, adjustable=False)


Footprint('TPS6213x', 'TPS6213x', 'QFN16',  # VQFN16
          Map(1, 'SW'),
          Map(2, 'SW'),
          Map(3, 'SW'),
          Map(4, 'PG'),
          Map(5, 'FB'),
          Map(6, 'AGND'),
          Map(7, 'FSW'),
          Map(8, 'DEF'),
          Map(9, 'SS/TR'),
          Map(10, 'AVIN'),
          Map(11, 'PVIN'),
          Map(12, 'PVIN'),
          Map(13, 'EN'),
          Map(14, 'VOS'),
          Map(15, 'PGND'),
          Map(16, 'PGND'),
          Map(17, 'EP'))


@circuit('TPS6213x')
def tps6213x(dev='TPS6213x', en=True, pg=False, fb=False):
    '''Returns a circuit for a TPS6213x Voltage Regulator.

    Keyword arguments:
    dev -- Device name
    en -- Connects EN to VIN when True (default True)
    pg -- Adds a pullup to PG or connects to GND when unused (default False)
    fb -- Feedback resistive voltage divider takes a tuple of resistor
          values (default False)
    '''

    Node('U', dev)

    # Input circuitry.
    # PVIN and AVIN must be connected to same source
    Net('VIN') + Ref('U')['PVIN', 'AVIN']
    # AGND, PGND and EP must be connected
    Net('GND') + Ref('U')['AGND', 'PGND', 'EP']

    # Input decoupling capacitors
    Node('CIN1', 'C', '10uF')
    Node('CIN2', 'C', '0.1uF')
    Net('VIN') + Ref('CIN1')['~'] + Ref('CIN2')['~']
    Net('GND') + Ref('CIN1')['~'] + Ref('CIN2')['~']

    # Output circuitry.
    # Recommended inductor values are 1/2.2uH.
    Node('L', 'L', '2.2uH')
    Net('SW') + Ref('U')['SW'] + Ref('L')['~']
    Net('VOUT') + Ref('L')['~'] + Ref('U')['VOS']

    # Output decoupling capacitor.
    Node('COUT', 'C', '22uF')
    Nets('VOUT', 'GND') + Ref('COUT')['~', '~']

    # Feedback voltage divider
    if fb:
        Node('FB_R1', 'R', fb[0])
        Node('FB_R2', 'R', fb[1])
        Net('VOUT') + Ref('FB_R1')['~']
        Net('FB') + Ref('FB_R1')['~'] + Ref('U')['FB'] + Ref('FB_R2')['~']
        Net('GND') + Ref('FB_R2')['~']
    else:
        # Connect FB to GND for fixed output voltage regulators.
        Net('GND') + Ref('U')['FB']

    # Misc configuration pins
    # EN pin
    if en:
        # Connect EN to VIN to enable device when power
        # is applied
        Net('VIN') + Ref('U')['EN']

    # Power good pin
    if pg:
        # PG requires a pullup when used
        Node('PG_PULLUP', 'R', '100K')
        Net('PG') + Ref('U')['PG'] + Ref('PG_PULLUP')['~']
        Net('VOUT') + Ref('PG_PULLUP')['~']
    else:
        # PG should be connected to GND when unused
        Net('GND') + Ref('U')['PG']

    # DEF and FSW pins are connected to GND by default
    Net('GND') + Ref('U')['DEF', 'FSW']

    # SS/TR controls the startup time after EN goes high
    Node('C_START', 'C', '3.3nF')
    Net('SS/TR') + Ref('C_START')['~'] + Ref('U')['SS/TR']
    Net('GND') + Ref('C_START')['~']
