import random
import struct
import gevent

from geventwebsocket import WebSocketError
import logbook
import time
from component import c

import packet_types

packet_header = struct.Struct('>H')
move_to = struct.Struct('>ff')

pong = struct.Struct('>HdHd')
ping = struct.Struct('>H')

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
            gevent.sleep()

        self.handle_logout()

    def recv(self):
        if self.ws is None:
            return None

        data = self.ws.receive()
        now = time.time()
        if data is None:
            return None

        packet_type,  = packet_header.unpack_from(data, 0)

        if packet_type == packet_types.PING:
            num, = ping.unpack_from(data, 2)
            self.send(pong.pack(packet_types.PONG, time.time(), num, now))
            return True

        logbook.warn('Unknown packet type: {0}', packet_type)
        return False

    def send(self, data):
        if self.ws is None:
            return

        # DEBUG?
        try:
            self.ws.send(data, binary=True)
        except WebSocketError:
            self.ws = None
            return self.on_disconnect()

    def handle_login(self):
        # assign player to island, send initial bla bla bla

        self.entity = self.island.spawn('meatbag', {
            c.Position: {'x': -10 + random.random() * 20., 'y': -10 + random.random() * 20.},
            c.NetworkViewer: {'socket': self},
            c.NetworkManager: {}
        })

    def handle_logout(self):
        pass

    def on_disconnect(self):
        self.ws = None
        print '{} disconnected'.format(self)
