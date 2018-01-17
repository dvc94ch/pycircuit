from enum import Enum


class BaseMaterial(Enum):
    def properties(self):
        return {}


class Conductor(BaseMaterial):
    Cu, Ag, Au = list(range(3))

    def properties(self):
        prop = {}

        _conductivity = {
            'Cu': 5.96 * 10**7, #S/m @ 20C
            'Ag': 6.30 * 10**7, #S/m @ 20C
            'Au': 4.10 * 10**7, #S/m @ 20C
        }

        prop['conductivity'] = _conductivity[self.name]
        return prop


class Dielectric(BaseMaterial):
    FR4, FR408, PVP = list(range(3))

    def properties(self):
        prop = {}

        _permittivity = {
            'PVP': 3, #Er ref: Guess
            'FR4': 4.6, #Er @1MHz ref: OSHPark
            'FR408': 3.66, #Er @1GHz ref: OSHPark
        }

        prop['permittivity'] = _permittivity[self.name]
        return prop


class SolderMask(BaseMaterial):
    Purple, Red, Green, Blue, Black, White = list(range(6))

    def properties(self):
        prop = {}

        _color = {
            'Purple': 'purple',
            'Red': 'red',
            'Green': 'green',
            'Blue': 'blue',
            'Black': 'black',
            'White': 'white',
        }

        prop['color'] = _color[self.name]
        return prop


class SolderPaste(BaseMaterial):
    Any = list(range(1))


class Adhesive(BaseMaterial):
    Any = list(range(1))


class SilkScreen(BaseMaterial):
    Any = list(range(1))


class Finish(BaseMaterial):
    ENIG = list(range(1))


class MaterialType(Enum):
    Conductor, Dielectric, SolderPaste, Adhesive, SolderMask, SilkScreen, Finish \
        = list(range(7))

    def get_class(self):
        _class = {
            MaterialType.Conductor: Conductor,
            MaterialType.Dielectric: Dielectric,
            MaterialType.SolderMask: SolderMask,
            MaterialType.SolderPaste: SolderPaste,
            MaterialType.Adhesive: Adhesive,
            MaterialType.SilkScreen: SilkScreen,
            MaterialType.Finish: Finish,
        }

        return _class[self]


class Material(object):
    def __init__(self, material_type, material=None):
        assert isinstance(material_type, MaterialType)
        self.material_type = material_type

        _class = material_type.get_class()
        if _class is not None:
            assert isinstance(material, _class)
        self.material = material

        self.is_conductor = False
        if material_type is MaterialType.Conductor:
            self.is_conductor = True

    def to_object(self):
        obj = {
            'material_type': self.material_type.name
        }

        if self.material is not None:
            obj['material'] = self.material.name
            obj['properties'] = self.material.properties()

        return obj

    @classmethod
    def from_object(cls, obj):
        material_type = MaterialType[obj['material_type']]
        material = material_type.get_class()[obj['material']]
        return cls(material_type, material)


class Materials(object):
    # Conductors
    Cu = Material(MaterialType.Conductor, Conductor.Cu)
    Ag = Material(MaterialType.Conductor, Conductor.Ag)
    Au = Material(MaterialType.Conductor, Conductor.Au)
    # Dielectrics
    FR4 = Material(MaterialType.Dielectric, Dielectric.FR4)
    FR408 = Material(MaterialType.Dielectric, Dielectric.FR408)
    PVP = Material(MaterialType.Dielectric, Dielectric.PVP)
    # Soldermasks
    PurpleSolderMask = Material(MaterialType.SolderMask, SolderMask.Purple)
    # Finishes
    ENIG = Material(MaterialType.Finish, Finish.ENIG)
    # Misc
    SolderPaste = Material(MaterialType.SolderPaste, SolderPaste.Any)
    SilkScreen = Material(MaterialType.SilkScreen, SilkScreen.Any)
    Adhesive = Material(MaterialType.Adhesive, Adhesive.Any)


class Layer(object):
    def __init__(self, name, thickness, material):
        self.name = name
        self.thickness = thickness
        self.material = material

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def to_object(self):
        return {
            'name': self.name,
            'thickness': self.thickness,
            'material': self.material.to_object()
        }

    @classmethod
    def from_object(cls, obj):
        return cls(obj['name'], obj['thickness'], Material.from_object(obj['material']))


class RoutingLayer(object):
    def __init__(self, layer):
        self.layer = layer
        self.segments = []
        self.vias = []


class PlacementLayer(object):
    def __init__(self, layer, flip=False):
        self.layer = layer
        self.flip = flip
        self.packages = []


class Layers(object):
    def __init__(self, layers):
        self.layers = layers

        self.placement_layers = []
        self.routing_layers = []

        # Add routing layers
        for layer in self.layers:
            if layer.material.is_conductor:
                self.routing_layers.append(RoutingLayer(layer))

        # Add placement layers
        top = PlacementLayer(self.routing_layers[0].layer)
        bottom = PlacementLayer(self.routing_layers[-1].layer, flip=True)
        self.placement_layers += [top, bottom]

    def __getitem__(self, index):
        return self.layers[index]

    def __iter__(self):
        return iter(self.layers)

    def iter_conductive(self):
        for layer in self.layers:
            if layer.material.is_conductor:
                yield layer

    def __str__(self):
        return str([str(layer) for layer in self.layers])

    def to_object(self):
        return [layer.to_object() for layer in self.layers]

    @classmethod
    def from_object(cls, obj):
        return cls([Layer.from_object(layer) for layer in obj])
