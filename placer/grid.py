import math

class Grid(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[' ' for i in range(width)] for i in range(height)]

    def add_box(self, box):
        h = int(box.height)
        w = int(box.width)
        b = int(box.bottom())
        l = int(box.left())
        for y in range(h):
            for x in range(w):
                self.grid[b + y][l + x] = box.symbol

    def __str__(self):
        result = '_' * (self.width + 2) + '\n'
        for line in reversed(self.grid):
            result += '|'
            for char in line:
                result += char
            result += '|\n'
        result += '_' * (self.width + 2) + '\n'
        return result
