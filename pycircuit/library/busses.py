from pycircuit.device import *


Bus('OP',
    Fun('+', Fun.INPUT),
    Fun('-', Fun.INPUT),
    Fun('OUT', Fun.OUTPUT))

Bus('PWM',
    Fun('0', Fun.OUTPUT),
    Fun('1', Fun.OUTPUT),
    Fun('2', Fun.OUTPUT),
    Fun('3', Fun.OUTPUT))

Bus('UART',
    Fun('TX', Fun.OUTPUT),
    Fun('RX', Fun.INPUT))

Bus('JTAG:M',
    Fun('TCK', Fun.OUTPUT),
    Fun('TDO', Fun.INPUT),
    Fun('TMS', Fun.OUTPUT),
    Fun('TDI', Fun.OUTPUT))

Bus('JTAG:S',
    Fun('TCK', Fun.INPUT),
    Fun('TDO', Fun.OUTPUT),
    Fun('TMS', Fun.INPUT),
    Fun('TDI', Fun.INPUT))

Bus('I2C:M',
    Fun('SDA', Fun.BIDIR),
    Fun('SCL', Fun.OUTPUT))

Bus('I2C:S',
    Fun('SDA', Fun.BIDIR),
    Fun('SCL', Fun.INPUT))

Bus('SPI:M',
    Fun('SCLK', Fun.OUTPUT),
    Fun('MOSI', Fun.OUTPUT),
    Fun('MISO', Fun.INPUT),
    Fun('SS0', Fun.OUTPUT),
    Fun('SS1', Fun.OUTPUT),
    Fun('SS2', Fun.OUTPUT),
    Fun('SS3', Fun.OUTPUT))

Bus('SPI:S',
    Fun('SCLK', Fun.INPUT),
    Fun('MOSI', Fun.INPUT),
    Fun('MISO', Fun.OUTPUT),
    Fun('SS', Fun.INPUT))

Bus('QSPI:M',
    Fun('DQ3', Fun.BIDIR),
    Fun('DQ2', Fun.BIDIR),
    Fun('DQ1', Fun.BIDIR),
    Fun('DQ0', Fun.BIDIR),
    Fun('SCLK', Fun.OUTPUT),
    Fun('SS0', Fun.OUTPUT),
    Fun('SS1', Fun.OUTPUT),
    Fun('SS2', Fun.OUTPUT),
    Fun('SS3', Fun.OUTPUT))

Bus('QSPI:S',
    Fun('DQ3', Fun.BIDIR),
    Fun('DQ2', Fun.BIDIR),
    Fun('DQ1', Fun.BIDIR),
    Fun('DQ0', Fun.BIDIR),
    Fun('SCLK', Fun.INPUT),
    Fun('SS', Fun.INPUT))

Bus('USB2',
    Fun('D+', Fun.BIDIR),
    Fun('D-', Fun.BIDIR))

Bus('USB3',
    Fun('TX1+', Fun.OUTPUT),
    Fun('TX1-', Fun.OUTPUT),
    Fun('RX1+', Fun.INPUT),
    Fun('RX1-', Fun.INPUT),
    Fun('TX2+', Fun.OUTPUT),
    Fun('TX2-', Fun.OUTPUT),
    Fun('RX2+', Fun.INPUT),
    Fun('RX2-', Fun.INPUT))
