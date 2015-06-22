from struct import Struct
from mathx import Vector2


transform_struct = Struct('>fff')


class Entity(object):
    id = None
    position = None
    bearing = None

    def __init__(self, position=None, bearing=None):
        self.position = position or Vector2()
        self.bearing = bearing or 0

    @property
    def packed_transform(self):
        return transform_struct.pack(self.position.x, self.position.y, self.bearing)

    # not sure if this will ever be called
    def unpack_transform(self, data):
        self.position.x, self.position.y, self.bearing = transform_struct.unpack(data)
