import random
import struct
import ujson
from geventwebsocket import WebSocketError
import logbook
from mathx import Vector2
import packet_types

packet_header = struct.Struct('>H')
move_to = struct.Struct('>ff')

class PlayerSocket(object):
    def __init__(self, ws):
        self.player = None
        self.ws = ws

    def on_connect(self):
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
            self.player.move_to(x, y)
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
        self.player.id = random.randint(1, 1234)

    def handle_logout(self):
        pass

    def on_disconnect(self):
        if self.player and self.player.island:
            self.player.island.remove_entity(self.player)

        print '{} disconnected'.format(self)
