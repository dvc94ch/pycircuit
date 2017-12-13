from z3 import *


class Bin(object):
    counter = 0

    def __init__(self, width, height):
        self.id = Bin.counter
        Bin.counter += 1

        self.width = width
        self.height = height

    def dim(self):
        return (self.width, self.height)

    def center(self):
        return (self.width / 2, self.height / 2)

    def area(self):
        return self.width * self.height

    def __str__(self):
        return 'width=%s height=%s area=%s' % (self.width, self.height,
                                               self.area())


class Z3Bin(Bin):
    def __init__(self):
        super().__init__(0, 0)
        self.var_width = Int('bin%s_w' % str(self.id))
        self.var_height = Int('bin%s_h' % str(self.id))
        self.var_area = Int('bin%s_a' % str(self.id))
        self.var_center_x = Int('bin%s_cx' % str(self.id))
        self.var_center_y = Int('bin%s_cy' % str(self.id))

    def var_center(self):
        return (self.var_center_x, self.var_center_y)

    def range_constraint(self):
        return And(self.var_width >= 0,
                   self.var_height >= 0,
                   self.var_width == 2 * self.var_center_x,
                   self.var_height == 2 * self.var_center_y)

    def area_constraint(self, area):
        return And(self.var_area == self.var_width * self.var_height,
                   self.var_area <= area)

    def eval(self, model):
        self.width = model[self.var_width].as_long()
        self.height = model[self.var_height].as_long()
