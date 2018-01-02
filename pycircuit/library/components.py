from pycircuit.component import *


### Passive Devices
Component('Z', 'Impedance',
          Pin('1', Fun('~'), optional=False),
          Pin('2', Fun('~'), optional=False))

Component('R', 'Resistor',
          Pin('1', Fun('~'), optional=False),
          Pin('2', Fun('~'), optional=False))

Component('C', 'Capacitor',
          Pin('1', BusFun('Ceramic', '~'),
              BusFun('Electrolytic', '+'), optional=False),
          Pin('2', BusFun('Ceramic', '~'),
              BusFun('Electrolytic', '-'), optional=False))

Component('L', 'Inductor',
          Pin('1', Fun('~'), optional=False),
          Pin('2', Fun('~'), optional=False))

Component('V', 'Voltage source',
          PwrOut('+', optional=False),
          PwrOut('-', optional=False))

Component('S', 'Switch',
          Pin('1', Fun('~'), optional=False),
          Pin('2', Fun('~'), optional=False))

Component('XTAL', 'Crystal',
          Pin('1', Fun('~'), optional=False),
          Pin('2', Fun('~'), optional=False))

Component('TP', 'Test point',
          Pin('TP', optional=False))

Component('J2P', 'Jumper 2-pins',
          Pin('1', Fun('~'), optional=False),
          Pin('2', Fun('~'), optional=False))

Component('J3P', 'Jumper 3-pins',
          Pin('1', Fun('~'), optional=False),
          Pin('2', Fun('~'), optional=False),
          Pin('C', optional=False))

Component('ANT', 'Antenna', Pin('ANT', optional=False))

Component('Transformer_1P_1S', 'Transformer with one primary and one secondary winding',
          Pin('L1.1', optional=False),
          Pin('L1.2', optional=False),
          Pin('L2.1', optional=False),
          Pin('L2.2', optional=False))


### Active Devices
Component('D', 'Diode',
          Pin('A', optional=False),
          Pin('C', optional=False))

Component('Q', 'Bipolar transistor',
          Pin('B', optional=False),
          Pin('C', optional=False),
          Pin('E', optional=False),
          Pin('SUBSTRATE'))

Component('M', 'Mosfet',
          Pin('G', optional=False),
          Pin('D', optional=False),
          Pin('S', optional=False),
          Pin('SUBSTRATE'))

Component('OP', 'Opamp',
          PwrIn('V+', optional=False),
          PwrIn('V-', optional=False),
          In('+', optional=False),
          In('-', optional=False),
          Out('OUT', optional=False))

Component('RGB_A', 'RGB LED (Common Anode)',
          PwrIn('A', optional=False),
          In('R', optional=False),
          In('G', optional=False),
          In('B', optional=False))

Component('RGB_C', 'RGB LED (Common Cathode)',
          In('R', optional=False),
          In('G', optional=False),
          In('B', optional=False),
          PwrIn('C', optional=False))

Component('CLK', 'Clock',
          PwrIn('VDD', optional=False),
          PwrIn('GND', optional=False),
          Out('CLK', optional=False))

Component('QSPI:S', 'Quad SPI Slave',
          PwrIn('VDD', optional=False),
          PwrIn('GND', optional=False),
          In('SCLK', optional=False),
          Io('DQ0'),
          Io('DQ1'),
          Io('DQ2'),
          Io('DQ3'),
          In('SS', optional=False))

Component('I2C:S', 'I2C Slave',
          PwrIn('VDD', optional=False),
          PwrIn('GND', optional=False),
          Io('SDA', optional=False),
          In('SCL', optional=False))
