from mathx.vector2 cimport Vector2
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

    cdef bint intersects(self, AABB other):
        # AABBs that are 'touching' do not intersect
        return (fabs(self.center.x - other.center.x) * 2 < (self.hwidth + other.hwidth) * 2) and \
               (fabs(self.center.y - other.center.y) * 2 < (self.hheight + other.hheight) * 2)

    cdef bint contains_point(self, Vector2 point):
        return self.center.x - self.hwidth <= point.x <= self.center.x + self.hwidth and \
               self.center.y - self.hheight <= point.y <= self.center.y + self.hheight

    cdef bint contains_aabb(self, AABB other):
        return self.left() <= other.left() and self.right() >= other.right() and \
               self.top() <= other.top() and self.bottom() >= other.bottom()

    cdef float left(self):
        return self.center.x - self.hwidth

    cdef float right(self):
        return self.center.x + self.hwidth

    cdef float top(self):
        return self.center.y - self.hheight

    cdef float bottom(self):
        return  self.center.y + self.hheight

    def __repr__(self):
        return 'AABB({}, {}, {})'.format(self.center, self.hwidth, self.hheight)
