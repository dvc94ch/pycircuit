from pycircuit.device import *



### Connectors
## Power Connectors
# DC Connector
Device('DCCONN', Pin('V'), Pin('GND'))


## Data Connectors
# USB Connector
Device('USBCONN',
       Pin('GND'),
       Pin('VBUS'),
       Pin('D+', Bus('USB', 'D+')),
       Pin('D-', Bus('USB', 'D-')))

# USB-C Connector
Device('USBCCONN',
       Pin('GND'),
       Pin('VBUS'),
       Pin('TX1+', Bus('USB3', 'TX1+')),
       Pin('TX1-', Bus('USB3', 'TX1-')),
       Pin('RX1+', Bus('USB3', 'RX1+')),
       Pin('RX1-', Bus('USB3', 'RX1-')),
       Pin('TX2+', Bus('USB3', 'TX2+')),
       Pin('TX2-', Bus('USB3', 'TX2-')),
       Pin('RX2+', Bus('USB3', 'RX2+')),
       Pin('RX2-', Bus('USB3', 'RX2-')),
       Pin('D+', Bus('USB', 'D+')),
       Pin('D-', Bus('USB', 'D-')),
       Pin('CC1', Bus('CC', 'CC1')),
       Pin('CC2', Bus('CC', 'CC2')),
       Pin('SBU1', Bus('SBU', 'SBU1')),
       Pin('SBU2', Bus('SBU', 'SBU2')))
