from pycircuit.device import *


### Voltage Regulators
# Step Down Converter 1A
Device('TPS6229x',
       Pin('VIN'),
       Pin('EN'),
       Pin('GND'),
       Pin('MODE'),
       Pin('SW'),
       Pin('FB'))



### Communication Controllers
# USB C port controller
Device('TPS65982', Pin('1'))
