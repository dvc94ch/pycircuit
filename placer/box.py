from enum import Enum
from z3 import *
import math
import uuid


class Anchor(Enum):
    Min = 0
    Center = 1
    Max = 2


class Coord(object):
    def __init__(self, anchor):
        self.anchor = anchor
        self.value = 0


class Box(object):
    counter = 0
    symbols = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+[]{};:\'",./<>?|\\'

    def __init__(self, inst, width, height, x_anchor=Anchor.Min, y_anchor=Anchor.Min):
        self.symbol = Box.symbols[Box.counter % len(Box.symbols)]
        Box.counter += 1

        self.inst = inst
        self.x = Coord(x_anchor)
        self.y = Coord(y_anchor)
        self.width = width
        self.height = height

    def set_position(self, x, y):
        self.x.value = x
        self.y.value = y
        return self

    def top(self):
        if self.y.anchor == Anchor.Max:
            return self.y.value
        if self.y.anchor == Anchor.Min:
            return self.y.value + self.height
        if self.y.anchor == Anchor.Center:
            return self.y.value + self.height / 2

    def bottom(self):
        if self.y.anchor == Anchor.Min:
            return self.y.value
        if self.y.anchor == Anchor.Max:
            return self.y.value - self.height
        if self.y.anchor == Anchor.Center:
            return self.y.value - self.height / 2

    def right(self):
        if self.x.anchor == Anchor.Max:
            return self.x.value
        if self.x.anchor == Anchor.Min:
            return self.x.value + self.width
        if self.x.anchor == Anchor.Center:
            return self.x.value + self.width / 2

    def left(self):
        if self.x.anchor == Anchor.Min:
            return self.x.value
        if self.x.anchor == Anchor.Max:
            return self.x.value - self.width
        if self.x.anchor == Anchor.Center:
            return self.x.value - self.width / 2

    def area(self):
        return self.height * self.width

    def place_inst(self, offset, grid_size):
        inst_attributes = self.inst.attributes
        x = (self.x.value + offset[0]) * grid_size
        y = (self.y.value + offset[1]) * grid_size
        inst_attributes.place(inst_attributes.layer, x, y)

    def __str__(self):
        return 'x=%s y=%s w=%s h=%s' % (self.x.value, self.y.value,
                                        self.height, self.width)

    @classmethod
    def from_inst(cls, inst):
        return cls(inst, inst.device.package.courtyard.ipc_width,
                   inst.device.package.courtyard.ipc_height)


class Z3Box(Box):

    def __init__(self, inst, width, height):
        super().__init__(inst, width, height, Anchor.Center, Anchor.Center)

        self.const_rx = int(math.ceil(width / 2))
        self.const_ry = int(math.ceil(height / 2))

        self.var_x = Int('%s_x' % str(inst.uid))
        self.var_y = Int('%s_y' % str(inst.uid))
        self.var_rot = Bool('%s_rot' % str(inst.uid))
        self.var_rx = Int('%s_rx' % str(inst.uid))
        self.var_ry = Int('%s_ry' % str(inst.uid))

    def range_constraint(self, bin):
        return And(self.var_x >= self.var_rx,
                   self.var_x <= bin.var_width - self.var_rx,
                   self.var_y >= self.var_ry,
                   self.var_y <= bin.var_height - self.var_ry)

    def rotation_constraint(self, allow_rotate=False):
        # Enabling rotation makes things much slower
        return And(
            BoolVal(True) if allow_rotate else self.var_rot == False,
            Implies(Not(self.var_rot), And(self.var_rx == self.const_rx,
                                           self.var_ry == self.const_ry)),
            Implies(self.var_rot, And(self.var_rx == self.const_ry,
                                      self.var_ry == self.const_rx))
        )

    def fix_position_constraint(self, x, y):
        return And(self.var_x == x, self.var_y == y)

    def overlap_constraint(self, other):
        return Or(
            self.var_x - other.var_x >= self.var_rx + other.var_rx,
            other.var_x - self.var_x >= self.var_rx + other.var_rx,
            self.var_y - other.var_y >= self.var_ry + other.var_ry,
            other.var_y - self.var_y >= self.var_ry + other.var_ry
        )

    def set_rotation(self, rotation):
        width, height = self.width, self.height
        if rotation:
            self.width = height
            self.height = width

    def eval(self, model):
        self.set_position(model[self.var_x].as_long(),
                          model[self.var_y].as_long())
        self.set_rotation(is_true(model[self.var_rot]))
