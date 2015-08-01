from binascii import hexlify
import random
import struct
from time import clock
import gevent
import gevent.queue

from geventwebsocket import WebSocketError
import logbook
import time
from component import c
from mathx.vector2 import Vector2

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

        # print hexlify(data)

        now = clock()
        if data is None:
            return None

        packet_type,  = packet_header.unpack_from(data, 0)

        if packet_type == packet_types.PING:
            num, = ping.unpack_from(data, 1)
            # bounce ping back immediately
            self.ws.send(pong.pack(packet_types.PONG, clock(), num, now) + '\0', binary=True)
            return True
        elif packet_type == packet_types.CMD_CONTEXTUAL_POSITION:
            x, y = struct.unpack_from('>ff', data, 1)
            self.log.debug('Move to {}, {}', x, y)
            self.entity.controller.handle_context_position(Vector2(x, y))
        elif packet_type == packet_types.CMD_CONTEXTUAL_ENTITY:
            ent_id, = struct.unpack_from('>I', data, 1)
            ent = self.entity.island.get_entity(ent_id)
            
            self.entity.controller.handle_context_entity(ent)
        elif packet_type == packet_types.CMD_MENU_REQ_ENTITY:
            ent_id, = struct.unpack_from('>I', data, 1)
            ent = self.entity.island.get_entity(ent_id)
            self.log.info('Requesting menu for {}', ent)
            self.entity.controller.handle_menu_req_entity(ent)
        elif packet_type == packet_types.CMD_MENU_EXEC_ENTITY:
            ent_id, str_len = struct.unpack_from('>IB', data, 1)
            action, = struct.unpack_from('>{}s'.format(str_len), data, 6)
            ent = self.entity.island.get_entity(ent_id)
            self.log.info('Executing action `{}` on {}', action, ent)
            self.entity.controller.handle_menu_exec_entity(ent, action)
        elif packet_type == packet_types.CMD_MENU_REQ_POSITION:
            print 'menreq pos'
        elif packet_type == packet_types.CMD_MENU_EXEC_POSITION:
            print 'menexec pos'
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

            gevent.sleep(1/1000.)

        return self.on_disconnect()

    def handle_login(self):
        # assign player to island, send initial bla bla bla

        self.entity = self.island.spawn('meatbag', {
            c.NetworkViewer: {'socket': self},
            c.MeatbagController: {'socket': self}
        }, pos=Vector2.random_inside(15.0))

        self.send(struct.pack('>BfI', packet_types.DO_ASSIGN_CONTROL, clock(), self.entity.id))

    def handle_logout(self):
        pass

    def on_disconnect(self):
        self.ws = None
        print '{} disconnected'.format(self)
