import inspect
from struct import Struct
import os
import struct

from logbook import Logger

import config
from mathx import Vector2
import packet_types


transform_struct = Struct('>fff')

class Entity(object):
    client_class = 'Entity'
    _class_attributes = {}

    def __init__(self, position=None, bearing=None):
        self._local_attributes = {}
        self._dirty = False
        self._id = None
        self.position = position or Vector2()
        self.bearing = bearing or 0
        self.island = None
        self.log = Logger('UnboundEntity')

    def __getitem__(self, item):
        return self._local_attributes.get(item) or self._class_attributes[item][1]

    def __setitem__(self, key, value):
        self._local_attributes[key] = value

    def get_all_attributes(self):
        tmp = self._class_attributes.copy()
        tmp.update(self._local_attributes)

        return tmp

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, val):
        self._id = val
        self.log = Logger('{} #{}'.format(self.classpath, self._id))

    @property
    def classpath(self):
        return '.'.join((self.__module__, self.__class__.__name__))

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
        packet = struct.pack(
            '>HB{}sfff'.format(len(self.client_class)),
            packet_types.SPAWN,
            len(self.client_class),
            self.client_class,
            self.position.x,
            self.position.y,
            self.bearing
        )

        # TODO : pack in attributes...
        packet += self.pack_attributes()

        print repr(packet)

        for pl in players:
            pl.socket.send(packet)

    def pack_attributes(self):
        fmt = ['>B']  # number of properties
        args = []

        prop_count = 0

        for k, (t, v) in self.get_all_attributes().iteritems():
            prop_count += 1
            fmt.append('B%dsc' % len(k))
            args.extend([len(k), k, t])

            if t == 's':  # smallstring - limited 2^8 bytes
                fmt.append('B%ds' % len(v))
                args.extend([len(v), v])
            elif t == 'S':  # string - limited 2^16 bytes
                fmt.append('H%ds' % len(v))
                args.extend([len(v), v])
            else:
                assert len(t) == 1, 'complex attribute types not yet implemented'

                fmt.append(t)
                args.append(v)

        fmt = ''.join(fmt)

        return struct.pack(fmt, prop_count, *args)

    @classmethod
    def subclass_attributes(cls, attrs):
        ret = cls._class_attributes.copy()
        ret.update(attrs)
        return ret

    def __repr__(self):
        return '{self.classpath}({self.id})'.format(self=self)
