from gevent.monkey import patch_all
from config import DB_DIR

patch_all(ssl=False)
from pyximport import pyximport
pyximport.install()


from math import pi
import random
from mathx import Vector2


from logbook.queues import ZeroMQHandler


import gevent
import socket
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket.server import WebSocketServer
import logbook
logbook.default_handler.level = logbook.DEBUG
from network.player import PlayerWebsocket


def reset_db():
    logbook.warn("Resetting Database")
    import shutil, os

    try:
        shutil.rmtree(DB_DIR)
    except:
        pass

    os.mkdir(DB_DIR)
    return True

respawn = False
# respawn = reset_db()


from entitydef import load_defs
load_defs()

from component import c
from island import Island


import logging
logging.basicConfig(level=logging.DEBUG)

from gevent import pywsgi
from web.app import create_app

ws_zmq_handler = ZeroMQHandler('tcp://127.0.0.1:9009', bubble=True)

island = Island(0)
island.log_handler = ws_zmq_handler
island.start()


def spawn_crap(name, num, scalebase=1.0, modscale=0.0, rot=False):
    for x in range(num):
        ent = island.spawn(name, pos=Vector2.random_inside(30))

        if modscale:
            ent.Sprite.data.scale = scalebase + random.random() * modscale
            ent.Position.data.z = ent.Sprite.data.scale / 2.

        if rot:
            ent.Position.data.r = 2.*pi * random.random()

def spawn_all():
    spawn_crap('tree', 1, scalebase=1.5, modscale=1.0)
    #spawn_crap('tree', 20, scalebase=1.5, modscale=1.0)
    spawn_crap('rock', 10, scalebase=1.0, modscale=4.0)
    spawn_crap('crate', 10, rot=True)
    # spawn_crap('log', 15)
    spawn_crap('stone_axe', 5, rot=True)

if respawn:
    spawn_all()

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

# logbook.info('starting webserver on :{0}', web_server.server_port)
# web_server.start()

logbook.info('starting websocket on :{0}', ws_server.server_port)
ws_server.start()
# disable nagle's
ws_server.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

logbook.info('waiting')

def spawn_things():
    pass

gevent.wait()
