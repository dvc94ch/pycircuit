from distutils.core import setup

setup(
    name='pycircuit',
    packages=['pycircuit',
              'pycircuit.library',
              'pycircuit.formats',
              'pycircuit.library.sifive',
              'pycircuit.library.lattice',
              'pycircuit.library.ftdi',
              'pycircuit.library.ti',
              ],
    version='0.0.1',
    description='Library for composing circuits and pcb layouts',
    long_description=open('README.md').read(),
    author='David Craven',
    author_email='david@craven.ch',
    url='https://github.com/dvc94ch/pycircuit',
    keywords=['eda', 'cad', 'hdl', 'kicad'],
    install_requires=['numpy', 'scipy', 'shapely', 'pykicad', 'graphviz', 'z3-solver'],
    tests_require=['pytest'],
    license='ISC'
)
