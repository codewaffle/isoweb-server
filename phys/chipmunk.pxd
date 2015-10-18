cdef extern from "chipmunk/chipmunk.h":
    cdef struct cpSpace
    cdef struct cpBody
    cdef struct cpShape

    cpSpace *cpSpaceNew()
    cpBody* cpSpaceAddBody(cpSpace *space, cpBody *body)
    cpShape* cpSpaceAddShape(cpSpace *space, cpShape *shape)

