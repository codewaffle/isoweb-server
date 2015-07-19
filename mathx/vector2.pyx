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