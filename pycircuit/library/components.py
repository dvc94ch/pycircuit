from pycircuit.component import *


### Passive Devices
Component('Z', 'Impedance',
          Pin('A', Fun('~'), optional=False),
          Pin('B', Fun('~'), optional=False))

Component('R', 'Resistor',
          Pin('A', Fun('~'), optional=False),
          Pin('B', Fun('~'), optional=False))

Component('C', 'Capacitor',
          Pin('A', BusFun('Ceramic', '~'),
              BusFun('Electrolytic', '+'), optional=False),
          Pin('B', BusFun('Ceramic', '~'),
              BusFun('Electrolytic', '-'), optional=False))

Component('L', 'Inductor',
          Pin('A', Fun('~'), optional=False),
          Pin('B', Fun('~'), optional=False))

Component('V', 'Voltage source',
          Out('+', optional=False),
          In('-', optional=False))

Component('S', 'Switch',
          Pin('A', Fun('~'), optional=False),
          Pin('B', Fun('~'), optional=False))

Component('XTAL', 'Crystal',
          Pin('A', Fun('~'), optional=False),
          Pin('B', Fun('~'), optional=False))

Component('TP', 'Test point',
          Pin('TP', optional=False))

Component('J2P', 'Jumper 2-pins',
          Pin('A', Fun('~'), optional=False),
          Pin('B', Fun('~'), optional=False))

Component('J3P', 'Jumper 3-pins',
          Pin('A', Fun('~'), optional=False),
          Pin('B', Fun('~'), optional=False),
          Pin('C', optional=False))

Component('ANT', 'Antenna', Pin('ANT', optional=False))

Component('Transformer_1P_1S', 'Transformer with one primary and one secondary winding',
          Pin('L1.1', optional=False),
          Pin('L1.2', optional=False),
          Pin('L2.1', optional=False),
          Pin('L2.2', optional=False))


### Active Devices
Component('D', 'Diode',
          In('+', optional=False),
          Out('-', optional=False))

Component('Q', 'Bipolar transistor',
          In('B', optional=False),
          In('C', optional=False),
          Out('E', optional=False),
          Out('SUBSTRATE'))

Component('M', 'Mosfet',
          In('G', optional=False),
          In('D', optional=False),
          Out('S', optional=False),
          Out('SUBSTRATE'))

Component('OP', 'Opamp',
          Pwr('VCC', optional=False),
          Pwr('VEE', optional=False),
          In('+', optional=False),
          In('-', optional=False),
          Out('OUT', optional=False))

Component('RGB_A', 'RGB LED (Common Anode)',
          In('+', optional=False),
          Out('R', optional=False),
          Out('G', optional=False),
          Out('B', optional=False))

Component('RGB_C', 'RGB LED (Common Cathode)',
          In('R', optional=False),
          In('G', optional=False),
          In('B', optional=False),
          Out('-', optional=False))

Component('CLK', 'Clock',
          Pwr('VDD', optional=False),
          Gnd('GND', optional=False),
          Out('CLK', optional=False))

Component('QSPI:S', 'Quad SPI Slave',
          Pwr('VDD', optional=False),
          Gnd('GND', optional=False),
          In('SCLK', optional=False),
          Io('DQ0'),
          Io('DQ1'),
          Io('DQ2'),
          Io('DQ3'),
          In('SS', optional=False))

Component('I2C:S', 'I2C Slave',
          Pwr('VDD', optional=False),
          Gnd('GND', optional=False),
          Io('SDA', optional=False),
          In('SCL', optional=False))
