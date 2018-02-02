from pycircuit.device import *
from pycircuit.footprint import *
from pycircuit.circuit import *
from pycircuit.library import *


Device('FE310-G000', pins=[
    Pwr('GND', descr='0V Ground input'),
    PwrIn('VDD', descr='+1.8V Core voltage supply input'),
    PwrIn('IVDD', descr='+3.3V I/O voltage supply input'),
    PwrIn('AON_VDD', descr='+1.8V Always-On core voltage supply input'),
    PwrIn('AON_IVDD', descr='+1.8V Always-On I/O voltage supply input'),
    PwrIn('PLL_AVDD', descr='+1.8V PLL Supply input'),
    Pwr('PLL_AVSS', descr='''PLL VSS input.  Connect through a capacitor to
    PLL_AVDD, not to GND'''),
    PwrIn('OTP_AIVDD', descr='+3.3V OTP Supply Input'),

    Pin('XTAL_XI', descr='16MHz Crystal Oscillator Input'),
    Pin('XTAL_XO', descr='16MHz Crystal Oscillator Output'),

    Pin('JTAG_TCK', Fun('JTAG:S', 'TCK')),
    Pin('JTAG_TDO', Fun('JTAG:S', 'TDO')),
    Pin('JTAG_TMS', Fun('JTAG:S', 'TMS')),
    Pin('JTAG_TDI', Fun('JTAG:S', 'TDI')),

    Pin('QSPI_DQ_3', Fun('QSPI:M', 'DQ3')),
    Pin('QSPI_DQ_2', Fun('QSPI:M', 'DQ2')),
    Pin('QSPI_DQ_1', Fun('QSPI:M', 'DQ1')),
    Pin('QSPI_DQ_0', Fun('QSPI:M', 'DQ0')),
    Pin('QSPI_CS', Fun('QSPI:M', 'SS0')),
    Pin('QSPI_SCK', Fun('QSPI:M', 'SCLK')),

    Pin('GPIO_0', 'GPIO', Fun('PWM0', 'PWM', '0')),
    Pin('GPIO_1', 'GPIO', Fun('PWM0', 'PWM', '1')),
    Pin('GPIO_2', 'GPIO', Fun('PWM0', 'PWM', '2'), Fun('SPI1', 'SPI:M', 'SS0')),
    Pin('GPIO_3', 'GPIO', Fun('PWM0', 'PWM', '3'), Fun('SPI1', 'SPI:M', 'MOSI')),
    Pin('GPIO_4', 'GPIO', Fun('SPI1', 'SPI:M', 'MISO')),
    Pin('GPIO_5', 'GPIO', Fun('SPI1', 'SPI:M', 'SCLK')),
    Pin('GPIO_9', 'GPIO', Fun('SPI1', 'SPI:M', 'SS1')),
    Pin('GPIO_10', 'GPIO', Fun('PWM2', 'PWM', '0'), Fun('SPI1', 'SPI:M', 'SS2')),
    Pin('GPIO_11', 'GPIO', Fun('PWM2', 'PWM', '1')),
    Pin('GPIO_12', 'GPIO', Fun('PWM2', 'PWM', '2')),
    Pin('GPIO_13', 'GPIO', Fun('PWM2', 'PWM', '3')),
    Pin('GPIO_16', 'GPIO', Fun('UART0', 'UART', 'RX')),
    Pin('GPIO_17', 'GPIO', Fun('UART0', 'UART', 'TX')),
    Pin('GPIO_18', 'GPIO'),
    Pin('GPIO_19', 'GPIO', Fun('PWM1', 'PWM', '1')),
    Pin('GPIO_20', 'GPIO', Fun('PWM1', 'PWM', '0')),
    Pin('GPIO_21', 'GPIO', Fun('PWM1', 'PWM', '2')),
    Pin('GPIO_22', 'GPIO', Fun('PWM1', 'PWM', '3')),
    Pin('GPIO_23', 'GPIO'),

    Out('AON_PMU_OUT_1',  # domain='aon',
        descr='Programmable SLEEP control'),

    Out('AON_PMU_OUT_0',  # domain='aon'
        descr='Programmable SLEEP control'),

    In('AON_PMU_DWAKEUP_N',  # domain='aon',
       descr='Digital Wake-from-sleep.  Active low.'),

    In('AON_ERST_N',  # domain='aon',
       descr='External System Reset.  Active low.'),

    In('AON_PSD_LFALTCLK',  # domain='aon',
       descr='Optional 32kHz Clock input'),

    In('AON_PSD_LFCLKSEL',  # domain='aon',
       descr='''32kHz clock source selector.  When
       driven low, AON_PSD_LFALTCLK input is used as the 32kHz low-frequency
       clock source.  When left unconnected or driven high, the internal LFROSC
       source is used.''')
])


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


