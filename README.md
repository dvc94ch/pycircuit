# Circuit Description Library

Attempts to make designing and building electronics easy and fun by
making design reuse and collaboration simple and making design intent
explicit.

Supports autoplacing and autorouting engines. An example autoplacer
using Z3 is provided, and an example autorouter using monosat.

## Devices

```python
from pycircuit.device import *

Device('MCU', pins=[
       Pin('GND'),
       Pin('VCC'),
       Pin('XTAL_XI', Fun('XTAL', 'XI')),
       Pin('XTAL_XO', Fun('XTAL', 'XO')),
       Pin('JTAG_TCK', Fun('JTAG', 'TCK')),
       Pin('JTAG_TDO', Fun('JTAG', 'TDO')),
       Pin('JTAG_TMS', Fun('JTAG', 'TMS')),
       Pin('JTAG_TDI', Fun('JTAG', 'TDI')),
       Pin('GPIO_1', 'GPIO', Fun('UART1', 'UART', 'TX')),
       Pin('GPIO_2', 'GPIO', Fun('UART1', 'UART', 'RX')),
       Pin('GPIO_3', 'GPIO'),
       Pin('GPIO_4', 'GPIO'),
       Pin('GPIO_5', 'GPIO', Fun('UART2', 'UART', 'TX')),
       Pin('GPIO_6', 'GPIO', Fun('UART2', 'UART', 'RX')),
       Pin('GPIO_7', 'GPIO')
       ])
```

## Packages

```python
from pycircuit.package import *

Package('0805', IPCGrid(4, 8), TwoPads(1.9),
        package_size=(1.4, 2.15), pad_size=(1.5, 1.3))

Package('QFN16', RectCrtyd(5.3, 5.3), QuadPads(16, pitch=0.65, radius=2, thermal_pad=2.5),
        package_size=(5, 5), pad_size=(0.35, 0.8))
```

## Footprints

```python
from pycircuit.footprint import *

Footprint('MCUQFN16', 'MCU', 'QFN16',
          Map(1, 'GPIO_1'),
          Map(2, 'GPIO_2'),
          Map(3, 'GPIO_3'),
          Map(4, 'GPIO_4'),
          Map(5, 'VCC'),
          Map(6, 'GND'),
          Map(7, 'GPIO_5'),
          Map(8, 'GPIO_6'),
          Map(9, 'XTAL_XI'),
          Map(10, 'XTAL_XO'),
          Map(11, 'GPIO_7'),
          Map(12, 'JTAG_TCK'),
          Map(13, 'JTAG_TDO'),
          Map(14, 'JTAG_TMS'),
          Map(15, 'JTAG_TDI'),
          Map(17, 'GND'))
```

## Circuits

```python
from pycircuit.circuit import *

@circuit('LED')
def led():
    Node('Rs', 'R')
    Node('LED', 'D')

    Net('IN') + Ref('Rs')['~']
    Ref('Rs')['~'] + Ref('LED')['A']
    Ref('LED')['K'] + Net('GND')

@circuit('RGB')
def rgb():
    Sub('RED', led())
    Sub('GREEN', led())
    Sub('BLUE', led())

    for net in ['RED', 'GREEN', 'BLUE']:
        Net(net) + Ref(net)['IN']
    Net('GND') + Refs()['GND']

@circuit('TOP')
def top():
    Node('BAT1', 'BAT')
    Node('OSC1', 'XTAL')
    Node('MCU1', 'MCU')
    Sub('RGB1', rgb())

    Net('VCC') + Refs()['VCC']
    Net('GND') + Refs()['GND']
    Ref('MCU1')['XTAL'] + Ref('OSC1')['XTAL']
    Ref('MCU1')['UART']['RX', 'TX'] + Ref('MCU1')['UART']['TX', 'RX']
    Ref('MCU1')['GPIO'] + Ref('RGB1')['RED', 'GREEN', 'BLUE']
```

## Assign footprints

```python
from pycircuit.pcb import *

circuit = top()

# Decoupling schematic capture from layout
# means that we have to manually construct
# NodeAttributes for each node.
for node in circuit.iter_nodes():
    node.attrs = NodeAttributes(node)

# Set footprints
for node in circuit.nodes_by_device('R'):
    node.set_footprint('R0805')

for node in circuit.nodes_by_device('D'):
    node.set_footprint('D0805')

circuit.node_by_name('OSC1').set_footprint('OSC0805')
circuit.node_by_name('BAT1').set_footprint('BAT0805')

mcu1 = circuit.node_by_name('MCU1')
mcu1.set_footprint('MCUQFN16')
```

## Place

```python
i = 0
for node in circuit.iter_nodes():
    if node.footprint.package.name == '0805':
        node.place(i * 5, 0, 90)
        i += 1

mcu1.place(10, 10)
mcu1.flip()

# Show some statistics
bat = circuit.node_by_name('BAT1')
print('MCU1 area:', mcu1.area())
print('BAT1 area:', bat.area())
print('MCU1 intersects itself:', mcu1.intersects(mcu1))
print('MCU1 intersects BAT1:', mcu1.intersects(bat))

for net in circuit.iter_nets():
    print('net', net.name, net.half_perimeter_length())
```

## Route

```python
pcb = Pcb(circuit)
pcb.move_to('BAT1', '1')
dist = pcb.distance('MCU1', '5')
pcb.segment(dy=dist[1])
pcb.via()
pcb.segment_to('MCU1', '5')

# Print some more statistics
print(pcb.net.length())
```

## Export

```python
from pycircuit.export import *

# Export circuit to graph
export_circuit_to_graphviz(circuit)
# Export pcb to svg
export_pcb_to_svg(pcb)

# Convert pcb to kicad
kpcb = pcb_to_kicad(pcb)
# Use pykicad to postprocess the pcb
# Save pcb to file
export_pcb(kpcb)
```

![Graphviz](https://user-images.githubusercontent.com/741807/33948211-a306313a-e026-11e7-86c6-e07ea202af9a.png)
![SVG](https://user-images.githubusercontent.com/741807/33948212-a3320544-e026-11e7-8b61-f16453c99eff.png)
![SVG](https://user-images.githubusercontent.com/741807/33948213-a351320c-e026-11e7-97d2-cac0b53ec065.png)
![KiCad](https://user-images.githubusercontent.com/741807/28041533-23af0726-65ca-11e7-8759-b010181a5372.png)


# License
ISC License

Copyright (c) 2017, David Craven

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE
OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.
