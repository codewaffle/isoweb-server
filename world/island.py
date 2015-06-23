import struct
import ujson
from gevent import Greenlet
import gevent
import time
from logbook import Logger
from entity.player.player import Player
from mathx import RNG
import packet_types


class Island(Greenlet):
    _entities = None
    _players = None
    update_rate = 0.05

    def __init__(self, seed):
        super(Island, self).__init__()
        self.id = self.seed = seed
        self._entities = []
        self._players = []
        self._dirty = set()

        self.log = Logger('Island {}'.format(self.id))

        self.rng = RNG(seed)
        self.width = self.rng.randint(15, 150)
        self.height = self.rng.randint(self.width/2, self.width*2)
        self.log.debug('Initialized')

    def update(self, dt):
        for ent in self._entities:
            prev_state = (ent.position.x, ent.position.y, ent.bearing)
            ent.update(dt)

            if prev_state != (ent.position.x, ent.position.y, ent.bearing):
                ent.set_dirty()

    def update_players(self):
        packet = [struct.pack('>HIH', packet_types.ISLAND_UPDATE, self.id, len(self._dirty))]

        for e in self._dirty:
            packet.append(struct.pack('>I', e.id))
            packet.append(e.packed_transform)

            e._dirty = False

        self._dirty.clear()

        packet = ''.join(packet)

        for pl in self._players:
            pl.socket.send(packet)

    def add_entity(self, ent):
        self._entities.append(ent)
        self.log.debug('Added entity {0}', ent)
        ent.island = self

        if isinstance(ent, Player):
            self._players.append(ent)

    def remove_entity(self, ent):
        ent.island = None
        self.log.debug('Removed entity {0}', ent)
        self._entities.remove(ent)

        if isinstance(ent, Player):
            self._players.remove(ent)

    def run(self):
        while True:
            start = time.clock()
            # tick entities
            self.update(self.update_rate)

            # send updates to players..
            self.update_players()
            delta = start - time.clock()

            gevent.sleep(max(self.update_rate-delta, 0))

    def add_dirty(self, ent):
        self._dirty.add(ent)
