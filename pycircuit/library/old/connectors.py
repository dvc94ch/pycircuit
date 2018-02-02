from pycircuit.device import *


# Connectors
# Power Connectors
# DC Connector
Device('DCCONN', pins=[
    Pwr('GND'),
    PwrOut('V')
])


# Data Connectors
# USB Connector
Device('USBCONN', pins=[
    Pwr('GND'),
    PwrOut('VBUS'),
    Pin('D+', Fun('USB2', 'D+')),
    Pin('D-', Fun('USB2', 'D-'))
])

# USB-C Connector
Device('USBCCONN', pins=[
    Pwr('GND'),
    PwrOut('VBUS'),
    Pin('TX1+', Fun('USB3', 'TX1+')),
    Pin('TX1-', Fun('USB3', 'TX1-')),
    Pin('RX1+', Fun('USB3', 'RX1+')),
    Pin('RX1-', Fun('USB3', 'RX1-')),
    Pin('TX2+', Fun('USB3', 'TX2+')),
    Pin('TX2-', Fun('USB3', 'TX2-')),
    Pin('RX2+', Fun('USB3', 'RX2+')),
    Pin('RX2-', Fun('USB3', 'RX2-')),
    Pin('D+', Fun('USB2', 'D+')),
    Pin('D-', Fun('USB2', 'D-')),
    Pin('CC1'),
    Pin('CC2'),
    Pin('SBU1'),
    Pin('SBU2')
])
