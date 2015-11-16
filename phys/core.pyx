from random import random

from mathx.vector2 import Vector2
from phys.cm cimport *
from cpython.ref cimport PyObject
from phys.const import CATEGORY_ANY, CATEGORY_COLLIDER, CATEGORY_REPLICATE, COLLISION_ENTITY
from cpython.mem cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free
from phys.space cimport PhysicsSpace, SpaceMember, MemberData
from math import pi, atan2


cdef void wrapUpdatePosition(cpBody *body, cpFloat dt):
    cdef cpVect p = body.p
    cdef cpFloat a = body.a

    cdef object ent

    cpBodyUpdatePosition(body, dt)

    if p.x != body.p.x or p.y != body.p.y or a != body.a:
        md = <object>body.userData
        try:
            ent = md.get_entity()
        except:
            print("Failed to get_entity()")

        ent.Position._update()


cdef class BaseMember(SpaceMember):
    def setup(self):
        self.body = cpBodyNewStatic()
        setup_entity_body(self.entity, self.body)

        self.shape = cpCircleShapeNew(self.body, 0.1, cpv(0,0))
        setup_entity_shape(self.entity, self.shape)
        self.shape.filter.categories = CATEGORY_ANY | CATEGORY_REPLICATE
        self.shape.filter.mask = 1

cdef class TestMember(SpaceMember):
    def setup(self):
        self.body = cpBodyNew(75, cpMomentForCircle(75, 0, 0.333, cpv(0,0)))
        setup_entity_body(self.entity, self.body)

        self.shape = cpCircleShapeNew(self.body, 0.333, cpv(0,0))
        setup_entity_shape(self.entity, self.shape)
        self.shape.filter.categories = CATEGORY_ANY | CATEGORY_COLLIDER | CATEGORY_REPLICATE
        self.shape.filter.mask = CATEGORY_COLLIDER


cdef void updateVelocityLandFriction(cpBody *body, cpVect gravity, cpFloat damping, cpFloat dt):
    cdef float sqr_vel = body.v.x*body.v.x + body.v.y*body.v.y

    if sqr_vel < 0.1:
        damping = 0.4
    else:
        damping = 0.95

    body.w *= .9

    cpBodyUpdateVelocity(body, gravity, damping, dt)


cdef class RaftTestMember(SpaceMember):
    def setup(self):
        cdef cpVect points_array[5]
        points_array[0].x = -0.793
        points_array[0].y = -0.895

        points_array[1].x = 0.793
        points_array[1].y = -0.895

        points_array[2].x = 0.793
        points_array[2].y = 0.895

        points_array[3].x = -0.793
        points_array[3].y = 0.895

        points_array[4] = points_array[0]

        cdef cpFloat moment = cpMomentForPoly(750, 4, points_array, cpv(0,0), 0.05)

        self.body = cpBodyNew(750, moment)
        cpBodySetVelocityUpdateFunc(self.body, updateVelocityLandFriction)
        setup_entity_body(self.entity, self.body)

        self.shape = cpPolyShapeNewRaw(self.body, 4, points_array, 0.05)
        setup_entity_shape(self.entity, self.shape)

        self.shape.filter.categories = CATEGORY_ANY | CATEGORY_COLLIDER | CATEGORY_REPLICATE
        self.shape.filter.mask = CATEGORY_COLLIDER


cdef setup_entity_body(entity, cpBody *body):
    cdef MemberData md = MemberData(entity)
    body.userData = <PyObject*>entity.member_data
    cpBodySetPositionUpdateFunc(body, wrapUpdatePosition)


cdef setup_entity_shape(entity, cpShape *shape):
    shape.userData = <PyObject*>entity
    cpShapeSetCollisionType(shape, COLLISION_ENTITY)
    cpShapeSetFriction(shape, 0.7)
