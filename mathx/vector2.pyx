from libc.math cimport sqrt
from random import uniform

cdef class Vector2:
    def __init__(self, x=0, y=0.):
        self.x, self.y = x,y

    def update(self, Vector2 other):
        self.x, self.y = other.x, other.y

    def update(self, float x, float y):
        self.x, self.y = x, y

    def dot(self, Vector2 other):
        return self.x*other.x+self.y*other.y

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __div__(self, other):
        return Vector2(self.x / other, self.y / other)

    def __mul__(self, other):
        return Vector2(self.x * other, self.y * other)

    def __repr__(self):
        return 'Vector2({s.x}, {s.y})'.format(s=self)

    # inline chainables
    def mul(self, float other):
        self.x *= other
        self.y *= other
        return self

    def div(self, float other):
        self.x /= other
        self.y /= other
        return self

    def add(self, Vector2 other):
        self.x += other.x
        self.y += other.y
        return self

    def sub(self, Vector2 other):
        self.x -= other.x
        self.y -= other.y
        return self

    @property
    def mag2(self):
        return self.x*self.x + self.y*self.y

    @property
    def magnitude(self):
        return sqrt(self.x*self.x + self.y*self.y)

    @property
    def normalized(self):
        return self / self.magnitude

    def normalize(self):
        """In-place normalize"""
        return self.div(self.magnitude)

    def lerp(self, other, alpha):
        return Vector2(self.x + (other.x - self.x) * alpha, self.y + (other.y - self.y) * alpha)

    def inplace_lerp(self, other, alpha):
        self.x += (other.x - self.x) * alpha
        self.y += (other.y - self.y) * alpha

        return self

    @classmethod
    def random(cls):
        return Vector2(uniform(-1.0, 1.0), uniform(-1.0, 1.0)).normalize()
