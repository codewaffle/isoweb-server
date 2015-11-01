cdef class EntityCategory:
    VALID = 1 << 0 # if mask is 0 then masking is broke? i think? anyway..
    ANY = 1 << 1
    COLLIDER = 1 << 2
    TERRAIN = 1 << 3
    REPLICATE = 1 << 4
    BOUNDARY = 1 << 5

cdef class CollisionType:
    ENTITY = 1
    BOUNDARY = 2