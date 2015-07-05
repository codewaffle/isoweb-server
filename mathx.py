# this file should mirror mathx.coffee
from math import floor, ceil, sqrt


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
        return sqrt(self.dot(self))

    @property
    def sqr_magnitude(self):
        return self.dot(self)

    def __repr__(self):
        return 'Vector2({s.x}, {s.y})'.format(s=self)

class Rect(object):
    __slots__ = ['top', 'right', 'bottom', 'left']

    def __repr__(self):
        return 'Rect({s.left}, {s.bottom}, {s.right}, {s.top})'.format(s=self)

    def __init__(self, left=0, bottom=0, right=0, top=0):
        self.left = int(min(left, right))
        self.right = int(max(left, right))
        self.top = int(max(bottom, top))
        self.bottom = int(min(bottom, top))

    def __contains__(self, item):
        if isinstance(item, Vector2):
            return self.left <= item.x < self.right and self.bottom <= item.y < self.top
        elif isinstance(item, Rect):
            return item.left >= self.left and item.right <= self.right and item.top <= self.top and item.bottom >= self.bottom

    def set_bounds(self, left, bottom, right, top):
        self.left = int(min(left, right))
        self.right = int(max(left, right))
        self.top = int(max(bottom, top))
        self.bottom = int(min(bottom, top))
        return self

    def set_center(self, center):
        diff = self.center - center
        self.left = int(self.left + diff.x)
        self.right = int(self.right + diff.x)
        self.top = int(self.top + diff.y)
        self.bottom = int(self.bottom + diff.y)
        return self

    def set_width(self, val):
        diff = (val - self.width) / 2.
        self.left = int(self.left - ceil(diff))
        self.right = int(self.right + floor(diff))
        return self

    def set_height(self, val):
        diff = (val - self.height) / 2.
        self.top = int(self.top + ceil(diff))
        self.bottom = int(self.bottom - floor(diff))
        return self

    def set_size(self, width, height):
        return self.set_width(width).set_height(height)

    def expand(self, left, bottom, right, top):
        return self.set_bounds(min(left, self.left), min(bottom, self.bottom), max(right, self.right), max(top, self.top))

    def contract(self, left, bottom, right, top):
        return self.set_bounds(max(left, self.left), max(bottom, self.bottom), min(right, self.right), min(top, self.top))

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.top - self.bottom

    @property
    def center(self):
        return Vector2((self.right - self.left) / 2., (self.top - self.bottom) / 2.)
