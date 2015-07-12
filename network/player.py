import random
import struct

from geventwebsocket import WebSocketError
import logbook

from entity.retired.player import Player
import packet_types

packet_header = struct.Struct('>H')
move_to = struct.Struct('>ff')

class PlayerWebsocket(object):
    def __init__(self, ws):
        self.entity = None

        self.ws = ws
        self.island = None
        self.log = logbook.Logger('PlayerSocket({})'.format(str(id(self))))

    def on_connect(self, island):
        self.log.debug('on_connect')
        self.island = island
        self.handle_login()

        while self.recv():
            pass

        self.handle_logout()

    def recv(self):
        data = self.ws.receive()
        if data is None:
            return None

        packet_type,  = packet_header.unpack_from(data, 0)

        if packet_type == packet_types.MOVE_TO:
            x, y = move_to.unpack_from(data, 2)
            self.entity.request_move_to(x, y)
            return True

        logbook.warn('Unknown packet type: {0}', packet_type)
        return False

    def send(self, data):
        try:
            self.ws.send(data, binary=True)
        except WebSocketError:
            return self.on_disconnect()

    def handle_login(self):
        # assign player to island, send initial bla bla bla

        self.player = Player()
        self.player.id = random.randint(1, 1234)
        #self.player.position.x = random.random() * 50
        #self.player.position.y = random.random() * 50
        self.player.position.x = 0.1
        self.player.position.y = 0.1
        self.player.bearing = random.random() * 360 - 180
        self.player.socket = self
        self.player.set_dirty()
        self.island.add_entity(self.player)

        # TODO : this should be spawned by the island, i think..
        self.player.spawn([self.player])

    def handle_logout(self):
        pass

    def on_disconnect(self):
        if self.player and self.player.island:
            self.player.island.remove_entity(self.player)

        print '{} disconnected'.format(self)
