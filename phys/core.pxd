from phys.cm cimport *
from libcpp.vector cimport vector
from cpython.ref cimport PyObject

cdef class PhysicsSpace:
    cdef cpSpace *space


cdef class SpaceMember:
    cdef PhysicsSpace region
    cdef cpShape* shape
    cdef cpBody* body

    cpdef void set_region(self, PhysicsSpace)
    cpdef void clear_region(self)

    cpdef void set_position(self, cpVect)
    cpdef void set_position_components(self, cpFloat, cpFloat)
    cpdef cpVect get_position(self)
    cpdef cpFloat get_rotation(self)
    cpdef object entity
    cpdef cpFloat get_mass(self)

    cpdef find_nearby(self, float radius, unsigned int mask)

    cdef PyObject *data_ptr


cdef setup_entity_body(entity, cpBody *)
cdef setup_entity_shape(entity, cpShape *)