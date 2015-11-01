cdef extern from "const.h":
    cpdef enum:
        CATEGORY_VALID
        CATEGORY_ANY
        CATEGORY_COLLIDER
        CATEGORY_TERRAIN
        CATEGORY_REPLICATE
        CATEGORY_BOUNDARY

    cpdef enum:
        COLLISION_ENTITY
        COLLISION_BOUNDARY