from phys.core cimport *
from phys.cm cimport *

cdef class TerrainMember(RegionMember):
    def setup(self):
        self.body = cpBodyNew(0, 0)
        setup_entity_body(self.entity, self.body)

