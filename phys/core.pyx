from mathx.vector2 import Vector2
from phys.cm cimport *
from cpython.ref cimport PyObject
from phys.const import EntityCategory
from phys.space cimport PhysicsSpace, SpaceMember
from math import pi, atan2




cdef void wrapUpdatePosition(cpBody *body, cpFloat dt):
    cdef cpVect p = body.p
    cdef cpFloat a = body.a

    cdef object ent

    cpBodyUpdatePosition(body, dt)

    if p.x != body.p.x or p.y != body.p.y or a != body.a:
        ent = <object>body.userData
        ent.Position._update()


cdef class TestMember(SpaceMember):
    def setup(self):
        self.body = cpBodyNew(75, cpMomentForCircle(75, 0, 0.333, cpv(0,0)))
        setup_entity_body(self.entity, self.body)

        self.shape = cpCircleShapeNew(self.body, 0.333, cpv(0,0))
        setup_entity_shape(self.entity, self.shape)
        self.shape.filter.categories = EntityCategory.ANY | EntityCategory.COLLIDER | EntityCategory.REPLICATE
        self.shape.filter.mask = EntityCategory.COLLIDER


cdef void updateVelocityLandFriction(cpBody *body, cpVect gravity, cpFloat damping, cpFloat dt):
    damping = 1.0
    cpBodyUpdateVelocity(body, gravity, damping, dt)


cdef class RaftTestMember(SpaceMember):
    def setup(self):
        cdef cpVect points_array[5]
        points_array[0].x = -1
        points_array[0].y = -1

        points_array[1].x = 1
        points_array[1].y = -1

        points_array[2].x = 1
        points_array[2].y = 1

        points_array[3].x = -1
        points_array[3].y = 1

        points_array[4] = points_array[0]

        cdef cpFloat moment = cpMomentForPoly(750, 4, points_array, cpv(0,0), 0)

        self.body = cpBodyNew(750, moment)
        cpBodySetVelocityUpdateFunc(self.body, updateVelocityLandFriction)
        setup_entity_body(self.entity, self.body)

        self.shape = cpPolyShapeNewRaw(self.body, 4, points_array, 0)
        setup_entity_shape(self.entity, self.shape)

        self.shape.filter.categories = EntityCategory.ANY | EntityCategory.COLLIDER | EntityCategory.REPLICATE
        self.shape.filter.mask = EntityCategory.COLLIDER


cdef setup_entity_body(entity, cpBody *body):
    body.userData = <PyObject*>entity
    cpBodySetPositionUpdateFunc(body, wrapUpdatePosition)
    # self.body.position_func = wrapUpdatePosition


cdef setup_entity_shape(entity, cpShape *shape):
    shape.userData = <PyObject*>entity
