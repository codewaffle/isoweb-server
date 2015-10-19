cdef class Vector2:
    cdef public float x
    cdef public float y

    cpdef dot(self, Vector2)

    cpdef Vector2 mul(self, float other)
    cpdef Vector2 div(self, float other)
    cpdef Vector2 add(self, Vector2 other)
    cpdef Vector2 sub(self, Vector2 other)

    cpdef Vector2 normalize(self)
    cpdef Vector2 lerp(self, other, alpha)
    cpdef Vector2 inplace_lerp(self, other, alpha)


