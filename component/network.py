import struct
from time import time, clock
from component import BaseComponent
from component.base import component_method
from entity import ObFlags
import packet_types


class NetworkViewer(BaseComponent):
    data = {
        'socket': None,
        'visibility_radius': 300
    }

    @component_method
    def initialize(self):
        self.entity.cache.network_viewer = {}
        self.entity.scheduler.schedule(func=self.entity.NetworkViewer.update)

    @component_method
    def update(self, dt):
        now = clock()

        cache = self.entity.cache.network_viewer

        visible = self.entity.Position.find_nearby(self.data.visibility_radius, flags=ObFlags.REPLICATE)

        # cur = set(cache.keys())
        # exit = cur - visible
        # enter = visible - cur

        # loop through previously-and-still-visible entities and only process those that are due.
        # entities that were not previously visible but cached can still sit around in the cache and only get
        # delta updated! TODO : we need a packet for visibility.
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
                packet = struct.pack(''.join(packet_fmt), *packet_data)
                # print repr(packet)
                self.data.socket.send(packet)

        # TODO : cleanup old entities?
        # TODO : send the 'go invisible' packet here.. at some point we'll flush it from cache and
        # TODO : also tell the client to flush it

        # update @ 20hz
        return -1/20.


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
