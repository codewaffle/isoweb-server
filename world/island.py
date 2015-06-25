import struct
import time

from gevent import Greenlet
import gevent
from logbook import Logger

from entity.player import Player
from mathx import RNG
import packet_types


class Island(Greenlet):
    _entities = None
    _players = None
    update_rate = 0.05

    def __init__(self, seed):
        super(Island, self).__init__()
        self.id = self.seed = seed
        self._entities = set()
        self._players = set()
        self._dirty_entities = set()

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
        packet = [struct.pack('>HIH', packet_types.ISLAND_UPDATE, self.id, len(self._dirty_entities))]

        for e in self._dirty_entities:
            packet.append(struct.pack('>I', e.id))
            packet.append(e.packed_transform)

            e._dirty = False

        self._dirty_entities.clear()

        packet = ''.join(packet)

        for pl in self._players:
            pl.socket.send(packet)

    def add_entity(self, ent):
        self._entities.add(ent)
        self.log.debug('Added entity {0}', ent)
        ent.island = self
        self._dirty_entities.add(ent)

        if isinstance(ent, Player):
            self._players.add(ent)

    def remove_entity(self, ent):
        ent.island = None
        self.log.debug('Removed entity {0}', ent)
        self._entities.remove(ent)

        try:
            self._dirty_entities.remove(ent)
        except KeyError:
            pass

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
        self._dirty_entities.add(ent)
