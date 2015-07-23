from math import pi
import random
from gevent.monkey import patch_all

patch_all(ssl=False)
from pyximport import pyximport
pyximport.install()

from logbook.queues import ZeroMQHandler


import gevent
import socket
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket.server import WebSocketServer
import logbook
logbook.default_handler.level = logbook.DEBUG
from network.player import PlayerWebsocket


from entitydef import load_defs
load_defs()

from component import c
from island import Island


import logging
logging.basicConfig(level=logging.DEBUG)

from gevent import pywsgi
from web.app import create_app

ws_zmq_handler = ZeroMQHandler('tcp://127.0.0.1:9009', bubble=True)

island = Island()
island.log_handler = ws_zmq_handler
island.start()

# spawn a buncha treez
for x in range(100):
    ent = island.spawn('tree', {
        c.Position: {'x': -60. + random.random() * 120., 'y': -60. + random.random() * 120.},
        c.NetworkManager: {},
        #c.Crawler: {}
    })
    ent.Sprite.data.scale = 1.5 + random.random()
    ent.Position.data.r = 2.*pi * random.random()
    ent.Position.data.z = ent.Sprite.data.scale / 2.

for x2 in range(12):
    e = island.spawn('meatbag', {
        c.Position: {'x': -256. + random.random() * 512., 'y': -256. + random.random() * 512.},
        c.NetworkManager: {},
        c.SimpleWander: {
            'velocity': 7.5
        }
    })


for x3 in range(50):
    e = island.spawn('rock', {
        c.Position: {'x': -60. + random.random() * 120., 'y': -60. + random.random() * 120.},
        c.NetworkManager: {}
    })
    e.Sprite.data.scale = 1.5 + random.random()
    e.Position.data.r = 2. * pi * random.random()

for x4 in range(5):
    e = island.spawn('crate', {
        c.Position: {'x': -60. + random.random() * 120., 'y': -60. + random.random() * 120.},
        c.NetworkManager: {}
    })
    # e.Mesh.data.scale = 1.5 + random.random()
    e.Position.data.r = 2. * pi * random.random()

def ws_app(env, start):
    if env['PATH_INFO'] == '/player':
        ws = env['wsgi.websocket']
        ws.stream.handler.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        ps = PlayerWebsocket(ws)

        return ps.on_connect(island)

ws_server = WebSocketServer(
    ('', 10000),
    ws_app,
    handler_class=WebSocketHandler
)

web_server = pywsgi.WSGIServer(
    ("", 9000),
    create_app()
)

logbook.info('starting webserver on :{0}', web_server.server_port)
web_server.start()

logbook.info('starting websocket on :{0}', ws_server.server_port)
ws_server.start()
# disable nagle's
ws_server.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

logbook.info('waiting')

def spawn_things():
    pass

gevent.wait()
