from gevent.monkey import patch_all
patch_all(ssl=False)

import random
import gevent
import socket
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket.server import WebSocketServer
import logbook
logbook.default_handler.level = logbook.DEBUG
from entity.player import Player
from websocket.player import PlayerSocket

from world.island import Island


import logging
logging.basicConfig(level=logging.DEBUG)

from gevent import pywsgi
from web.app import create_app

island = Island(42)

def ws_app(env, start):
    if env['PATH_INFO'] == '/player':
        ps = PlayerSocket(env['wsgi.websocket'])
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

logbook.info('starting dev island')
island.start()

logbook.info('waiting')
gevent.wait()
