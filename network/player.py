import random
import struct
from time import clock
import gevent
import gevent.queue

from geventwebsocket import WebSocketError
import logbook
import time
from component import c

import packet_types

packet_header = struct.Struct('>B')
move_to = struct.Struct('>ff')

pong = struct.Struct('>BfHd')
ping = struct.Struct('>H')


class PlayerWebsocket(object):
    def __init__(self, ws):
        self.entity = None
        self.ws = ws
        self.island = None
        self.log = logbook.Logger('PlayerSocket({})'.format(str(id(self))))
        self.packet_queue = gevent.queue.Queue()

    def on_connect(self, island):
        self.log.debug('on_connect')
        self.island = island
        self.handle_login()

        gevent.spawn(self.send_handler)

        while self.recv():
            gevent.sleep(0.001)

        self.handle_logout()

    def recv(self):
        if self.ws is None:
            return None

        data = self.ws.receive()
        now = clock()
        if data is None:
            return None

        packet_type,  = packet_header.unpack_from(data, 0)

        if packet_type == packet_types.PING:
            num, = ping.unpack_from(data, 1)
            self.send(pong.pack(packet_types.PONG, clock(), num, now))
            return True
        elif packet_type == packet_types.CMD_MOVE:
            pass
        elif packet_type == packet_types.CMD_CONTEXTUAL:
            pass
        elif packet_type == packet_types.CMD_MENU_REQ:
            pass
        elif packet_type == packet_types.CMD_MENU_EXEC:
            pass
        else:
            logbook.warn('Unknown packet type: {0}', packet_type)

        return True

    def send(self, data):
        self.packet_queue.put(data)

    def send_handler(self):
        pkt = []
        get = self.packet_queue.get
        empty = self.packet_queue.empty

        while self.ws is not None:
            try:
                while not empty():
                    pkt.append(get())

                if pkt:
                    self.ws.send(''.join(pkt) + '\0', binary=True)
                    pkt = []
            except WebSocketError:
                self.ws = None
                print 'failed send'
                return self.on_disconnect()

            gevent.sleep(1/100.)

        return self.on_disconnect()

    def handle_login(self):
        # assign player to island, send initial bla bla bla

        self.entity = self.island.spawn('meatbag', {
            c.Position: {'x': -10 + random.random() * 20., 'y': -10 + random.random() * 20.},
            c.NetworkViewer: {'socket': self},
            c.NetworkManager: {}
        })

        self.send(struct.pack('>BfI', packet_types.DO_ASSIGN_CONTROL, clock(), self.entity.id))

    def handle_logout(self):
        pass

    def on_disconnect(self):
        self.ws = None
        print '{} disconnected'.format(self)
