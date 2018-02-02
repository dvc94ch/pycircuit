from setuptools import setup, find_packages

setup(
    name='pycircuit',
    packages=find_packages(exclude=['tests', 'examples']),
    version='0.0.2',
    description='Library for composing circuits and pcb layouts',
    long_description=open('README.md').read(),
    author='David Craven',
    author_email='david@craven.ch',
    url='https://github.com/dvc94ch/pycircuit',
    keywords=['eda', 'cad', 'hdl', 'kicad'],
    install_requires=[
        'numpy', 'scipy', 'shapely', 'pykicad', 'z3-solver'
    ],
    tests_require=['pytest'],
    license='ISC'
)
