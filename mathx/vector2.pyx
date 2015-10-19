from libc.math cimport sqrt
from random import uniform
from phys.cm cimport *

cdef class Vector2:
    def __init__(self, x=0, y=0.):
        self.x, self.y = x,y

    def to_cpVect(self):
        return cpv(self.x, self.y)

    def update(self, Vector2 other):
        self.x, self.y = other.x, other.y

    def update(self, float x, float y):
        self.x, self.y = x, y

    cpdef dot(self, Vector2 other):
        return self.x*other.x+self.y*other.y

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __truediv__(self, other):
        return Vector2(self.x / other, self.y / other)

    def __mul__(self, other):
        return Vector2(self.x * other, self.y * other)

    def __repr__(self):
        return 'Vector2({s.x}, {s.y})'.format(s=self)

    # inline chainables
    cpdef Vector2 mul(self, float other):
        self.x *= other
        self.y *= other
        return self

    cpdef Vector2 div(self, float other):
        self.x /= other
        self.y /= other
        return self

    cpdef Vector2 add(self, Vector2 other):
        self.x += other.x
        self.y += other.y
        return self

    cpdef Vector2 sub(self, Vector2 other):
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

    cpdef Vector2 normalize(self):
        """In-place normalize"""
        return self.div(self.magnitude)

    cpdef Vector2 lerp(self, other, alpha):
        return self * (1.0 - alpha) + (other * alpha)


    cpdef Vector2 inplace_lerp(self, other, alpha):
        self.x = self.x * (1.0 - alpha) + (other.x * alpha)
        self.y = self.y * (1.0 - alpha) + (other.y * alpha)

        return self

    @classmethod
    def random_unit(cls):
        return Vector2(uniform(-1.0, 1.0), uniform(-1.0, 1.0)).normalize()

    @classmethod
    def random_inside(cls, radius=1.0):
        return cls.random_unit().mul(uniform(0.0, radius))
