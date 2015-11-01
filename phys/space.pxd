from phys.cm cimport *

from cpython.ref cimport PyObject


cdef class PhysicsSpace:
    cdef cpSpace *space

    cpdef void add_member(self, SpaceMember member)
    cpdef void remove_member(self, SpaceMember member)


cdef class SpaceMember:
    cdef PhysicsSpace space
    cdef cpShape* shape
    cdef cpBody* body
    cdef cpFloat mass

    cpdef void set_space(self, PhysicsSpace)
    cpdef void clear_space(self)

    cpdef void set_position(self, cpVect)
    cpdef void set_position_components(self, cpFloat, cpFloat)
    cpdef cpVect get_position(self)
    cpdef cpFloat get_rotation(self)
    cpdef object entity
    cpdef cpFloat get_mass(self)

    cpdef find_nearby(self, float radius, unsigned int mask)

    cdef PyObject *data_ptr

cdef class MemberData:
    cdef PyObject *entity_ptr

    cdef PhysicsSpace space
    cdef PhysicsSpace outer_space

