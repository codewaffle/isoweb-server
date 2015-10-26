from phys.cm cimport *
from cpython.ref cimport PyObject
from phys.const import EntityCategory

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
    def __init__(self, entity):
        self.entity = entity

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

    def get_position_components(self):
        cdef cpVect pos = self.get_position()
        return pos.x, pos.y

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
    def setup_test_body(self):
        self.body = cpBodyNew(1, 0.5)
        setup_entity_body(self.entity, self.body)

        self.shape = cpCircleShapeNew(self.body, 1, cpv(0,0))
        self.shape.userData = <PyObject*>self.entity
        self.shape.filter.categories = EntityCategory.ANY | EntityCategory.COLLIDER | EntityCategory.REPLICATE
        self.shape.filter.mask = EntityCategory.COLLIDER


cdef setup_entity_body(entity, cpBody *body):
    body.userData = <PyObject*>entity
    cpBodySetPositionUpdateFunc(body, wrapUpdatePosition)
    # self.body.position_func = wrapUpdatePosition
