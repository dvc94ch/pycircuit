from distutils.core import setup

setup(
    name='pycircuit',
    packages=['pycircuit', 'pycircuit.library'],
    version='0.0.1',
    description='Library for composing circuits and pcb layouts',
    long_description=open('README.md').read(),
    author='David Craven',
    author_email='david@craven.ch',
    url='https://github.com/dvc94ch/pycircuit',
    keywords=['eda', 'cad', 'hdl', 'kicad'],
    install_requires=['numpy', 'scipy', 'shapely', 'pykicad', 'graphviz'],
    tests_require=['pytest'],
    license='ISC'
)
