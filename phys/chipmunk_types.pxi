cdef extern from "chipmunk/chipmunk_private.h":
    ctypedef float cpFloat
    ctypedef bint cpBool
    ctypedef int cpTimestamp
    ctypedef void* cpDataPointer
    ctypedef int cpHashValue

    cdef struct cpVect:
        float x
        float y

    cdef struct cpBB:
        float l
        float b
        float r
        float t

    cdef struct cpTransform:
        float a, b, c, d, tx, ty

    cdef struct cpBodyType
    cdef struct cpPolyline
    cdef struct cpPolylineSet
    cdef struct cpPointQueryInfo
    cdef struct cpSegmentQueryInfo
    cdef struct cpCollisionType
    cdef struct cpShapeFilter
    cdef struct cpSimpleMotor
    cdef struct cpSpaceDebugDrawOptions
    cdef struct cpSpaceHash
    cdef struct cpBBTree
    cdef struct cpSpatialIndex
    cdef struct cpSweep1D



    cdef struct cpArray
    cdef struct cpHashSet
    cdef struct cpBody
    cdef struct cpShape
    cdef struct cpCircleShape
    cdef struct cpSegmentShape
    cdef struct cpPolyShape
    cdef struct cpConstraint
    cdef struct cpPinJoint
    cdef struct cpSlideJoint
    cdef struct cpPivotJoint
    cdef struct cpGrooveJoint
    cdef struct cpDampedSpring
    cdef struct cpDampedRotarySpring
    cdef struct cpRotaryLimitJoint
    cdef struct cpRatchetJoint
    cdef struct cpGearJoint
    cdef struct cpSimpleMotorJoint
    cdef struct cpCollisionHandler
    cdef struct cpContactPointSet
    cdef struct cpArbiter
    
    cdef struct cpSpace:
        int iterations

        cpVect gravity
        cpFloat damping

        cpFloat idleSpeedThreshold
        cpFloat sleepTimeThreshold

        cpFloat collisionSlop
        cpFloat collisionBias
        cpTimestamp collisionPersistence

        cpDataPointer userData

        cpTimestamp stamp
        cpFloat curr_dt

        cpArray *dynamicBodies
        cpArray *staticBodies
        cpArray *rousedBodies
        cpArray *sleepingComponents

        cpHashValue shapeIDCounter
        cpSpatialIndex *staticShapes
        cpSpatialIndex *dynamicShapes

        cpArray *constraints

        cpArray *arbiters
        # cpContactBufferHeader *contactBuffersHead
        cpHashSet *cachedArbiters
        cpArray *pooledArbiters

        cpArray *allocatedBuffers
        unsigned int locked

        cpBool usesWildcards
        cpHashSet *collisionHandlers
        # cpCollisionHandler defaultHandler

        cpBool skipPostStep
        cpArray *postStepCallbacks

        cpBody *staticBody
        # cpBody _staticBody
