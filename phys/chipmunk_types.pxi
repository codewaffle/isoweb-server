cdef extern from "chipmunk/chipmunk_private.h":
    ctypedef double cpFloat
    ctypedef bint cpBool
    ctypedef int cpTimestamp
    ctypedef void* cpDataPointer
    ctypedef int cpHashValue
    ctypedef int cpCollisionID
    ctypedef int cpBitmask
    ctypedef int cpGroup


    cdef struct cpVect:
        cpFloat x, y

    cdef struct cpBB:
        cpFloat l, b, r, t

    cdef struct cpTransform:
        cpFloat a, b, c, d, tx, ty

    cdef struct cpBodyType
    cdef struct cpPolyline
    cdef struct cpPolylineSet
    cdef struct cpPointQueryInfo
    cdef struct cpSegmentQueryInfo
    cdef struct cpCollisionType

    cdef struct cpShapeFilter:
        cpGroup group
        cpBitmask categories
        cpBitmask mask

    cdef struct cpSimpleMotor
    cdef struct cpSpaceDebugDrawOptions
    cdef struct cpSpaceHash
    cdef struct cpBBTree
    cdef struct cpSpatialIndex
    cdef struct cpSweep1D



    cdef struct cpArray
    cdef struct cpHashSet
    cdef struct cpBody:
        # mass and it's inverse
        cpFloat m;
        cpFloat m_inv;

        # moment of inertia and it's inverse
        cpFloat i;
        cpFloat i_inv;

        # center of gravity
        cpVect cog;

        # position, velocity, force
        cpVect p;
        cpVect v;
        cpVect f;

        # Angle, angular velocity, torque (radians)
        cpFloat a;
        cpFloat w;
        cpFloat t;

        cpTransform transform;

        cpDataPointer userData;

        # "pseudo-velocities" used for eliminating overlap.
        # Erin Catto has some papers that talk about what these are.
        cpVect v_bias;
        cpFloat w_bias;

        cpSpace *space;

        cpShape *shapeList;
        cpArbiter *arbiterList;
        cpConstraint *constraintList;


    cdef struct cpShape:
        # const cpShapeClass *klass

        cpSpace *space
        cpBody *body
        # cpShapeMassInfo massInfo
        cpBB bb

        cpBool sensor

        cpFloat e
        cpFloat u
        cpVect surfaceV

        cpDataPointer userData

        # cpCollisionType type
        cpShapeFilter filter

        cpShape *next
        cpShape *prev

        cpHashValue hashid
        
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
    struct cpSpaceDebugColor
    
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

    ctypedef void (*cpSpaceBBQueryFunc)(cpShape *shape, void *data)
    ctypedef void (*cpBodyVelocityFunc)(cpBody *body, cpVect gravity, cpFloat damping, cpFloat dt)
    ctypedef void (*cpBodyPositionFunc)(cpBody *body, cpFloat dt)
    ctypedef void (*cpBodyShapeIteratorFunc)(cpBody *body, cpShape *shape, void *data)
    ctypedef void (*cpBodyConstraintIteratorFunc)(cpBody *body, cpConstraint *constraint, void *data)
    ctypedef void (*cpBodyArbiterIteratorFunc)(cpBody *body, cpArbiter *arbiter, void *data)
    ctypedef void (*cpConstraintPreSolveFunc)(cpConstraint *constraint, cpSpace *space)
    ctypedef void (*cpConstraintPostSolveFunc)(cpConstraint *constraint, cpSpace *space);

    ctypedef void (*cpCollisionPostSolveFunc)(cpArbiter *arb, cpSpace *space, cpDataPointer userData)
    ctypedef void (*cpCollisionSeparateFunc)(cpArbiter *arb, cpSpace *space, cpDataPointer userData)
    ctypedef void (*cpPostStepFunc)(cpSpace *space, void *key, void *data)
    ctypedef void (*cpSpacePointQueryFunc)(cpShape *shape, cpVect point, cpFloat distance, cpVect gradient, void *data)
    ctypedef void (*cpSpaceSegmentQueryFunc)(cpShape *shape, cpVect point, cpVect normal, cpFloat alpha, void *data)
    ctypedef void (*cpSpaceBBQueryFunc)(cpShape *shape, void *data)
    ctypedef void (*cpSpaceShapeQueryFunc)(cpShape *shape, cpContactPointSet *points, void *data)
    ctypedef void (*cpSpaceBodyIteratorFunc)(cpBody *body, void *data)
    ctypedef void (*cpSpaceShapeIteratorFunc)(cpShape *shape, void *data)
    ctypedef void (*cpSpaceConstraintIteratorFunc)(cpConstraint *constraint, void *data)

    ctypedef cpCollisionID (*cpSpatialIndexQueryFunc)(void *obj1, void *obj2, cpCollisionID id, void *data)
    ctypedef void (*cpSpatialIndexIteratorFunc)(void *obj, void *data)

