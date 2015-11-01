from mathx.vector2 import Vector2
from phys.cm cimport *
from phys import const
from cpython.ref cimport PyObject
from phys.const import EntityCategory, CollisionType
from math import pi, atan2


cdef void find_results(cpShape *shape, void *data):
    results = <object>data
    ent = <object>shape.userData
    results.add(ent)

cdef class PhysicsSpace:

    def __cinit__(self):
        self.space = cpSpaceNew()
        cpdef cpCollisionHandler* handler = cpSpaceAddCollisionHandler(self.space, CollisionType.BOUNDARY, CollisionType.ENTITY)
        self.space.damping = 0.8
        self.space.idleSpeedThreshold = 0.1
        self.space.sleepTimeThreshold = 0.5

        cpSpaceSetIterations(self.space, 5)
        cpSpaceSetGravity(self.space, cpv(0,0))

        #cdef cpShape* ground = cpSegmentShapeNew(self.space.staticBody, cpv(-20, 5), cpv(20, -5), 0)
        #cpShapeSetFriction(ground, 1)
        #cpSpaceAddShape(self.space, ground)

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

        filt.categories = EntityCategory.BOUNDARY
        filt.mask = <int>-1

        for i in range(len(boundary_points)-1):
            bp0 = cpv(boundary_points[i][0], boundary_points[i][1])
            bp1 = cpv(boundary_points[i+1][0], boundary_points[i+1][1])
            seg = cpSegmentShapeNew(body, bp0, bp1, 0.1)
            cpShapeSetFilter(seg, filt)
            cpShapeSetCollisionType(seg, CollisionType.BOUNDARY)
            cpSpaceAddShape(self.space, seg)

        cpSpaceAddBody(self.space, body)


cdef class SpaceMember:
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

    cpdef cpFloat get_mass(self):
        return cpBodyGetMass(self.body)

    cpdef void set_region(self, PhysicsSpace region):
        if region == self.region:
            return

        self.clear_region()
        self.region = region

        if region:
            assert self.shape
            assert self.body
            cpSpaceAddShape(region.space, self.shape)
            cpSpaceAddBody(region.space, self.body)
        cpBodyActivate(self.body)

    cpdef void clear_region(self):
        if self.region is None:
            return

        cpSpaceRemoveShape(self.region.space, self.shape)
        cpSpaceRemoveBody(self.region.space, self.body)
        self.region = None

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