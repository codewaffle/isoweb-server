from phys.cm cimport *

cdef class RegionBase:
    cdef cpSpace *space


cdef class RegionMember:
    cdef RegionBase region
    cdef cpShape* shape
    cdef cpBody* body

    cdef void set_region(self, RegionBase)
    cdef void clear_region(self)

    cdef void set_position(self, cpVect)
    cdef cpVect get_position(self)