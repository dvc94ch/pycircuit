from pycircuit.device import *
from pycircuit.footprint import *
from pycircuit.circuit import *


Device('TPS6229x', descr='''1A Step-Down Converter''', pins=[
    PwrIn('VIN', descr='''VIN power supply pin.'''),

    In('EN', descr='''This is the enable pin of the device.  Pulling this pin to
    low forces the device into shutdown mode. Pulling this pin to high enables
    the device. This pin must be terminated.'''),

    Pwr('GND', descr='''GND supply pin.'''),

    In('MODE', descr='''High forces the device to operate in fixed-frequency PWM
    mode.  When Low enables the power save mode with automatic transition from
    PFM mode to fixed-frequency PWM mode.'''),

    PwrOut('SW', descr='''This is the switch pin and is connected to the
    internal MOSFET switches.  Connect the external inductor between this
    terminal and the output capacitor.'''),

    In('FB', descr='''Feedback pin for the internal regulation loop.  Connect
    the external resistor divider to this pin.  In case of fixed output voltage
    option, connect this pin directly to the output capacitor.'''),

    Pwr('EP', descr='''Connect the exposed thermal pad to GND.''')
])

#Device('TPS62290', adjustable=True)
#Device('TPS62291', vout=3.3)
#Device('TPS62293', vout=1.8)

Footprint('TPS6229x', 'TPS6229x', 'QFN16',  # 'SON',
          Map(1, 'SW'),
          Map(2, 'MODE'),
          Map(3, 'FB'),
          Map(4, 'EN'),
          Map(5, 'VIN'),
          Map(6, 'GND'),
          Map(7, 'EP'))


@circuit('TPS6229x')
def tps6229x(dev='TPS6229x', en=True, mode=True, fb=False):

    Node('U', dev)

    Net('GND') + Ref('U')['GND', 'EP']
    Net('VIN') + Ref('U')['VIN']

    Node('CIN', 'C', '10uF')
    Nets('VIN', 'GND') + Ref('CIN')['~', '~']

    Node('L', 'L', '2.2mH')
    Net('SW') + Ref('U')['SW'] + Ref('L')['~']
    Net('VOUT') + Ref('L')['~']

    Node('COUT', 'C', '10uF')
    Nets('VOUT', 'GND') + Ref('COUT')['~', '~']

    if en:
        Net('VIN') + Ref('U')['EN']

    if mode:
        Net('GND') + Ref('U')['MODE']

    if fb:
        Node('FB_R1', 'R', fb[0])
        Node('FB_R2', 'R', fb[1])
        Node('FB_C', 'C', '22pF')
        Net('VOUT') + Ref('FB_R1')['~'] + Ref('FB_C')['~']
        Net('FB') + Ref('U')['FB'] + Ref('FB_R1')['~'] + \
            Ref('FB_C')['~'] + Ref('FB_R2')['~']
    else:
        Net('VOUT') + Ref('U')['FB']
