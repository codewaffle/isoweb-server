import asyncio
from binascii import hexlify
from queue import Queue
import random
import struct
from isoweb_time import clock
from autobahn.twisted.websocket import WebSocketServerProtocol
from entity import Entity

import logbook
import time
import component
from mathx.vector2 import Vector2

import packet_types
from twisted.internet import task, reactor
from twisted.internet.defer import inlineCallbacks
from util import sleep, to_bytes

packet_header = struct.Struct('>B')
move_to = struct.Struct('>ff')

pong = struct.Struct('>BfHd')
ping = struct.Struct('>H')

_chatters = set()


def broadcast(message_from, message):
    print('[Broadcast] {}: {}'.format(message_from, message))
    pkt = struct.pack(
        '>BfBB{}sH{}s'.format(len(message_from), len(message)),
        *to_bytes([packet_types.MESSAGE, clock(), 1, len(message_from), message_from, len(message), message])
    )

    for ch in _chatters:
        ch.send(pkt)


def entity_text(ent, message):
    print('[EntityText] {}: {}'.format(ent, message))
    pkt = struct.pack(
        '>BfBIH{}s'.format(len(message)),
        *to_bytes([packet_types.MESSAGE, clock(), 3, ent.id, len(message), message])
    )

    for ch in _chatters:
        ch.send(pkt)


class PlayerWebsocket(WebSocketServerProtocol):
    def __init__(self):
        super(PlayerWebsocket, self).__init__()
        self.entity = None
        self.region = None
        self.log = logbook.Logger('PlayerSocket({})'.format(str(id(self))))
        self.packet_queue = Queue()

    def onOpen(self):
        self.log.debug('onOpen()')
        self.send_handler()

    #@inlineCallbacks
    def onMessage(self, payload, isBinary):
        # self.log.debug('onMessage({})', hexlify(payload))


        now = clock()
        if payload is None:
            return

        packet_type,  = packet_header.unpack_from(payload, 0)

        if self.region is None:
            self.handshake(payload)

        if packet_type == packet_types.PING:
            num, = ping.unpack_from(payload, 1)
            # bounce ping back immediately
            self.sendMessage(pong.pack(packet_types.PONG, clock(), num, now) + b'\0', isBinary=True)
            return
        elif packet_type == packet_types.MESSAGE:
            message_len, = struct.unpack_from('>H', payload, 1)
            message, = struct.unpack_from('>{}s'.format(message_len), payload, 3)
            #broadcast(self.entity.name, message)
            entity_text(self.entity, message)

        elif packet_type == packet_types.CMD_CONTEXTUAL_POSITION:
            x, y = struct.unpack_from('>ff', payload, 1)
            # self.log.debug('Move to {}, {}', x, y)
            self.entity.controller.handle_context_position(Vector2(x, y))
        elif packet_type == packet_types.CMD_CONTEXTUAL_ENTITY:
            ent_id, = struct.unpack_from('>I', payload, 1)
            ent = Entity.get(ent_id)
            self.entity.controller.handle_context_entity(ent)
        elif packet_type == packet_types.CMD_MENU_REQ_ENTITY:
            ent_id, = struct.unpack_from('>I', payload, 1)
            ent = Entity.get(ent_id)
            self.log.info('Requesting menu for {}', ent)
            self.entity.controller.handle_menu_req_entity(ent)
        elif packet_type == packet_types.CMD_MENU_EXEC_ENTITY:
            ent_id, str_len = struct.unpack_from('>IB', payload, 1)
            action, = struct.unpack_from('>{}s'.format(str_len), payload, 6)
            ent = Entity.get(ent_id)
            self.log.info('Executing action `{}` on {}', action, ent)
            self.entity.controller.handle_menu_exec_entity(ent, action)
        elif packet_type == packet_types.CMD_MENU_REQ_POSITION:
            print('menreq pos')
        elif packet_type == packet_types.CMD_MENU_EXEC_POSITION:
            print('menexec pos')
        elif packet_types == packet_types.CONTAINER_HIDE:
            ent_id, = struct.unpack_from('>I', payload, 1)
            ent = Entity.get(ent_id)
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
                    self.sendMessage(b''.join(pkt) + b'\0', isBinary=True)
                    pkt = []
            except Exception as E:
                print('failed send')
                self.on_disconnect()
                return

            yield sleep(1/1000)

        self.on_disconnect()
        return

    def handshake(self, payload):
        self.region = self.factory.region
        # read token and match it up.
        # token = struct.unpack_from('>16s', payload, 0)

        # assign player to island, send initial bla bla bla

        self.entity = self.region.spawn(
            'meatbag',
            self.region._island_hax,
            spawn_components={
                'NetworkViewer': {'_socket': self},
                'MeatbagController': {'_socket': self}
            }, pos=Vector2.random_inside(5.0))

        self.entity.parent = self.region._island_hax
        self.entity.Position._update()

        msg = struct.pack('>BfI', packet_types.DO_ASSIGN_CONTROL, clock(), self.entity.id)

        self.send(msg)

        _chatters.add(self)

    def onClose(self, wasClean, code, reason):
        self.on_disconnect()

    def on_disconnect(self):
        _chatters.difference_update({self})
        self.log.info('on_disconnect')
        print('{} disconnected'.format(self))
