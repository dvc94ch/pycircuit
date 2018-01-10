# Circuit Description Library

## Getting started

`common_emitter.py`
```python
from pycircuit.circuit import *
from pycircuit.library import *


@circuit('Common Emitter', 'gnd', '12V', 'vin', 'vout')
def common_emitter_amplifer(self, gnd, vcc, vin, vout):
    nb, ne = nets('nb ne')
    Inst('Q', 'npn sot23')['B', 'C', 'E'] = nb, vout, ne

    # Current limiting resistor
    Inst('R', '1.2k')['~', '~'] = vcc, vout

    # Thermal stabilization (leads to a gain reduction)
    Inst('R', '220')['~', '~'] = ne, gnd
    # Shorts Re for AC signal (increases gain)
    Inst('C', '10uF')['~', '~'] = ne, gnd

    # Biasing resistors
    Inst('R', '20k')['~', '~'] = vcc, nb
    Inst('R', '3.6k')['~', '~'] = nb, gnd
    # Decoupling capacitor
    Inst('C', '10uF')['~', '~'] = vin, nb


if __name__ == '__main__':
    from pycircuit.formats import *
    from pycircuit.build import Builder

    Builder(common_emitter_amplifer()).compile()
```


![Schematic](https://user-images.githubusercontent.com/741807/34790831-53fb6d02-f643-11e7-895e-2c12e81b69c7.png)

## Optimization
`sallen_key/build.py`
```python
import numpy as np
import scipy.signal as sig
from pycircuit.build import Builder
from pycircuit.circuit import testbench
from pycircuit.optimize import Optimizer

from sallen_key import lp_sallen_key

def lp_optimize():
    spec = sig.butter(2, 2 * np.pi * 100, btype='low', analog=True)
    tb = Builder(testbench(lp_sallen_key())).compile()
    problem = Optimizer(tb, spec)
    cost = problem.optimize()
    print(cost)
    problem.plot_result()
    print(repr(problem.netlist))


if __name__ == '__main__':
    lp_optimize()
```

After 10s runtime. If it's not good enough run it again...
![Optimizer](https://user-images.githubusercontent.com/741807/34791214-943eb1ca-f644-11e7-991a-41c7727d9e62.png)

## Physical design
`joule_thief/build.py`
```python
import joule_thief
from pycircuit.build import Builder
from pycircuit.library.design_rules import oshpark_4layer
from placer import Placer
from router import Router
from pykicad.pcb import Zone

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
    Builder(joule_thief.top(), oshpark_4layer,
            place=place, route=route, post_process=post_process).build()
```

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
