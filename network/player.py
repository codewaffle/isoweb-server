import asyncio
from binascii import hexlify
from queue import Queue
import random
import struct
from time import clock
from autobahn.twisted.websocket import WebSocketServerProtocol

import logbook
import time
from component import c
from mathx.vector2 import Vector2

import packet_types
from twisted.internet import task, reactor
from twisted.internet.defer import inlineCallbacks
from util import sleep

packet_header = struct.Struct('>B')
move_to = struct.Struct('>ff')

pong = struct.Struct('>BfHd')
ping = struct.Struct('>H')


class PlayerWebsocket(WebSocketServerProtocol):
    def __init__(self):
        super(PlayerWebsocket, self).__init__()
        self.entity = None
        self.island = None
        self.log = logbook.Logger('PlayerSocket({})'.format(str(id(self))))
        self.packet_queue = Queue()

    def onOpen(self):
        self.send_handler()

    #@inlineCallbacks
    def onMessage(self, payload, isBinary):
        print(hexlify(payload))

        now = clock()
        if payload is None:
            return

        packet_type,  = packet_header.unpack_from(payload, 0)

        if packet_type == packet_types.PING:
            num, = ping.unpack_from(payload, 1)
            # bounce ping back immediately
            self.sendMessage(pong.pack(packet_types.PONG, clock(), num, now) + b'\0', isBinary=True)
            return
        elif packet_type == packet_types.CMD_CONTEXTUAL_POSITION:
            x, y = struct.unpack_from('>ff', payload, 1)
            self.log.debug('Move to {}, {}', x, y)
            self.entity.controller.handle_context_position(Vector2(x, y))
        elif packet_type == packet_types.CMD_CONTEXTUAL_ENTITY:
            ent_id, = struct.unpack_from('>I', payload, 1)
            ent = self.entity.island.get_entity(ent_id)
            self.entity.controller.handle_context_entity(ent)
        elif packet_type == packet_types.CMD_MENU_REQ_ENTITY:
            ent_id, = struct.unpack_from('>I', payload, 1)
            ent = self.entity.island.get_entity(ent_id)
            self.log.info('Requesting menu for {}', ent)
            self.entity.controller.handle_menu_req_entity(ent)
        elif packet_type == packet_types.CMD_MENU_EXEC_ENTITY:
            ent_id, str_len = struct.unpack_from('>IB', payload, 1)
            action, = struct.unpack_from('>{}s'.format(str_len), payload, 6)
            ent = self.entity.island.get_entity(ent_id)
            self.log.info('Executing action `{}` on {}', action, ent)
            self.entity.controller.handle_menu_exec_entity(ent, action)
        elif packet_type == packet_types.CMD_MENU_REQ_POSITION:
            print('menreq pos')
        elif packet_type == packet_types.CMD_MENU_EXEC_POSITION:
            print('menexec pos')
        elif packet_types == packet_types.CONTAINER_HIDE:
            ent_id, = struct.unpack_from('>I', payload, 1)
            ent = self.entity.island.get_entity(ent_id)
            self.entity.controller.handle_hide_container(ent)
        else:
            logbook.warn('Unknown packet type: {0}', packet_type)

        return

    def send(self, data):
        self.packet_queue.put(data)

    @inlineCallbacks
    def send_handler(self):
        pkt = []
        get = self.packet_queue.get
        empty = self.packet_queue.empty

        while True:
            try:
                while not empty():
                    pkt.append(get())

                if pkt:
                    data = b''.join(pkt) + b'\0'
                    print(hexlify(data))
                    self.sendMessage(data, isBinary=True)
                    pkt = []
            except Exception as E:
                print('failed send')
                self.on_disconnect()
                return

            # TODO: gevent sleep
            yield sleep(1/20)

        self.on_disconnect()
        return

    def handle_login(self):
        # assign player to island, send initial bla bla bla

        self.entity = self.island.spawn('meatbag', {
            c.NetworkViewer: {'_socket': self},
            c.MeatbagController: {'_socket': self}
        }, pos=Vector2.random_inside(5.0))

        self.send(struct.pack('>BfI', packet_types.DO_ASSIGN_CONTROL, clock(), self.entity.id))

    def handle_logout(self):
        pass

    def on_disconnect(self):
        self.ws = None
        print('{} disconnected'.format(self))
