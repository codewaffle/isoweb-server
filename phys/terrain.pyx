from phys.const import EntityCategory
from phys.core cimport *
from phys.cm cimport *
from cpython.mem cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free

cdef class TerrainMember(SpaceMember):
    def setup(self):
        points = self.data
        assert points

        self.body = cpBodyNewStatic()
        setup_entity_body(self.entity, self.body)

        cdef cpVect* points_array = <cpVect*>PyMem_Malloc(len(points) * sizeof(cpVect))

        i = 0
        for pt in points:
            points_array[i] = cpVect(pt[0], pt[1])
            i += 1

        print(points)
        self.shape = cpPolyShapeNewRaw(self.body, len(points), points_array, 0)
        setup_entity_shape(self.entity, self.shape)
        self.shape.filter.categories = EntityCategory.ANY | EntityCategory.TERRAIN | EntityCategory.REPLICATE
        self.shape.filter.mask = 1 # must be non-zero to show up in range queries

        PyMem_Free(points_array)
