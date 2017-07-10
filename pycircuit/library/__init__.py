from pycircuit.device import *
from pycircuit.library.packages import *



### Passive Devices
## RCL
# Resistor
Device('R', Pin('1', '~'), Pin('2', '~'))

# Capacitor
Device('C', Pin('1', '~'), Pin('2', '~'))

# Electrolytic Capacitor
Device('Cp', Pin('+'), Pin('-'))

# Inductor
Device('L', Pin('1', '~'), Pin('2', '~'))


## Other
# Battery
Device('BAT', Pin('VCC'), Pin('GND'))

# Crystal
Device('XTAL',
       Pin('XTAL_XI', Bus('XTAL', 'XI')),
       Pin('XTAL_XO', Bus('XTAL', 'XO')))

# Button
Device('BTN', Pin('1', '~'), Pin('2', '~'))

# Test Point
Device('TP', Pin('TP'))

# Jumper 2P
Device('J2P', Pin('1', '~'), Pin('2', '~'))

# Jumper 3P
Device('J3P', Pin('1', '~'), Pin('2', '~'), Pin('C'))

# Antenna
Device('ANT', Pin('ANT'))



### Active Devices
# Diode
Device('D', Pin('A'), Pin('K'))

# Bipolar transistor
Device('Q', Pin('B'), Pin('C'), Pin('E'), Pin('SUBSTRATE'))

# Mosfet
Device('M', Pin('G'), Pin('D'), Pin('S'), Pin('SUBSTRATE'))

# Opamp
Device('OP',
       Pin('V+'),
       Pin('V-'),
       Pin('-', Bus('OP', '-')),
       Pin('+', Bus('OP', '+')),
       Pin('OUT', Bus('OP', 'OUT')))

# RGB LED (Common Anode)
Device('RGB_A', Pin('A'), Pin('R'), Pin('G'), Pin('B'))

# RGB LED (Common Kathode)
Device('RGB_K', Pin('R'), Pin('G'), Pin('B'), Pin('K'))
