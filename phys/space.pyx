from mathx.vector2 import Vector2
from phys.cm cimport *
from cpython.ref cimport PyObject
from math import pi, atan2

from phys.const import *


cdef void find_results(cpShape *shape, void *data):
    results = <object>data
    ent = <object>shape.userData
    results.add(ent)


# ctypedef cpBool (*cpCollisionBeginFunc)(cpArbiter *arb, cpSpace *space, cpDataPointer userData)
# ctypedef cpBool (*cpCollisionPreSolveFunc)(cpArbiter *arb, cpSpace *space, cpDataPointer userData)
# ctypedef void (*cpCollisionPostSolveFunc)(cpArbiter *arb, cpSpace *space, cpDataPointer userData)
# ctypedef void (*cpCollisionSeparateFunc)(cpArbiter *arb, cpSpace *space, cpDataPointer userData)
cdef cpBool boundary_collision_pre(cpArbiter *arb, cpSpace *space, cpDataPointer userData):
    return True


cdef cpBool boundary_collision_begin(cpArbiter *arb, cpSpace *space, cpDataPointer userData):
    return True


cdef class PhysicsSpace:
    def __init__(self, PhysicsSpace parent_space):
        self.parent_space = parent_space
        print(parent_space)

    def __cinit__(self):
        self.space = cpSpaceNew()

        self.space.damping = 0.8
        self.space.idleSpeedThreshold = 0.1
        self.space.sleepTimeThreshold = 0.5

        cpSpaceSetIterations(self.space, 5)
        cpSpaceSetGravity(self.space, cpv(0,0))

        cpdef cpCollisionHandler* handler = cpSpaceAddCollisionHandler(self.space, COLLISION_BOUNDARY, COLLISION_ENTITY)
        handler.preSolveFunc = boundary_collision_pre
        handler.beginFunc = boundary_collision_begin

    def __dealloc__(self):
        cpSpaceFree(self.space)

    def step(self, float dt):
        cpSpaceStep(self.space, dt)

    def set_boundary(self, boundary_points):
        cdef int i
        cdef int l = len(boundary_points)
        cdef cpBody* body = cpBodyNewStatic()
        cdef cpShape *seg
        cdef cpShapeFilter filt
        cdef cpVect bp0
        cdef cpVect bp1

        filt.categories = CATEGORY_BOUNDARY | CATEGORY_COLLIDER
        filt.mask = <int>-1

        for i in range(len(boundary_points)-1):
            bp0 = cpv(boundary_points[i][0], boundary_points[i][1])
            bp1 = cpv(boundary_points[i+1][0], boundary_points[i+1][1])
            seg = cpSegmentShapeNew(body, bp0, bp1, 0.05)
            cpShapeSetFilter(seg, filt)
            cpShapeSetCollisionType(seg, COLLISION_BOUNDARY)
            cpSpaceAddShape(self.space, seg)

        cpSpaceAddBody(self.space, body)

    cpdef void add_member(self, SpaceMember member):
        cpSpaceAddShape(self.space, member.shape)
        cpSpaceAddBody(self.space, member.body)

    cpdef void remove_member(self, SpaceMember member):
        cpSpaceRemoveShape(self.space, member.shape)
        cpSpaceRemoveBody(self.space, member.body)

    def query_box(self, cpBB bounding_box, unsigned int mask):
        cdef cpShapeFilter filt
        filt.categories = 0xffffffff
        filt.mask = mask

        results = set()

        cpSpaceBBQuery(
            self.space,
            bounding_box,
            filt,
            find_results,
            <PyObject*>results
        )

        return results


cdef class SpaceMember:
    def __init__(self, entity, data=None):
        if data:
            self.data_ptr = <PyObject*>data

        self.entity = entity

        self.setup()

        entity.space_member = self

        if entity.parent and entity.parent.has_component('Space'):
            self.set_space(entity.parent.Space.space)
        else:
            self.set_space(self.entity.region.space)

    property data:
        def __get__(self):
            return <object>self.data_ptr

    def setup(self):
        cpBodySetMass(self.body, self.mass)

    cpdef cpFloat get_mass(self):
        return cpBodyGetMass(self.body)

    cpdef void set_space(self, PhysicsSpace space):
        if space == self.space:
            return

        self.clear_space()
        self.space = space

        if space:
            assert self.shape
            assert self.body
            space.add_member(self)

        cpBodyActivate(self.body)

    cpdef void clear_space(self):
        if self.space is None:
            return

        self.space.remove_member(self)
        self.space = None

    cpdef void set_position(self, cpVect pos):
        cpBodySetPosition(self.body, pos)
        cpBodyActivate(self.body)

    cpdef void set_position_components(self, cpFloat x, cpFloat y):
        cdef cpVect pos
        pos.x = x
        pos.y = y
        cpBodySetPosition(self.body, pos)
        cpBodyActivate(self.body)

    cpdef cpVect get_position(self):
        return cpBodyGetPosition(self.body)

    cpdef cpFloat get_rotation(self):
        cdef cpVect rot = cpBodyGetRotation(self.body)
        return atan2(rot.y, rot.x)

    def get_position_components(self):
        cdef cpVect pos = self.get_position()
        return pos.x, pos.y, self.get_rotation()

    def get_velocity_components(self):
        return self.body.v.x, self.body.v.y

    cpdef find_nearby(self, float radius, unsigned int mask):
        if not self.space:
            return set()

        cdef cpBB bb
        bb.l = self.get_position().x - radius
        bb.r = self.get_position().x + radius

        bb.b = self.get_position().y - radius
        bb.t = self.get_position().y + radius

        ret = self.space.query_box(
            bb,
            mask
        )

        if self.space.parent_space:
            # TODO : transform bbox into outer space
            ret.update(
                self.space.parent_space.query_box(
                    bb, mask
                )
            )

        return ret

    def __dealloc__(self):
        self.clear_space()

        if self.shape:
            cpShapeFree(self.shape)
            self.shape = NULL

        if self.body:
            cpBodyFree(self.body)
            self.body = NULL

    def set_force(self, float x, float y):
        cpBodySetForce(self.body, cpv(x,y))
        cpBodyActivate(self.body)

    def set_velocity(self, float x, float y):
        cpBodySetVelocity(self.body, cpv(x, y))
        cpBodyActivate(self.body)

    def set_velocity_components(self, float x, float y):
        cpBodySetVelocity(self.body, cpv(x, y))
        cpBodyActivate(self.body)

    def set_angle(self, float angle):
        cpBodySetAngle(self.body, angle)
        cpBodyActivate(self.body)

    property velocity:
        def __get__(self):
            return Vector2(self.body.v.x, self.body.v.y)

cdef class MemberData:
    def __init__(self, entity):
        entity.member_data = self
        self.entity_ptr = <PyObject*>entity

    def get_entity(self):
        return <object>self.entity_ptr
