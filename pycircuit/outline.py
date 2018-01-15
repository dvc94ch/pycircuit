from shapely.geometry.polygon import Polygon


class OutlineDesignRules(object):
    def __init__(self, min_drill_size, min_slot_width, min_cutout_size):
        self.min_drill_size = min_drill_size
        self.min_slot_width = min_slot_width
        self.min_cutout_size = min_cutout_size


class OutlineDesignRuleError(Exception):
    pass


class OutlineElement(object):
    def check(self, design_rules):
        assert isinstance(design_rules, OutlineDesignRules)
        raise NotImplementedError()


class Hole(OutlineElement):
    def __init__(self, position, drill_size):
        self.position = position
        self.drill_size = drill_size

    def check(self, design_rules):
        if self.drill_size < design_rules.min_drill_size:
            raise OutlineDesignRuleError('Hole drill size needs to be larger than %d',
                                         design_rules.min_drill_size)

    def to_object(self):
        return {
            'type': 'hole',
            'drill_size': self.drill_size,
            'x': float(self.position[0]),
            'y': float(self.position[1]),
        }


class Slot(OutlineElement):
    def __init__(self, position, drill_size, width, angle=0):
        self.position = position
        self.drill_size = drill_size
        self.width = width # hole to hole
        self.angle = angle

    def check(self, design_rules):
        if self.drill_size < design_rules.min_drill_size:
            raise OutlineDesignRuleError('Slot drill size needs to be larger than %d',
                                         design_rules.min_drill_size)
        if self.width < design_rules.min_slot_width + self.drill_size:
            raise OutlineDesignRuleError('Slot width needs to be larger than %d',
                                         design_rules.min_slot_width + self.drill_size)

    def to_object(self):
        return {
            'type': 'slot',
            'drill_size': self.drill_size,
            'width': self.width,
            'x': float(self.position[0]),
            'y': float(self.position[1]),
            'r': self.angle,
        }


class Cutout(OutlineElement):
    def __init__(self, polygon):
        assert isinstance(polygon, Polygon)
        self.polygon = polygon
        self.width = polygon.bounds[2] - polygon.bounds[0]
        self.height = polygon.bounds[3] - polygon.bounds[1]

    def check(self, design_rules):
        if self.height < design_rules.min_cutout_size:
            raise OutlineDesignRuleError('Cutout height must be larger than %d',
                                         design_rules.min_cutout_size)
        if self.width < design_rules.min_cutout_size:
            raise OutlineDesignRuleError('Cutout width must be larger than %d',
                                         design_rules.min_cutout_size)

    def to_object(self):
        return {
            'type': 'cutout',
            'polygon': str(self.polygon)
        }


class Outline(object):
    def __init__(self, exterior, interior, *features):
        assert isinstance(exterior, Polygon)
        assert isinstance(interior, Polygon)
        self.exterior = exterior
        self.interior = interior
        self.features = []

        for f in features:
            assert isinstance(f, OutlineElement)
            self.features.append(f)

    def __iter__(self):
        return iter(self.features)

    def check(self, design_rules):
        for f in self.features:
            f.check(design_rules)

    def to_object(self):
        return {
            'exterior': str(self.exterior),
            'interior': str(self.interior),
            'features': [f.to_object() for f in self.features]
        }
