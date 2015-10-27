from mathx.vector2 import Vector2
from phys.cm cimport *
from cpython.ref cimport PyObject
from phys.const import EntityCategory
from math import pi, atan2

cdef class RegionBase:

    def __cinit__(self):
        print("ALLOC")
        self.space = cpSpaceNew()
        cpSpaceSetIterations(self.space, 5)
        cpSpaceSetGravity(self.space, cpv(0,0))

        #cdef cpShape* ground = cpSegmentShapeNew(self.space.staticBody, cpv(-20, 5), cpv(20, -5), 0)
        #cpShapeSetFriction(ground, 1)
        #cpSpaceAddShape(self.space, ground)

    def __dealloc__(self):
        print("DEALLOC")
        cpSpaceFree(self.space)

    def step(self, float dt):
        cpSpaceStep(self.space, dt)


cdef class RegionMember:
    def __init__(self, entity, data=None):
        if data:
            self.data_ptr = <PyObject*>data

        self.entity = entity

        self.setup()

        entity.region_member = self

        self.set_region(self.entity.region)

    property data:
        def __get__(self):
            return <object>self.data_ptr

    def setup(self):
        pass

    cpdef void set_region(self, RegionBase region):
        if region == self.region:
            return

        self.clear_region()
        self.region = region

        if region:
            assert self.shape
            assert self.body
            cpSpaceAddShape(region.space, self.shape)
            cpSpaceAddBody(region.space, self.body)

    cpdef void clear_region(self):
        if self.region is None:
            return

        cpSpaceRemoveShape(self.region.space, self.shape)
        cpSpaceRemoveBody(self.region.space, self.body)
        self.region = None

    cpdef void set_position(self, cpVect pos):
        cpBodySetPosition(self.body, pos)

    cpdef void set_position_components(self, cpFloat x, cpFloat y):
        cdef cpVect pos
        pos.x = x
        pos.y = y
        cpBodySetPosition(self.body, pos)

    cpdef cpVect get_position(self):
        return cpBodyGetPosition(self.body)

    cpdef cpFloat get_rotation(self):
        cdef cpVect rot = cpBodyGetRotation(self.body)
        return atan2(rot.y, rot.x)


    def get_position_components(self):
        cdef cpVect pos = self.get_position()
        return pos.x, pos.y, self.get_rotation()

    def get_velocity_components(self):
        cdef cpVect vel = cpBodyGetVelocity(self.body)
        return vel.x, vel.y


    cpdef find_nearby(self, float radius, unsigned int mask):
        if not self.region:
            return set()

        cdef cpBB bb
        bb.l = self.get_position().x - radius
        bb.r = self.get_position().x + radius

        bb.b = self.get_position().y - radius
        bb.t = self.get_position().y + radius

        cdef cpShapeFilter filt
        filt.categories = 0xffffffff
        filt.mask = mask

        results = set()

        cpSpaceBBQuery(
            self.region.space,
            bb,
            filt,
            find_results,
            <PyObject*>results
        )

        return results

    def __dealloc__(self):
        self.clear_region()

        if self.shape:
            cpShapeFree(self.shape)
            self.shape = NULL

        if self.body:
            cpBodyFree(self.body)
            self.body = NULL

    def set_force(self, float x, float y):
        self.body.f.x = x
        self.body.f.y = y

    def set_velocity(self, float x, float y):
        self.body.v.x = x
        self.body.v.y = y

    def set_angle(self, float angle):
        self.body.a = angle

    property velocity:
        def __get__(self):
            return Vector2(self.body.v.x, self.body.v.y)

cdef void find_results(cpShape *shape, void *data):
    results = <object>data
    ent = <object>shape.userData
    results.add(ent)

cdef void wrapUpdatePosition(cpBody *body, cpFloat dt):
    cdef cpVect p = body.p
    cdef cpFloat a = body.a
    cdef object ent

    cpBodyUpdatePosition(body, dt)

    if p.x != body.p.x or p.y != body.p.y or a != body.a:
        ent = <object>body.userData
        ent.Position._update()


cdef class TestMember(RegionMember):
    def setup(self):
        self.body = cpBodyNew(1, 0.5)
        setup_entity_body(self.entity, self.body)

        self.shape = cpCircleShapeNew(self.body, 0.5, cpv(0,0))
        setup_entity_shape(self.entity, self.shape)
        self.shape.filter.categories = EntityCategory.ANY | EntityCategory.COLLIDER | EntityCategory.REPLICATE
        self.shape.filter.mask = EntityCategory.COLLIDER


cdef setup_entity_body(entity, cpBody *body):
    body.userData = <PyObject*>entity
    cpBodySetPositionUpdateFunc(body, wrapUpdatePosition)
    # self.body.position_func = wrapUpdatePosition


cdef setup_entity_shape(entity, cpShape *shape):
    shape.userData = <PyObject*>entity
