from pycircuit.device import *
from pycircuit.footprint import *


### FE310
Device('FE310-G000',
       # Power
       Pin('GND'),
       Pin('VDD'), # 1V8
       Pin('IVDD'), # 3V3
       Pin('AON_VDD'), # 1V8
       Pin('AON_IVDD'), # 1V8
       Pin('PLL_AVDD'), # 1V8
       Pin('PLL_AVSS'),
       Pin('OTP_AIVDD'), # 3V3
       # Clock
       Pin('XTAL_XI', Bus('XTAL', 'XI')), # 16MHz
       Pin('XTAL_XO', Bus('XTAL', 'XO')),
       # JTAG
       Pin('JTAG_TCK', Bus('JTAG', 'TCK')),
       Pin('JTAG_TDO', Bus('JTAG', 'TDO')),
       Pin('JTAG_TMS', Bus('JTAG', 'TMS')),
       Pin('JTAG_TDI', Bus('JTAG', 'TDI')),
       # QSPI
       Pin('QSPI_DQ_3', Bus('QSPI', 'DQ_3')),
       Pin('QSPI_DQ_2', Bus('QSPI', 'DQ_2')),
       Pin('QSPI_DQ_1', Bus('QSPI', 'DQ_1')),
       Pin('QSPI_DQ_0', Bus('QSPI', 'DQ_0')),
       Pin('QSPI_CS', Bus('QSPI', 'CS')),
       Pin('QSPI_SCK', Bus('QSPI', 'SCK')),
       # GPIO
       Pin('GPIO_0', 'GPIO', Bus('PWM0', 'PWM', '0')),
       Pin('GPIO_1', 'GPIO', Bus('PWM0', 'PWM', '1')),
       Pin('GPIO_2', 'GPIO', Bus('PWM0', 'PWM', '2'),
           Bus('SPI1', 'SPI', 'SS0')),
       Pin('GPIO_3', 'GPIO', Bus('PWM0', 'PWM', '3'),
           Bus('SPI1', 'SPI', 'MOSI')),
       Pin('GPIO_4', 'GPIO', Bus('SPI1', 'SPI', 'MISO')),
       Pin('GPIO_5', 'GPIO', Bus('SPI1', 'SPI', 'SCK')),
       Pin('GPIO_9', 'GPIO', Bus('SPI1', 'SPI', 'SS1')),
       Pin('GPIO_10', 'GPIO', Bus('PWM2', 'PWM', '0'),
           Bus('SPI1', 'SPI', 'SS2')),
       Pin('GPIO_11', 'GPIO', Bus('PWM2', 'PWM', '1')),
       Pin('GPIO_12', 'GPIO', Bus('PWM2', 'PWM', '2')),
       Pin('GPIO_13', 'GPIO', Bus('PWM2', 'PWM', '3')),
       Pin('GPIO_16', 'GPIO', Bus('UART0', 'UART', 'RX')),
       Pin('GPIO_17', 'GPIO', Bus('UART0', 'UART', 'TX')),
       Pin('GPIO_18', 'GPIO'),
       Pin('GPIO_19', 'GPIO', Bus('PWM1', 'PWM', '1')),
       Pin('GPIO_20', 'GPIO', Bus('PWM1', 'PWM', '0')),
       Pin('GPIO_21', 'GPIO', Bus('PWM1', 'PWM', '2')),
       Pin('GPIO_22', 'GPIO', Bus('PWM1', 'PWM', '3')),
       Pin('GPIO_23', 'GPIO'),
       # AON
       Pin('AON_PMU_OUT_1'),
       Pin('AON_PMU_OUT_0'),
       Pin('AON_PMU_DWAKEUP_N'),
       Pin('AON_ERST_N'),
       Pin('AON_PSD_LFALTCLK'),
       Pin('AON_PSD_LFCLKSEL'))


Footprint('FE310-G000', 'FE310-G000', 'QFN48',
          Map(1, 'QSPI_DQ_3'),
          Map(2, 'QSPI_DQ_2'),
          Map(3, 'QSPI_DQ_1'),
          Map(4, 'QSPI_DQ_0'),
          Map(5, 'QSPI_CS'),
          Map(6, 'VDD'),
          Map(7, 'PLL_AVDD'),
          Map(8, 'PLL_AVSS'),
          Map(9, 'XTAL_XI'),
          Map(10, 'XTAL_XO'),
          Map(11, 'IVDD'),
          Map(12, 'OTP_AIVDD'),
          Map(13, 'JTAG_TCK'),
          Map(14, 'JTAG_TDO'),
          Map(15, 'JTAG_TMS'),
          Map(16, 'JTAG_TDI'),
          Map(17, 'AON_PMU_OUT_1'),
          Map(18, 'AON_PMU_OUT_0'),
          Map(19, 'AON_IVDD'),
          Map(20, 'AON_PSD_LFALTCLK'),
          Map(21, 'AON_PSD_LFCLKSEL'),
          Map(22, 'AON_PMU_DWAKEUP_N'),
          Map(23, 'AON_VDD'),
          Map(24, 'AON_ERST_N'),
          Map(25, 'GPIO_0'),
          Map(26, 'GPIO_1'),
          Map(27, 'GPIO_2'),
          Map(28, 'GPIO_3'),
          Map(29, 'GPIO_4'),
          Map(30, 'VDD'),
          Map(31, 'GPIO_5'),
          Map(32, 'IVDD'),
          Map(33, 'GPIO_9'),
          Map(34, 'GPIO_10'),
          Map(35, 'GPIO_11'),
          Map(36, 'GPIO_12'),
          Map(37, 'GPIO_13'),
          Map(38, 'GPIO_16'),
          Map(39, 'GPIO_17'),
          Map(40, 'GPIO_18'),
          Map(41, 'GPIO_19'),
          Map(42, 'GPIO_20'),
          Map(43, 'GPIO_21'),
          Map(44, 'GPIO_22'),
          Map(45, 'GPIO_23'),
          Map(46, 'VDD'),
          Map(47, 'IVDD'),
          Map(48, 'QSPI_SCK'),
          Map(49, 'GND'))
