from mathx.vector2 cimport Vector2

cdef class AABB:
    cdef public Vector2 center
    cdef public float hwidth, hheight
