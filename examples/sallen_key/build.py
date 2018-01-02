import sallen_key
from pycircuit.build import Builder
from pycircuit.library.design_rules import oshpark_4layer

if __name__ == '__main__':
    Builder(sallen_key.top(), oshpark_4layer).build()
