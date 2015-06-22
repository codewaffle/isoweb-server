import struct
import ujson
from gevent import Greenlet
import gevent
import time
from enum import PacketType
from mathx import RNG


class Island(Greenlet):
    entities = None
    players = None
    update_rate = 0.05

    def __init__(self, seed):
        super(Island, self).__init__()
        self.id = self.seed = seed
        self.entities = []
        self.players = []

        self.rng = RNG(seed)
        self.width = self.rng.randint(15, 150)
        self.height = self.rng.randint(self.width/2, self.width*2)

    def update(self, dt):
        for ent in self.entities:
            ent.update(dt)

    def update_players(self, dt):
        packet = []
        packet.append(struct.pack('>HIH', PacketType.ISLAND_UPDATE, self.id, len(self.entities)))

        for e in self.entities:
            packet.append(struct.pack('>I', e.id))
            packet.append(e.packed_transform)

        packet = ''.join(packet)

        for pl in self.players:
            pl.socket.send(packet)

    def run(self):
        while True:
            start = time.clock()
            # tick entities
            self.update(self.update_rate)

            # send updates to players..
            self.update_players(self.update_rate)
            delta = start - time.clock()

            gevent.sleep(max(self.update_rate-delta, 0))
