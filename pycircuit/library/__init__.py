from pycircuit.device import *
from pycircuit.library.busses import *
from pycircuit.library.packages import *
from pycircuit.library.circuits import *


### Passive Devices
## RCL
# Resistor
Device('R', pins=[
    Pin('1', '~'),
    Pin('2', '~')
])

# Capacitor
Device('C', pins=[
    Pin('1', '~'),
    Pin('2', '~')
])

# Electrolytic Capacitor
Device('Cp', pins=[
    Pin('+'),
    Pin('-')
])

# Inductor
Device('L', pins=[
    Pin('1', '~'),
    Pin('2', '~')
])

## Other
# Battery
Device('BAT', pins=[
    Pin('VCC'),
    Pin('GND')
])

# Crystal
Device('XTAL', pins=[
    Pin('1', '~'),
    Pin('2', '~')
])

# Button
Device('BTN', pins=[
    Pin('1', '~'),
    Pin('2', '~')
])

# Test Point
Device('TP', pins=[
    Pin('TP')
])

# Jumper 2P
Device('J2P', pins=[
    Pin('1', '~'),
    Pin('2', '~')
])

# Jumper 3P
Device('J3P', pins=[
    Pin('1', '~'),
    Pin('2', '~'),
    Pin('C')
])

# Antenna
Device('ANT', pins=[
    Pin('ANT')
])



### Active Devices
# Diode
Device('D', pins=[
    Pin('A'),
    Pin('K')
])

# Bidirectional Diode
Device('DD', pins=[
    Pin('1', '~'),
    Pin('2', '~')
])

# Bipolar transistor
Device('Q', pins=[
    Pin('B'),
    Pin('C'),
    Pin('E'),
    Pin('SUBSTRATE')
])

# Mosfet
Device('M', pins=[
    Pin('G'),
    Pin('D'),
    Pin('S'),
    Pin('SUBSTRATE')
])

# Opamp
Device('OP', pins=[
    PwrIn('V+'),
    PwrIn('V-'),
    Pin('DN', Fun('OP', '-')),
    Pin('DP', Fun('OP', '+')),
    Pin('OUT', Fun('OP', 'OUT'))
])

Device('QOP', pins=[
    PwrIn('V+'),
    PwrIn('V-'),
    Pin('DN1', Fun('OP', '-')),
    Pin('DP1', Fun('OP', '+')),
    Pin('OUT1', Fun('OP', 'OUT')),
    Pin('DN2', Fun('OP', '-')),
    Pin('DP2', Fun('OP', '+')),
    Pin('OUT2', Fun('OP', 'OUT')),
    Pin('DN3', Fun('OP', '-')),
    Pin('DP3', Fun('OP', '+')),
    Pin('OUT3', Fun('OP', 'OUT')),
    Pin('DN4', Fun('OP', '-')),
    Pin('DP4', Fun('OP', '+')),
    Pin('OUT4', Fun('OP', 'OUT'))
])

# RGB LED (Common Anode)
Device('RGB_A', pins=[
    Pin('A'),
    Pin('R'),
    Pin('G'),
    Pin('B')
])

# RGB LED (Common Kathode)
Device('RGB_K', pins=[
    Pin('R'),
    Pin('G'),
    Pin('B'),
    Pin('K')
])

Device('CLK', pins=[
    PwrIn('VDD'),
    Pwr('GND'),
    Out('CLK')
])

Device('QSPI:S', pins=[
    PwrIn('VDD'),
    Pwr('GND'),
    Pin('SCLK', Fun('QSPI:S', 'SCLK')),
    Pin('DQ0', Fun('QSPI:S', 'DQ0')),
    Pin('DQ1', Fun('QSPI:S', 'DQ1')),
    Pin('DQ2', Fun('QSPI:S', 'DQ2')),
    Pin('DQ3', Fun('QSPI:S', 'DQ3')),
    Pin('SS', Fun('QSPI:S', 'SS'))
])

Device('I2C:S', pins=[
    PwrIn('VDD'),
    Pwr('GND'),
    Pin('SDA', Fun('I2C:S', 'SDA')),
    Pin('SCL', Fun('I2C:S', 'SCL'))
])
