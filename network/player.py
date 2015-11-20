from queue import Queue
import struct
from isoweb_time import clock
from autobahn.twisted.websocket import WebSocketServerProtocol
from entity import Entity

import logbook
from mathx.vector2 import Vector2

import packet_types
from twisted.internet.defer import inlineCallbacks
from util import sleep, to_bytes
import component
import ujson

packet_header = struct.Struct('>B')
move_to = struct.Struct('>ff')

pong = struct.Struct('>BfHd')
ping = struct.Struct('>H')


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

        try:
            # call registered packet handler
            self.entity.packet_handlers[packet_type](payload)
            return
        except KeyError:
            pass

        # no registered handler, try other types
        if packet_type == packet_types.PING:
            num, = ping.unpack_from(payload, 1)
            # bounce ping back immediately
            self.sendMessage(pong.pack(packet_types.PONG, clock(), num, now) + b'\0', isBinary=True)
            return
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

        meta_json = ujson.dumps({
            'asset_base': 'https://s3.amazonaws.com/demiverse-assets/'
        })

        self.send(struct.pack(
            '>BfH{}s'.format(len(meta_json)),
            packet_types.META, clock(), len(meta_json), to_bytes(meta_json)
        ))

        self.entity = self.region.spawn(
            'meatbag',
            self.region._island_hax,
            spawn_components={
                'NetworkViewer': {'_socket': self},
                'MeatbagController': {'_socket': self},
                'SimpleMovementController': {},
                'ActionController': {'_socket': self},
                'ContainerController': {},
                'CraftingController': {},
                'ChatController': {'_socket': self}
            }, pos=Vector2.random_inside(5.0))

        self.entity.parent = self.region._island_hax
        self.entity.Position._update()

        msg = struct.pack('>BfI', packet_types.DO_ASSIGN_CONTROL, clock(), self.entity.id)

        self.send(msg)

    def onClose(self, wasClean, code, reason):
        self.on_disconnect()

    def on_disconnect(self):
        self.log.info('on_disconnect')
        print('{} disconnected'.format(self))
