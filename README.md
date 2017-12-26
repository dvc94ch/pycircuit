# Circuit Description Library

## Getting started

`joule_thief.py`
```python
from pycircuit.circuit import *
from pycircuit.library import *


Device('BAT0805', 'BAT', '0805',
       Map('1', '+'),
       Map('2', '-'))

Package('TDK ACT45B', RectCrtyd(5.9, 3.4), DualPads(4, 2.5, radius=2.275),
        package_size=(5.9, 3.4), pad_size=(0.9, 1.35))

Device('TDK ACT45B', 'Transformer_1P_1S', 'TDK ACT45B',
       Map('1', 'L1.1'), Map('2', 'L2.1'), Map('3', 'L2.2'), Map('4', 'L1.2'))


@circuit('TOP')
def top():
    vcc, gnd, n1, n2, n3 = nets('VCC GND n1 n2 n3')

    with Inst('TR1', 'Transformer_1P_1S') as tr1:
        tr1['L1', 'L1'] = n1, n2
        tr1['L2', 'L2'] = vcc, n3

    Inst('BAT1', 'BAT')['+', '-'] = vcc, gnd
    Inst('R1', 'R', '10k 0805')['~', '~'] = vcc, n1
    Inst('Q1', 'Q', 'npn sot23')['B', 'C', 'E'] = n2, n3, gnd
    Inst('LED1', 'D', 'led red 0805')['A', 'C'] = n3, gnd
```

`build.py`
```python
import joule_thief
from pycircuit.build import Builder
from pycircuit.compiler import Compiler
from pycircuit.library.design_rules import oshpark_4layer
from placer import Placer
from router import Router
from pykicad.pcb import Zone


def compile(filein, fileout):
    compiler = Compiler()
    compiler.compile(filein, fileout)


def place(filein, fileout):
    placer = Placer()
    placer.place(filein, fileout)


def route(filein, fileout):
    router = Router()
    router.route(filein, fileout)


def post_process(pcb, kpcb):
    xmin, ymin, xmax, ymax = pcb.boundary()
    coords = [(xmin, ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin)]

    zone = Zone(net_name='GND', layer='F.Cu',
                polygon=coords, clearance=0.3)

    kpcb.zones.append(zone)
    return kpcb


if __name__ == '__main__':
    Builder('joule_thief', joule_thief.top, oshpark_4layer,
            compile, place, route, post_process).build()
```

`Makefile`
```make
PYCIRCUIT = ../..

build:
	python3 build.py

view:
	node $(PYCIRCUIT)/viewer/app.js 3000 net.dot.svg pcb.svg

kicad:
	pcbnew *.kicad_pcb &>/dev/null &

clean:
	rm -f *.net *.hash *.dot *.svg *.place *.route *.pro *.kicad_pcb

.PHONY: build view kicad clean
```

![Viewer](https://user-images.githubusercontent.com/741807/34364054-39b1362e-ea82-11e7-94b7-baf712e1aeab.png)
![KiCad](https://user-images.githubusercontent.com/741807/34364057-43e7ee62-ea82-11e7-9787-84fefaecbc49.png)

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
