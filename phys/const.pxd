from phys.cm cimport *

cdef:
    int CATEGORY_VALID = 1 << 0 # if mask is 0 then masking is broke? i think? anyway..
    int CATEGORY_ANY = 1 << 1
    int CATEGORY_COLLIDER = 1 << 2
    int CATEGORY_TERRAIN = 1 << 3
    int CATEGORY_REPLICATE = 1 << 4
    int CATEGORY_BOUNDARY = 1 << 5

cdef:
    int COLLISION_ENTITY = 1
    int COLLISION_BOUNDARY = 2