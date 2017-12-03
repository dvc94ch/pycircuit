from pycircuit.device import *
from pycircuit.package import *
from pycircuit.footprint import *
from pycircuit.library import *
from pycircuit.library.connectors import *
from pycircuit.library.sifive import *
from pycircuit.library.lattice import *
from pycircuit.library.ftdi import *
from pycircuit.library.ti import *


def print_devices():
    for device in Device.devices:
        print(repr(device))

def print_packages():
    for package in Package.packages:
        print(repr(package))

def print_footprints():
    for footprint in Footprint.footprints:
        print(repr(footprint))

if __name__ == '__main__':
    print_devices()
    print_packages()
    print_footprints()
