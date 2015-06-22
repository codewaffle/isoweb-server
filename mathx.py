# this file should mirror mathx.coffee
import math


class RNG(object):
    def __init__(self, seed):
        self.seed = seed % 233280

    def rand01(self):
        self.seed = (self.seed * 9301 + 49297) % 233280
        return self.seed/233280.0

    def randint(self, a, b=None):
        _max = b or a
        _min = a if b else 0

        return int(_min + (self.rand01() * (_max - _min)))


class Vector2(object):
    __slots__ = ['x', 'y']

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __div__(self, other):
        return Vector2(self.x / other, self.y / other)

    def __mul__(self, other):
        return Vector2(self.x * other, self.y * other)

    def dot(self, other):
        return self.x*other.x+self.y*other.y

    @property
    def magnitude(self):
        return math.sqrt(self.dot(self))

    @property
    def sqr_magnitude(self):
        return self.dot(self)