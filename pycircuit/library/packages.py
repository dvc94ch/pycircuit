from pycircuit.package import *



### Basic
for width in range(1, 3):
    for length in range(1, 21):
        t_length, t_width = 2.41 + (length - 1) * 2.54, 2.41
        Package('Pins_%dx%d' % (length, width), RectCrtyd(t_length, t_width),
                GridPads(width, length, pitch=2.54),
                package_size=(t_length, t_width),
                pad_size=(2.41, 2.41), pad_drill=.51, pad_shape='circle')

Package('0805', IPCGrid(4, 8), TwoPads(1.9),
        package_size=(1.4, 2.15), pad_size=(1.5, 1.3))

Package('SOT23', IPCGrid(8, 8), Sot23Pads(2.2, 0.95),
        package_size=(3, 1.4), pad_size=(1, 1.4))


### DIP
Package('DIP8', RectCrtyd(9.7, 12.55), DualPads(8, pitch=2.54, radius=3.81),
        package_size=(7.35, 12.21), pad_size=(1.6, 1.6),
        pad_shape='circle', pad_drill=0.8)


### QFN
Package('QFN16', RectCrtyd(5.3, 5.3), QuadPads(16, pitch=0.65, radius=2, thermal_pad=2.5),
        package_size=(5, 5), pad_size=(0.35, 0.8))

Package('QFN48', RectCrtyd(7.5, 7.5), QuadPads(48, pitch=0.5, radius=3.5, thermal_pad=5.1),
        package_size=(7, 7), pad_size=(0.28, 0.724)) # FIXME: Radius is only approximate!!

Package('QFN64', RectCrtyd(9, 9), QuadPads(64, 0.5, 4.5, thermal_pad=6),
        package_size=(9, 9), pad_size=(0.28, 0.724)) # FIXME: Radius is only approximate!!


### TQFP
Package('TQFP144', RectCrtyd(20, 20), QuadPads(144, pitch=0.5, radius=10)) # FIXME: Radius is only approximate!!


### BGA
Package('PBGA16_8x8', RectCrtyd(8, 8), GridPads(4, 4, pitch=1.5),
        package_size=(8, 8), pad_size=(.6, .6), pad_shape='circle')
