cimport Vector2
from math import fabs

cdef class AABB:
    def __init__(self, center, hwidth=0, hheight=None):
        if isinstance(center, AABB):
            self.center = Vector2(center.center)
            self.hwidth = center.hwidth
            self.hheight = center.hheight
        else:
            self.center = center
            self.hwidth = hwidth

            if hheight is None:
                self.hheight = hwidth
            else:
                self.hheight = hheight

    def intersects(self, other):
        return (fabs(self.center.x - other.center.x) * 2 < (self.hwidth + other.hwidth) * 2) and \
               (fabs(self.center.y - other.center.y) * 2 < (self.hheight + other.hheight) * 2)

    def __add__(self, other):
        self.center += other

    def __sub__(self, other):
        self.center -= other

    def contains(self, point):
        return self.center.x - self.hwidth < point.x < self.center.x + self.hwidth and \
               self.center.y - self.hheight < point.y < self.center.y + self.hheight
