from enum import Enum


class Conductor(Enum):
    Cu, Ag, Au = list(range(3))

    def conductivity(self):
        _conductivity = {
            'Cu': 5.96 * 10**7, #S/m @ 20C
            'Ag': 6.30 * 10**7, #S/m @ 20C
            'Au': 4.10 * 10**7, #S/m @ 20C
        }

        return _conductivity[self.name]


class Dielectric(Enum):
    FR4, FR408, PVP = list(range(3))

    def permittivity(self):
        _permittivity = {
            'PVP': 3, #Er ref: Guess
            'FR4': 4.6, #Er @1MHz ref: OSHPark
            'FR408': 3.66, #Er @1GHz ref: OSHPark
        }

        return _permittivity[self.name]


class Finish(Enum):
    ENIG = list(range(1))


class MaterialType(Enum):
    Conductor, Dielectric, SolderPaste, Adhesive, SolderMask, SilkScreen, Finish \
        = list(range(7))


class Material(object):
    def __init__(self, type, submaterial=None, color=None):
        assert isinstance(type, MaterialType)
        self.type = type
        self.is_conductor = False

        if type is MaterialType.Conductor:
            assert isinstance(submaterial, Conductor)
            self.submaterial = submaterial
            self.is_conductor = True
        elif type is MaterialType.Dielectric:
            assert isinstance(submaterial, Dielectric)
            self.submaterial = submaterial
        elif type is MaterialType.SolderMask:
            assert isinstance(color, str)
            self.color = color
        elif type is MaterialType.Finish:
            assert isinstance(submaterial, Finish)
            self.submaterial = submaterial

    def to_object(self):
        obj = {
            'material': self.type.name
        }

        if self.type is MaterialType.Conductor or \
           self.type is MaterialType.Dielectric or \
           self.type is MaterialType.Finish:
            obj['type'] = self.submaterial.name

        if self.type is MaterialType.Conductor:
            obj['conductivity'] = self.submaterial.conductivity()
        elif self.type is MaterialType.Dielectric:
            obj['permittivity'] = self.submaterial.permittivity()
        elif self.type is MaterialType.SolderMask:
            obj['color'] = self.color

        return obj


class Materials(object):
    # Conductors
    Cu = Material(MaterialType.Conductor, Conductor.Cu)
    Ag = Material(MaterialType.Conductor, Conductor.Ag)
    Au = Material(MaterialType.Conductor, Conductor.Au)
    # Dielectrics
    FR4 = Material(MaterialType.Dielectric, Dielectric.FR4)
    FR408 = Material(MaterialType.Dielectric, Dielectric.FR408)
    PVP = Material(MaterialType.Dielectric, Dielectric.PVP)
    # Misc
    SilkScreen = Material(MaterialType.SilkScreen)
    SolderMask = lambda color: Material(MaterialType.SolderMask, color=color)
    ENIG = Material(MaterialType.Finish, Finish.ENIG)


class Layer(object):
    def __init__(self, name, thickness, material):
        # Properties
        self.name = name
        self.thickness = thickness
        self.material = material
        # Stackup
        self.above = None
        self.below = None
        # Elements
        self.packages = []
        self.segments = []
        self.vias = []

        self.is_conductor = material.is_conductor

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def to_object(self):
        return {
            self.name: {
                'thickness': self.thickness,
                'material': self.material.to_object()
            }
        }


class Layers(object):
    def __init__(self, layers):
        for i, layer in enumerate(layers[0:-1]):
            layer.below = layers[i + 1]
        for i, layer in enumerate(layers[1:]):
            layer.above = layers[i]
        self.layers = layers

        conductive = list(self.iter_conductive())
        self.top = conductive[0]
        self.bottom = conductive[-1]

    def __getitem__(self, index):
        return self.layers[index]

    def __iter__(self):
        return iter(self.layers)

    def iter_conductive(self):
        for layer in self.layers:
            if layer.is_conductor:
                yield layer

    def __str__(self):
        return str([str(layer) for layer in self.layers])

    def to_object(self):
        return [layer.to_object() for layer in self.layers]
