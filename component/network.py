from functools import partial
import struct
from isoweb_time import clock
from component import BaseComponent
from entity import ObFlags
from network.util import PacketBuilder
import packet_types
from util import to_bytes

packet_builder = PacketBuilder()

class NetworkViewer(BaseComponent):
    """
    Responsible for most of the work of figuring out what the client can see.
    """
    _socket = None
    visibility_radius = 20

    _current = None
    _cache = None
    _def_cache = None

    def initialize(self):
        self._current = set()
        self._cache = {}
        self._def_cache = set()
        self.entity.scheduler.schedule(func=self.update)

    def update(self):
        if not self._socket:
            self.destroy()
            return

        packet_builder.begin()
        now = clock()

        current = self._current
        cache = self._cache

        visible = self.entity.Position.find_nearby(self.visibility_radius, flags=ObFlags.REPLICATE)

        for ref in (current - visible):
            if ref.valid is False:  # destroyed/invalidated
                packet_builder.append('BfI', packet_types.ENTITY_DESTROY, clock(), ref.id)
                del cache[ref]
            else:  # hide dynamic/moving entities, stop updating static ones
                packet_builder.append('BfI', packet_types.ENTITY_DISABLE, clock(), ref.id)

            current.remove(ref)

        enter = visible - current

        enter_defs = set(e.entity_def for e in enter)
        enter_defs.difference_update(self._def_cache)

        # send component exports attached to this entity def.
        if enter_defs:
            for d in enter_defs:
                packet_builder.append(
                    'BfQH{}s'.format(len(d.exports_json)),
                    packet_types.ENTITYDEF_UPDATE,
                    clock(),
                    d.digest,
                    len(d.exports_json),
                    d.exports_json
                )
            self._def_cache.update(enter_defs)

        # loop through previously-and-still-visible entities and only process those that are due.
        # entities that were not previously visible but cached can still sit around in the cache and only get
        # delta updated!
        for ref in visible:
            when, last = cache.get(ref, (now, 0))

            # not ready to check this yet
            if when > now:
                continue

            header = False

            # append changes.
            for fmt, pdata in ref.changes_after(last):
                if not header:
                    packet_builder.append('BfI', packet_types.ENTITY_UPDATE, clock(), ref.id)
                    header = True
                packet_builder.append(fmt, *pdata)
            if header:
                packet_builder.append('B', 0)

            # queue up again based on priority or something.
            cache[ref] = now + 1 / 40., now  # for now, just ensure we update faster than the network rate so it's 1:1

        for ref in enter:
            packet_builder.append('BfI', packet_types.ENTITY_ENABLE, clock(), ref.id)

        current.update(enter)

        if packet_builder.values:
            self._socket.send(packet_builder.build())

        # update @ 20hz
        return -1 / 20.


class Replicated(BaseComponent):
    _name_replicator = None

    def initialize(self):
        self.entity.ob.flags |= ObFlags.REPLICATE
        self._name_replicator = name_replicator = string_replicator(partial(getattr, self.entity, 'name'), 'name')

        self.entity.snapshots[self.get_entitydef_hash] = 0
        self.entity.snapshots[name_replicator] = 0

    def get_entitydef_hash(self):
        return 'BQ', (packet_types.ENTITYDEF_HASH_UPDATE, self.entity.entity_def.digest)

    def on_destroy(self):
        self.entity.ob.flags &= ~ObFlags.REPLICATE
        try:
            del self.entity.snapshots[self._name_replicator]
        except KeyError:
            pass

        try:
            del self.entity.snapshots[self.get_entitydef_hash]
        except KeyError:
            pass


def string_replicator(func, attr_name):
    name_len = len(attr_name)

    def inner():
        res = str(func())
        res_len = len(res)
        return 'BB{}sH{}s'.format(name_len, res_len), [packet_types.STRING_UPDATE, name_len, attr_name, res_len, res]

    return inner


def float_replicator(func, attr_name):
    name_len = len(attr_name)

    def inner():
        res = float(func())
        return 'BB{}sf'.format(name_len), [packet_types.FLOAT_UPDATE, name_len, attr_name, res]

    return inner
