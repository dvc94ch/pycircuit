import itertools
from pycircuit.device import *

for device in ['R', 'C']:
    for package in ['0805']:
        Device('%s%s' % (device, package), device, package,
               Map('1', 'A'),
               Map('2', 'B'))

for package in ['0805']:
    Device('D%s' % package, 'D', package,
           Map('1', '+'),
           Map('2', '-'))

for a, b, c in itertools.permutations('BCE', 3):
    Device('SOT23' + a + b + c, 'Q', 'SOT23',
           Map('1', a),
           Map('2', b),
           Map('3', c),
           Map(None, 'SUBSTRATE'))

for a, b, c in itertools.permutations('GSD'):
    Device('SOT23' + a + b + c, 'M', 'SOT23',
           Map('1', a),
           Map('2', b),
           Map('3', c),
           Map(None, 'SUBSTRATE'))

Device('TP', 'TP', 'PAD', Map('1', 'TP'))
