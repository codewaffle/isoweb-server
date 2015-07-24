cimport Vector2
from libc.math cimport fabs

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

    cdef intersects(self, AABB other):
        return (fabs(self.center.x - other.center.x) * 2 < (self.hwidth + other.hwidth) * 2) and \
               (fabs(self.center.y - other.center.y) * 2 < (self.hheight + other.hheight) * 2)

    def __add__(self, AABB other):
        self.center += other

    def __sub__(self, AABB other):
        self.center -= other

    cdef contains(self, Vector2 point):
        return self.center.x - self.hwidth < point.x < self.center.x + self.hwidth and \
               self.center.y - self.hheight < point.y < self.center.y + self.hheight