@circuit('AON-BTN')
def aon_btn(name, debounce=False):
    Sub(name + '_BTN', button())
    Node(name + '_D', 'D')
    Node(name + '_R', 'R', '100K')

    Net('VDD_1V8') + Ref(name + '_R')['~']
    Net('IN') + Ref(name + '_D')['A'] + Ref(name + '_R')['~']
    Net(name) + Ref(name + '_D')['K'] + Ref(name + '_BTN')['IN']
    Net('VDD_3V3') + Ref(name + '_BTN')['VDD']
    Net('GND') + Ref(name + '_BTN')['GND']

    if debounce:
        Node(name + '_C', 'C', '10nF')
        # Shorts RESET_R on power glitch to instantaneously
        # discharge RESET_C
        Node(name + '_C_D', 'D')
        Net('VDD_1V8') + Ref(name + '_C_D')['K']
        Net('IN') + Ref(name + '_C')['~'] + Ref(name + '_C_D')['A']
        Net('GND') + Ref(name + '_C')['~']


@circuit('FE310-G000')
def fe310g000(qspi_flash=True, lfaltclk=True):
    '''Returns a circuit for a FE310-G000 Microcontroller.'''

    Node('U', 'FE310-G000')

    Net('VDD_1V8') + Ref('U')['VDD', 'AON_VDD', 'AON_IVDD']
    Net('VDD_3V3') + Ref('U')['IVDD', 'OTP_AIVDD']
    Net('GND') + Ref('U')['GND']

    # VDD decoupling caps
    Sub('VDD_C', decoupling_capacitors('10uF', '0.1uF', '0.1uF'))
    Net('VDD_1V8') + Ref('VDD_C')['VDD']
    Net('GND') + Ref('VDD_C')['VSS']

    # AON VDD decoupling caps
    Sub('AON_C', decoupling_capacitors('0.1uF'))
    Net('VDD_1V8') + Ref('AON_C')['VDD']
    Net('GND') + Ref('AON_C')['VSS']

    # IVDD decoupling caps
    Sub('IVDD_C', decoupling_capacitors('0.1uF', '0.1uF', '0.1uF'))
    Net('VDD_3V3') + Ref('IVDD_C')['VDD']
    Net('GND') + Ref('IVDD_C')['VSS']

    # PLL_AVDD decoupling caps
    Sub('PLL_C', decoupling_capacitors('0.1uF', '0.1uF'))
    Net('PLL_AVDD') + Ref('U')['PLL_AVDD'] + Ref('PLL_C')['VDD']
    Net('PLL_AVSS') + Ref('U')['PLL_AVSS'] + Ref('PLL_C')['VSS']

    # PLL_AVDD
    Node('PLL_R', 'R', '100')
    Net('VDD_1V8') + Ref('PLL_R')['~']
    Net('PLL_AVDD') + Ref('PLL_R')['~']

    # Crystal oscillator
    Sub('XTAL', pierce_oscillator('16MHz', '12pF'))
    Nets('XTAL_XI', 'XTAL_XO') + Ref('U')['XTAL_XI', 'XTAL_XO'] + \
        Ref('XTAL')['XTAL_XI', 'XTAL_XO']
    Net('GND') + Ref('XTAL')['GND']

    if qspi_flash:
        Node('FLASH', 'QSPI:S')
        Sub('FLASH_C', decoupling_capacitors('0.1uF'))
        Node('SS_PULLUP', 'R', '100K')

        for net in ['DQ0', 'DQ1', 'DQ2', 'DQ3', 'SCLK']:
            Net(net) + Ref('U')['QSPI:M'][net] + Ref('FLASH')['QSPI:S'][net]
        Net('SS') + Ref('U')['QSPI:M']['SS0'] + Ref('FLASH')['QSPI:S']['SS']

        Net('VDD_3V3') + Ref('SS_PULLUP')['~']
        Ref('SS_PULLUP')['~'] + Ref('FLASH')['SS']
        Net('VDD_3V3') + Refs('FLASH', 'FLASH_C')['VDD']
        Net('GND') + Ref('FLASH')['GND'] + Ref('FLASH_C')['VSS']

    if lfaltclk:
        Node('LFALTCLK', 'CLK')
        Sub('LFALTCLK_C', decoupling_capacitors('0.1uF'))
        Net() + Ref('U')['AON_PSD_LFALTCLK'] + Ref('LFALTCLK')['CLK']
        Net('VDD_1V8') + Refs('LFALTCLK', 'LFALTCLK_C')['VDD']
        Net('GND') + Ref('LFALTCLK')['GND'] + Ref('LFALTCLK_C')['VSS']

    # Reset and Wake BTN
    Sub('RESET_BLK', aon_btn('RESET', debounce=True))
    Net('AON_ERST_N') + Ref('U')['AON_ERST_N'] + Ref('RESET_BLK')['IN']

    Sub('WAKE_BLK', aon_btn('WAKE'))
    Net('AON_PMU_DWAKEUP_N') + \
        Ref('U')['AON_PMU_DWAKEUP_N'] + Ref('WAKE_BLK')['IN']

    Net('VDD_3V3') + Refs('RESET_BLK', 'WAKE_BLK')['VDD_3V3']
    Net('VDD_1V8') + Refs('RESET_BLK', 'WAKE_BLK')['VDD_1V8']
    Net('GND') + Refs('RESET_BLK', 'WAKE_BLK')['GND']

    # PMU
    Net('PMU_OUT_0') + Ref('U')['AON_PMU_OUT_0']
    Net('PMU_OUT_1') + Ref('U')['AON_PMU_OUT_1']
