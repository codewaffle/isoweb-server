from struct import Struct
from logbook import Logger
from mathx import Vector2


transform_struct = Struct('>fff')


class Entity(object):

    def __init__(self, position=None, bearing=None):
        self._dirty = False
        self.id = None
        self.position = position or Vector2()
        self.bearing = bearing or 0
        self.island = None
        # TODO: make a new log when we get an id
        self.log = Logger('Unbound Entity')

    def set_dirty(self):
        if self._dirty:
            return

        self._dirty = True

        if self.island:
            self.island.add_dirty(self)

    @property
    def scope(self):
        if self.island:
            return [pl.socket for pl in self.island._players]

        return []

    @property
    def packed_transform(self):
        return transform_struct.pack(self.position.x, self.position.y, self.bearing)

    # not sure if this will ever be called
    def unpack_transform(self, data):
        self.position.x, self.position.y, self.bearing = transform_struct.unpack(data)
