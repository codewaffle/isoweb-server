from functools import partial
import struct
from isoweb_time import clock
from component import BaseComponent
from component.base import component_method
from entity import ObFlags
import packet_types
from util import to_bytes


class NetworkViewer(BaseComponent):
    """
    Responsible for most of the work of figuring out what the client can see.
    """
    data = {
        '_socket': None,
        'visibility_radius': 20
    }

    @component_method
    def initialize(self):
        self.data._current = {}
        self.data._cache = {}
        self.data._def_cache = set()
        self.entity.scheduler.schedule(func=self.entity.NetworkViewer.update)

    @component_method
    def update(self):
        if not self.data._socket:
            self.destroy()
            return

        now = clock()

        current = self.data._current
        cache = self.data._cache

        visible = self.entity.Position.find_nearby(self.data.visibility_radius, flags=ObFlags.REPLICATE)

        for ref in (set(current.keys()) - visible):
            if ref.valid is False:  # destroyed/invalidated
                self.data._socket.send(struct.pack('>BfI', packet_types.ENTITY_DESTROY, clock(), ref.id))
                del cache[ref]
            else:  # hide dynamic/moving entities, stop updating static ones
                self.data._socket.send(struct.pack('>BfI', packet_types.ENTITY_HIDE, clock(), ref.id))

            del current[ref]

        enter = visible - set(current.keys())

        enter_defs = set(e.entity_def for e in enter)
        enter_defs.difference_update(self.data._def_cache)

        if enter_defs:
            for d in enter_defs:
                packet = struct.pack(
                    '>Bf4sH{}s'.format(len(d.exports_json)),
                    packet_types.ENTITYDEF_UPDATE,
                    clock(),
                    d.digest,
                    len(d.exports_json),
                    d.exports_json
                )

                # send() bundles the packets up so this should be safe
                self.data._socket.send(packet)
            self.data._def_cache.update(enter_defs)

        # loop through previously-and-still-visible entities and only process those that are due.
        # entities that were not previously visible but cached can still sit around in the cache and only get
        # delta updated!
        for ref in visible:
            when, last = cache.get(ref, (now, 0))

            # not ready to check this yet
            if when > now:
                continue

            packet_fmt = []
            packet_data = []

            # append changes.
            for fmt, pdata in ref.changes_after(last):
                packet_fmt.append(fmt)
                packet_data.extend(pdata)

            # queue up again based on priority or something.
            cache[ref] = now + 1/20., now  # for now, just ensure we update faster than the network rate so it's 1:1

            if packet_fmt:
                # entity update header
                packet_fmt = ['>BfI'] + packet_fmt + ['B']
                packet_data = [packet_types.ENTITY_UPDATE, clock(), ref.id] + packet_data + [0]

                # SEND
                packet = struct.pack(''.join(packet_fmt), *to_bytes(packet_data))
                self.data._socket.send(packet)

        for ref in enter:
            self.data._socket.send(struct.pack('>BfI', packet_types.ENTITY_SHOW, clock(), ref.id))

        # update @ 20hz
        return -1/20.

class Replicated(BaseComponent):
    @component_method
    def initialize(self):
        self.entity.ob.flags |= ObFlags.REPLICATE
        self.data._name_replicator = name_replicator = string_replicator(partial(getattr, self.entity, 'name'), 'name')

        self.entity.snapshots[self.get_entitydef_hash] = 0
        self.entity.snapshots[name_replicator] = 0

    @component_method
    def get_entitydef_hash(self):
        return 'B4s', (packet_types.ENTITYDEF_HASH_UPDATE, self.entity.entity_def.digest)

    @component_method
    def on_destroy(self):
        self.entity.ob.flags &= ~ObFlags.REPLICATE
        try:
            del self.entity.snapshots[self.data._name_replicator]
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
