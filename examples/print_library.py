from pycircuit.library import *


def print_components():
    for comp in Component.components:
        print(repr(comp))


def print_packages():
    for package in Package.packages:
        print(repr(package))


def print_devices():
    for device in Device.devices:
        print(repr(device))


if __name__ == '__main__':
    print_components()
    print_packages()
    print_devices()
