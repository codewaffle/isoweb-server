cdef class EntityCategory:
    ANY = 1 << 0

    COLLIDER = 1 << 2
    TERRAIN = 1 << 3
    REPLICATE = 1 << 4