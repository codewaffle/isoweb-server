from phys.const import EntityCategory
from phys.core cimport *
from phys.cm cimport *

cdef class TerrainMember(RegionMember):
    def setup(self):
        self.body = cpBodyNewStatic()
        setup_entity_body(self.entity, self.body)

        self.shape = cpCircleShapeNew(self.body, 2, cpv(0,0))
        setup_entity_shape(self.entity, self.shape)
        self.shape.filter.categories = EntityCategory.ANY | EntityCategory.TERRAIN | EntityCategory.REPLICATE
        self.shape.filter.mask = 1 # must be non-zero..
        # self.shape = cp
