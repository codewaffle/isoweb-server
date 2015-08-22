from mathx.vector2 cimport Vector2

cdef class AABB:
    cdef public Vector2 center
    cdef public float hwidth, hheight

    cdef bint intersects(self, AABB other)
    cdef bint contains_point(self, Vector2 point)
    cdef bint contains_aabb(self, AABB other)

    cdef float left(self)
    cdef float right(self)
    cdef float top(self)
    cdef float bottom(self)

