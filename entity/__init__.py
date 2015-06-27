from struct import Struct
import os
import struct

from logbook import Logger

import config
from mathx import Vector2
import packet_types


class EntityAttribute(object):
    def __init__(self, initial):
        self.val = initial

    def __get__(self, instance, owner):
        return self.val

    def __set__(self, instance, value):
        self.val = value

transform_struct = Struct('>fff')

class Entity(object):
    def __init__(self, position=None, bearing=None):
        self._dirty = False
        self._id = None
        self.position = position or Vector2()
        self.bearing = bearing or 0
        self.island = None
        self.log = Logger('UnboundEntity')

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, val):
        self._id = val
        self.log = Logger('{} #{}'.format(self.classname, self._id))

    @property
    def classname(self):
        return '.'.join((self.__class__.__module__, self.__class__.__name__))

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

    def save(self):
        self.log.debug('Saving')
        tmp_name = os.path.join(config.ENTITY_DIR, self.id + '.entity~')
        final_name = tmp_name[:-1]

        with open(tmp_name, 'wb') as fp:
            fp.write(self.build_binary_repr())

        os.rename(tmp_name, final_name)

    @classmethod
    def load(cls, entity_id):
        with open(os.path.join(config.ENTITY_DIR, entity_id + '.entity'), 'rb') as fp:

            pass

    def build_binary_repr(self):
        return ''

    def spawn(self, players=None):
        if players is None:
            players = ''  # TODO : initial spawn figures out its own scope (or all players or whatever..)

        # build the packet.
        classname = self.classname

        packet = struct.pack(
            '>HB{}sfff'.format(len(classname)),
            packet_types.SPAWN,
            len(classname),
            classname,
            self.position.x,
            self.position.y,
            self.bearing
        )

        for pl in players:
            pl.socket.send(packet)

    def __repr__(self):
        return '<{self.classname}({self.id})>'.format(self=self)
